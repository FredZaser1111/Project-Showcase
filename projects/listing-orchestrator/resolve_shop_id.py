"""Resolve ETSY_SHOP_ID using tokens already in .env (no browser)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from etsy_oauth import _resolve_shop_id, _upsert_env  # noqa: E402

load_dotenv(ROOT / ".env", override=True)
access = os.getenv("ETSY_ACCESS_TOKEN", "").strip()
if not access:
    raise SystemExit("No ETSY_ACCESS_TOKEN — run etsy_oauth.py first.")
if not os.getenv("ETSY_SHARED_SECRET", "").strip():
    raise SystemExit("Set ETSY_SHARED_SECRET in .env first.")

shop_id = _resolve_shop_id(access)
if not shop_id:
    raise SystemExit("Could not resolve shop_id. Double-check ETSY_SHARED_SECRET.")
_upsert_env({"ETSY_SHOP_ID": shop_id})
print(f"Wrote ETSY_SHOP_ID={shop_id}")
print("Next: python verify_accounts.py --channels etsy")
