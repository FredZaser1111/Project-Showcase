package com.showcase.partsinventory.controller;

import com.showcase.partsinventory.model.AgentCaseRequest;
import com.showcase.partsinventory.model.OpenApproval;
import com.showcase.partsinventory.model.PoApprovalWebhookRequest;
import com.showcase.partsinventory.repository.AgentCaseRepository;
import com.showcase.partsinventory.repository.ApprovalQueueRepository;
import com.showcase.partsinventory.repository.WorkflowEventRepository;
import com.showcase.partsinventory.service.ApprovalWebhookService;
import jakarta.validation.Valid;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class IntegrationController {

    private final ApprovalWebhookService webhooks;
    private final ApprovalQueueRepository approvals;
    private final AgentCaseRepository cases;
    private final WorkflowEventRepository events;
    private final NamedParameterJdbcTemplate jdbc;

    public IntegrationController(
            ApprovalWebhookService webhooks,
            ApprovalQueueRepository approvals,
            AgentCaseRepository cases,
            WorkflowEventRepository events,
            NamedParameterJdbcTemplate jdbc
    ) {
        this.webhooks = webhooks;
        this.approvals = approvals;
        this.cases = cases;
        this.events = events;
        this.jdbc = jdbc;
    }

    @PostMapping("/webhooks/po-approved")
    public Map<String, Object> poApproved(@Valid @RequestBody PoApprovalWebhookRequest request) {
        return webhooks.handlePoApproved(request);
    }

    @GetMapping("/approvals")
    public List<OpenApproval> openApprovals() {
        return approvals.listOpen();
    }

    @GetMapping("/views/parts-on-hand")
    public List<Map<String, Object>> partsOnHand() {
        return jdbc.query("SELECT * FROM v_parts_on_hand ORDER BY part_key", (rs, rowNum) -> Map.of(
                "part_key", rs.getString("part_key"),
                "sku", rs.getString("sku"),
                "description", rs.getString("description"),
                "unit_cost", rs.getBigDecimal("unit_cost"),
                "supplier", rs.getString("supplier"),
                "reorder_point", rs.getInt("reorder_point"),
                "qty_on_hand", rs.getInt("qty_on_hand"),
                "in_stock", rs.getBoolean("in_stock"),
                "below_reorder_point", rs.getBoolean("below_reorder_point")
        ));
    }

    @PostMapping("/cases")
    public Map<String, Object> upsertCase(@Valid @RequestBody AgentCaseRequest request) {
        cases.upsert(
                request.caseId(),
                request.project(),
                request.assetId(),
                request.decision(),
                request.payload()
        );
        return Map.of("caseId", request.caseId(), "status", "upserted");
    }

    @GetMapping("/cases")
    public List<Map<String, Object>> listCases(@RequestParam(defaultValue = "20") int limit) {
        return cases.listRecent(Math.min(Math.max(limit, 1), 100));
    }

    @GetMapping("/workflow-events")
    public List<Map<String, Object>> workflowEvents(
            @RequestParam(required = false) String caseId,
            @RequestParam(defaultValue = "20") int limit
    ) {
        return events.listRecent(caseId, Math.min(Math.max(limit, 1), 100));
    }
}
