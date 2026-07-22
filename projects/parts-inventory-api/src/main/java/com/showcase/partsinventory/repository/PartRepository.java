package com.showcase.partsinventory.repository;

import com.showcase.partsinventory.model.PartInventory;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public class PartRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public PartRepository(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<PartInventory> findAll() {
        String sql = """
                SELECT p.part_key, p.sku, p.description, p.unit_cost, p.supplier, p.reorder_point,
                       COALESCE(s.qty_on_hand, 0) AS qty_on_hand
                FROM parts p
                LEFT JOIN stock_levels s ON s.part_key = p.part_key
                ORDER BY p.part_key
                """;
        return jdbc.query(sql, (rs, rowNum) -> mapRow(rs.getString("part_key"),
                rs.getString("sku"),
                rs.getString("description"),
                rs.getBigDecimal("unit_cost"),
                rs.getString("supplier"),
                rs.getInt("reorder_point"),
                rs.getInt("qty_on_hand")));
    }

    public Optional<PartInventory> findByKey(String partKey) {
        String sql = """
                SELECT p.part_key, p.sku, p.description, p.unit_cost, p.supplier, p.reorder_point,
                       COALESCE(s.qty_on_hand, 0) AS qty_on_hand
                FROM parts p
                LEFT JOIN stock_levels s ON s.part_key = p.part_key
                WHERE p.part_key = :partKey
                """;
        List<PartInventory> rows = jdbc.query(sql, new MapSqlParameterSource("partKey", partKey),
                (rs, rowNum) -> mapRow(rs.getString("part_key"),
                        rs.getString("sku"),
                        rs.getString("description"),
                        rs.getBigDecimal("unit_cost"),
                        rs.getString("supplier"),
                        rs.getInt("reorder_point"),
                        rs.getInt("qty_on_hand")));
        return rows.stream().findFirst();
    }

    public int lockQty(String partKey) {
        String sql = """
                SELECT qty_on_hand FROM stock_levels
                WHERE part_key = :partKey
                FOR UPDATE
                """;
        Integer qty = jdbc.queryForObject(sql, new MapSqlParameterSource("partKey", partKey), Integer.class);
        return qty == null ? 0 : qty;
    }

    public void updateQty(String partKey, int newQty) {
        String sql = """
                UPDATE stock_levels
                SET qty_on_hand = :qty, updated_at = NOW()
                WHERE part_key = :partKey
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("partKey", partKey)
                .addValue("qty", newQty));
    }

    private static PartInventory mapRow(
            String partKey,
            String sku,
            String description,
            BigDecimal unitCost,
            String supplier,
            int reorderPoint,
            int qty
    ) {
        return new PartInventory(partKey, sku, description, unitCost, supplier, reorderPoint, qty, true, qty > 0);
    }
}
