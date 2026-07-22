"""Etsy Open API v3 adapter — draft listing + ranked image carousel when live."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path

import httpx

from ..models import CanonicalListing, PublishReceipt, SaleEvent
from ..etsy_auth import etsy_api_key_header, etsy_credentials_ready
from .mock_util import mock_receipt, mock_sales

ETSY_API = "https://openapi.etsy.com/v3/application"


class EtsyAdapter:
    name = "etsy"

    def __init__(self) -> None:
        self.api_key = os.getenv("ETSY_API_KEY", "").strip()
        self.token = os.getenv("ETSY_ACCESS_TOKEN", "").strip()
        self.shop_id = os.getenv("ETSY_SHOP_ID", "").strip()
        self.activate = os.getenv("ETSY_ACTIVATE_LISTINGS", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }

    @property
    def live(self) -> bool:
        if os.getenv("ORCHESTRATOR_FORCE_MOCK", "").strip().lower() in {"1", "true", "yes"}:
            return False
        return etsy_credentials_ready()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "x-api-key": etsy_api_key_header(),
        }

    def _ensure_shipping_profile_id(self, client: httpx.Client) -> int | None:
        env_id = os.getenv("ETSY_SHIPPING_PROFILE_ID", "").strip()
        if env_id.isdigit():
            return int(env_id)

        list_url = f"{ETSY_API}/shops/{self.shop_id}/shipping-profiles"
        resp = client.get(list_url, headers=self._headers())
        if resp.status_code < 400:
            for row in resp.json().get("results") or []:
                sid = row.get("shipping_profile_id")
                if sid:
                    return int(sid)

        create = client.post(
            list_url,
            headers=self._headers(),
            data={
                "title": "Cozy standard US shipping",
                "origin_country_iso": "US",
                "primary_cost": "6.00",
                "secondary_cost": "0.00",
                "min_processing_time": "1",
                "max_processing_time": "3",
                "processing_time_unit": "business_days",
                "origin_postal_code": os.getenv("ETSY_ORIGIN_POSTAL_CODE", "10001"),
                "destination_country_iso": "US",
                "min_delivery_days": "3",
                "max_delivery_days": "7",
            },
        )
        if create.status_code >= 400:
            return None
        sid = create.json().get("shipping_profile_id")
        return int(sid) if sid else None

    def _ensure_readiness_state_id(self, client: httpx.Client) -> int | None:
        """Physical listings need a readiness_state_id; reuse or create ready_to_ship."""
        env_id = os.getenv("ETSY_READINESS_STATE_ID", "").strip()
        if env_id.isdigit():
            return int(env_id)

        list_url = f"{ETSY_API}/shops/{self.shop_id}/readiness-state-definitions"
        resp = client.get(list_url, headers=self._headers())
        if resp.status_code < 400:
            for row in resp.json().get("results") or []:
                rid = row.get("readiness_state_id")
                if rid:
                    return int(rid)

        create = client.post(
            list_url,
            headers=self._headers(),
            data={
                "readiness_state": "ready_to_ship",
                "min_processing_time": "1",
                "max_processing_time": "3",
                "processing_time_unit": "days",
            },
        )
        if create.status_code >= 400:
            # Older field names
            create = client.post(
                list_url,
                headers=self._headers(),
                data={
                    "readiness_state": "ready_to_ship",
                    "min_processing_days": "1",
                    "max_processing_days": "3",
                },
            )
        if create.status_code >= 400:
            return None
        rid = create.json().get("readiness_state_id")
        return int(rid) if rid else None

    def _upload_images(
        self, client: httpx.Client, listing_id: str, image_paths: list[str]
    ) -> list[dict]:
        uploaded: list[dict] = []
        url = f"{ETSY_API}/shops/{self.shop_id}/listings/{listing_id}/images"
        for rank, path_str in enumerate(image_paths[:10], start=1):
            path = Path(path_str)
            if not path.is_file():
                continue
            mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            with path.open("rb") as fh:
                resp = client.post(
                    url,
                    headers=self._headers(),
                    files={"image": (path.name, fh, mime)},
                    data={"rank": str(rank)},
                )
            if resp.status_code >= 400:
                uploaded.append(
                    {
                        "rank": rank,
                        "path": path.name,
                        "error": f"{resp.status_code} {resp.text[:200]}",
                    }
                )
                continue
            body = resp.json()
            uploaded.append(
                {
                    "rank": rank,
                    "path": path.name,
                    "listing_image_id": body.get("listing_image_id"),
                }
            )
        return uploaded

    def _activate_listing(self, client: httpx.Client, listing_id: str) -> dict:
        url = f"{ETSY_API}/shops/{self.shop_id}/listings/{listing_id}"
        resp = client.patch(url, headers=self._headers(), data={"state": "active"})
        if resp.status_code >= 400:
            return {"activate_error": f"{resp.status_code} {resp.text[:200]}"}
        return {"state": "active"}

    def publish(self, listing: CanonicalListing) -> PublishReceipt:
        if not self.live:
            return mock_receipt(listing, "etsy")

        taxonomy = int(os.getenv("ETSY_TAXONOMY_ID") or "0") or 1
        create_url = f"{ETSY_API}/shops/{self.shop_id}/listings"

        with httpx.Client(timeout=90.0) as client:
            readiness_id = self._ensure_readiness_state_id(client)
            shipping_id = self._ensure_shipping_profile_id(client)
            form: dict[str, str] = {
                "quantity": "1",
                "title": listing.title[:140],
                "description": listing.description or listing.title,
                "price": str(listing.price),
                "who_made": os.getenv("ETSY_WHO_MADE", "someone_else").strip() or "someone_else",
                "when_made": os.getenv("ETSY_WHEN_MADE", "2020_2026").strip() or "2020_2026",
                "taxonomy_id": str(taxonomy),
                "type": "physical",
                "should_auto_renew": "true",
                "is_supply": os.getenv("ETSY_IS_SUPPLY", "false").strip() or "false",
            }
            if readiness_id:
                form["readiness_state_id"] = str(readiness_id)
            if shipping_id:
                form["shipping_profile_id"] = str(shipping_id)
            else:
                raise RuntimeError(
                    "Etsy requires a shipping profile. Create one in Shop Manager "
                    "or set ETSY_SHIPPING_PROFILE_ID / ETSY_ORIGIN_POSTAL_CODE."
                )

            resp = client.post(create_url, headers=self._headers(), data=form)
            if resp.status_code >= 400:
                detail_err = resp.text[:500]
                if "invalid_token" in detail_err or "access token is expired" in detail_err:
                    receipt = mock_receipt(listing, "etsy")
                    return receipt.model_copy(
                        update={
                            "detail": {
                                **receipt.detail,
                                "fallback": "expired_or_invalid_token",
                                "etsy_error": detail_err[:200],
                            }
                        }
                    )
                hint = ""
                if "invalid_marketplace" in detail_err or "cannot sell this item" in detail_err:
                    hint = (
                        " Etsy blocks finished goods made by someone else unless they "
                        "qualify as vintage (20+ years), supplies, or use production partners. "
                        "For modern streetwear resale, prefer eBay / own site; for vintage set "
                        "ETSY_WHEN_MADE to a 20+ year window (e.g. before_2007)."
                    )
                raise httpx.HTTPStatusError(
                    f"Etsy create listing failed: {detail_err}{hint}",
                    request=resp.request,
                    response=resp,
                )
            data = resp.json()
            listing_id = str(data.get("listing_id"))
            image_results = self._upload_images(client, listing_id, listing.image_paths)

            detail: dict = {
                "images": image_results,
                "readiness_state_id": readiness_id,
                "taxonomy_id": taxonomy,
                "state": "draft",
                "carousel_note": "Images uploaded in order: hero graphic first, then authenticity photos.",
            }
            status = "draft"
            ok_images = image_results and not any("error" in r for r in image_results)
            if self.activate and ok_images:
                detail.update(self._activate_listing(client, listing_id))
                if detail.get("state") == "active":
                    status = "published"

        return PublishReceipt(
            sku=listing.sku,
            channel="etsy",
            mode="live",
            external_id=listing_id,
            url=f"https://www.etsy.com/listing/{listing_id}",
            status=status,
            detail=detail,
        )

    def recent_sales(self, limit: int = 20) -> list[SaleEvent]:
        if not self.live:
            return mock_sales("etsy", limit)

        headers = self._headers()
        url = f"{ETSY_API}/shops/{self.shop_id}/receipts"
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
