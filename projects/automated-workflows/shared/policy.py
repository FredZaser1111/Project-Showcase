"""HITL / auto-action policy for predictive maintenance (documented business rules)."""

from __future__ import annotations

from typing import Any

from .thresholds import FAILURE_DAYS_THRESHOLD

# Cost above this always requires manager approval even if parts are in stock.
HIGH_COST_HITL_USD = 1000.0


def decide_procurement_policy(
    *,
    days_to_failure: float,
    unit_cost: float,
    in_stock: bool,
) -> dict[str, Any]:
    """Return policy decision used by the agent / recruiters can cite in interviews."""
    if days_to_failure > FAILURE_DAYS_THRESHOLD:
        return {
            "action": "monitor_only",
            "hitl_required": False,
            "reason": f"days_to_failure {days_to_failure} > threshold {FAILURE_DAYS_THRESHOLD}",
        }
    if not in_stock:
        return {
            "action": "expedite_po_pending_approval",
            "hitl_required": True,
            "reason": "out_of_stock_requires_manager_po",
        }
    if unit_cost >= HIGH_COST_HITL_USD:
        return {
            "action": "reserve_with_manager_notify",
            "hitl_required": True,
            "reason": f"unit_cost {unit_cost} >= high_cost_hitl {HIGH_COST_HITL_USD}",
        }
    return {
        "action": "auto_reserve_and_schedule_pm",
        "hitl_required": False,
        "reason": "in_stock_and_below_high_cost_threshold",
    }
