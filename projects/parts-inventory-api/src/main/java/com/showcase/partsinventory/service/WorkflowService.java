package com.showcase.partsinventory.service;

import com.showcase.partsinventory.model.PartInventory;
import com.showcase.partsinventory.model.PurchaseOrder;
import com.showcase.partsinventory.model.ReserveOrOrderRequest;
import com.showcase.partsinventory.model.ReserveOrOrderResponse;
import com.showcase.partsinventory.model.StockMovement;
import com.showcase.partsinventory.repository.ApprovalQueueRepository;
import com.showcase.partsinventory.repository.PartRepository;
import com.showcase.partsinventory.repository.PurchaseOrderRepository;
import com.showcase.partsinventory.repository.StockMovementRepository;
import com.showcase.partsinventory.repository.WorkflowEventRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

@Service
public class WorkflowService {

    private final PartRepository parts;
    private final StockMovementRepository movements;
    private final PurchaseOrderRepository purchaseOrders;
    private final ApprovalQueueRepository approvals;
    private final WorkflowEventRepository events;

    public WorkflowService(
            PartRepository parts,
            StockMovementRepository movements,
            PurchaseOrderRepository purchaseOrders,
            ApprovalQueueRepository approvals,
            WorkflowEventRepository events
    ) {
        this.parts = parts;
        this.movements = movements;
        this.purchaseOrders = purchaseOrders;
        this.approvals = approvals;
        this.events = events;
    }

    public List<PurchaseOrder> listOpenPurchaseOrders() {
        return purchaseOrders.findOpen();
    }

    /**
     * Core automation: if on-hand covers need, append RESERVE; else append PO + approval queue.
     */
    @Transactional
    public ReserveOrOrderResponse reserveOrOrder(ReserveOrOrderRequest request) {
        PartInventory part = parts.findByKey(request.partKey())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown part: " + request.partKey()));

        events.append(
                "inventory_checked",
                request.partKey(),
                request.caseId(),
                Map.of("qty", part.qty(), "need", request.qty())
        );

        int onHand = parts.lockQty(request.partKey());
        boolean canReserve = onHand >= request.qty();

        if (canReserve) {
            int newBalance = onHand - request.qty();
            StockMovement movement = movements.append(
                    request.partKey(),
                    "RESERVE",
                    -request.qty(),
                    newBalance,
                    request.caseId(),
                    request.reason() == null ? "Predictive maintenance reserve" : request.reason()
            );
            parts.updateQty(request.partKey(), newBalance);
            events.append(
                    "reserved",
                    request.partKey(),
                    request.caseId(),
                    Map.of(
                            "movement_id", movement.movementId().toString(),
                            "qty", request.qty(),
                            "balance_after", newBalance
                    )
            );

            PartInventory refreshed = parts.findByKey(request.partKey()).orElse(part);
            return new ReserveOrOrderResponse(
                    "reserve_and_schedule_pm",
                    true,
                    refreshed,
                    movement,
                    null,
                    null,
                    "reserved"
            );
        }

        String narrative = String.format(
                "Purchase Order DRAFT for %s%nSupplier: %s%nSKU: %s x %d @ $%s%nReason: %s%nStock status: OUT OF STOCK — expedite order.",
                request.assetId() == null ? "asset" : request.assetId(),
                part.supplier(),
                part.sku(),
                request.qty(),
                part.unitCost(),
                request.reason() == null ? "Predictive maintenance shortfall" : request.reason()
        );

        PurchaseOrder po = purchaseOrders.append(
                part.partKey(),
                part.sku(),
                part.supplier(),
                request.qty(),
                part.unitCost(),
                "pending_manager_approval",
                request.caseId(),
                request.assetId(),
                narrative
        );
        String approvalId = approvals.append(po.poId(), "pending_manager_approval", request.caseId());
        events.append(
                "po_drafted",
                request.partKey(),
                request.caseId(),
                Map.of(
                        "po_id", po.poId().toString(),
                        "approval_queue_id", approvalId,
                        "qty", request.qty()
                )
        );

        ReserveOrOrderResponse.PurchaseOrderView view = new ReserveOrOrderResponse.PurchaseOrderView(
                po.poId(),
                po.partKey(),
                po.sku(),
                po.supplier(),
                po.qty(),
                po.unitCost(),
                false,
                po.status(),
                approvalId,
                po.assetId(),
                po.caseId(),
                po.narrative()
        );

        return new ReserveOrOrderResponse(
                "expedite_po_pending_approval",
                false,
                part,
                null,
                view,
                approvalId,
                "po_drafted"
        );
    }
}
