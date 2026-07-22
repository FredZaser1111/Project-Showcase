package com.showcase.partsinventory.model;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

public record OpenApproval(
        String approvalId,
        String approvalStatus,
        String caseId,
        OffsetDateTime queuedAt,
        UUID poId,
        String partKey,
        String sku,
        String supplier,
        int qty,
        BigDecimal unitCost,
        String assetId,
        String poStatus,
        String narrative
) {}
