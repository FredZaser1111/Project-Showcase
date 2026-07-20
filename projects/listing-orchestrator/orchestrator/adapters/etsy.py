"""Etsy Open API v3 adapter — mock when credentials missing."""

from __future__ import annotations

import os

import httpx

from ..models import CanonicalListing, PublishReceipt, SaleEvent
from .mock_util import mock_receipt, mock_sales


class EtsyAdapter:
    name = "etsy"

    def __init__(self) -> None:
        self.api_key = os.getenv("ETSY_API_KEY", "").strip()
        self.token = os.getenv("ETSY_ACCESS_TOKEN", "").strip()
        self.shop_id = os.getenv("ETSY_SHOP_ID", "").strip()

    @property
    def live(self) -> bool:
        return bool(self.api_key and self.token and self.shop_id)

    def publish(self, listing: CanonicalListing) -> PublishReceipt:
        if not self.live:
            return mock_receipt(listing, "etsy")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        url = f"https://openapi.etsy.com/v3/application/shops/{self.shop_id}/listings"
        # taxonomy_id 1 is a placeholder — production should map category → Etsy taxonomy
        payload = {
            "quantity": 1,
            "title": listing.title[:140],
            "description": listing.description,
            "price": listing.price,
            "who_made": "someone_else",
            "when_made": "2020_2024",
            "taxonomy_id": 1,
            "type": "physical",
            "should_auto_renew": True,
        }
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        listing_id = str(data.get("listing_id") or data.get("listing_id"))
        return PublishReceipt(
            sku=listing.sku,
            channel="etsy",
            mode="live",
            external_id=listing_id,
            url=f"https://www.etsy.com/listing/{listing_id}",
            status="published",
            detail={"taxonomy_note": "Set a real taxonomy_id for your category before production."},
        )

    def recent_sales(self, limit: int = 20) -> list[SaleEvent]:
        if not self.live:
            return mock_sales("etsy", limit)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
        }
        url = f"https://openapi.etsy.com/v3/application/shops/{self.shop_id}/receipts"
        with httpx.Client(timeout=45.0) as client:
            resp = client.get(url, headers=headers, params={"limit": min(limit, 50)})
            resp.raise_for_status()
            receipts = resp.json().get("results", [])
        events: list[SaleEvent] = []
        for receipt in receipts:
            events.append(
                SaleEvent(
                    sale_id=str(receipt.get("receipt_id")),
                    channel="etsy",
                    sku=str(receipt.get("receipt_id")),
                    title=str(receipt.get("message_from_buyer") or "Etsy order"),
                    price=float(receipt.get("grandtotal") or receipt.get("total_price") or 0) / 100.0
                    if isinstance(receipt.get("grandtotal"), int)
                    else float(receipt.get("grandtotal") or 0),
                    buyer_email=receipt.get("buyer_email"),
                    buyer_name=receipt.get("name"),
                    marketing_consent=False,
                    sold_at=str(receipt.get("created_timestamp") or ""),
                )
            )
        return events[:limit]
