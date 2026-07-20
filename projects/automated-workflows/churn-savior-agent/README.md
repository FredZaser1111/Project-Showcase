# Autonomous Customer Churn Savior Agent

XGBoost scores **churn probability**. For customers above **80%** risk, a LangGraph agent looks up a mock CRM profile, analyzes support ticket text, and drafts a tailored retention offer or AM escalation.

## Run

```bash
cd projects/automated-workflows/churn-savior-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r ../requirements.txt
python train.py
python run_agent.py
```

## Flow

1. Train classifier on `data/customers.csv`
2. Filter customers with `P(churn) > 0.80`
3. Agent: Salesforce mock → ticket LLM analysis → offer / escalation draft → JSON case packet

## Threshold

`CHURN_HIGH_RISK = 0.80` (see `../shared/thresholds.py`)
