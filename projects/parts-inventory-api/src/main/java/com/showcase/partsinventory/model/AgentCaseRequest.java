package com.showcase.partsinventory.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.Map;

public record AgentCaseRequest(
        @NotBlank String caseId,
        String project,
        String assetId,
        String decision,
        @NotNull Map<String, Object> payload
) {}
