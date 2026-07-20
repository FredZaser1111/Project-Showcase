"""Mock inventory + approval queue tools for the maintenance agent."""

from __future__ import annotations

from typing import Any

# Part catalogs keyed by asset family prefix
INVENTORY: dict[str, dict[str, Any]] = {
    "bearing-kit-a": {"sku": "BRG-A-220", "qty": 12, "unit_cost": 480.0, "supplier": "NorthPeak Industrial"},
    "bearing-kit-b": {"sku": "BRG-B-110", "qty": 0, "unit_cost": 620.0, "supplier": "NorthPeak Industrial"},
    "motor-seal": {"sku": "MSL-44", "qty": 3, "unit_cost": 95.0, "supplier": "Helix Parts Co"},
    "vfd-module": {"sku": "VFD-900", "qty": 0, "unit_cost": 2400.0, "supplier": "Helix Parts Co"},
}

_APPROVAL_SEQ = 1000


def recommend_part(asset_id: str, vibration_rms: float) -> str:
    if vibration_rms >= 5.5:
        return "vfd-module"
    if vibration_rms >= 3.5:
        return "bearing-kit-b"
    if "ASSET-0" in asset_id or int(asset_id.split("-")[-1]) % 2 == 0:
        return "bearing-kit-a"
    return "motor-seal"


def check_inventory(part_key: str) -> dict[str, Any]:
    item = INVENTORY.get(part_key)
    if not item:
        return {"part_key": part_key, "found": False, "qty": 0}
    return {"part_key": part_key, "found": True, **item, "in_stock": item["qty"] > 0}


def enqueue_approval(po: dict[str, Any]) -> str:
    global _APPROVAL_SEQ
    _APPROVAL_SEQ += 1
    queue_id = f"APPR-{_APPROVAL_SEQ}"
    # Stub: in production this would POST to Appian / email a manager queue
    po["approval_queue_id"] = queue_id
    po["status"] = "pending_manager_approval"
    return queue_id
