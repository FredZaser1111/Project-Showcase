"""Publish seed inventory to Shopify / eBay / Etsy (mock if no credentials)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from orchestrator.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish seed packs to marketplaces")
    parser.add_argument(
        "--seed",
        type=Path,
        default=ROOT / "data" / "demo_seed",
        help="Root folder of SKU packs (each subfolder = one SKU)",
    )
    parser.add_argument(
        "--channels",
        default="shopify,ebay,etsy",
        help="Comma-separated: shopify,ebay,etsy",
    )
    args = parser.parse_args()
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    log = run_pipeline(args.seed, channels=channels)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
