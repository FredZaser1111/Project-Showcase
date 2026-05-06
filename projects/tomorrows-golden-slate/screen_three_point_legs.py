#!/usr/bin/env python3
"""Screen high-volume three-point prop legs for positive expected value.

This tool intentionally uses only Python's standard library so the project can
start lightweight. Feed it a CSV of tomorrow's candidate 3PT props after you
collect sportsbook odds and your model probabilities.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROBABILITY_FIELDS = ("model_probability", "predicted_probability", "projection_probability")
MARKET_FIELDS = ("market", "prop", "bet")
LINE_FIELDS = ("line", "line_3pm", "threshold")
OPPOSING_ODDS_FIELDS = ("opposing_american_odds", "under_american_odds", "opposite_american_odds")
SEASON_3PA_FIELDS = ("season_3pa", "three_pa_pg", "three_pa_per_game", "3pa_pg")
RECENT_3PA_FIELDS = ("recent_3pa", "last10_three_pa_pg", "last_10_3pa", "last10_3pa", "last5_3pa")
SEASON_3P_PCT_FIELDS = ("season_3p_pct", "season_three_pct", "three_point_pct")
RECENT_3P_PCT_FIELDS = ("recent_3p_pct", "last10_3p_pct", "last_10_3p_pct", "last5_3p_pct")
SEASON_HIT_RATE_FIELDS = ("season_hit_rate",)
LAST10_HIT_RATE_FIELDS = ("last10_hit_rate", "last_10_hit_rate", "recent_hit_rate")
LAST5_HIT_RATE_FIELDS = ("last5_hit_rate", "last_5_hit_rate")
MATCHUP_INDEX_FIELDS = ("opponent_3pa_allowed_index",)
MATCHUP_RANK_FIELDS = ("opponent_3pa_allowed_rank",)


@dataclass(frozen=True)
class Candidate:
    player: str
    team: str
    opponent: str
    market: str
    line: str
    american_odds: int
    model_probability: float
    implied_probability: float
    no_vig_probability: float | None
    edge: float
    no_vig_edge: float | None
    ev_per_unit: float
    golden_score: float
    plus_money: bool
    current_3pa: float | None
    volume_delta: float | None
    best_hit_rate: float | None
    probability_source: str
    notes: str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def parse_float(value: str | None, field_name: str, *, required: bool = False) -> float | None:
    if value is None or value.strip() == "":
        if required:
            raise ValueError(f"missing required field: {field_name}")
        return None
    cleaned = value.strip().replace(",", "")
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
        return float(cleaned) / 100
    return float(cleaned)


def parse_probability(value: str | None, field_name: str) -> float:
    probability = parse_float(value, field_name, required=True)
    assert probability is not None
    if probability > 1:
        probability = probability / 100
    if probability < 0 or probability > 1:
        raise ValueError(f"{field_name} must be between 0 and 1, got {value!r}")
    return probability


def get_first(row: dict[str, str], field_names: Iterable[str]) -> str | None:
    for field_name in field_names:
        value = row.get(field_name)
        if value is not None and value.strip():
            return value
    return None


def get_float(row: dict[str, str], field_names: Iterable[str], *, required: bool = False) -> float | None:
    value = get_first(row, field_names)
    label = next(iter(field_names), "value")
    return parse_float(value, label, required=required)


def get_probability(row: dict[str, str], field_names: Iterable[str], *, required: bool = False) -> float | None:
    value = get_first(row, field_names)
    if value is None and not required:
        return None
    label = next(iter(field_names), "probability")
    return parse_probability(value, label)


def american_to_decimal(american_odds: int) -> float:
    if american_odds == 0:
        raise ValueError("american_odds cannot be 0")
    if american_odds > 0:
        return 1 + (american_odds / 100)
    return 1 + (100 / abs(american_odds))


def american_to_implied_probability(american_odds: int) -> float:
    decimal_odds = american_to_decimal(american_odds)
    return 1 / decimal_odds


def decimal_to_american(decimal_odds: float) -> int:
    if decimal_odds < 1:
        raise ValueError("decimal odds must be at least 1")
    profit = decimal_odds - 1
    if profit >= 1:
        return round(profit * 100)
    return round(-100 / profit)


def expected_value_per_unit(model_probability: float, american_odds: int) -> float:
    profit_if_win = american_to_decimal(american_odds) - 1
    return (model_probability * profit_if_win) - (1 - model_probability)


def no_vig_probability(american_odds: int, opposing_american_odds: int | None) -> float | None:
    if opposing_american_odds is None:
        return None
    side_probability = american_to_implied_probability(american_odds)
    opposing_probability = american_to_implied_probability(opposing_american_odds)
    total_probability = side_probability + opposing_probability
    if total_probability <= 0:
        return None
    return side_probability / total_probability


def parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "underdog"}


def poisson_tail(mean: float, needed_makes: int) -> float:
    """Probability of at least needed_makes from a Poisson scoring model."""

    if needed_makes <= 0:
        return 1.0
    if mean <= 0:
        return 0.0

    cumulative = 0.0
    probability = math.exp(-mean)
    for makes in range(needed_makes):
        if makes > 0:
            probability *= mean / makes
        cumulative += probability
    return clamp(1 - cumulative, 0, 1)


def weighted_average(pairs: Iterable[tuple[float | None, float]]) -> float | None:
    numerator = 0.0
    denominator = 0.0
    for value, weight in pairs:
        if value is None:
            continue
        numerator += value * weight
        denominator += weight
    if denominator == 0:
        return None
    return numerator / denominator


def derive_model_probability(
    *,
    line: float | None,
    season_3pa: float | None,
    recent_3pa: float | None,
    season_3p_pct: float | None,
    recent_3p_pct: float | None,
    season_hit_rate: float | None,
    last10_hit_rate: float | None,
    last5_hit_rate: float | None,
    minutes: float | None,
    usage_rate: float | None,
    matchup_index: float | None,
    matchup_rank: float | None,
    team_is_underdog: bool,
    spread: float | None,
) -> float | None:
    if line is None:
        return None

    projected_attempts = weighted_average(((season_3pa, 0.4), (recent_3pa, 0.6)))
    projected_3p_pct = weighted_average(((season_3p_pct, 0.45), (recent_3p_pct, 0.55)))
    if projected_attempts is None or projected_3p_pct is None:
        return None

    if matchup_index is None and matchup_rank is not None:
        # Rank above league midpoint means the defense allows more 3PA.
        matchup_index = 1 + ((matchup_rank - 15.5) / 15.5 * 0.08)
    matchup_index = matchup_index if matchup_index is not None else 1.0

    minutes_factor = clamp((minutes or 30.0) / 30.0, 0.85, 1.15)
    usage_factor = clamp((usage_rate or 0.20) / 0.20, 0.90, 1.10)
    underdog_factor = 1.03 if team_is_underdog or (spread is not None and spread > 0) else 1.0

    adjusted_attempts = projected_attempts * matchup_index * minutes_factor * usage_factor * underdog_factor
    expected_makes = adjusted_attempts * clamp(projected_3p_pct, 0.25, 0.50)
    needed_makes = math.floor(line) + 1
    volume_probability = poisson_tail(expected_makes, needed_makes)

    hit_rate_probability = weighted_average(
        (
            (season_hit_rate, 0.25),
            (last10_hit_rate, 0.35),
            (last5_hit_rate, 0.40),
        )
    )
    if hit_rate_probability is None:
        return clamp(volume_probability, 0.01, 0.90)
    return clamp((volume_probability * 0.55) + (hit_rate_probability * 0.45), 0.01, 0.90)


def golden_score(
    *,
    edge: float,
    ev_per_unit: float,
    american_odds: int,
    season_3pa: float | None,
    last10_3pa: float | None,
    season_hit_rate: float | None,
    last10_hit_rate: float | None,
    last5_hit_rate: float | None,
) -> float:
    """Composite ranking score for the user's underdog/high-ceiling style."""

    current_3pa = last10_3pa if last10_3pa is not None else season_3pa
    volume_bonus = 0.0
    if current_3pa is not None:
        # Reward shooters already clearing strong volume. Cap keeps score sane.
        volume_bonus = clamp((current_3pa - 6) / 6, 0, 1) * 10

    volume_delta_bonus = 0.0
    if last10_3pa is not None and season_3pa is not None:
        volume_delta_bonus = clamp((last10_3pa - season_3pa) / 3, -1, 1) * 5

    hit_rates = [rate for rate in (season_hit_rate, last10_hit_rate, last5_hit_rate) if rate is not None]
    hit_rate_bonus = 0.0
    if hit_rates:
        hit_rate_bonus = clamp((max(hit_rates) - 0.5) / 0.2, 0, 1) * 5

    plus_money_bonus = 3 if american_odds > 0 else 0

    return (edge * 100) + (ev_per_unit * 20) + volume_bonus + volume_delta_bonus + hit_rate_bonus + plus_money_bonus


