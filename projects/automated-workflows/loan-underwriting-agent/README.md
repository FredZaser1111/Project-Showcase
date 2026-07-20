# Loan Underwriting & Risk Mitigation Agent

XGBoost estimates **loan default risk**. Clear cases auto-decide; **gray-zone** (40–60%) routes to a compliance investigator agent, then an Appian-style HITL webhook stub.

**Related mindset:** [EasyVisa](../../capstones/easyvisa/) classification / case outcomes → this demo emphasizes threshold routing and human-in-the-loop escalation.

## Run

```bash
cd projects/automated-workflows/loan-underwriting-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r ../requirements.txt
python train.py
python run_agent.py
```

## Flow

1. Train classifier on `data/loans.csv`
2. **Triager** agent reads risk score
3. Safe / clear-fraud → auto flag; gray zone → **Compliance Investigator**
4. **Appian Bridge** packages report + webhook payload for HITL review

## Thresholds

- Auto-approve: risk &lt; 0.40
- Gray zone / HITL: 0.40–0.60
- Auto-deny: risk &gt; 0.60
