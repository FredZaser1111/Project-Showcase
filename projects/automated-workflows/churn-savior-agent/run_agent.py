"""LangGraph churn agent: score → CRM → ticket analysis → offer/escalation."""

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
from shared.schemas import ChurnCase  # noqa: E402
from shared.thresholds import CHURN_HIGH_RISK  # noqa: E402

from tools import crm_lookup  # noqa: E402

MODEL_PATH = ROOT / "models" / "churn_risk.joblib"
DATA_PATH = ROOT / "data" / "customers.csv"
OUT_DIR = ROOT / "outputs"


class ChurnState(TypedDict, total=False):
    customer_id: str
    features: dict[str, float]
    ticket_text: str
    row: dict[str, Any]
    churn_probability: float
    crm_profile: dict[str, Any]
    ticket_analysis: str
    offer_or_escalation: str
    llm_mode: str
    case: dict[str, Any]


def score_node(state: ChurnState) -> ChurnState:
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]
    row = [[state["features"][f] for f in features]]
    prob = float(model.predict_proba(row)[0][1])
    return {**state, "churn_probability": round(prob, 4)}


def gate(state: ChurnState) -> str:
    return "crm" if state["churn_probability"] > CHURN_HIGH_RISK else "skip"


def crm_node(state: ChurnState) -> ChurnState:
    profile = crm_lookup(pd.Series(state["row"]))
    return {**state, "crm_profile": profile}


def analyze_and_draft_node(state: ChurnState) -> ChurnState:
    profile = state["crm_profile"]
    ticket = state["ticket_text"]
    mock_analysis = (
        f"Ticket themes for {profile['company_name']} ({profile['industry']}, {profile['company_size']}): "
        f"\"{ticket}\" — primary driver appears retention-threatening; recommend proactive outreach."
    )
    analysis, mode1 = complete(
        system="You analyze B2B SaaS support tickets for churn drivers. Be concise.",
        user=f"CRM={json.dumps(profile)}. Ticket={ticket}. Summarize why they may churn.",
        mock_fallback=mock_analysis,
    )
    size = profile.get("company_size", "SMB")
    discount = {"SMB": "15%", "Mid-Market": "12%", "Enterprise": "10%"}.get(size, "10%")
    mock_offer = (
        f"To: {profile['account_manager']}\n"
        f"Subject: High churn risk — {profile['company_name']} ({state['churn_probability']:.0%})\n\n"
        f"Customer shows {state['churn_probability']:.0%} churn probability. "
        f"Suggested dynamic offer: {discount} loyalty credit for 2 billing cycles + success review. "
        f"If Enterprise, escalate to dedicated QBR within 5 business days.\n\n"
        f"Ticket insight: {analysis[:240]}"
    )
    offer, mode2 = complete(
        system="You draft tailored retention offers and AM escalation emails.",
        user=(
            f"Profile={json.dumps(profile)}. Churn={state['churn_probability']}. "
            f"Analysis={analysis}. Draft offer or escalation."
        ),
        mock_fallback=mock_offer,
    )
    mode = mode2 if mode2 != "mock" else mode1
    return {
        **state,
        "ticket_analysis": analysis,
        "offer_or_escalation": offer,
        "llm_mode": mode,
    }


def finalize_high_risk(state: ChurnState) -> ChurnState:
    case = ChurnCase(
        project="churn-savior-agent",
        case_id=state["customer_id"],
        customer_id=state["customer_id"],
        score=state["churn_probability"],
        churn_probability=state["churn_probability"],
        decision="retention_outreach",
        summary=state.get("ticket_analysis", "")[:300],
        actions=["scored_churn", "crm_lookup", "analyzed_tickets", "drafted_offer_or_escalation"],
        crm_profile=state.get("crm_profile", {}),
        ticket_analysis=state.get("ticket_analysis", ""),
        offer_or_escalation=state.get("offer_or_escalation", ""),
        hitl_required=True,
        llm_mode=state.get("llm_mode", "mock"),  # type: ignore[arg-type]
        artifacts={"features": state["features"]},
    )
    return {**state, "case": case.model_dump()}


def skip_node(state: ChurnState) -> ChurnState:
    case = ChurnCase(
        project="churn-savior-agent",
        case_id=state["customer_id"],
        customer_id=state["customer_id"],
        score=state["churn_probability"],
        churn_probability=state["churn_probability"],
        decision="monitor_only",
        summary=f"Below threshold ({state['churn_probability']:.1%} ≤ {CHURN_HIGH_RISK:.0%}). No outreach.",
        actions=["scored_churn"],
        hitl_required=False,
        llm_mode="mock",
        artifacts={"features": state["features"]},
    )
    return {**state, "case": case.model_dump()}


def build_graph():
    g = StateGraph(ChurnState)
    g.add_node("score", score_node)
    g.add_node("crm", crm_node)
    g.add_node("draft", analyze_and_draft_node)
    g.add_node("finalize", finalize_high_risk)
    g.add_node("skip", skip_node)
    g.set_entry_point("score")
    g.add_conditional_edges("score", gate, {"crm": "crm", "skip": "skip"})
    g.add_edge("crm", "draft")
    g.add_edge("draft", "finalize")
    g.add_edge("finalize", END)
    g.add_edge("skip", END)
    return g.compile()


def main() -> None:
    if not MODEL_PATH.exists():
        from train import train

        train()

    df = pd.read_csv(DATA_PATH)
    features = joblib.load(MODEL_PATH)["features"]
    graph = build_graph()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Prefer high-proxy-risk customers so demos show the savior path
    df = df.copy()
    df["_proxy"] = (
        df["support_tickets_90d"] * 0.4
        + df["usage_drop_pct"] * 0.05
        + df["payment_late_count"]
        - df["login_frequency_30d"] * 0.1
        - df["nps_score"] * 0.3
    )
    sample = df.nlargest(8, "_proxy")

    cases: list[dict[str, Any]] = []
    for _, row in sample.iterrows():
        state: ChurnState = {
            "customer_id": str(row["customer_id"]),
            "features": {f: float(row[f]) for f in features},
            "ticket_text": str(row["latest_ticket_text"]),
            "row": row.to_dict(),
        }
        result = graph.invoke(state)
        cases.append(result["case"])

    out_path = OUT_DIR / "churn_cases.json"
    out_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(json.dumps(cases, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
