# Automated Workflows

Predictive score → autonomous investigation → workflow action (HITL when needed). Built for Appian-style case management and hyperautomation.

Each demo trains a small **XGBoost** model on synthetic data, then runs a **LangGraph** agent that reads the score, calls mock enterprise tools, and emits a structured JSON case packet. LLM copy uses a **mock by default**; set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for live generation.

| Project | Domain | Predictive piece | Agentic piece |
| --- | --- | --- | --- |
| [predictive-maintenance-agent](predictive-maintenance-agent/) | Procurement / supply chain | Days until machine failure | Inventory check → draft PO → manager approval stub |
| [loan-underwriting-agent](loan-underwriting-agent/) | Banking / risk | Loan default probability | Triager → compliance investigator → HITL webhook bridge |
| [churn-savior-agent](churn-savior-agent/) | CRM / retention | Customer churn probability | CRM lookup → ticket analysis → tailored offer / escalation |

## Shared pattern

```
Synthetic CSV → XGBoost train/score → threshold gate → LangGraph tools + LLM → JSON case packet
```

Business thresholds live in [`shared/thresholds.py`](shared/thresholds.py).

## Quick start (any project)

```bash
cd projects/automated-workflows/<project-name>
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r ../requirements.txt
python train.py
python run_agent.py
```

Outputs land in each project's `outputs/` folder. No API key required.

## Portfolio links

- Maintenance continues the [ReneWind](../capstones/renewind/) predictive-maintenance capstone into autonomous procurement.
- Loan underwriting echoes [EasyVisa](../capstones/easyvisa/)-style classification with enterprise gray-zone routing.
