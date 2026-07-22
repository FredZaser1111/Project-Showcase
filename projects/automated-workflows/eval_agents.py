#!/usr/bin/env python3
"""CI-friendly eval harness for predictive-maintenance agent decision logic.

Force mock inventory so the suite is deterministic without Docker/Java:
  set PARTS_API_BASE_URL=mock

Exit code 0 on full pass; writes predictive-maintenance-agent/outputs/eval_report.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
AGENT = ROOT / "predictive-maintenance-agent"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AGENT))

os.environ["PARTS_API_BASE_URL"] = "mock"

from shared.thresholds import FAILURE_DAYS_THRESHOLD  # noqa: E402
from tools import recommend_part, reserve_or_order  # noqa: E402


def threshold_route(days_to_failure: float) -> str:
    return "inventory" if days_to_failure <= FAILURE_DAYS_THRESHOLD else "skip"


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    kind = case["kind"]
    if kind == "recommend_part":
        got = recommend_part(case["asset_id"], float(case["vibration_rms"]))
        ok = got == case["expected_part"]
        return {"id": case["id"], "ok": ok, "got": got, "expected": case["expected_part"]}
    if kind == "threshold_gate":
        got = threshold_route(float(case["days_to_failure"]))
        ok = got == case["expected_route"]
        return {"id": case["id"], "ok": ok, "got": got, "expected": case["expected_route"]}
    if kind == "reserve_or_order":
        result = reserve_or_order(
            case["part_key"],
            qty=int(case.get("qty", 1)),
            case_id=f"EVAL-{case['id']}",
            asset_id="ASSET-EVAL",
        )
        got_decision = result.get("decision")
        got_stock = bool(result.get("partsInStock"))
        ok = got_decision == case["expected_decision"] and got_stock == bool(case["expected_in_stock"])
        return {
            "id": case["id"],
            "ok": ok,
            "got": {"decision": got_decision, "partsInStock": got_stock, "source": result.get("source")},
            "expected": {
                "decision": case["expected_decision"],
                "partsInStock": case["expected_in_stock"],
            },
        }
    return {"id": case.get("id", "?"), "ok": False, "error": f"unknown kind {kind}"}


def main() -> int:
    cases = json.loads((ROOT / "eval" / "golden_maintenance.json").read_text(encoding="utf-8"))
    results = [run_case(c) for c in cases]
    passed = sum(1 for r in results if r.get("ok"))
    report = {
        "suite": "predictive-maintenance",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }
    out_dir = AGENT / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "eval_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
