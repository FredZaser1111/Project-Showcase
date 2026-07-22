-- Equipment / spare-parts inventory DBMS (PostgreSQL).
-- MariaDB: swap UUID with CHAR(36), TIMESTAMPTZ with DATETIME(6), JSONB with JSON,
--          NUMERIC stays; use AUTO_INCREMENT or UUID() for ids as preferred.

CREATE TABLE IF NOT EXISTS parts (
    part_key      TEXT PRIMARY KEY,
    sku           TEXT NOT NULL UNIQUE,
    description   TEXT NOT NULL DEFAULT '',
    unit_cost     NUMERIC(12, 2) NOT NULL DEFAULT 0,
    supplier      TEXT NOT NULL DEFAULT '',
    reorder_point INT NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_levels (
    part_key      TEXT PRIMARY KEY REFERENCES parts(part_key) ON DELETE CASCADE,
    qty_on_hand   INT NOT NULL DEFAULT 0 CHECK (qty_on_hand >= 0),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Append-only ledger: never UPDATE/DELETE rows in application code.
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id   UUID PRIMARY KEY,
    part_key      TEXT NOT NULL REFERENCES parts(part_key),
    movement_type TEXT NOT NULL CHECK (movement_type IN ('RECEIPT', 'RESERVE', 'ISSUE', 'ADJUST')),
    qty_delta     INT NOT NULL,
    balance_after INT NOT NULL,
    case_id       TEXT,
    reason        TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id         UUID PRIMARY KEY,
    part_key      TEXT NOT NULL REFERENCES parts(part_key),
    sku           TEXT NOT NULL,
    supplier      TEXT NOT NULL,
    qty           INT NOT NULL CHECK (qty > 0),
    unit_cost     NUMERIC(12, 2) NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending_manager_approval',
    case_id       TEXT,
    asset_id      TEXT,
    narrative     TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approval_queue (
    approval_id   TEXT PRIMARY KEY,
    po_id         UUID NOT NULL REFERENCES purchase_orders(po_id),
    status        TEXT NOT NULL DEFAULT 'pending_manager_approval',
    case_id       TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_events (
    event_id      UUID PRIMARY KEY,
    event_type    TEXT NOT NULL,
    part_key      TEXT,
    case_id       TEXT,
    detail        JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE SEQUENCE IF NOT EXISTS approval_seq START 1000;

CREATE INDEX IF NOT EXISTS idx_stock_movements_part ON stock_movements(part_key);
CREATE INDEX IF NOT EXISTS idx_stock_movements_created ON stock_movements(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_workflow_events_case ON workflow_events(case_id);

-- Seed matches predictive-maintenance-agent mock inventory.
INSERT INTO parts (part_key, sku, description, unit_cost, supplier, reorder_point) VALUES
    ('bearing-kit-a', 'BRG-A-220', 'Bearing kit A (220mm)', 480.00, 'NorthPeak Industrial', 2),
    ('bearing-kit-b', 'BRG-B-110', 'Bearing kit B (110mm heavy)', 620.00, 'NorthPeak Industrial', 1),
    ('motor-seal', 'MSL-44', 'Motor seal assembly', 95.00, 'Helix Parts Co', 2),
    ('vfd-module', 'VFD-900', 'Variable frequency drive module', 2400.00, 'Helix Parts Co', 1)
ON CONFLICT (part_key) DO NOTHING;

INSERT INTO stock_levels (part_key, qty_on_hand) VALUES
    ('bearing-kit-a', 12),
    ('bearing-kit-b', 0),
    ('motor-seal', 3),
    ('vfd-module', 0)
ON CONFLICT (part_key) DO NOTHING;

-- Durable agent case packets (Track C Phase 1).
CREATE TABLE IF NOT EXISTS agent_cases (
    case_id       TEXT PRIMARY KEY,
    project       TEXT NOT NULL DEFAULT 'predictive-maintenance-agent',
    asset_id      TEXT,
    decision      TEXT NOT NULL DEFAULT '',
    payload       JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_cases_created ON agent_cases(created_at DESC);

-- Reporting views for Bus App / Appian-style record lists.
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
