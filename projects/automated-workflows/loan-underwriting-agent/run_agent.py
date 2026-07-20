"""Multi-agent LangGraph: Triager → Compliance Investigator → Appian Bridge."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Literal, TypedDict

import joblib
import pandas as pd
from langgraph.graph import END, StateGraph

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from shared.llm import complete  # noqa: E402
from shared.schemas import LoanCase  # noqa: E402
from shared.thresholds import LOAN_GRAY_HIGH, LOAN_GRAY_LOW  # noqa: E402

from tools import lookup_regulations  # noqa: E402

MODEL_PATH = ROOT / "models" / "default_risk.joblib"
DATA_PATH = ROOT / "data" / "loans.csv"
OUT_DIR = ROOT / "outputs"

Route = Literal["auto_approve", "auto_deny", "compliance_review"]


class LoanState(TypedDict, total=False):
    application_id: str
    region: str
    features: dict[str, float]
    default_risk: float
    route: Route
    compliance_report: str
    webhook_payload: dict[str, Any]
    llm_mode: str
    case: dict[str, Any]


def score_node(state: LoanState) -> LoanState:
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]
    row = [[state["features"][f] for f in features]]
    risk = float(model.predict_proba(row)[0][1])
    return {**state, "default_risk": round(risk, 4)}


def triager_node(state: LoanState) -> LoanState:
    risk = state["default_risk"]
    if risk < LOAN_GRAY_LOW:
        route: Route = "auto_approve"
    elif risk > LOAN_GRAY_HIGH:
        route = "auto_deny"
    else:
        route = "compliance_review"
    return {**state, "route": route}


def route_after_triage(state: LoanState) -> str:
    if state["route"] == "compliance_review":
        return "compliance"
    return "bridge"


def compliance_node(state: LoanState) -> LoanState:
    regs = lookup_regulations(state.get("region", "northeast"))
    mock = (
        f"Compliance review for {state['application_id']}\n"
        f"Default risk: {state['default_risk']:.1%} (gray zone {LOAN_GRAY_LOW:.0%}-{LOAN_GRAY_HIGH:.0%}).\n"
        f"Applicant signals: credit={state['features']['credit_score']}, "
        f"DTI={state['features']['debt_to_income']}, "
        f"prior_delinquencies={state['features']['prior_delinquencies']}.\n"
        "Applicable regional rules:\n- " + "\n- ".join(regs) + "\n"
        "Recommendation: hold funding pending human underwriter attestation of compensating factors."
    )
    text, mode = complete(
        system="You are a banking compliance investigator. Produce structured, citation-aware risk summaries.",
        user=(
            f"App {state['application_id']} risk={state['default_risk']}. "
            f"Features={json.dumps(state['features'])}. Region={state.get('region')}. "
            f"Regulations={regs}. Write a short compliance report for HITL review."
        ),
        mock_fallback=mock,
    )
    return {**state, "compliance_report": text, "llm_mode": mode}


def bridge_node(state: LoanState) -> LoanState:
    route = state["route"]
    hitl = route == "compliance_review"
    decision_map = {
        "auto_approve": "approve_automated",
        "auto_deny": "deny_automated",
        "compliance_review": "escalate_hitl",
    }
    webhook = {
        "destination": "appian_hitl_review_dashboard",
        "application_id": state["application_id"],
        "default_risk": state["default_risk"],
        "route": route,
        "hitl_required": hitl,
        "compliance_report": state.get("compliance_report"),
        "features": state["features"],
        "region": state.get("region"),
    }
    case = LoanCase(
        project="loan-underwriting-agent",
        case_id=state["application_id"],
        application_id=state["application_id"],
        score=state["default_risk"],
        default_risk=state["default_risk"],
        route=route,
        decision=decision_map[route],
        summary=(
            state.get("compliance_report", f"Routed as {route} at risk {state['default_risk']:.1%}")[:400]
        ),
        actions=["scored_default_risk", "triaged", *(["compliance_investigated"] if hitl else []), "webhook_packaged"],
        compliance_report=state.get("compliance_report"),
        webhook_payload=webhook,
        hitl_required=hitl,
        llm_mode=state.get("llm_mode", "mock"),  # type: ignore[arg-type]
        artifacts={"region": state.get("region"), "features": state["features"]},
    )
    return {**state, "webhook_payload": webhook, "case": case.model_dump()}


def build_graph():
    g = StateGraph(LoanState)
    g.add_node("score", score_node)
    g.add_node("triager", triager_node)
    g.add_node("compliance", compliance_node)
    g.add_node("bridge", bridge_node)
    g.set_entry_point("score")
    g.add_edge("score", "triager")
    g.add_conditional_edges("triager", route_after_triage, {"compliance": "compliance", "bridge": "bridge"})
    g.add_edge("compliance", "bridge")
    g.add_edge("bridge", END)
    return g.compile()


def pick_applications(df: pd.DataFrame, features: list[str], model) -> pd.DataFrame:
    """Score the book and sample approve / gray-zone / deny for a readable demo."""
    scored = df.copy()
    scored["_risk"] = model.predict_proba(scored[features])[:, 1]
    low = scored[scored["_risk"] < LOAN_GRAY_LOW].nsmallest(2, "_risk")
    gray = scored[
        (scored["_risk"] >= LOAN_GRAY_LOW) & (scored["_risk"] <= LOAN_GRAY_HIGH)
    ].assign(_d=(scored["_risk"] - 0.5).abs()).nsmallest(3, "_d")
    high = scored[scored["_risk"] > LOAN_GRAY_HIGH].nlargest(2, "_risk")
    mixed = pd.concat([low, gray, high]).drop_duplicates("application_id")
    return mixed.drop(columns=[c for c in mixed.columns if c.startswith("_")])


def main() -> None:
    if not MODEL_PATH.exists():
        from train import train

        train()

    df = pd.read_csv(DATA_PATH)
    bundle = joblib.load(MODEL_PATH)
    features = bundle["features"]
    model = bundle["model"]
    graph = build_graph()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []

    for _, row in pick_applications(df, features, model).iterrows():
        state: LoanState = {
            "application_id": str(row["application_id"]),
            "region": str(row.get("region", "northeast")),
            "features": {f: float(row[f]) for f in features},
        }
        result = graph.invoke(state)
        cases.append(result["case"])

    out_path = OUT_DIR / "loan_cases.json"
    out_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(json.dumps(cases, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
