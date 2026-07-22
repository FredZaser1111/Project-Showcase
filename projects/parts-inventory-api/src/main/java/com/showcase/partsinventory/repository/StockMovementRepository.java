package com.showcase.partsinventory.repository;

import com.showcase.partsinventory.model.StockMovement;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;

@Repository
public class StockMovementRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public StockMovementRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public StockMovement append(
            String partKey,
            String movementType,
            int qtyDelta,
            int balanceAfter,
            String caseId,
            String reason
    ) {
        UUID id = UUID.randomUUID();
        String sql = """
                INSERT INTO stock_movements
                    (movement_id, part_key, movement_type, qty_delta, balance_after, case_id, reason)
                VALUES
                    (:id, :partKey, :type, :qtyDelta, :balanceAfter, :caseId, :reason)
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("partKey", partKey)
                .addValue("type", movementType)
                .addValue("qtyDelta", qtyDelta)
                .addValue("balanceAfter", balanceAfter)
                .addValue("caseId", caseId)
                .addValue("reason", reason == null ? "" : reason));

        return findById(id);
    }

    public StockMovement findById(UUID id) {
        String sql = """
                SELECT movement_id, part_key, movement_type, qty_delta, balance_after, case_id, reason, created_at
                FROM stock_movements WHERE movement_id = :id
                """;
        return jdbc.queryForObject(sql, new MapSqlParameterSource("id", id), (rs, rowNum) -> new StockMovement(
                (UUID) rs.getObject("movement_id"),
                rs.getString("part_key"),
                rs.getString("movement_type"),
                rs.getInt("qty_delta"),
                rs.getInt("balance_after"),
                rs.getString("case_id"),
                rs.getString("reason"),
                toOffset(rs.getTimestamp("created_at"))
        ));
    }

    public List<StockMovement> findAll(String partKey) {
        StringBuilder sql = new StringBuilder("""
                SELECT movement_id, part_key, movement_type, qty_delta, balance_after, case_id, reason, created_at
                FROM stock_movements
                """);
        MapSqlParameterSource params = new MapSqlParameterSource();
        if (partKey != null && !partKey.isBlank()) {
            sql.append(" WHERE part_key = :partKey");
            params.addValue("partKey", partKey);
        }
        sql.append(" ORDER BY created_at DESC");
        return jdbc.query(sql.toString(), params, (rs, rowNum) -> new StockMovement(
                (UUID) rs.getObject("movement_id"),
                rs.getString("part_key"),
                rs.getString("movement_type"),
                rs.getInt("qty_delta"),
                rs.getInt("balance_after"),
                rs.getString("case_id"),
                rs.getString("reason"),
                toOffset(rs.getTimestamp("created_at"))
        ));
    }

    private static OffsetDateTime toOffset(Timestamp ts) {
        return ts == null ? null : ts.toInstant().atOffset(ZoneOffset.UTC);
    }
}
