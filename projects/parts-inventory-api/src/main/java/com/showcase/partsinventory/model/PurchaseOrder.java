package com.showcase.partsinventory.model;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

public record PurchaseOrder(
        UUID poId,
        String partKey,
        String sku,
        String supplier,
        int qty,
        BigDecimal unitCost,
        String status,
        String caseId,
        String assetId,
        String narrative,
        OffsetDateTime createdAt
) {}
