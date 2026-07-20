"""CRM contact log for marketing blasts (consent-aware)."""

from __future__ import annotations

import json
from pathlib import Path

from .models import SaleEvent


def append_contacts(sales: list[SaleEvent], contacts_path: Path) -> int:
    contacts_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with contacts_path.open("a", encoding="utf-8") as fh:
        for sale in sales:
            if not sale.buyer_email:
                continue
            row = {
                "email": sale.buyer_email,
                "name": sale.buyer_name,
                "channel": sale.channel,
                "sku": sale.sku,
                "sale_id": sale.sale_id,
                "marketing_consent": sale.marketing_consent,
                "sold_at": sale.sold_at,
                "ok_to_blast": sale.marketing_consent,
            }
            fh.write(json.dumps(row) + "\n")
            written += 1
    return written
