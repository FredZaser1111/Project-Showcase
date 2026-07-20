"""Generate synthetic factory sensor data and train an XGBoost days-to-failure model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "sensors.csv"
MODEL_DIR = ROOT / "models"
FEATURES = ["vibration_rms", "temperature_c", "hours_run", "oil_pressure_psi", "motor_amps"]


def synthesize(n: int = 800, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    vibration = rng.uniform(0.5, 8.0, n)
    temperature = rng.uniform(40, 110, n)
    hours = rng.uniform(100, 20000, n)
    oil = rng.uniform(20, 80, n)
    amps = rng.uniform(5, 45, n)
    # Higher vibration/temp/hours and lower oil → fewer days remaining
    days = (
        45
        - 3.2 * vibration
        - 0.18 * (temperature - 60)
        - 0.0012 * hours
        + 0.15 * oil
        - 0.25 * amps
        + rng.normal(0, 2.5, n)
    )
    days = np.clip(days, 0.5, 60.0)
    asset_ids = [f"ASSET-{i:04d}" for i in range(n)]
    return pd.DataFrame(
        {
            "asset_id": asset_ids,
            "vibration_rms": vibration.round(3),
            "temperature_c": temperature.round(2),
            "hours_run": hours.round(1),
            "oil_pressure_psi": oil.round(2),
            "motor_amps": amps.round(2),
            "days_to_failure": days.round(2),
        }
    )


def train() -> dict:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA.exists():
        synthesize().to_csv(DATA, index=False)

    df = pd.read_csv(DATA)
    x = df[FEATURES]
    y = df["days_to_failure"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        objective="reg:squarederror",
    )
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred)),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "features": FEATURES,
    }

    joblib.dump({"model": model, "features": FEATURES}, MODEL_DIR / "days_to_failure.joblib")
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
