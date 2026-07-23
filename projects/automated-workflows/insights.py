#!/usr/bin/env python3
"""Grounded GenAI recommendations over inventory workflow events (with citations).

Prefers live Parts Inventory API events; falls back to maintenance case JSON.
Mock LLM by default — set OPENAI_API_KEY / ANTHROPIC_API_KEY for live copy.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from shared.llm import complete  # noqa: E402

OUT = ROOT / "predictive-maintenance-agent" / "outputs" / "insights.json"
CASES = ROOT / "predictive-maintenance-agent" / "outputs" / "maintenance_cases.json"


def _http_json(url: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=3.0) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, list) else []


def load_events() -> list[dict[str, Any]]:
    base = os.environ.get("PARTS_API_BASE_URL", "http://localhost:8080").rstrip("/")
    if base.lower() not in {"mock", "off", "none"}:
        try:
            return _http_json(f"{base}/api/workflow-events?limit=30")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            pass
    if not CASES.exists():
        return []
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    events: list[dict[str, Any]] = []
    for case in cases:
        events.append(
            {
                "event_id": f"local-{case.get('case_id')}",
                "event_type": case.get("decision"),
                "case_id": case.get("case_id"),
                "part_key": (case.get("purchase_order") or {}).get("part_key"),
                "detail": json.dumps(
                    {
                        "hitl_required": case.get("hitl_required"),
                        "parts_in_stock": case.get("parts_in_stock"),
                        "summary": case.get("summary", "")[:200],
                    }
                ),
            }
        )
    return events


def main() -> None:
    events = load_events()
    citations = [
        {
            "event_id": e.get("event_id"),
            "event_type": e.get("event_type"),
            "case_id": e.get("case_id"),
            "part_key": e.get("part_key"),
        }
        for e in events[:12]
    ]
    context = json.dumps(citations, indent=2)
    mock = (
        "Recommended next actions (mock):\n"
        "1. Clear open HITL approvals for out-of-stock VFDs before weekend PM windows "
        f"[cite: {citations[0]['event_id'] if citations else 'n/a'}].\n"
        "2. Auto-reserve in-stock bearing kits under $1000 per policy; notify dock B.\n"
        "3. Review repeated expedite POs for the same SKU — raise reorder_point.\n"
        "Citations refer to workflow_events.event_id values."
    )
    text, mode = complete(
        system=(
            "You are a maintenance planner. Recommend at most 3 next actions. "
            "Every claim must cite an event_id from the provided context."
        ),
        user=f"Workflow events:\n{context}\n\nRecommend next actions with citations.",
        mock_fallback=mock,
    )
    payload = {
        "llm_mode": mode,
        "citation_count": len(citations),
        "citations": citations,
        "recommendation": text,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
