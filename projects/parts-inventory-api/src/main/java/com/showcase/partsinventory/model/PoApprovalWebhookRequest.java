package com.showcase.partsinventory.model;

import jakarta.validation.constraints.NotBlank;

public record PoApprovalWebhookRequest(
        @NotBlank String approvalId,
        @NotBlank String decision,
        Boolean receiveStock,
        String note
) {}
