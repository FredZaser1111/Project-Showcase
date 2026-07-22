"""LangGraph agent: score → inventory → PO draft → approval queue."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TypedDict

import joblib
import pandas as pd
from langgraph.graph import END, StateGraph

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from shared.llm import complete  # noqa: E402
from shared.schemas import MaintenanceCase  # noqa: E402
from shared.thresholds import FAILURE_DAYS_THRESHOLD  # noqa: E402

from tools import check_inventory, persist_case, recommend_part, reserve_or_order  # noqa: E402

MODEL_PATH = ROOT / "models" / "days_to_failure.joblib"
DATA_PATH = ROOT / "data" / "sensors.csv"
OUT_DIR = ROOT / "outputs"


class MaintState(TypedDict, total=False):
    asset_id: str
    features: dict[str, float]
    days_to_failure: float
    part_key: str
    inventory: dict[str, Any]
    purchase_order: dict[str, Any]
    approval_queue_id: str
    summary: str
    llm_mode: str
    case: dict[str, Any]


def score_asset(state: MaintState) -> MaintState:
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]
    row = [[state["features"][f] for f in features]]
    days = max(0.0, float(model.predict(row)[0]))
    return {**state, "days_to_failure": round(days, 2)}


def inventory_node(state: MaintState) -> MaintState:
    part = recommend_part(state["asset_id"], state["features"]["vibration_rms"])
    inv = check_inventory(part)
    return {**state, "part_key": part, "inventory": inv}


def draft_po_node(state: MaintState) -> MaintState:
    inv = state["inventory"]
    mock = (
        f"Purchase Order DRAFT for {state['asset_id']}\n"
        f"Supplier: {inv.get('supplier', 'TBD')}\n"
        f"SKU: {inv.get('sku', state['part_key'])} x 1 @ ${inv.get('unit_cost', 0):.2f}\n"
        f"Reason: Predictive model estimates failure in {state['days_to_failure']} days "
        f"(threshold {FAILURE_DAYS_THRESHOLD}). Vibration RMS={state['features']['vibration_rms']}.\n"
        f"Stock status: {'IN STOCK — reserve & schedule PM' if inv.get('in_stock') else 'OUT OF STOCK — expedite order'}.\n"
        "Terms: Net 30, ship to Warehouse Dock B, reference predictive-maintenance case."
    )
    text, mode = complete(
        system="You draft concise industrial purchase orders matching supplier template constraints.",
        user=(
            f"Asset {state['asset_id']} fails in ~{state['days_to_failure']} days. "
            f"Inventory: {json.dumps(inv)}. Features: {json.dumps(state['features'])}. "
            "Draft a PO narrative for manager approval."
        ),
        mock_fallback=mock,
    )
    po = {
        "asset_id": state["asset_id"],
        "part_key": state["part_key"],
        "sku": inv.get("sku"),
        "supplier": inv.get("supplier"),
        "qty": 1,
        "unit_cost": inv.get("unit_cost"),
        "in_stock_at_draft": bool(inv.get("in_stock")),
        "narrative": text,
    }
    return {**state, "purchase_order": po, "llm_mode": mode, "summary": text[:280]}


def approval_node(state: MaintState) -> MaintState:
    """Persist reserve or PO via parts-inventory-api (JDBC append) when available."""
    case_id = f"PM-{state['asset_id']}"
    workflow = reserve_or_order(
        state["part_key"],
        qty=1,
        case_id=case_id,
        asset_id=state["asset_id"],
        reason=f"Predicted failure in {state['days_to_failure']} days",
    )
    parts_in_stock = bool(workflow.get("partsInStock", state["inventory"].get("in_stock")))
    decision = str(workflow.get("decision") or (
        "reserve_and_schedule_pm" if parts_in_stock else "expedite_po_pending_approval"
    ))
    po = dict(state["purchase_order"])
    api_po = workflow.get("purchaseOrder")
    if isinstance(api_po, dict):
        # Normalize Java camelCase fields into the case packet
        po.update(
            {
                "sku": api_po.get("sku", po.get("sku")),
                "supplier": api_po.get("supplier", po.get("supplier")),
                "qty": api_po.get("qty", po.get("qty")),
                "unit_cost": float(api_po["unitCost"]) if api_po.get("unitCost") is not None else po.get("unit_cost"),
                "status": api_po.get("status", "pending_manager_approval"),
                "po_id": str(api_po.get("poId")) if api_po.get("poId") else None,
                "narrative": api_po.get("narrative") or po.get("narrative"),
            }
        )
    queue_id = workflow.get("approvalQueueId")
    if queue_id:
        po["approval_queue_id"] = queue_id
        po["status"] = po.get("status") or "pending_manager_approval"
    elif parts_in_stock:
        po["status"] = "reserved_from_stock"
        po["approval_queue_id"] = None

    inventory = workflow.get("inventory") if isinstance(workflow.get("inventory"), dict) else state["inventory"]
    actions = [
        "scored_days_to_failure",
        "checked_inventory",
        "drafted_purchase_order",
        "appended_inventory_workflow",
    ]
    if queue_id:
        actions.append("enqueued_manager_approval")

    case = MaintenanceCase(
        project="predictive-maintenance-agent",
        case_id=case_id,
        asset_id=state["asset_id"],
        score=state["days_to_failure"],
        days_to_failure=state["days_to_failure"],
        decision=decision,
        summary=state.get("summary", ""),
        actions=actions,
        parts_in_stock=parts_in_stock,
        purchase_order=po,
        approval_queue_id=queue_id,
        hitl_required=bool(queue_id) or not parts_in_stock,
        llm_mode=state.get("llm_mode", "mock"),  # type: ignore[arg-type]
        artifacts={
            "inventory": inventory,
            "features": state["features"],
            "workflow_event": workflow.get("eventType"),
            "inventory_source": inventory.get("source") if isinstance(inventory, dict) else workflow.get("source"),
            "movement": workflow.get("movement"),
        },
    )
    return {**state, "purchase_order": po, "approval_queue_id": queue_id or None, "case": case.model_dump()}


def should_act(state: MaintState) -> str:
    if state["days_to_failure"] <= FAILURE_DAYS_THRESHOLD:
        return "inventory"
    return "skip"


def skip_node(state: MaintState) -> MaintState:
    case = MaintenanceCase(
        project="predictive-maintenance-agent",
        case_id=f"PM-{state['asset_id']}",
        asset_id=state["asset_id"],
        score=state["days_to_failure"],
        days_to_failure=state["days_to_failure"],
        decision="monitor_only",
        summary=f"Asset healthy enough ({state['days_to_failure']} days > {FAILURE_DAYS_THRESHOLD}). No PO.",
        actions=["scored_days_to_failure"],
        parts_in_stock=True,
        hitl_required=False,
        llm_mode="mock",
        artifacts={"features": state["features"]},
    )
    return {**state, "case": case.model_dump()}


def build_graph():
    g = StateGraph(MaintState)
    g.add_node("score", score_asset)
    g.add_node("inventory", inventory_node)
    g.add_node("draft_po", draft_po_node)
    g.add_node("approval", approval_node)
    g.add_node("skip", skip_node)
    g.set_entry_point("score")
    g.add_conditional_edges("score", should_act, {"inventory": "inventory", "skip": "skip"})
    g.add_edge("inventory", "draft_po")
    g.add_edge("draft_po", "approval")
    g.add_edge("approval", END)
    g.add_edge("skip", END)
    return g.compile()


def pick_assets(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """Prefer at-risk assets so the demo shows the procurement path."""
    scored = df.copy()
    # Rough heuristic pre-filter using vibration/temp; agent will rescore with model
    scored["_risk"] = scored["vibration_rms"] * 2 + (scored["temperature_c"] - 60) * 0.1
    return scored.nlargest(limit, "_risk").drop(columns=["_risk"])


def main() -> None:
    if not MODEL_PATH.exists():
        from train import train

        train()

    df = pd.read_csv(DATA_PATH)
    features = joblib.load(MODEL_PATH)["features"]
    graph = build_graph()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []

    for _, row in pick_assets(df).iterrows():
        state: MaintState = {
            "asset_id": str(row["asset_id"]),
            "features": {f: float(row[f]) for f in features},
        }
        result = graph.invoke(state)
        case = result["case"]
        cases.append(case)
        if persist_case(case):
            case.setdefault("artifacts", {})
            if isinstance(case["artifacts"], dict):
                case["artifacts"]["persisted_to_parts_api"] = True

    out_path = OUT_DIR / "maintenance_cases.json"
    out_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(json.dumps(cases, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
