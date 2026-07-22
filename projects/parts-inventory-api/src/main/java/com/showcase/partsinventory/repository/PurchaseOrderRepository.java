package com.showcase.partsinventory.repository;

import com.showcase.partsinventory.model.PurchaseOrder;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;

@Repository
public class PurchaseOrderRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public PurchaseOrderRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public PurchaseOrder append(
            String partKey,
            String sku,
            String supplier,
            int qty,
            BigDecimal unitCost,
            String status,
            String caseId,
            String assetId,
            String narrative
    ) {
        UUID id = UUID.randomUUID();
        String sql = """
                INSERT INTO purchase_orders
                    (po_id, part_key, sku, supplier, qty, unit_cost, status, case_id, asset_id, narrative)
                VALUES
                    (:id, :partKey, :sku, :supplier, :qty, :unitCost, :status, :caseId, :assetId, :narrative)
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("partKey", partKey)
                .addValue("sku", sku)
                .addValue("supplier", supplier)
                .addValue("qty", qty)
                .addValue("unitCost", unitCost)
                .addValue("status", status)
                .addValue("caseId", caseId)
                .addValue("assetId", assetId)
                .addValue("narrative", narrative == null ? "" : narrative));
        return findById(id);
    }

    public PurchaseOrder findById(UUID id) {
        String sql = """
                SELECT po_id, part_key, sku, supplier, qty, unit_cost, status, case_id, asset_id, narrative, created_at
                FROM purchase_orders WHERE po_id = :id
                """;
        return jdbc.queryForObject(sql, new MapSqlParameterSource("id", id), (rs, rowNum) -> map(rs));
    }

    public List<PurchaseOrder> findOpen() {
        String sql = """
                SELECT po_id, part_key, sku, supplier, qty, unit_cost, status, case_id, asset_id, narrative, created_at
                FROM purchase_orders
                WHERE status <> 'closed'
                ORDER BY created_at DESC
                """;
        return jdbc.query(sql, (rs, rowNum) -> map(rs));
    }

    private static PurchaseOrder map(java.sql.ResultSet rs) throws java.sql.SQLException {
        Timestamp ts = rs.getTimestamp("created_at");
        return new PurchaseOrder(
                (UUID) rs.getObject("po_id"),
                rs.getString("part_key"),
                rs.getString("sku"),
                rs.getString("supplier"),
                rs.getInt("qty"),
                rs.getBigDecimal("unit_cost"),
                rs.getString("status"),
                rs.getString("case_id"),
                rs.getString("asset_id"),
                rs.getString("narrative"),
                ts == null ? null : ts.toInstant().atOffset(ZoneOffset.UTC)
        );
    }
}
