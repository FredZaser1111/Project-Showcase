"""Verify marketplace credentials; refresh Etsy access token when needed."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from etsy_oauth import _upsert_env  # noqa: E402
from orchestrator.etsy_auth import etsy_api_key_header  # noqa: E402


def refresh_etsy_if_needed() -> bool:
    api_key = os.getenv("ETSY_API_KEY", "").strip()
    refresh = os.getenv("ETSY_REFRESH_TOKEN", "").strip()
    if not api_key or not refresh:
        return False
    resp = httpx.post(
        "https://api.etsy.com/v3/public/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": api_key,
            "refresh_token": refresh,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=45.0,
    )
    if resp.status_code >= 400:
        print(f"etsy refresh failed: {resp.status_code} {resp.text[:200]}")
        return False
    data = resp.json()
    updates = {"ETSY_ACCESS_TOKEN": data["access_token"]}
    if data.get("refresh_token"):
        updates["ETSY_REFRESH_TOKEN"] = data["refresh_token"]
    _upsert_env(updates)
    os.environ["ETSY_ACCESS_TOKEN"] = updates["ETSY_ACCESS_TOKEN"]
    print("etsy: refreshed access token")
    return True


def check_etsy() -> None:
    api_key = os.getenv("ETSY_API_KEY", "").strip()
    secret = os.getenv("ETSY_SHARED_SECRET", "").strip()
    token = os.getenv("ETSY_ACCESS_TOKEN", "").strip()
    shop_id = os.getenv("ETSY_SHOP_ID", "").strip()
    if not api_key:
        print("etsy: MOCK (missing ETSY_API_KEY)")
        print("       -> set ETSY_API_KEY then run: python etsy_oauth.py")
        return
    if not secret:
        print("etsy: MOCK (missing ETSY_SHARED_SECRET)")
        print("       -> Your Apps -> See API Key Details -> Shared Secret -> .env")
        return
    if not (token and shop_id):
        print("etsy: MOCK (missing ETSY_ACCESS_TOKEN / ETSY_SHOP_ID)")
        print("       -> run: python etsy_oauth.py")
        return

    headers = {"Authorization": f"Bearer {token}", "x-api-key": etsy_api_key_header()}
    resp = httpx.get(
        f"https://openapi.etsy.com/v3/application/shops/{shop_id}",
        headers=headers,
        timeout=45.0,
    )
    if resp.status_code == 401:
        print("etsy: access token expired - refreshing...")
        if refresh_etsy_if_needed():
            token = os.getenv("ETSY_ACCESS_TOKEN", "").strip()
            headers["Authorization"] = f"Bearer {token}"
            resp = httpx.get(
                f"https://openapi.etsy.com/v3/application/shops/{shop_id}",
                headers=headers,
                timeout=45.0,
            )
    if resp.status_code >= 400:
        print(f"etsy: ERROR {resp.status_code} {resp.text[:300]}")
        return
    shop = resp.json()
    name = shop.get("shop_name") or ""
    print(f"etsy: LIVE · shop_id={shop_id} · name={name}")


def check_ebay() -> None:
    token = os.getenv("EBAY_ACCESS_TOKEN", "").strip()
    env = os.getenv("EBAY_ENVIRONMENT", "sandbox").lower()
    if not token:
        print("ebay: MOCK (missing EBAY_ACCESS_TOKEN)")
        return
    base = (
        "https://api.sandbox.ebay.com"
        if env != "production"
        else "https://api.ebay.com"
    )
    resp = httpx.get(
        f"{base}/sell/inventory/v1/inventory_item",
        headers={"Authorization": f"Bearer {token}", "Content-Language": "en-US"},
        params={"limit": 1},
        timeout=45.0,
    )
    if resp.status_code >= 400:
        print(f"ebay: ERROR ({env}) {resp.status_code} {resp.text[:300]}")
        return
    print(f"ebay: LIVE · environment={env}")


def check_shopify() -> None:
    domain = os.getenv("SHOPIFY_STORE_DOMAIN", "").strip()
    token = os.getenv("SHOPIFY_ADMIN_TOKEN", "").strip()
    if not (domain and token):
        print("shopify: SKIPPED (no credentials - intentional for now)")
        return
    print("shopify: credentials present (not verified in this pass)")


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", default="etsy,ebay,shopify")
    args = parser.parse_args()
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    checkers = {"etsy": check_etsy, "ebay": check_ebay, "shopify": check_shopify}
    for name in channels:
        if name in checkers:
            checkers[name]()


if __name__ == "__main__":
    main()
