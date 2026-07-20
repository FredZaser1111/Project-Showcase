"""Generate synthetic loan data and train an XGBoost default-risk classifier."""

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
DATA = ROOT / "data" / "loans.csv"
MODEL_DIR = ROOT / "models"
FEATURES = [
    "credit_score",
    "debt_to_income",
    "employment_years",
    "loan_amount",
    "loan_term_months",
    "prior_delinquencies",
]


def synthesize(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    credit = rng.integers(520, 820, n)
    dti = rng.uniform(0.08, 0.65, n)
    emp = rng.uniform(0, 25, n)
    amount = rng.uniform(5000, 120000, n)
    term = rng.choice([24, 36, 48, 60], n)
    prior = rng.integers(0, 6, n)
    logit = (
        -0.012 * (credit - 650)
        + 4.5 * (dti - 0.3)
        - 0.08 * emp
        + 0.000008 * amount
        + 0.35 * prior
        + rng.normal(0, 0.4, n)
    )
    prob = 1 / (1 + np.exp(-logit))
    defaulted = (rng.random(n) < prob).astype(int)
    return pd.DataFrame(
        {
            "application_id": [f"LN-{i:05d}" for i in range(n)],
            "credit_score": credit,
            "debt_to_income": dti.round(3),
            "employment_years": emp.round(1),
            "loan_amount": amount.round(2),
            "loan_term_months": term,
            "prior_delinquencies": prior,
            "region": rng.choice(["northeast", "southeast", "midwest", "west"], n),
            "defaulted": defaulted,
        }
    )


def train() -> dict:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        synthesize().to_csv(DATA, index=False)

    df = pd.read_csv(DATA)
    x = df[FEATURES]
    y = df["defaulted"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    model = XGBClassifier(
        n_estimators=120,
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
    joblib.dump({"model": model, "features": FEATURES}, MODEL_DIR / "default_risk.joblib")
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
