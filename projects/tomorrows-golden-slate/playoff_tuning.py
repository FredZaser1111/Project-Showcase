#!/usr/bin/env python3
"""Playoff-specific projection adjustments for Golden Ticket builds.

The goal is not to replace the prop screeners. This module centralizes the
playoff assumptions we apply before comparing a modeled probability to a book's
price.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


TOP_ROTATION_BOOST = 0.175
BENCH_IMPACT_FACTOR = 0.82
PLAYOFF_PACE_PENALTY = 0.95
TRUE_SHOOTING_DROP = 0.023
OFFENSIVE_RATING_DROP = 4.3


@dataclass(frozen=True)
class PlayoffInputs:
    season_rate: float
    last10_rate: float
    series_rate: float | None = None
    clutch_rate: float | None = None
    base_minutes: float = 32.0
    rotation_rank: int = 5
    game_number: int = 2
    elimination_game: bool = False
    series_involves_denver: bool = False
    veteran_poise: float = 0.0
    floor_spacing: float = 0.0
    shot_quality: float = 0.0


@dataclass(frozen=True)
class PlayoffProjection:
    adjusted_probability: float
    adjusted_minutes: float
    pace_factor: float
    efficiency_factor: float
    series_weight: float
    clutch_weight: float
    urgency_multiplier: float


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def adjusted_minutes(base_minutes: float, rotation_rank: int) -> float:
    """Boost top-seven playoff roles and discount fragile bench roles."""

    if rotation_rank <= 7:
        return base_minutes * (1 + TOP_ROTATION_BOOST)
    return base_minutes * BENCH_IMPACT_FACTOR


def pace_factor(*, series_involves_denver: bool) -> float:
    """Apply playoff pace drag except in Denver-linked series."""

    return 1.0 if series_involves_denver else PLAYOFF_PACE_PENALTY


def efficiency_factor(*, shot_quality: float = 0.0) -> float:
    """Convert TS% and offensive-rating pressure into a probability drag.

    `shot_quality` is centered at 0. Positive values represent a cleaner than
    expected shot diet, while negative values represent forced low-value looks.
    """

    ts_component = 1 - TRUE_SHOOTING_DROP
    ortg_component = 1 - (OFFENSIVE_RATING_DROP / 100)
    shot_quality_component = 1 + clamp(shot_quality, -0.08, 0.08)
    return clamp(ts_component * ortg_component * shot_quality_component, 0.80, 1.08)


def blend_rate(inputs: PlayoffInputs) -> tuple[float, float, float]:
    """Weight series trends ahead of full-season history."""

    if inputs.series_rate is None:
        series_weight = 0.0
        last10_weight = 0.60
        season_weight = 0.40
    else:
        series_weight = 0.60
        last10_weight = 0.25
        season_weight = 0.15

    blended = (
        (inputs.series_rate or 0.0) * series_weight
        + inputs.last10_rate * last10_weight
        + inputs.season_rate * season_weight
    )

    clutch_weight = 0.0
    if inputs.clutch_rate is not None:
        clutch_weight = 0.12 if inputs.game_number < 6 and not inputs.elimination_game else 0.20
        blended = (blended * (1 - clutch_weight)) + (inputs.clutch_rate * clutch_weight)

    return blended, series_weight, clutch_weight


def urgency_multiplier(inputs: PlayoffInputs) -> float:
    """Boost stable veteran/floor-spacing profiles in Game 6/7 or elimination spots."""

    if inputs.game_number < 6 and not inputs.elimination_game:
        return 1.0

    poise = clamp(inputs.veteran_poise, 0.0, 1.0)
    spacing = clamp(inputs.floor_spacing, 0.0, 1.0)
    return 1 + (0.035 * poise) + (0.025 * spacing)


def adjusted_probability(inputs: PlayoffInputs) -> PlayoffProjection:
    base_rate, series_weight, clutch_weight = blend_rate(inputs)
    minutes_factor = adjusted_minutes(inputs.base_minutes, inputs.rotation_rank) / max(inputs.base_minutes, 1.0)
    pace = pace_factor(series_involves_denver=inputs.series_involves_denver)
    efficiency = efficiency_factor(shot_quality=inputs.shot_quality)
    urgency = urgency_multiplier(inputs)

    probability = base_rate * minutes_factor * pace * efficiency * urgency
    probability = clamp(probability, 0.01, 0.95)

    return PlayoffProjection(
        adjusted_probability=probability,
        adjusted_minutes=adjusted_minutes(inputs.base_minutes, inputs.rotation_rank),
        pace_factor=pace,
        efficiency_factor=efficiency,
        series_weight=series_weight,
        clutch_weight=clutch_weight,
        urgency_multiplier=urgency,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply playoff projection tuning to a prop hit-rate profile.")
    parser.add_argument("--season-rate", type=float, required=True)
    parser.add_argument("--last10-rate", type=float, required=True)
    parser.add_argument("--series-rate", type=float)
    parser.add_argument("--clutch-rate", type=float)
    parser.add_argument("--base-minutes", type=float, default=32.0)
    parser.add_argument("--rotation-rank", type=int, default=5)
    parser.add_argument("--game-number", type=int, default=2)
    parser.add_argument("--elimination-game", action="store_true")
    parser.add_argument("--series-involves-denver", action="store_true")
    parser.add_argument("--veteran-poise", type=float, default=0.0)
    parser.add_argument("--floor-spacing", type=float, default=0.0)
    parser.add_argument("--shot-quality", type=float, default=0.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    projection = adjusted_probability(PlayoffInputs(**vars(args)))
    print(json.dumps(asdict(projection), indent=2))


if __name__ == "__main__":
    main()
