"""Etsy OAuth (PKCE) — link your Cozy seller shop to listing-orchestrator .env."""

from __future__ import annotations

import base64
import hashlib
import http.server
import os
import secrets
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import httpx
from dotenv import load_dotenv

from orchestrator.etsy_auth import etsy_api_key_header

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
REDIRECT_URI = "http://localhost:8765/callback"
SCOPES = "listings_r listings_w shops_r shops_w transactions_r"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _upsert_env(updates: dict[str, str]) -> None:
    lines: list[str] = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    keys = set(updates)
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            out.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in keys:
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def _resolve_shop_id(access: str) -> str:
    headers = {
        "Authorization": f"Bearer {access}",
        "x-api-key": etsy_api_key_header(),
    }
    with httpx.Client(timeout=45.0) as client:
        me = client.get("https://openapi.etsy.com/v3/application/users/me", headers=headers)
        if me.status_code < 400:
            data = me.json()
            shop_id = str(data.get("shop_id") or "")
            user_id = str(data.get("user_id") or data.get("user_id") or "")
            if shop_id:
                return shop_id
            if user_id:
                shops = client.get(
                    f"https://openapi.etsy.com/v3/application/users/{user_id}/shops",
                    headers=headers,
                )
                if shops.status_code < 400:
                    results = shops.json().get("results") or []
                    if results:
                        return str(results[0].get("shop_id") or "")
            print(f"users/me OK but no shop_id in body: {list(data.keys())}", flush=True)
        else:
            print(f"users/me failed: {me.status_code} {me.text[:300]}", flush=True)
    return ""


def main() -> None:
    load_dotenv(ENV_PATH)
    client_id = os.getenv("ETSY_API_KEY", "").strip()
    shared_secret = os.getenv("ETSY_SHARED_SECRET", "").strip()
    if not client_id:
        raise SystemExit(
            "Set ETSY_API_KEY (Etsy app keystring) in .env first.\n"
            "Create an app at https://www.etsy.com/developers/your-apps"
        )
    if not shared_secret:
        raise SystemExit(
            "Set ETSY_SHARED_SECRET in .env (Your Apps → See API Key Details → Shared Secret).\n"
            "Etsy requires x-api-key as keystring:shared_secret."
        )

    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    state = secrets.token_urlsafe(16)

    auth_qs = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    auth_url = f"https://www.etsy.com/oauth/connect?{auth_qs}"

    result: dict[str, str] = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("state", [None])[0] != state:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"State mismatch")
                return
            if "error" in qs:
                result["error"] = qs["error"][0]
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"OAuth error - see terminal")
                return
            result["code"] = qs.get("code", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Etsy connected</h1><p>You can close this tab.</p></body></html>"
            )

        def log_message(self, format, *args):  # noqa: A003
            return

    server = http.server.HTTPServer(("127.0.0.1", 8765), Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("Opening Etsy authorization in your browser…", flush=True)
    print("If it does not open, visit:\n", auth_url, "\n", flush=True)
    webbrowser.open(auth_url)
    thread.join(timeout=300)
    server.server_close()

    if result.get("error"):
        raise SystemExit(f"OAuth error: {result['error']}")
    code = result.get("code")
    if not code:
        raise SystemExit("No authorization code received (timed out?). Try again.")

    print("Exchanging code for tokens…", flush=True)
    token_resp = httpx.post(
        "https://api.etsy.com/v3/public/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "code": code,
            "code_verifier": verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=45.0,
    )
    token_resp.raise_for_status()
    tokens = token_resp.json()
    access = tokens["access_token"]
    refresh = tokens.get("refresh_token", "")

    # Persist tokens immediately so a shop_id lookup failure does not lose OAuth work.
    _upsert_env(
        {
            "ETSY_API_KEY": client_id,
            "ETSY_ACCESS_TOKEN": access,
            "ETSY_REFRESH_TOKEN": refresh,
        }
    )
    print("Wrote access + refresh tokens to .env", flush=True)

    print("Resolving shop id…", flush=True)
    shop_id = _resolve_shop_id(access)
    if not shop_id:
        raise SystemExit(
            "Tokens saved, but shop_id could not be resolved.\n"
            "Confirm ETSY_SHARED_SECRET is correct, then re-run or set ETSY_SHOP_ID manually."
        )

    _upsert_env({"ETSY_SHOP_ID": shop_id})
    print("Wrote tokens + shop id to .env", flush=True)
    print(f"  ETSY_SHOP_ID={shop_id}", flush=True)
    print("Next: python verify_accounts.py --channels etsy", flush=True)


if __name__ == "__main__":
    main()
