package com.showcase.partsinventory.model;

import java.time.OffsetDateTime;
import java.util.UUID;

public record StockMovement(
        UUID movementId,
        String partKey,
        String movementType,
        int qtyDelta,
        int balanceAfter,
        String caseId,
        String reason,
        OffsetDateTime createdAt
) {}
