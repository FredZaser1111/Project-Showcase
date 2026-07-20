"""Generate synthetic customer behavior data and train churn classifier."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "customers.csv"
MODEL_DIR = ROOT / "models"
FEATURES = [
    "login_frequency_30d",
    "support_tickets_90d",
    "usage_drop_pct",
    "payment_late_count",
    "nps_score",
    "tenure_months",
]


def synthesize(n: int = 900, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    logins = rng.integers(0, 40, n)
    tickets = rng.integers(0, 12, n)
    usage_drop = rng.uniform(-10, 80, n)
    late = rng.integers(0, 5, n)
    nps = rng.integers(0, 11, n)
    tenure = rng.integers(1, 60, n)
    logit = (
        -0.08 * logins
        + 0.35 * tickets
        + 0.04 * usage_drop
        + 0.55 * late
        - 0.25 * nps
        - 0.02 * tenure
        + rng.normal(0, 0.5, n)
    )
    prob = 1 / (1 + np.exp(-logit))
    churned = (rng.random(n) < prob).astype(int)
    industries = rng.choice(["SaaS", "Healthcare", "Retail", "Manufacturing", "Finance"], n)
    sizes = rng.choice(["SMB", "Mid-Market", "Enterprise"], n, p=[0.45, 0.35, 0.2])
    ticket_templates = [
        "Billing confusion after plan change; waiting on refund.",
        "Product downtime last week; team lost confidence.",
        "Onboarding incomplete; champion left the company.",
        "Competitor demo scheduled; pricing feels high.",
        "Feature gap vs roadmap promises; escalation requested.",
    ]
    tickets_text = rng.choice(ticket_templates, n)
    return pd.DataFrame(
        {
            "customer_id": [f"CUS-{i:05d}" for i in range(n)],
            "company_name": [f"Acme Corp {i}" for i in range(n)],
            "industry": industries,
            "company_size": sizes,
            "account_manager": [f"AM-{(i % 8) + 1}" for i in range(n)],
            "login_frequency_30d": logins,
            "support_tickets_90d": tickets,
            "usage_drop_pct": usage_drop.round(1),
            "payment_late_count": late,
            "nps_score": nps,
            "tenure_months": tenure,
            "latest_ticket_text": tickets_text,
            "churned": churned,
        }
    )


def train() -> dict:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        synthesize().to_csv(DATA, index=False)

    df = pd.read_csv(DATA)
    x = df[FEATURES]
    y = df["churned"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
    )
    model.fit(x_train, y_train)
    proba = model.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "features": FEATURES,
        "positive_rate": float(y.mean()),
    }
    joblib.dump({"model": model, "features": FEATURES}, MODEL_DIR / "churn_risk.joblib")
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
