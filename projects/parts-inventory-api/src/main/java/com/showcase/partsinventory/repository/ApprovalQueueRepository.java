package com.showcase.partsinventory.repository;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public class ApprovalQueueRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public ApprovalQueueRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public String nextApprovalId() {
        Integer seq = jdbc.getJdbcTemplate().queryForObject("SELECT nextval('approval_seq')", Integer.class);
        int n = seq == null ? 1000 : seq;
        return "APPR-" + n;
    }

    public String append(UUID poId, String status, String caseId) {
        String approvalId = nextApprovalId();
        String sql = """
                INSERT INTO approval_queue (approval_id, po_id, status, case_id)
                VALUES (:approvalId, :poId, :status, :caseId)
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("approvalId", approvalId)
                .addValue("poId", poId)
                .addValue("status", status)
                .addValue("caseId", caseId));
        return approvalId;
    }
}
