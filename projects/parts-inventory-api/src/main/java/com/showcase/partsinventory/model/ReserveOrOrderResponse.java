package com.showcase.partsinventory.model;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

/**
 * Shape expected by predictive-maintenance-agent tools when calling the live API.
 */
public record ReserveOrOrderResponse(
        String decision,
        boolean partsInStock,
        PartInventory inventory,
        StockMovement movement,
        PurchaseOrderView purchaseOrder,
        String approvalQueueId,
        String eventType
) {
    public record PurchaseOrderView(
            UUID poId,
            String partKey,
            String sku,
            String supplier,
            int qty,
            BigDecimal unitCost,
            boolean inStockAtDraft,
            String status,
            String approvalQueueId,
            String assetId,
            String caseId,
            String narrative
    ) {}

    public Map<String, Object> inventoryMap() {
        return Map.of(
                "part_key", inventory.partKey(),
                "found", inventory.found(),
                "sku", inventory.sku() == null ? "" : inventory.sku(),
                "qty", inventory.qty(),
                "unit_cost", inventory.unitCost() == null ? 0 : inventory.unitCost().doubleValue(),
                "supplier", inventory.supplier() == null ? "" : inventory.supplier(),
                "in_stock", inventory.inStock()
        );
    }
}
