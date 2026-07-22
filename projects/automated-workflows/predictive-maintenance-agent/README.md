# Predictive Maintenance & Procurement Agent

XGBoost predicts **days until machine failure** from sensor features. When failure is within **7 days**, a LangGraph agent checks spare-parts inventory, drafts a purchase order, and queues manager approval.

**Prior art:** [ReneWind](../../capstones/renewind/) (McCombs NN predictive maintenance) → this demo adds the autonomous procurement / HITL bridge.

**Live inventory (optional):** [parts-inventory-api](../../parts-inventory-api/) — Spring Boot + JDBC + PostgreSQL. When the API is up, `check_inventory` and `reserve_or_order` append stock movements / POs / approval rows instead of using the in-memory mock.

## Run (mock inventory — no Java required)

```bash
cd projects/automated-workflows/predictive-maintenance-agent
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r ../requirements.txt
python train.py
python run_agent.py
```

Optional: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for live PO narrative text.

## Run with live Parts Inventory API

```bash
# Terminal 1
cd projects/parts-inventory-api
docker compose up -d
mvn spring-boot:run

# Terminal 2
cd projects/automated-workflows/predictive-maintenance-agent
set PARTS_API_BASE_URL=http://localhost:8080
python run_agent.py
```

Open HITL inbox: http://localhost:8080/inbox

If the API is unreachable, tools fall back to the mock catalog automatically. Set `PARTS_API_BASE_URL=mock` to force mock mode.

Cases are written to `outputs/maintenance_cases.json` and, when the API is up, upserted into Postgres `agent_cases`.

## Eval

```bash
cd projects/automated-workflows
python eval_agents.py
```

## Flow

1. Train regression model on `data/sensors.csv`
2. Score assets; activate agent when `days_to_failure <= 7`
3. Agent: inventory lookup → LLM PO draft → **append reserve or PO** (API or mock) → JSON case packet

## Threshold

`FAILURE_DAYS_THRESHOLD = 7` (see `../shared/thresholds.py`)
