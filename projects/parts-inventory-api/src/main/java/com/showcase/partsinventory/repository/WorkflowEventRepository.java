package com.showcase.partsinventory.repository;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

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
}
