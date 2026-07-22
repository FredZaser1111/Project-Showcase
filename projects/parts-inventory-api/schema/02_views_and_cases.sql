-- Apply on an existing Postgres volume that already ran 01_parts_inventory.sql.
-- Fresh `docker compose up` applies the full schema file instead.

CREATE TABLE IF NOT EXISTS agent_cases (
    case_id       TEXT PRIMARY KEY,
    project       TEXT NOT NULL DEFAULT 'predictive-maintenance-agent',
    asset_id      TEXT,
    decision      TEXT NOT NULL DEFAULT '',
    payload       JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_cases_created ON agent_cases(created_at DESC);

CREATE OR REPLACE VIEW v_parts_on_hand AS
SELECT
    p.part_key,
    p.sku,
    p.description,
    p.unit_cost,
    p.supplier,
    p.reorder_point,
    COALESCE(s.qty_on_hand, 0) AS qty_on_hand,
    COALESCE(s.qty_on_hand, 0) > 0 AS in_stock,
    COALESCE(s.qty_on_hand, 0) <= p.reorder_point AS below_reorder_point,
    s.updated_at AS stock_updated_at
FROM parts p
LEFT JOIN stock_levels s ON s.part_key = p.part_key;

CREATE OR REPLACE VIEW v_open_approvals AS
SELECT
    a.approval_id,
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
WHERE a.status = 'pending_manager_approval'
ORDER BY a.created_at ASC;
