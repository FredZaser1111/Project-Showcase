"""Inventory + approval tools for the maintenance agent.

When PARTS_API_BASE_URL is set (default http://localhost:8080 if reachable),
calls the Spring Boot / JDBC parts-inventory-api. Falls back to in-memory mock
so demos still run without Docker/Java.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

# Part catalogs keyed by asset family prefix (mock fallback)
INVENTORY: dict[str, dict[str, Any]] = {
    "bearing-kit-a": {"sku": "BRG-A-220", "qty": 12, "unit_cost": 480.0, "supplier": "NorthPeak Industrial"},
    "bearing-kit-b": {"sku": "BRG-B-110", "qty": 0, "unit_cost": 620.0, "supplier": "NorthPeak Industrial"},
    "motor-seal": {"sku": "MSL-44", "qty": 3, "unit_cost": 95.0, "supplier": "Helix Parts Co"},
    "vfd-module": {"sku": "VFD-900", "qty": 0, "unit_cost": 2400.0, "supplier": "Helix Parts Co"},
}

_APPROVAL_SEQ = 1000
_DEFAULT_BASE = "http://localhost:8080"


def _api_base() -> str | None:
    """Return API base URL when configured, or None to force mock."""
    raw = os.environ.get("PARTS_API_BASE_URL", "").strip()
    if raw.lower() in {"", "off", "mock", "none"}:
        # Auto-try local API unless explicitly disabled
        if raw.lower() in {"off", "mock", "none"}:
            return None
        return _DEFAULT_BASE
    return raw.rstrip("/")


def _http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: float = 3.0) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read().decode("utf-8")
        return json.loads(payload) if payload else {}


def api_available() -> bool:
    base = _api_base()
    if not base:
        return False
    try:
        health = _http_json("GET", f"{base}/api/health", timeout=1.5)
        return str(health.get("status", "")).upper() == "UP"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return False


def recommend_part(asset_id: str, vibration_rms: float) -> str:
    if vibration_rms >= 5.5:
        return "vfd-module"
    if vibration_rms >= 3.5:
        return "bearing-kit-b"
    if "ASSET-0" in asset_id or int(asset_id.split("-")[-1]) % 2 == 0:
        return "bearing-kit-a"
    return "motor-seal"


def _mock_check_inventory(part_key: str) -> dict[str, Any]:
    item = INVENTORY.get(part_key)
    if not item:
        return {"part_key": part_key, "found": False, "qty": 0, "in_stock": False, "source": "mock"}
    return {"part_key": part_key, "found": True, **item, "in_stock": item["qty"] > 0, "source": "mock"}


def check_inventory(part_key: str) -> dict[str, Any]:
    base = _api_base()
    if base:
        try:
            row = _http_json("GET", f"{base}/api/parts/{part_key}")
            row["source"] = "parts-inventory-api"
            return row
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            pass
    return _mock_check_inventory(part_key)


def enqueue_approval(po: dict[str, Any]) -> str:
    """Mock HITL queue when live API is unavailable."""
    global _APPROVAL_SEQ
    _APPROVAL_SEQ += 1
    queue_id = f"APPR-{_APPROVAL_SEQ}"
    po["approval_queue_id"] = queue_id
    po["status"] = "pending_manager_approval"
    return queue_id


def _normalize_inventory(raw: dict[str, Any] | None, part_key: str) -> dict[str, Any]:
    """Accept snake_case (GET /parts) or camelCase (PartInventory JSON)."""
    if not raw:
        return {"part_key": part_key, "found": False, "qty": 0, "in_stock": False}
    qty = int(raw.get("qty", raw.get("qtyOnHand", 0)) or 0)
    unit_cost = raw.get("unit_cost", raw.get("unitCost", 0))
    return {
        "part_key": raw.get("part_key") or raw.get("partKey") or part_key,
        "found": bool(raw.get("found", True)),
        "sku": raw.get("sku"),
        "qty": qty,
        "unit_cost": float(unit_cost) if unit_cost is not None else 0.0,
        "supplier": raw.get("supplier"),
        "in_stock": bool(raw.get("in_stock", raw.get("inStock", qty > 0))),
        "description": raw.get("description"),
        "reorder_point": raw.get("reorder_point", raw.get("reorderPoint")),
        "source": raw.get("source", "parts-inventory-api"),
    }


def reserve_or_order(
    part_key: str,
    qty: int = 1,
    *,
    case_id: str | None = None,
    asset_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Append RESERVE or PO+approval via JDBC API; mock fallback mutates local INVENTORY."""
    base = _api_base()
    if base:
        try:
            result = _http_json(
                "POST",
                f"{base}/api/workflows/reserve-or-order",
                {
                    "partKey": part_key,
                    "qty": qty,
                    "caseId": case_id,
                    "assetId": asset_id,
                    "reason": reason or "Predictive maintenance agent",
                },
            )
            inv_raw = result.get("inventory") if isinstance(result.get("inventory"), dict) else {}
            result["inventory"] = _normalize_inventory(inv_raw, part_key)
            result["source"] = "parts-inventory-api"
            # Normalize top-level aliases for agent consumers
            if "partsInStock" not in result and "parts_in_stock" in result:
                result["partsInStock"] = result["parts_in_stock"]
            if "approvalQueueId" not in result and "approval_queue_id" in result:
                result["approvalQueueId"] = result["approval_queue_id"]
            if "purchaseOrder" not in result and "purchase_order" in result:
                result["purchaseOrder"] = result["purchase_order"]
            if "eventType" not in result and "event_type" in result:
                result["eventType"] = result["event_type"]
            return result
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            pass

    inv = _mock_check_inventory(part_key)
    if inv.get("found") and inv.get("qty", 0) >= qty:
        INVENTORY[part_key]["qty"] = max(0, int(INVENTORY[part_key]["qty"]) - qty)
        inv = _mock_check_inventory(part_key)
        return {
            "decision": "reserve_and_schedule_pm",
            "partsInStock": True,
            "inventory": inv,
            "movement": {"movementType": "RESERVE", "qtyDelta": -qty, "source": "mock"},
            "purchaseOrder": None,
            "approvalQueueId": None,
            "eventType": "reserved",
            "source": "mock",
        }

    po: dict[str, Any] = {
        "part_key": part_key,
        "sku": inv.get("sku"),
        "supplier": inv.get("supplier"),
        "qty": qty,
        "unit_cost": inv.get("unit_cost"),
        "in_stock_at_draft": False,
        "asset_id": asset_id,
        "case_id": case_id,
    }
    approval_id = enqueue_approval(po)
    return {
        "decision": "expedite_po_pending_approval",
        "partsInStock": False,
        "inventory": inv,
        "movement": None,
        "purchaseOrder": po,
        "approvalQueueId": approval_id,
        "eventType": "po_drafted",
        "source": "mock",
    }
