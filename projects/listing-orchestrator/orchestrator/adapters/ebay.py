"""eBay Sell Inventory adapter — mock when OAuth token missing."""

from __future__ import annotations

import os

import httpx

from ..models import CanonicalListing, PublishReceipt, SaleEvent
from .mock_util import mock_receipt, mock_sales


class EbayAdapter:
    name = "ebay"

    def __init__(self) -> None:
        self.token = os.getenv("EBAY_ACCESS_TOKEN", "").strip()
        env = os.getenv("EBAY_ENVIRONMENT", "sandbox").lower()
        self.base = (
            "https://api.sandbox.ebay.com"
            if env != "production"
            else "https://api.ebay.com"
        )

    @property
    def live(self) -> bool:
        if os.getenv("ORCHESTRATOR_FORCE_MOCK", "").strip().lower() in {"1", "true", "yes"}:
            return False
        return bool(self.token)

    def publish(self, listing: CanonicalListing) -> PublishReceipt:
        if not self.live:
            return mock_receipt(listing, "ebay")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Content-Language": "en-US",
        }
        item_url = f"{self.base}/sell/inventory/v1/inventory_item/{listing.sku}"
        payload = {
            "availability": {"shipToLocationAvailability": {"quantity": 1}},
            "condition": "USED_EXCELLENT" if listing.condition != "New" else "NEW",
            "product": {
                "title": listing.title[:80],
                "description": listing.description,
                "aspects": {
                    "Brand": [listing.brand],
                    "Size": [listing.size],
                },
            },
        }
        with httpx.Client(timeout=45.0) as client:
            resp = client.put(item_url, headers=headers, json=payload)
            resp.raise_for_status()
        return PublishReceipt(
            sku=listing.sku,
            channel="ebay",
            mode="live",
            external_id=listing.sku,
            url=None,
            status="inventory_upserted",
            detail={
                "note": "Inventory item upserted. Create offer + publish via Offer API or Seller Hub next."
            },
        )

    def recent_sales(self, limit: int = 20) -> list[SaleEvent]:
        if not self.live:
            return mock_sales("ebay", limit)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.base}/sell/fulfillment/v1/order"
        with httpx.Client(timeout=45.0) as client:
            resp = client.get(url, headers=headers, params={"limit": min(limit, 50)})
            resp.raise_for_status()
            orders = resp.json().get("orders", [])
        events: list[SaleEvent] = []
        for order in orders:
            buyer = order.get("buyer") or {}
            line = (order.get("lineItems") or [{}])[0]
            events.append(
                SaleEvent(
                    sale_id=str(order.get("orderId")),
                    channel="ebay",
                    sku=str(line.get("sku") or "unknown"),
                    title=str(line.get("title") or "eBay order"),
                    price=float(
                        (order.get("pricingSummary") or {}).get("total", {}).get("value") or 0
                    ),
                    buyer_email=None,
                    buyer_name=buyer.get("username"),
                    marketing_consent=False,
                    sold_at=str(order.get("creationDate") or ""),
                )
            )
        return events
