#!/usr/bin/env python3
"""Local web app for Tomorrow's Golden Slate.

Run this file, paste a CSV slate into the browser, and screen high-volume 3PT
legs without installing third-party packages.
"""

from __future__ import annotations

import argparse
import json
import math
import threading
import webbrowser
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from screen_three_point_legs import (
    Candidate,
    american_to_decimal,
    build_candidate,
    decimal_to_american,
    filter_candidates,
    load_candidates_from_text,
    pct,
    signed_pct,
)


HOST = "127.0.0.1"
PORT = 8000


def candidate_to_dict(candidate: Candidate) -> dict[str, Any]:
    data = asdict(candidate)
    data["odds_label"] = money(candidate.american_odds)
    data["model_probability_label"] = pct(candidate.model_probability)
    data["implied_probability_label"] = pct(candidate.implied_probability)
    data["edge_label"] = signed_pct(candidate.edge)
    data["no_vig_probability_label"] = pct(candidate.no_vig_probability) if candidate.no_vig_probability is not None else "-"
    data["no_vig_edge_label"] = signed_pct(candidate.no_vig_edge) if candidate.no_vig_edge is not None else "-"
    data["ev_per_unit_label"] = f"{candidate.ev_per_unit:+.3f}"
    data["current_3pa_label"] = f"{candidate.current_3pa:.1f}" if candidate.current_3pa is not None else "-"
    data["volume_delta_label"] = f"{candidate.volume_delta:+.1f}" if candidate.volume_delta is not None else "-"
    data["best_hit_rate_label"] = pct(candidate.best_hit_rate) if candidate.best_hit_rate is not None else "-"
    data["golden_score_label"] = f"{candidate.golden_score:.1f}"
    return data


