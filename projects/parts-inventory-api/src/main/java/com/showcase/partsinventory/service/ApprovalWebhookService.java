package com.showcase.partsinventory.service;

import com.showcase.partsinventory.model.MovementRequest;
import com.showcase.partsinventory.model.OpenApproval;
import com.showcase.partsinventory.model.PoApprovalWebhookRequest;
import com.showcase.partsinventory.model.StockMovement;
import com.showcase.partsinventory.repository.ApprovalQueueRepository;
import com.showcase.partsinventory.repository.PurchaseOrderRepository;
import com.showcase.partsinventory.repository.WorkflowEventRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

@Service
public class ApprovalWebhookService {

    private final ApprovalQueueRepository approvals;
    private final PurchaseOrderRepository purchaseOrders;
    private final InventoryService inventory;
    private final WorkflowEventRepository events;

    public ApprovalWebhookService(
            ApprovalQueueRepository approvals,
            PurchaseOrderRepository purchaseOrders,
            InventoryService inventory,
            WorkflowEventRepository events
    ) {
        this.approvals = approvals;
        this.purchaseOrders = purchaseOrders;
        this.inventory = inventory;
        this.events = events;
    }

    @Transactional
    public Map<String, Object> handlePoApproved(PoApprovalWebhookRequest request) {
        OpenApproval row = approvals.findByIdAnyStatus(request.approvalId())
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Unknown approval: " + request.approvalId()));

        if (!"pending_manager_approval".equals(row.approvalStatus())) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "Approval already decided: " + row.approvalStatus()
            );
        }

        String decision = request.decision().trim().toLowerCase(Locale.ROOT);
        boolean approved = decision.equals("approved") || decision.equals("approve");
        boolean rejected = decision.equals("rejected") || decision.equals("reject") || decision.equals("denied");
        if (!approved && !rejected) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "decision must be approved or rejected"
            );
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("approvalId", row.approvalId());
        result.put("poId", row.poId());
        result.put("caseId", row.caseId());

        if (rejected) {
            approvals.updateStatus(row.approvalId(), "rejected");
            purchaseOrders.updateStatus(row.poId(), "rejected");
            events.append(
                    "po_rejected",
                    row.partKey(),
                    row.caseId(),
                    Map.of(
                            "approval_id", row.approvalId(),
                            "po_id", row.poId().toString(),
                            "note", request.note() == null ? "" : request.note()
                    )
            );
            result.put("status", "rejected");
            result.put("movement", null);
            return result;
        }

        approvals.updateStatus(row.approvalId(), "approved");
        purchaseOrders.updateStatus(row.poId(), "approved");
        events.append(
                "po_approved",
                row.partKey(),
                row.caseId(),
                Map.of(
                        "approval_id", row.approvalId(),
                        "po_id", row.poId().toString(),
                        "note", request.note() == null ? "" : request.note()
                )
        );

        StockMovement movement = null;
        boolean receive = request.receiveStock() == null || Boolean.TRUE.equals(request.receiveStock());
        if (receive) {
            movement = inventory.appendMovement(new MovementRequest(
                    row.partKey(),
                    "RECEIPT",
                    row.qty(),
                    row.caseId(),
                    "PO approved receipt " + row.poId()
            ));
            purchaseOrders.updateStatus(row.poId(), "received");
            events.append(
                    "po_received",
                    row.partKey(),
                    row.caseId(),
                    Map.of(
                            "po_id", row.poId().toString(),
                            "movement_id", movement.movementId().toString(),
                            "qty", row.qty()
                    )
            );
        }

        result.put("status", receive ? "approved_and_received" : "approved");
        result.put("movement", movement);
        return result;
    }
}
