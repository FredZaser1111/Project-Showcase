"""Shared mock publish/sales for offline demos and missing credentials."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from ..models import CanonicalListing, Channel, PublishReceipt, SaleEvent


def mock_receipt(listing: CanonicalListing, channel: Channel) -> PublishReceipt:
    digest = hashlib.sha1(f"{channel}:{listing.sku}".encode()).hexdigest()[:10]
    return PublishReceipt(
        sku=listing.sku,
        channel=channel,
        mode="mock",
        external_id=f"mock_{channel}_{digest}",
        url=f"https://example.com/{channel}/listings/{listing.sku}",
        status="published_mock",
        detail={"title": listing.title, "price": listing.price},
    )


def mock_sales(channel: Channel, limit: int = 3) -> list[SaleEvent]:
    now = datetime.now(timezone.utc).isoformat()
    events: list[SaleEvent] = []
    for i in range(min(limit, 3)):
        events.append(
            SaleEvent(
                sale_id=f"{channel}_sale_{i+1}",
                channel=channel,
                sku=f"DEMO-SKU-{i+1:03d}",
                title=f"Demo {channel} sale #{i+1}",
                price=80.0 + i * 15,
                buyer_email=f"buyer{i+1}@example.com",
                buyer_name=f"Buyer {i+1}",
                marketing_consent=i % 2 == 0,
                sold_at=now,
            )
        )
    return events
