package com.showcase.partsinventory.model;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ReserveOrOrderRequest(
        @NotBlank String partKey,
        @NotNull @Min(1) Integer qty,
        String caseId,
        String assetId,
        String reason
) {}
