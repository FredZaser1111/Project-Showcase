"""Shopify Admin API adapter — mock when credentials missing."""

from __future__ import annotations

import os

import httpx

from ..models import CanonicalListing, PublishReceipt, SaleEvent
from .mock_util import mock_receipt, mock_sales


class ShopifyAdapter:
    name = "shopify"

    def __init__(self) -> None:
        self.domain = os.getenv("SHOPIFY_STORE_DOMAIN", "").strip()
        self.token = os.getenv("SHOPIFY_ADMIN_TOKEN", "").strip()

    @property
    def live(self) -> bool:
        if os.getenv("ORCHESTRATOR_FORCE_MOCK", "").strip().lower() in {"1", "true", "yes"}:
            return False
        return bool(self.domain and self.token)

    def publish(self, listing: CanonicalListing) -> PublishReceipt:
        if not self.live:
            return mock_receipt(listing, "shopify")

        url = f"https://{self.domain}/admin/api/2024-10/products.json"
        payload = {
            "product": {
                "title": listing.title,
                "body_html": listing.description.replace("\n", "<br/>"),
                "vendor": listing.brand,
                "product_type": listing.category,
                "tags": ", ".join(listing.tags),
                "status": "active",
                "variants": [
                    {
                        "price": str(listing.price),
                        "sku": listing.sku,
                        "option1": listing.size,
                    }
                ],
                "options": [{"name": "Size", "values": [listing.size]}],
                "metafields": [
                    {
                        "namespace": "cozy",
                        "key": "condition",
                        "value": listing.condition,
                        "type": "single_line_text_field",
                    },
                    {
                        "namespace": "cozy",
                        "key": "authenticity_note",
                        "value": listing.authenticity_note,
                        "type": "multi_line_text_field",
                    },
                ],
            }
        }
        headers = {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            product = resp.json()["product"]
        return PublishReceipt(
            sku=listing.sku,
            channel="shopify",
            mode="live",
            external_id=str(product["id"]),
            url=f"https://{self.domain}/products/{product.get('handle', '')}",
            status="published",
            detail={"handle": product.get("handle")},
        )

    def recent_sales(self, limit: int = 20) -> list[SaleEvent]:
        if not self.live:
            return mock_sales("shopify", limit)

        url = f"https://{self.domain}/admin/api/2024-10/orders.json"
        headers = {"X-Shopify-Access-Token": self.token}
        params = {"status": "any", "limit": min(limit, 50)}
        with httpx.Client(timeout=45.0) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            orders = resp.json().get("orders", [])
        events: list[SaleEvent] = []
        for order in orders:
            email = order.get("email") or order.get("contact_email")
            line = (order.get("line_items") or [{}])[0]
            events.append(
                SaleEvent(
                    sale_id=str(order["id"]),
                    channel="shopify",
                    sku=str(line.get("sku") or "unknown"),
                    title=str(line.get("title") or order.get("name")),
                    price=float(order.get("total_price") or 0),
                    buyer_email=email,
                    buyer_name=f"{order.get('customer', {}).get('first_name', '')} {order.get('customer', {}).get('last_name', '')}".strip()
                    or None,
                    marketing_consent=bool(
                        order.get("buyer_accepts_marketing")
                        or (order.get("customer") or {}).get("accepts_marketing")
                    ),
                    sold_at=str(order.get("created_at") or ""),
                )
            )
        return events