def build_candidate(row: dict[str, str], row_number: int) -> Candidate:
    player = (row.get("player") or "").strip()
    if not player:
        raise ValueError(f"row {row_number}: missing required field: player")

    market = (get_first(row, MARKET_FIELDS) or "").strip()
    if not market:
        raise ValueError(f"row {row_number}: missing one of: {', '.join(MARKET_FIELDS)}")

    raw_odds = parse_float(row.get("american_odds"), "american_odds", required=True)
    assert raw_odds is not None
    american_odds = int(raw_odds)
    opposing_raw_odds = get_float(row, OPPOSING_ODDS_FIELDS)
    opposing_american_odds = int(opposing_raw_odds) if opposing_raw_odds is not None else None

    line = get_first(row, LINE_FIELDS)
    numeric_line = get_float(row, LINE_FIELDS)
    season_3pa = get_float(row, SEASON_3PA_FIELDS)
    last10_3pa = get_float(row, RECENT_3PA_FIELDS)
    current_3pa = last10_3pa if last10_3pa is not None else season_3pa
    volume_delta = None
    if last10_3pa is not None and season_3pa is not None:
        volume_delta = last10_3pa - season_3pa

    season_hit_rate = get_probability(row, SEASON_HIT_RATE_FIELDS)
    last10_hit_rate = get_probability(row, LAST10_HIT_RATE_FIELDS)
    last5_hit_rate = get_probability(row, LAST5_HIT_RATE_FIELDS)
    hit_rates = [rate for rate in (season_hit_rate, last10_hit_rate, last5_hit_rate) if rate is not None]
    best_hit_rate = max(hit_rates) if hit_rates else None

    probability_source = "provided"
    supplied_probability = get_probability(row, PROBABILITY_FIELDS)
    if supplied_probability is None:
        supplied_probability = derive_model_probability(
            line=numeric_line,
            season_3pa=season_3pa,
            recent_3pa=last10_3pa,
            season_3p_pct=get_probability(row, SEASON_3P_PCT_FIELDS),
            recent_3p_pct=get_probability(row, RECENT_3P_PCT_FIELDS),
            season_hit_rate=season_hit_rate,
            last10_hit_rate=last10_hit_rate,
            last5_hit_rate=last5_hit_rate,
            minutes=get_float(row, ("minutes", "projected_minutes")),
            usage_rate=get_probability(row, ("usage_rate", "usage")),
            matchup_index=get_float(row, MATCHUP_INDEX_FIELDS),
            matchup_rank=get_float(row, MATCHUP_RANK_FIELDS),
            team_is_underdog=parse_bool(row.get("team_is_underdog")),
            spread=parse_float(row.get("spread"), "spread"),
        )
        probability_source = "derived"
    if supplied_probability is None:
        raise ValueError(
            f"row {row_number}: provide model_probability or enough shooting inputs to derive one"
        )

    model_probability = supplied_probability
    implied_probability = american_to_implied_probability(american_odds)
    market_probability = no_vig_probability(american_odds, opposing_american_odds)
    edge = model_probability - implied_probability
    market_edge = model_probability - market_probability if market_probability is not None else None
    ev_per_unit = expected_value_per_unit(model_probability, american_odds)

    score = golden_score(
        edge=edge,
        ev_per_unit=ev_per_unit,
        american_odds=american_odds,
        season_3pa=season_3pa,
        last10_3pa=last10_3pa,
        season_hit_rate=season_hit_rate,
        last10_hit_rate=last10_hit_rate,
        last5_hit_rate=last5_hit_rate,
    )

    return Candidate(
        player=player,
        team=(row.get("team") or "").strip(),
        opponent=(row.get("opponent") or "").strip(),
        market=market,
        line=(line or "").strip(),
        american_odds=american_odds,
        model_probability=model_probability,
        implied_probability=implied_probability,
        no_vig_probability=market_probability,
        edge=edge,
        no_vig_edge=market_edge,
        ev_per_unit=ev_per_unit,
        golden_score=score,
        plus_money=american_odds > 0,
        current_3pa=current_3pa,
        volume_delta=volume_delta,
        best_hit_rate=best_hit_rate,
        probability_source=probability_source,
        notes=(row.get("notes") or "").strip(),
    )