def money(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def build_parlays(candidates: list[Candidate], *, size: int, max_combos: int) -> list[dict[str, Any]]:
    if size <= 1 or len(candidates) < size:
        return []

    import itertools

    combos: list[dict[str, Any]] = []
    for legs in itertools.combinations(candidates, size):
        model_probability = math.prod(leg.model_probability for leg in legs)
        decimal_odds = math.prod(american_to_decimal(leg.american_odds) for leg in legs)
        implied_probability = 1 / decimal_odds
        ev_per_unit = (model_probability * (decimal_odds - 1)) - (1 - model_probability)
        edge = model_probability - implied_probability
        combos.append(
            {
                "legs": [candidate_to_dict(leg) for leg in legs],
                "odds": money(decimal_to_american(decimal_odds)),
                "model_probability": model_probability,
                "model_probability_label": pct(model_probability),
                "implied_probability": implied_probability,
                "implied_probability_label": pct(implied_probability),
                "edge": edge,
                "edge_label": signed_pct(edge),
                "ev_per_unit": ev_per_unit,
                "ev_per_unit_label": f"{ev_per_unit:+.3f}",
            }
        )

    combos.sort(key=lambda item: (item["ev_per_unit"], item["edge"]), reverse=True)
    return combos[:max_combos]


def screen_payload(payload: dict[str, Any]) -> dict[str, Any]:
    candidates = load_candidates_from_text(str(payload.get("csv", "")))
    filtered = filter_candidates(
        candidates,
        min_probability=float(payload.get("min_probability", 0.50)),
        min_edge=float(payload.get("min_edge", 0.0)),
        min_no_vig_edge=float(payload.get("min_no_vig_edge", 0.0)),
        min_ev=float(payload.get("min_ev", 0.0)),
        min_3pa=float(payload.get("min_3pa", 6.0)),
        require_hit_rate_support=bool(payload.get("require_hit_rate_support", True)),
        require_plus_money=bool(payload.get("require_plus_money", True)),
    )
    top = max(1, int(payload.get("top", 15)))
    parlay_size = int(payload.get("parlay_size", 2))
    max_combos = max(1, int(payload.get("max_combos", 10)))
    visible = filtered[:top]
    return {
        "count": len(filtered),
        "legs": [candidate_to_dict(candidate) for candidate in visible],
        "parlays": build_parlays(visible, size=parlay_size, max_combos=max_combos),
    }


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tomorrow's Golden Slate</title>
  <style>
    :root {
      --bg: #0f1419;
      --panel: #18212b;
      --panel-2: #202b36;
      --border: #334353;
      --text: #edf3f8;
      --muted: #9dadbd;
      --gold: #f6c65b;
      --green: #46d78f;
      --red: #ff6b75;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, rgba(246, 198, 91, 0.14), transparent 30rem), var(--bg);
      color: var(--text);
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 32px 18px 56px; }
    header { margin-bottom: 24px; }
    h1 { margin: 0 0 8px; font-size: clamp(28px, 5vw, 46px); letter-spacing: -0.04em; }
    .lede { margin: 0; color: var(--muted); max-width: 780px; line-height: 1.6; }
    .grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; }
    @media (min-width: 980px) { .grid { grid-template-columns: 0.9fr 1.1fr; align-items: start; } }
    .card {
      background: rgba(24, 33, 43, 0.92);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 18px 80px rgba(0, 0, 0, 0.22);
    }
    label { display: block; color: var(--muted); font-size: 13px; font-weight: 700; margin-bottom: 6px; }
    textarea, input, select {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: #101820;
      color: var(--text);
      padding: 11px 12px;
      font: inherit;
    }
    textarea { min-height: 330px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }
    .filters { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
    @media (min-width: 720px) { .filters { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
    .checks { display: flex; flex-wrap: wrap; gap: 12px; margin: 14px 0; color: var(--muted); }
    .checks label { display: inline-flex; align-items: center; gap: 8px; margin: 0; font-weight: 600; }
    .checks input { width: auto; }
    button {
      border: 0;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--gold), #f09819);
      color: #15110a;
      cursor: pointer;
      font-weight: 800;
      padding: 12px 16px;
    }
    button.secondary { background: var(--panel-2); color: var(--text); border: 1px solid var(--border); }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .summary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
    .stat { background: var(--panel-2); border: 1px solid var(--border); border-radius: 14px; padding: 14px; }
    .stat span { display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .stat strong { display: block; font-size: 26px; margin-top: 2px; }
    .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 14px; }
    table { border-collapse: collapse; min-width: 920px; width: 100%; }
    th, td { padding: 10px 12px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
    th { color: var(--muted); background: #121b23; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
    tr:last-child td { border-bottom: 0; }
    .edge { color: var(--green); font-weight: 800; }
    .muted { color: var(--muted); }
    .error { background: rgba(255, 107, 117, 0.12); border: 1px solid rgba(255, 107, 117, 0.45); color: #ffd4d7; padding: 12px; border-radius: 12px; margin-bottom: 14px; }
    .parlay { background: var(--panel-2); border: 1px solid var(--border); border-radius: 14px; padding: 14px; margin-top: 12px; }
    .parlay strong { color: var(--gold); }
    .small { font-size: 12px; color: var(--muted); line-height: 1.5; }
    code { color: var(--gold); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Tomorrow's Golden Slate</h1>
      <p class="lede">Paste tomorrow's 3PM prop slate as CSV. The tool keeps high-volume legs with 50%+ model probability, positive EV, and edge over the book's implied price.</p>
    </header>
    <div class="grid">
      <section class="card">
        <label for="csvInput">CSV slate</label>
        <textarea id="csvInput" spellcheck="false"></textarea>
        <div class="filters">
          <div><label>Min probability</label><input id="minProbability" type="number" step="0.01" value="0.50"></div>
          <div><label>Min edge</label><input id="minEdge" type="number" step="0.01" value="0.00"></div>
          <div><label>Min no-vig edge</label><input id="minNoVigEdge" type="number" step="0.01" value="0.00"></div>
          <div><label>Min EV/unit</label><input id="minEv" type="number" step="0.01" value="0.00"></div>
          <div><label>Min current 3PA</label><input id="min3pa" type="number" step="0.1" value="6.0"></div>
          <div><label>Top legs</label><input id="top" type="number" min="1" value="15"></div>
          <div><label>Parlay size</label><input id="parlaySize" type="number" min="0" max="6" value="2"></div>
          <div><label>Max parlays</label><input id="maxCombos" type="number" min="1" value="10"></div>
        </div>
        <div class="checks">
          <label><input id="requirePlusMoney" type="checkbox" checked> Plus-money only</label>
          <label><input id="requireHitRate" type="checkbox" checked> Require hit-rate support</label>
        </div>
        <div class="actions">
          <button id="screenBtn">Screen slate</button>
          <button class="secondary" id="sampleBtn" type="button">Load sample</button>
        </div>
        <p class="small"><label for="csvFile">Or upload CSV</label><input id="csvFile" type="file" accept=".csv,text/csv"></p>
        <p class="small">Tip: include <code>under_american_odds</code> when you have it. That lets the app compare your model to the no-vig fair market too.</p>
      </section>
      <section class="card">
        <div id="error"></div>
        <div class="summary">
          <div class="stat"><span>Eligible legs</span><strong id="legCount">0</strong></div>
          <div class="stat"><span>Top parlay EV</span><strong id="topParlayEv">-</strong></div>
        </div>
        <h2>Ranked +EV legs</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th><th>Player</th><th>Market</th><th>Odds</th><th>Model</th><th>Implied</th><th>Edge</th><th>No-vig edge</th><th>EV</th><th>3PA</th><th>Hit rate</th><th>Src</th>
              </tr>
            </thead>
            <tbody id="legsBody"><tr><td colspan="12" class="muted">No slate screened yet.</td></tr></tbody>
          </table>
        </div>
        <h2>Top parlay combinations</h2>
        <div id="parlays"><p class="muted">Run the screener to rank combinations.</p></div>
      </section>
    </div>
  </div>
  <script>
    const sampleCsv = SAMPLE_CSV_JSON;
    const $ = (id) => document.getElementById(id);

    function payload() {
      return {
        csv: $("csvInput").value,
        min_probability: Number($("minProbability").value),
        min_edge: Number($("minEdge").value),
        min_no_vig_edge: Number($("minNoVigEdge").value),
        min_ev: Number($("minEv").value),
        min_3pa: Number($("min3pa").value),
        top: Number($("top").value),
        parlay_size: Number($("parlaySize").value),
        max_combos: Number($("maxCombos").value),
        require_plus_money: $("requirePlusMoney").checked,
        require_hit_rate_support: $("requireHitRate").checked
      };
    }

    function setError(message) {
      $("error").innerHTML = message ? `<div class="error">${message}</div>` : "";
    }

    function render(data) {
      $("legCount").textContent = data.count;
      $("topParlayEv").textContent = data.parlays.length ? data.parlays[0].ev_per_unit_label : "-";
      $("legsBody").innerHTML = data.legs.length ? data.legs.map((leg, index) => `
        <tr>
          <td>${index + 1}</td>
          <td><strong>${escapeHtml(leg.player)}</strong><br><span class="muted">${escapeHtml(leg.team)} vs ${escapeHtml(leg.opponent)}</span></td>
          <td>${escapeHtml([leg.market, leg.line].filter(Boolean).join(" "))}</td>
          <td>${leg.odds_label}</td>
          <td>${leg.model_probability_label}</td>
          <td>${leg.implied_probability_label}</td>
          <td class="edge">${leg.edge_label}</td>
          <td class="edge">${leg.no_vig_edge_label}</td>
          <td class="edge">${leg.ev_per_unit_label}</td>
          <td>${leg.current_3pa_label}</td>
          <td>${leg.best_hit_rate_label}</td>
          <td>${leg.probability_source}</td>
        </tr>
      `).join("") : `<tr><td colspan="12" class="muted">No legs passed the current filters.</td></tr>`;

      $("parlays").innerHTML = data.parlays.length ? data.parlays.map((parlay, index) => `
        <div class="parlay">
          <strong>${index + 1}. ${parlay.legs.map((leg) => escapeHtml(leg.player)).join(" + ")}</strong>
          <div class="small">Odds ${parlay.odds} | Model ${parlay.model_probability_label} | Implied ${parlay.implied_probability_label} | Edge ${parlay.edge_label} | EV/unit ${parlay.ev_per_unit_label}</div>
        </div>
      `).join("") : `<p class="muted">Not enough eligible legs for that parlay size.</p>`;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    async function screenSlate() {
      setError("");
      const response = await fetch("/api/screen", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload())
      });
      const data = await response.json();
      if (!response.ok) {
        setError(escapeHtml(data.error || "Could not screen slate."));
        return;
      }
      render(data);
    }

    $("screenBtn").addEventListener("click", () => screenSlate().catch((error) => setError(escapeHtml(error.message))));
    $("sampleBtn").addEventListener("click", () => { $("csvInput").value = sampleCsv; screenSlate(); });
    $("csvFile").addEventListener("change", async (event) => {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      $("csvInput").value = await file.text();
      screenSlate().catch((error) => setError(escapeHtml(error.message)));
    });
    $("csvInput").value = sampleCsv;
    screenSlate().catch(() => {});
  </script>
</body>
</html>
"""


def index_html() -> str:
    sample_path = __file__.replace("app.py", "example_candidates.csv")
    with open(sample_path, encoding="utf-8") as sample_file:
        sample_csv = sample_file.read().strip()
    return INDEX_HTML.replace("SAMPLE_CSV_JSON", json.dumps(sample_csv))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_text(index_html(), content_type="text/html")
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/screen":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body) if body else {}
            result = screen_payload(payload)
        except Exception as exc:  # noqa: BLE001 - local tool should return readable errors.
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self.send_json(result)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_text(self, content: str, *, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, payload: dict[str, Any], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_text(json.dumps(payload), content_type="application/json", status=status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Tomorrow's Golden Slate local web app.")
    parser.add_argument("--host", default=HOST, help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=PORT, help="Port to bind.")
    parser.add_argument("--no-browser", action="store_true", help="Do not try to open a browser automatically.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"Tomorrow's Golden Slate is running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        if not args.no_browser:
            threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
