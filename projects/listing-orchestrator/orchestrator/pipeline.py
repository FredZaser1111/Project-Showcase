"""End-to-end: seed → vision → copy → canonical JSON → channel publish → ledger."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from dotenv import load_dotenv

from .adapters import get_adapters
from .copywriter import write_listing_copy
from .ledger import append_ledger
from .models import CanonicalListing, PublishReceipt
from .seed import discover_sku_dirs, load_sku_pack
from .vision import enrich_vision

ROOT = Path(__file__).resolve().parents[1]


def build_listing(sku_dir: Path) -> CanonicalListing:
    sku, images, meta = load_sku_pack(sku_dir)
    if not images:
        raise FileNotFoundError(f"No images in {sku_dir}")
    vision = enrich_vision(images, meta)
    title, description, tags = write_listing_copy(sku, vision, meta)
    price = float(meta.get("price") or 96)
    size = str(meta.get("size") or "One Size")
    condition = meta.get("condition") or vision.condition_guess
    item_id = str(meta.get("item_id") or uuid.uuid4())
    roles = meta.get("images") if isinstance(meta.get("images"), list) else []
    return CanonicalListing(
        sku=sku,
        title=title,
        description=description,
        brand=vision.brand,
        category=vision.category,
        condition=condition,
        price=price,
        size=size,
        tags=tags,
        authenticity_note=meta.get("authenticity_note")
        or (
            "Independent reseller - not affiliated with the brands carried. "
            "Authenticity reviewed in-house."
        ),
        image_paths=[str(p) for p in images],
        image_roles=[{"file": str(r.get("file", "")), "role": str(r.get("role", "product"))} for r in roles if isinstance(r, dict)],
        vision=vision,
        source_dir=str(sku_dir),
        item_id=item_id,
    )


def run_pipeline(
    seed_root: Path,
    channels: list[str] | None = None,
    out_dir: Path | None = None,
) -> dict:
    load_dotenv(ROOT / ".env")
    out_dir = out_dir or (ROOT / "outputs")
    listings_dir = out_dir / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)

    listings: list[CanonicalListing] = []
    receipts: list[PublishReceipt] = []
    ledger_rows: list[dict] = []
    adapters = get_adapters(channels)

    for sku_dir in discover_sku_dirs(seed_root):
        listing = build_listing(sku_dir)
        listings.append(listing)
        (listings_dir / f"{listing.sku}.json").write_text(
            listing.model_dump_json(indent=2), encoding="utf-8"
        )
        for adapter in adapters:
            receipt = adapter.publish(listing)
            receipts.append(receipt)
            row = append_ledger(listing, receipt, item_id=listing.item_id or None)
            ledger_rows.append(
                {
                    "item_id": row.item_id,
                    "sku": row.sku,
                    "channel": row.channel,
                    "external_id": row.external_id,
                    "status": row.status,
                    "mode": row.mode,
                }
            )

    log = {
        "seed_root": str(seed_root),
        "listing_count": len(listings),
        "receipts": [r.model_dump() for r in receipts],
        "ledger": {
            "path": str(out_dir / "inventory_ledger.csv"),
            "rows_appended": ledger_rows,
        },
    }
    (out_dir / "publish_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log
