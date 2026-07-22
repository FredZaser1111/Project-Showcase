# Automated Workflows

Predictive score → autonomous investigation → workflow action (HITL when needed). Built for Appian-style case management and hyperautomation.

Each demo trains a small **XGBoost** model on synthetic data, then runs a **LangGraph** agent that reads the score, calls mock enterprise tools, and emits a structured JSON case packet. LLM copy uses a **mock by default**; set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for live generation.

| Project | Domain | Predictive piece | Agentic piece |
| --- | --- | --- | --- |
| [predictive-maintenance-agent](predictive-maintenance-agent/) | Procurement / supply chain | Days until machine failure | Inventory check → draft PO → manager approval stub |
| [loan-underwriting-agent](loan-underwriting-agent/) | Banking / risk | Loan default probability | Triager → compliance investigator → HITL webhook bridge |
| [churn-savior-agent](churn-savior-agent/) | CRM / retention | Customer churn probability | CRM lookup → ticket analysis → tailored offer / escalation |

**Related DBMS / API demo:** [parts-inventory-api](../parts-inventory-api/) — Spring Boot + JDBC + PostgreSQL spare-parts service. The maintenance agent can call it over REST to **append** stock movements, purchase orders, and approval-queue rows (falls back to mock when the API is down).

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

### Eval harness (maintenance — Track C Phase 1)

```bash
cd projects/automated-workflows
# uses shared .venv if present
.venv\Scripts\python.exe eval_agents.py
```

Writes `predictive-maintenance-agent/outputs/eval_report.json` (part recommendation, threshold gate, reserve-or-order decisions). Exit code nonzero on failures.

### Optional: live spare-parts inventory (maintenance agent)

```bash
cd projects/parts-inventory-api
docker compose up -d
mvn spring-boot:run
# then run predictive-maintenance-agent with PARTS_API_BASE_URL=http://localhost:8080
```

## Portfolio links

- Maintenance continues the [ReneWind](../capstones/renewind/) predictive-maintenance capstone into autonomous procurement.
- Loan underwriting echoes [EasyVisa](../capstones/easyvisa/)-style classification with enterprise gray-zone routing.
