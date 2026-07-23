"""Inventory ledger — CSV bootstrap with optional Postgres append backend.

Set ``DATABASE_URL=postgresql://cozy:cozy_dev@localhost:5432/cozy_inventory``
(after ``docker compose up -d``) to write ``items`` + ``channel_listings`` +
``workflow_events``. CSV remains the default for recruiter demos.
"""

from __future__ import annotations

import csv
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .models import CanonicalListing, PublishReceipt

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "outputs" / "inventory_ledger.csv"

CSV_COLUMNS = [
    "item_id",
    "sku",
    "title",
    "brand",
    "category",
    "condition",
    "size",
    "price",
    "status",
    "channel",
    "external_id",
    "url",
    "image_count",
    "mode",
    "published_at",
    "source_dir",
]


@dataclass
class LedgerRow:
    item_id: str
    sku: str
    title: str
    brand: str
    category: str
    condition: str
    size: str
    price: float
    status: str
    channel: str
    external_id: str
    url: str
    image_count: int
    mode: str
    published_at: str
    source_dir: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


class LedgerBackend(Protocol):
    def append(self, row: LedgerRow) -> LedgerRow: ...


class CsvLedgerBackend:
    """Flat-file ledger (Excel-friendly). Same columns as ``channel_listings`` join view."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_CSV

    def append(self, row: LedgerRow) -> LedgerRow:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists() or self.path.stat().st_size == 0
        with self.path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            payload = {k: asdict(row).get(k) for k in CSV_COLUMNS}
            writer.writerow(payload)
        return row


class PostgresLedgerBackend:
    """Append items + channel_listings + workflow_events in one transaction."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        # Always mirror to CSV so Excel demos keep working.
        self.csv = CsvLedgerBackend()

    def append(self, row: LedgerRow) -> LedgerRow:
        import json

        import psycopg

        listing_row_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO items (
                        item_id, sku, title, brand, category, condition, size, price, status, source_dir
                    ) VALUES (
                        %(item_id)s::uuid, %(sku)s, %(title)s, %(brand)s, %(category)s, %(condition)s,
                        %(size)s, %(price)s, %(status)s, %(source_dir)s
                    )
                    ON CONFLICT (sku) DO UPDATE SET
                        title = EXCLUDED.title,
                        brand = EXCLUDED.brand,
                        category = EXCLUDED.category,
                        condition = EXCLUDED.condition,
                        size = EXCLUDED.size,
                        price = EXCLUDED.price,
                        status = EXCLUDED.status,
                        source_dir = EXCLUDED.source_dir,
                        updated_at = NOW()
                    RETURNING item_id::text
                    """,
                    {
                        "item_id": row.item_id,
                        "sku": row.sku,
                        "title": row.title,
                        "brand": row.brand,
                        "category": row.category,
                        "condition": row.condition,
                        "size": row.size,
                        "price": row.price,
                        "status": row.status,
                        "source_dir": row.source_dir,
                    },
                )
                item_id = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO channel_listings (
                        listing_row_id, item_id, channel, external_id, url, status, mode, published_at
                    ) VALUES (
                        %(listing_row_id)s::uuid, %(item_id)s::uuid, %(channel)s, %(external_id)s,
                        %(url)s, %(status)s, %(mode)s, %(published_at)s::timestamptz
                    )
                    ON CONFLICT (channel, external_id) DO UPDATE SET
                        url = EXCLUDED.url,
                        status = EXCLUDED.status,
                        mode = EXCLUDED.mode,
                        published_at = EXCLUDED.published_at
                    """,
                    {
                        "listing_row_id": listing_row_id,
                        "item_id": item_id,
                        "channel": row.channel,
                        "external_id": row.external_id,
                        "url": row.url,
                        "status": row.status,
                        "mode": row.mode,
                        "published_at": row.published_at,
                    },
                )
                cur.execute(
                    """
                    INSERT INTO workflow_events (event_id, item_id, event_type, detail)
                    VALUES (
                        %(event_id)s::uuid,
                        %(item_id)s::uuid,
                        'listing_published',
                        %(detail)s::jsonb
                    )
                    """,
                    {
                        "event_id": event_id,
                        "item_id": item_id,
                        "detail": json.dumps(
                            {
                                "channel": row.channel,
                                "external_id": row.external_id,
                                "sku": row.sku,
                                "mode": row.mode,
                            }
                        ),
                    },
                )
            conn.commit()
        row.item_id = item_id
        row.extra["postgres"] = True
        row.extra["listing_row_id"] = listing_row_id
        return self.csv.append(row)


_backend: LedgerBackend | None = None


def get_ledger_backend() -> LedgerBackend:
    global _backend
    if _backend is None:
        db_url = os.getenv("DATABASE_URL", "").strip()
        if db_url.startswith("postgresql"):
            try:
                _backend = PostgresLedgerBackend(db_url)
            except Exception:  # noqa: BLE001 — fall back if driver missing
                _backend = CsvLedgerBackend()
        else:
            _backend = CsvLedgerBackend()
    return _backend


def set_ledger_backend(backend: LedgerBackend) -> None:
    """Swap in a Postgres backend later without changing publish callers."""
    global _backend
    _backend = backend


def row_from_publish(listing: CanonicalListing, receipt: PublishReceipt, item_id: str | None = None) -> LedgerRow:
    return LedgerRow(
        item_id=item_id or str(uuid.uuid4()),
        sku=listing.sku,
        title=listing.title,
        brand=listing.brand,
        category=listing.category,
        condition=str(listing.condition),
        size=listing.size,
        price=listing.price,
        status=receipt.status,
        channel=receipt.channel,
        external_id=receipt.external_id,
        url=receipt.url or "",
        image_count=len(listing.image_paths),
        mode=receipt.mode,
        published_at=datetime.now(timezone.utc).isoformat(),
        source_dir=listing.source_dir,
    )


def append_ledger(listing: CanonicalListing, receipt: PublishReceipt, item_id: str | None = None) -> LedgerRow:
    """Single entry point for inventory ledger writes (CSV and/or Postgres)."""
    row = row_from_publish(listing, receipt, item_id=item_id)
    return get_ledger_backend().append(row)
