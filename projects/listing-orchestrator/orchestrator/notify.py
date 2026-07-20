"""Seller sold notifications (stdout + optional file)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import SaleEvent


def notify_seller(sales: list[SaleEvent], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seller_notifications.json"
    payload = {
        "notify_email": os.getenv("SELLER_NOTIFY_EMAIL"),
        "sales": [s.model_dump() for s in sales],
        "message": f"{len(sales)} sale(s) detected — check channel dashboards to fulfill.",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(payload["message"])
    for s in sales:
        print(f"  - [{s.channel}] {s.title} · {s.buyer_email or 'no-email'} · ${s.price}")
    return path
