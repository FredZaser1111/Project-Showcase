"""End-to-end: seed → vision → copy → canonical JSON → channel publish."""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

from .adapters import get_adapters
from .copywriter import write_listing_copy
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
        vision=vision,
        source_dir=str(sku_dir),
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
    adapters = get_adapters(channels)

    for sku_dir in discover_sku_dirs(seed_root):
        listing = build_listing(sku_dir)
        listings.append(listing)
        (listings_dir / f"{listing.sku}.json").write_text(
            listing.model_dump_json(indent=2), encoding="utf-8"
        )
        for adapter in adapters:
            receipts.append(adapter.publish(listing))

    log = {
        "seed_root": str(seed_root),
        "listing_count": len(listings),
        "receipts": [r.model_dump() for r in receipts],
    }
    (out_dir / "publish_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log
