# Predictive Maintenance & Procurement Agent

XGBoost predicts **days until machine failure** from sensor features. When failure is within **7 days**, a LangGraph agent checks mock inventory, drafts a purchase order, and queues manager approval.

**Prior art:** [ReneWind](../../capstones/renewind/) (McCombs NN predictive maintenance) → this demo adds the autonomous procurement / HITL bridge.

## Run

```bash
cd projects/automated-workflows/predictive-maintenance-agent
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r ../requirements.txt
python train.py
python run_agent.py
```

Optional: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for live PO narrative text.

## Flow

1. Train regression model on `data/sensors.csv`
2. Score assets; activate agent when `days_to_failure <= 7`
3. Agent: inventory lookup → LLM PO draft → approval-queue stub → JSON case packet

## Threshold

`FAILURE_DAYS_THRESHOLD = 7` (see `../shared/thresholds.py`)
