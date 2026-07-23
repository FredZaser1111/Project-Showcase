package com.showcase.partsinventory.repository;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Repository
public class WorkflowEventRepository {

    private final NamedParameterJdbcTemplate jdbc;
    private final ObjectMapper objectMapper;

    public WorkflowEventRepository(NamedParameterJdbcTemplate jdbc, ObjectMapper objectMapper) {
        this.jdbc = jdbc;
        this.objectMapper = objectMapper;
    }

    public UUID append(String eventType, String partKey, String caseId, Map<String, Object> detail) {
        UUID id = UUID.randomUUID();
        String json;
        try {
            json = objectMapper.writeValueAsString(detail == null ? Map.of() : detail);
        } catch (JsonProcessingException e) {
            json = "{}";
        }
        String sql = """
                INSERT INTO workflow_events (event_id, event_type, part_key, case_id, detail)
                VALUES (:id, :eventType, :partKey, :caseId, CAST(:detail AS jsonb))
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("eventType", eventType)
                .addValue("partKey", partKey)
                .addValue("caseId", caseId)
                .addValue("detail", json));
        return id;
    }

    public List<Map<String, Object>> listRecent(String caseId, int limit) {
        StringBuilder sql = new StringBuilder("""
                SELECT event_id::text AS event_id, event_type, part_key, case_id, detail::text AS detail, created_at
                FROM workflow_events
                """);
        MapSqlParameterSource params = new MapSqlParameterSource();
        if (caseId != null && !caseId.isBlank()) {
            sql.append(" WHERE case_id = :caseId");
            params.addValue("caseId", caseId);
        }
        sql.append(" ORDER BY created_at DESC LIMIT :limit");
        params.addValue("limit", limit);
        return jdbc.query(sql.toString(), params, (rs, rowNum) -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("event_id", rs.getString("event_id"));
            row.put("event_type", rs.getString("event_type"));
            row.put("part_key", rs.getString("part_key"));
            row.put("case_id", rs.getString("case_id"));
            row.put("detail", rs.getString("detail"));
            Timestamp ts = rs.getTimestamp("created_at");
            OffsetDateTime created = ts == null ? null : ts.toInstant().atOffset(ZoneOffset.UTC);
            row.put("created_at", created);
            return row;
        });
    }
}
