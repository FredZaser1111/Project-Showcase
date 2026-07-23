# Resume bullets + interview kit (Track C Phase 4)

## Business Application Engineering (pick 3)

- Built a spare-parts inventory service (Spring Boot, JDBC, PostgreSQL) with append-only stock movements, purchase orders, and a manager HITL approval inbox — the same process/integration pattern used in BPM platforms.
- Integrated a predictive-maintenance agent to the inventory API over REST so at-risk assets automatically reserve stock or enqueue POs with durable `workflow_events` audit rows.
- Designed MariaDB-portable SQL (views `v_parts_on_hand`, `v_open_approvals`) and a PO approval webhook that appends RECEIPT movements after manager decision.

## Agentic AI Engineer (pick 3)

- Shipped LangGraph agents (maintenance, loan, churn) with mock-by-default LLMs, structured JSON case packets, and a CI eval harness (`eval_agents.py`, 7/7 golden cases).
- Added tool tracing (`latency_ms`, `case_id`, LLM mode) and procurement policy (threshold + cost → auto-reserve vs HITL) for production-shaped agent behavior.
- Grounded GenAI recommendations on workflow events with explicit `event_id` citations (`insights.py`), plus optional Postgres case persistence via `POST /api/cases`.

## Shared / commerce

- Production-path listing orchestrator: vision → listing copy → Shopify/eBay/Etsy adapters with mock-safe demos; inventory ledger promotes to Postgres when `DATABASE_URL` is set.

## Portfolio links (paste in applications)

- https://fredzaser1111.github.io/Project-Showcase/
- https://fredzaser1111.github.io/Project-Showcase/projects/listing-orchestrator/demo/
- https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/parts-inventory-api
- https://github.com/FredZaser1111/Project-Showcase/blob/main/projects/BPM_APPIAN_MAPPING.md

## 10 SQL interview answers (against parts schema)

1. **On-hand by SKU:** `SELECT * FROM v_parts_on_hand ORDER BY qty_on_hand;`
2. **Below reorder:** `SELECT * FROM v_parts_on_hand WHERE below_reorder_point;`
3. **Open approvals:** `SELECT * FROM v_open_approvals;`
4. **Movement history:** `SELECT * FROM stock_movements WHERE part_key = 'bearing-kit-a' ORDER BY created_at DESC;`
5. **Balance check:** sum of `qty_delta` should equal current `qty_on_hand` for a part after seed reset.
6. **PO aging:** `SELECT approval_id, NOW() - queued_at AS age FROM v_open_approvals;`
7. **Events for case:** `SELECT * FROM workflow_events WHERE case_id = 'PM-ASSET-0387';`
8. **Idempotent listing (Cozy):** `UNIQUE (channel, external_id)` on `channel_listings`.
9. **Upsert item by SKU:** `INSERT ... ON CONFLICT (sku) DO UPDATE` (see `PostgresLedgerBackend`).
10. **MariaDB swap:** UUID→CHAR(36), TIMESTAMPTZ→DATETIME(6), JSONB→JSON (`MARIADB.md`).

## 5-minute walkthrough script

1. Pages home → Parts Inventory + Maintenance cards  
2. Show eval report pass rate  
3. Sketch reserve-or-order + HITL webhook  
4. Open BPM mapping doc one-liner  
5. Offer to live-run `eval_agents.py` or mock listing demo
