"""Inventory ledger — CSV bootstrap with a Postgres-ready append API.

Phase 1 writes ``outputs/inventory_ledger.csv``.
Phase 2 can swap ``append_ledger`` to insert into PostgreSQL using the same
``LedgerRow`` fields (see ``schema/inventory.sql``).
"""

from __future__ import annotations

import csv
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
    """Flat-file ledger (Excel-friendly). Same columns as future ``channel_listings`` join view."""

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


_backend: LedgerBackend | None = None


def get_ledger_backend() -> LedgerBackend:
    global _backend
    if _backend is None:
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
    """Single entry point for inventory ledger writes (CSV now, Postgres later)."""
    row = row_from_publish(listing, receipt, item_id=item_id)
    return get_ledger_backend().append(row)
