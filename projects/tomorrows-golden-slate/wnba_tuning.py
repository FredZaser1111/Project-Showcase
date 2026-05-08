#!/usr/bin/env python3
"""WNBA opening-week projection adjustments.

This utility is intentionally lightweight. It estimates how much an opener prop
should move from last-season baseline once role, minutes, usage, and market lag
are considered.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


SHOOTING_MARKETS = {"points", "threes", "field_goals"}
ACTIVITY_MARKETS = {"rebounds", "assists", "rebounds_assists", "pra", "steals", "blocks"}


@dataclass(frozen=True)
class WnbaOpenerInputs:
    baseline_probability: float
    role_continuity: float = 0.5
    minutes_confidence: float = 0.5
    usage_change: float = 0.0
    market_lag: float = 0.0
    preseason_role_signal: float = 0.0
    chemistry_risk: float = 0.0
    rookie_or_new_team: bool = False
    market_type: str = "points"


@dataclass(frozen=True)
class WnbaOpenerProjection:
    adjusted_probability: float
    role_factor: float
    minutes_factor: float
    usage_factor: float
    market_lag_factor: float
    preseason_factor: float
    volatility_factor: float
    chemistry_factor: float


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def role_factor(role_continuity: float, rookie_or_new_team: bool) -> float:
    continuity = clamp(role_continuity, 0.0, 1.0)
    factor = 0.94 + (continuity * 0.12)
    if rookie_or_new_team:
        factor -= 0.04 * (1 - continuity)
    return clamp(factor, 0.86, 1.08)


def minutes_factor(minutes_confidence: float) -> float:
    confidence = clamp(minutes_confidence, 0.0, 1.0)
    return clamp(0.88 + (confidence * 0.22), 0.82, 1.12)


def usage_factor(usage_change: float) -> float:
    return clamp(1 + clamp(usage_change, -0.20, 0.25), 0.78, 1.25)


def market_lag_factor(market_lag: float) -> float:
    return clamp(1 + clamp(market_lag, -0.15, 0.20), 0.82, 1.22)


def preseason_factor(preseason_role_signal: float) -> float:
    # Preseason confirms role, not shooting skill. Keep the cap modest.
    return clamp(1 + (clamp(preseason_role_signal, -1.0, 1.0) * 0.04), 0.94, 1.04)


def volatility_factor(market_type: str) -> float:
    normalized = market_type.strip().lower().replace("+", "_").replace(" ", "_")
    if normalized in SHOOTING_MARKETS:
        return 0.97
    if normalized in ACTIVITY_MARKETS:
        return 1.02
    return 1.0


def chemistry_factor(chemistry_risk: float, rookie_or_new_team: bool) -> float:
    risk = clamp(chemistry_risk, 0.0, 1.0)
    base = 1 - (risk * 0.08)
    if rookie_or_new_team:
        base -= 0.03 * risk
    return clamp(base, 0.86, 1.0)


def adjusted_probability(inputs: WnbaOpenerInputs) -> WnbaOpenerProjection:
    role = role_factor(inputs.role_continuity, inputs.rookie_or_new_team)
    minutes = minutes_factor(inputs.minutes_confidence)
    usage = usage_factor(inputs.usage_change)
    lag = market_lag_factor(inputs.market_lag)
    preseason = preseason_factor(inputs.preseason_role_signal)
    volatility = volatility_factor(inputs.market_type)
    chemistry = chemistry_factor(inputs.chemistry_risk, inputs.rookie_or_new_team)

    probability = (
        inputs.baseline_probability
        * role
        * minutes
        * usage
        * lag
        * preseason
        * volatility
        * chemistry
    )

    return WnbaOpenerProjection(
        adjusted_probability=clamp(probability, 0.01, 0.92),
        role_factor=role,
        minutes_factor=minutes,
        usage_factor=usage,
        market_lag_factor=lag,
        preseason_factor=preseason,
        volatility_factor=volatility,
        chemistry_factor=chemistry,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply WNBA opener regular-season tuning to a prop probability.")
    parser.add_argument("--baseline-probability", type=float, required=True)
    parser.add_argument("--role-continuity", type=float, default=0.5, help="0-1 stability score.")
    parser.add_argument("--minutes-confidence", type=float, default=0.5, help="0-1 projected minutes confidence.")
    parser.add_argument("--usage-change", type=float, default=0.0, help="Expected usage delta, e.g. 0.10.")
    parser.add_argument("--market-lag", type=float, default=0.0, help="Book lag estimate, e.g. 0.08.")
    parser.add_argument("--preseason-role-signal", type=float, default=0.0, help="-1 to 1 role signal.")
    parser.add_argument("--chemistry-risk", type=float, default=0.0, help="0-1 chemistry uncertainty.")
    parser.add_argument("--rookie-or-new-team", action="store_true")
    parser.add_argument("--market-type", default="points")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    projection = adjusted_probability(WnbaOpenerInputs(**vars(args)))
    print(json.dumps(asdict(projection), indent=2))


if __name__ == "__main__":
    main()