def load_candidates(path: Path) -> list[Candidate]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row")
        return [build_candidate(row, index + 2) for index, row in enumerate(reader)]


def filter_candidates(
    candidates: Iterable[Candidate],
    *,
    min_probability: float,
    min_edge: float,
    min_no_vig_edge: float,
    min_ev: float,
    min_3pa: float,
    require_hit_rate_support: bool,
    require_plus_money: bool,
) -> list[Candidate]:
    filtered = []
    for candidate in candidates:
        if candidate.model_probability < min_probability:
            continue
        if candidate.edge < min_edge:
            continue
        if candidate.no_vig_edge is not None and candidate.no_vig_edge < min_no_vig_edge:
            continue
        if candidate.ev_per_unit < min_ev:
            continue
        if candidate.current_3pa is None or candidate.current_3pa < min_3pa:
            continue
        if (
            require_hit_rate_support
            and candidate.best_hit_rate is not None
            and candidate.best_hit_rate < min_probability
        ):
            continue
        if require_plus_money and not candidate.plus_money:
            continue
        filtered.append(candidate)
    return sorted(filtered, key=lambda item: (item.golden_score, item.ev_per_unit), reverse=True)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.1f}%"


def money(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def maybe_float(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}"


def render_table(candidates: list[Candidate], *, top: int) -> None:
    selected = candidates[:top]
    if not selected:
        print("No legs passed the current +EV filters.")
        return

    headers = [
        "rank",
        "player",
        "market",
        "odds",
        "model_p",
        "implied_p",
        "edge",
        "no_vig_p",
        "no_vig_edge",
        "ev/unit",
        "3pa",
        "vol_delta",
        "hit_rate",
        "src",
        "score",
    ]
    rows = []
    for index, candidate in enumerate(selected, start=1):
        rows.append(
            [
                str(index),
                candidate.player,
                f"{candidate.market} {candidate.line}".strip(),
                money(candidate.american_odds),
                pct(candidate.model_probability),
                pct(candidate.implied_probability),
                signed_pct(candidate.edge),
                pct(candidate.no_vig_probability) if candidate.no_vig_probability is not None else "-",
                signed_pct(candidate.no_vig_edge) if candidate.no_vig_edge is not None else "-",
                f"{candidate.ev_per_unit:+.3f}",
                maybe_float(candidate.current_3pa),
                maybe_float(candidate.volume_delta),
                pct(candidate.best_hit_rate) if candidate.best_hit_rate is not None else "-",
                candidate.probability_source,
                f"{candidate.golden_score:.1f}",
            ]
        )

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    print("Eligible +EV 3PT legs")
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def render_parlays(candidates: list[Candidate], *, size: int, max_combos: int) -> None:
    if size <= 1:
        return
    if len(candidates) < size:
        print(f"\nNot enough eligible legs to build {size}-leg parlays.")
        return

    combos = []
    for legs in itertools.combinations(candidates, size):
        model_probability = math.prod(leg.model_probability for leg in legs)
        decimal_odds = math.prod(american_to_decimal(leg.american_odds) for leg in legs)
        implied_probability = 1 / decimal_odds
        ev_per_unit = (model_probability * (decimal_odds - 1)) - (1 - model_probability)
        edge = model_probability - implied_probability
        combos.append((ev_per_unit, edge, model_probability, decimal_odds, legs))

    combos.sort(reverse=True, key=lambda item: (item[0], item[1]))
    print("\nTop parlay combinations by EV")
    print("Assumption: legs are independent. Recheck correlation, injuries, and live odds before using.")
    for index, (ev_per_unit, edge, model_probability, decimal_odds, legs) in enumerate(combos[:max_combos], start=1):
        leg_names = " + ".join(f"{leg.player} ({money(leg.american_odds)})" for leg in legs)
        print(
            f"{index}. {leg_names} | odds {money(decimal_to_american(decimal_odds))} "
            f"| model_p {pct(model_probability)} | implied_p {pct(1 / decimal_odds)} "
            f"| edge {signed_pct(edge)} | ev/unit {ev_per_unit:+.3f}"
        )


def write_csv(path: Path, candidates: list[Candidate]) -> None:
    fieldnames = [
        "player",
        "team",
        "opponent",
        "market",
        "line",
        "american_odds",
        "model_probability",
        "implied_probability",
        "no_vig_probability",
        "edge",
        "no_vig_edge",
        "ev_per_unit",
        "golden_score",
        "current_3pa",
        "volume_delta",
        "best_hit_rate",
        "probability_source",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow({field: getattr(candidate, field) for field in fieldnames})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screen 3PT prop legs for +EV lotto parlay candidates.")
    parser.add_argument("csv_path", type=Path, help="CSV file containing tomorrow's candidate 3PT props.")
    parser.add_argument("--min-probability", type=float, default=0.50, help="Minimum model win probability.")
    parser.add_argument("--min-edge", type=float, default=0.0, help="Minimum model edge over implied probability.")
    parser.add_argument(
        "--min-no-vig-edge",
        type=float,
        default=0.0,
        help="Minimum model edge over no-vig market probability when opposing odds are available.",
    )
    parser.add_argument("--min-ev", type=float, default=0.0, help="Minimum EV per 1 unit staked.")
    parser.add_argument("--min-3pa", type=float, default=6.0, help="Minimum current/recent 3PA per game.")
    parser.add_argument(
        "--allow-unsupported-hit-rates",
        action="store_true",
        help="Do not filter candidates whose known hit rates are below the probability floor.",
    )
    parser.add_argument("--allow-minus-money", action="store_true", help="Do not require underdog/plus-money legs.")
    parser.add_argument("--top", type=int, default=15, help="Number of legs to print.")
    parser.add_argument("--parlay-size", type=int, default=0, help="Optional parlay size to rank from eligible legs.")
    parser.add_argument("--max-combos", type=int, default=10, help="Number of parlay combinations to print.")
    parser.add_argument("--write-csv", type=Path, help="Optional path to write filtered candidates as CSV.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_candidates(args.csv_path)
    filtered = filter_candidates(
        candidates,
        min_probability=args.min_probability,
        min_edge=args.min_edge,
        min_no_vig_edge=args.min_no_vig_edge,
        min_ev=args.min_ev,
        min_3pa=args.min_3pa,
        require_hit_rate_support=not args.allow_unsupported_hit_rates,
        require_plus_money=not args.allow_minus_money,
    )

    render_table(filtered, top=args.top)
    render_parlays(filtered[: args.top], size=args.parlay_size, max_combos=args.max_combos)

    if args.write_csv:
        write_csv(args.write_csv, filtered)
        print(f"\nWrote {len(filtered)} filtered legs to {args.write_csv}")


if __name__ == "__main__":
    main()
