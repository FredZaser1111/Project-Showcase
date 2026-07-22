package com.showcase.partsinventory.repository;

import com.showcase.partsinventory.model.OpenApproval;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
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

    public void updateStatus(String approvalId, String status) {
        String sql = "UPDATE approval_queue SET status = :status WHERE approval_id = :approvalId";
        int updated = jdbc.update(sql, new MapSqlParameterSource()
                .addValue("approvalId", approvalId)
                .addValue("status", status));
        if (updated == 0) {
            throw new EmptyResultDataAccessException("Unknown approval_id: " + approvalId, 1);
        }
    }

    public Optional<OpenApproval> findByIdAnyStatus(String approvalId) {
        String sql = """
                SELECT a.approval_id,
                       a.status AS approval_status,
                       a.case_id,
                       a.created_at AS queued_at,
                       po.po_id,
                       po.part_key,
                       po.sku,
                       po.supplier,
                       po.qty,
                       po.unit_cost,
                       po.asset_id,
                       po.status AS po_status,
                       po.narrative
                FROM approval_queue a
                JOIN purchase_orders po ON po.po_id = a.po_id
                WHERE a.approval_id = :approvalId
                """;
        List<OpenApproval> rows = jdbc.query(sql, new MapSqlParameterSource("approvalId", approvalId),
                (rs, rowNum) -> mapOpen(rs));
        return rows.stream().findFirst();
    }

    public List<OpenApproval> listOpen() {
        String sql = """
                SELECT approval_id, approval_status, case_id, queued_at, po_id, part_key, sku, supplier,
                       qty, unit_cost, asset_id, po_status, narrative
                FROM v_open_approvals
                """;
        return jdbc.query(sql, (rs, rowNum) -> mapOpen(rs));
    }

    private static OpenApproval mapOpen(java.sql.ResultSet rs) throws java.sql.SQLException {
        Timestamp ts = rs.getTimestamp("queued_at");
        return new OpenApproval(
                rs.getString("approval_id"),
                rs.getString("approval_status"),
                rs.getString("case_id"),
                ts == null ? null : ts.toInstant().atOffset(ZoneOffset.UTC),
                (UUID) rs.getObject("po_id"),
                rs.getString("part_key"),
                rs.getString("sku"),
                rs.getString("supplier"),
                rs.getInt("qty"),
                rs.getBigDecimal("unit_cost"),
                rs.getString("asset_id"),
                rs.getString("po_status"),
                rs.getString("narrative")
        );
    }
}
