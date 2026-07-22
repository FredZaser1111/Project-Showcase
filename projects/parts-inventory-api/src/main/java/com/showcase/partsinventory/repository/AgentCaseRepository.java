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

@Repository
public class AgentCaseRepository {

    private final NamedParameterJdbcTemplate jdbc;
    private final ObjectMapper objectMapper;

    public AgentCaseRepository(NamedParameterJdbcTemplate jdbc, ObjectMapper objectMapper) {
        this.jdbc = jdbc;
        this.objectMapper = objectMapper;
    }

    public void upsert(String caseId, String project, String assetId, String decision, Map<String, Object> payload) {
        String json;
        try {
            json = objectMapper.writeValueAsString(payload == null ? Map.of() : payload);
        } catch (JsonProcessingException e) {
            json = "{}";
        }
        String sql = """
                INSERT INTO agent_cases (case_id, project, asset_id, decision, payload)
                VALUES (:caseId, :project, :assetId, :decision, CAST(:payload AS jsonb))
                ON CONFLICT (case_id) DO UPDATE SET
                    project = EXCLUDED.project,
                    asset_id = EXCLUDED.asset_id,
                    decision = EXCLUDED.decision,
                    payload = EXCLUDED.payload,
                    created_at = NOW()
                """;
        jdbc.update(sql, new MapSqlParameterSource()
                .addValue("caseId", caseId)
                .addValue("project", project == null ? "predictive-maintenance-agent" : project)
                .addValue("assetId", assetId)
                .addValue("decision", decision == null ? "" : decision)
                .addValue("payload", json));
    }

    public List<Map<String, Object>> listRecent(int limit) {
        String sql = """
                SELECT case_id, project, asset_id, decision, payload::text AS payload, created_at
                FROM agent_cases
                ORDER BY created_at DESC
                LIMIT :limit
                """;
        return jdbc.query(sql, new MapSqlParameterSource("limit", limit), (rs, rowNum) -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("caseId", rs.getString("case_id"));
            row.put("project", rs.getString("project"));
            row.put("assetId", rs.getString("asset_id"));
            row.put("decision", rs.getString("decision"));
            row.put("payload", rs.getString("payload"));
            Timestamp ts = rs.getTimestamp("created_at");
            OffsetDateTime created = ts == null ? null : ts.toInstant().atOffset(ZoneOffset.UTC);
            row.put("createdAt", created);
            return row;
        });
    }
}
