# Parts Inventory API

Spring Boot 3 + **JDBC** + **PostgreSQL** spare-parts inventory service. Demonstrates Appian-style skills: relational SQL, REST integration, and automated workflows that **append** stock-movement / PO / approval records (not silent overwrites).

Pairs with [predictive-maintenance-agent](../automated-workflows/predictive-maintenance-agent/): score → HTTP inventory check → append RESERVE or PO rows → HITL approval case packet.

Cozy commerce Postgres (listing-orchestrator ledger Phase 2) uses the same append-ledger idea in a different domain—this project is the equipment/supply path.

## Architecture

```
LangGraph maintenance agent
        │  REST
        ▼
Spring Boot (NamedParameterJdbcTemplate)
        │  SQL INSERT (append)
        ▼
PostgreSQL  (parts · stock_levels · stock_movements · purchase_orders · approval_queue · workflow_events)
```

**Invariant:** controllers never update `stock_levels` directly. `InventoryService` / `WorkflowService` always `INSERT` into `stock_movements` (or PO/approval tables), then update on-hand qty in the same transaction.

## Prerequisites

- Java 17+
- Maven 3.9+
- Docker (for Postgres)

## Quick start

```bash
cd projects/parts-inventory-api
docker compose up -d
# wait until healthy, then:
mvn spring-boot:run
```

Health check:

```bash
curl http://localhost:8080/api/health
curl http://localhost:8080/api/parts
```

### Append workflow (reserve or expedite PO)

```bash
# In-stock part → appends RESERVE movement
curl -s -X POST http://localhost:8080/api/workflows/reserve-or-order ^
  -H "Content-Type: application/json" ^
  -d "{\"partKey\":\"bearing-kit-a\",\"qty\":1,\"caseId\":\"PM-DEMO-1\",\"assetId\":\"ASSET-0001\",\"reason\":\"PM demo\"}"

# Out-of-stock → appends purchase_orders + approval_queue rows
curl -s -X POST http://localhost:8080/api/workflows/reserve-or-order ^
  -H "Content-Type: application/json" ^
  -d "{\"partKey\":\"vfd-module\",\"qty\":1,\"caseId\":\"PM-DEMO-2\",\"assetId\":\"ASSET-0387\",\"reason\":\"PM demo\"}"

curl http://localhost:8080/api/movements?partKey=bearing-kit-a
curl http://localhost:8080/api/purchase-orders
```

## REST surface

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` or `/inbox` | HITL approval inbox (Thymeleaf) |
| GET | `/api/health` | DB ping |
| GET | `/api/parts` | Parts + on-hand qty |
| GET | `/api/parts/{partKey}` | Single part (`in_stock` derived) |
| GET | `/api/views/parts-on-hand` | SQL view `v_parts_on_hand` |
| POST | `/api/movements` | Append RECEIPT / RESERVE / ISSUE / ADJUST |
| GET | `/api/movements?partKey=` | Append-only ledger history |
| POST | `/api/workflows/reserve-or-order` | Automation: reserve if stock else PO + approval |
| GET | `/api/purchase-orders` | Open POs |
| GET | `/api/approvals` | Open HITL approvals (`v_open_approvals`) |
| POST | `/api/webhooks/po-approved` | Approve/reject PO; optional RECEIPT append |
| POST | `/api/cases` | Upsert agent case packet (`agent_cases`) |
| GET | `/api/cases` | Recent durable cases |
| GET | `/api/workflow-events` | Append-only audit events (optional `caseId`) |

### Approve a PO (webhook)

```bash
curl -s -X POST http://localhost:8080/api/webhooks/po-approved ^
  -H "Content-Type: application/json" ^
  -d "{\"approvalId\":\"APPR-1001\",\"decision\":\"approved\",\"receiveStock\":true}"
```

### Existing Postgres volume upgrade

If Compose data volume already exists, apply views/cases once:

```bash
docker compose exec -T parts-db psql -U parts -d parts_inventory < schema/02_views_and_cases.sql
```

## Seed catalog

Matches the maintenance agent mock:

| part_key | sku | qty | supplier |
| --- | --- | --- | --- |
| bearing-kit-a | BRG-A-220 | 12 | NorthPeak Industrial |
| bearing-kit-b | BRG-B-110 | 0 | NorthPeak Industrial |
| motor-seal | MSL-44 | 3 | Helix Parts Co |
| vfd-module | VFD-900 | 0 | Helix Parts Co |

Schema: [`schema/parts_inventory.sql`](schema/parts_inventory.sql). MariaDB type mapping: [`MARIADB.md`](MARIADB.md).

## Wire the Python agent

```bash
# Terminal 1 — this API (after docker compose up -d)
mvn spring-boot:run

# Terminal 2 — agent (auto-discovers http://localhost:8080)
cd ../automated-workflows/predictive-maintenance-agent
python run_agent.py
```

Env knobs:

| Variable | Effect |
| --- | --- |
| `PARTS_API_BASE_URL` unset | Tries `http://localhost:8080`, falls back to mock |
| `PARTS_API_BASE_URL=http://host:port` | Force that base URL |
| `PARTS_API_BASE_URL=mock` | Force in-memory mock |

## Appian JD mapping

| JD theme | Artifact here |
| --- | --- |
| Relational DB / SQL / Postgres (MariaDB-friendly) | `schema/parts_inventory.sql` + JDBC repositories |
| API integrations (REST / JDBC) | Spring REST + `NamedParameterJdbcTemplate` |
| Automate complex workflows | `POST /api/workflows/reserve-or-order` + LangGraph agent |
| HITL / production ops | `approval_queue` + `/inbox` + `POST /api/webhooks/po-approved` |
| AI-assisted process | Predictive score gates the inventory workflow |
| Durable case memory | `agent_cases` table + `POST /api/cases` from the agent |

## Config

[`src/main/resources/application.yml`](src/main/resources/application.yml) → JDBC URL `localhost:5433` (Compose maps host 5433 → container 5432 so it does not clash with Cozy inventory on 5432).
