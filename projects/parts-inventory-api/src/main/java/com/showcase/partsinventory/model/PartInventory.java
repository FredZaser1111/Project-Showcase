package com.showcase.partsinventory.model;

import java.math.BigDecimal;

public record PartInventory(
        String partKey,
        String sku,
        String description,
        BigDecimal unitCost,
        String supplier,
        int reorderPoint,
        int qty,
        boolean found,
        boolean inStock
) {
    public static PartInventory notFound(String partKey) {
        return new PartInventory(partKey, null, null, null, null, 0, 0, false, false);
    }
}
