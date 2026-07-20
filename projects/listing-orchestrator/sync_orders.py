"""Sync recent sales → seller notify + consent-aware contact log."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from orchestrator.adapters import get_adapters  # noqa: E402
from orchestrator.crm import append_contacts  # noqa: E402
from orchestrator.notify import notify_seller  # noqa: E402


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", default="shopify,ebay,etsy")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    adapters = get_adapters(channels)
    sales = []
    for adapter in adapters:
        sales.extend(adapter.recent_sales(limit=args.limit))

    out = ROOT / "outputs"
    notify_path = notify_seller(sales, out)
    written = append_contacts(sales, out / "contacts.jsonl")
    summary = {
        "sales": len(sales),
        "contacts_appended": written,
        "notify_file": str(notify_path),
        "contacts_file": str(out / "contacts.jsonl"),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
