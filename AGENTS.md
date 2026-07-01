# AGENTS.md

## Cursor Cloud specific instructions

This is a small monorepo ("Project Showcase") with three deliverables:

| Path | What it is | Runnable here? |
| --- | --- | --- |
| `index.html` | Static GitHub Pages landing page | Yes — serve with any static server |
| `projects/nba-z-lock/` | Flask + scikit-learn NBA game predictor | Yes — main app |
| `projects/seo-optimizer/` | Windows `.exe` + launcher scripts only (no source committed) | No — not runnable in Linux/CI |

### nba-z-lock (main app)

- Python app. Dependencies live in `projects/nba-z-lock/requirements.txt` and are installed into a local venv at `projects/nba-z-lock/venv` (the update script handles this). `python3.12-venv` (apt) is required to create the venv and is already provisioned in the VM snapshot.
- Standard run/build/train commands are documented in `projects/nba-z-lock/README.md` and `README_SETUP.md`. Use the venv interpreter, e.g. `projects/nba-z-lock/venv/bin/python app.py` (run from inside `projects/nba-z-lock`). App serves at http://127.0.0.1:5000.
- `.env` is created by copying `env.example`. No API key is needed for local dev because `config.API_PROVIDER` defaults to `nba_api` (no key), but see the network caveat below.

- IMPORTANT network caveat: `nba_api` talks to `stats.nba.com`, which is NOT reachable from this environment (requests time out after ~30s). Consequences:
  - Live data collection (`scripts/collect_historical_data.py`) and the `/api/roster/<id>` endpoint will hang/fail. The web UI still works for predictions — the roster fetch is async and only powers the optional injury feature; it does not block "Get Prediction".
  - The `test_*.py` scripts and `test_full_setup.py` mostly hit `stats.nba.com` and will fail on network, not because the code is broken.

- Offline data + model: because live collection is blocked, generate schema-compatible sample data with `projects/nba-z-lock/scripts/generate_sample_data.py` (writes `data/teams.json` + `data/historical_games.json` using the real static team list and synthetic games), then train with `python models/train_model.py` (~90s) to produce `models/best_model.pkl`. These data/model files are git-ignored and regenerable; they are not "real" NBA results, only enough to exercise the full prediction pipeline. If `stats.nba.com` ever becomes reachable, prefer the real `scripts/collect_historical_data.py` instead.
- The prediction path (`/api/predict`) uses cached/estimated player stats (`use_cache=True`), so it does NOT hit the network and returns in <1s once a model exists.

- Lint/tests: there is no configured linter or pytest suite. A byte-compile check (`python -m compileall`) works as a syntax gate; `python setup.py` verifies dependencies are importable.

### Landing page

- Static; serve the repo root with e.g. `python3 -m http.server 8080` and open `/index.html`.
