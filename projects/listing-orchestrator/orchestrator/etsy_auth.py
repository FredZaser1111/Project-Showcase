"""Shared Etsy auth helpers — x-api-key must be keystring:shared_secret (Feb 2026+)."""

from __future__ import annotations

import os


def etsy_api_key_header() -> str:
    """Return the x-api-key value Etsy expects."""
    key = os.getenv("ETSY_API_KEY", "").strip()
    secret = os.getenv("ETSY_SHARED_SECRET", "").strip()
    if not key:
        return ""
    if secret:
        return f"{key}:{secret}"
    # Fallback for older setups; live OpenAPI calls will 403 without secret.
    return key


def etsy_credentials_ready() -> bool:
    return bool(
        os.getenv("ETSY_API_KEY", "").strip()
        and os.getenv("ETSY_SHARED_SECRET", "").strip()
        and os.getenv("ETSY_ACCESS_TOKEN", "").strip()
        and os.getenv("ETSY_SHOP_ID", "").strip()
    )
