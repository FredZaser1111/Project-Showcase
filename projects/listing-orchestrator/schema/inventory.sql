-- Cozy Connoisseur inventory DBMS schema (PostgreSQL).
-- MariaDB: swap UUID with CHAR(36), TIMESTAMPTZ with DATETIME(6), JSONB with JSON.

CREATE TABLE IF NOT EXISTS items (
    item_id       UUID PRIMARY KEY,
    sku           TEXT NOT NULL UNIQUE,
    title         TEXT NOT NULL DEFAULT '',
    brand         TEXT NOT NULL DEFAULT '',
    category      TEXT NOT NULL DEFAULT '',
    condition     TEXT NOT NULL DEFAULT 'Lightly Used',
    size          TEXT NOT NULL DEFAULT '',
    price         NUMERIC(12, 2) NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'draft',
    source_dir    TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS item_images (
    image_id      UUID PRIMARY KEY,
    item_id       UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    path          TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'product',
    sort_order    INT NOT NULL DEFAULT 1,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS channel_listings (
    listing_row_id UUID PRIMARY KEY,
    item_id       UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    channel       TEXT NOT NULL,
    external_id   TEXT NOT NULL,
    url           TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'published',
    mode          TEXT NOT NULL DEFAULT 'live',
    published_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (channel, external_id)
);

CREATE TABLE IF NOT EXISTS workflow_events (
    event_id      UUID PRIMARY KEY,
    item_id       UUID REFERENCES items(item_id) ON DELETE SET NULL,
    event_type    TEXT NOT NULL,
    detail        JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_items_sku ON items(sku);
CREATE INDEX IF NOT EXISTS idx_channel_listings_item ON channel_listings(item_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_item ON workflow_events(item_id);
