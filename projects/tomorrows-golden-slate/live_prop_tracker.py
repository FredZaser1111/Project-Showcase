#!/usr/bin/env python3
"""Manual live prop tracker for in-game sweat decisions.

This is designed for quick updates from a sportsbook or box score. It does not
scrape live stats; instead, paste the current stat line and optional cash-out
offer to get a clear read.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class TrackerInput:
    player: str
    target: float
    rebounds: int
    assists: int
    quarter: int
    seconds_left_in_quarter: int
    payout: float | None
    cashout_offer: float | None
    remaining_leg_american_odds: int | None


def game_seconds_elapsed(quarter: int, seconds_left_in_quarter: int) -> int:
    quarter = max(1, min(4, quarter))
    elapsed_before_quarter = (quarter - 1) * 600
    elapsed_in_quarter = 600 - max(0, min(600, seconds_left_in_quarter))
    return elapsed_before_quarter + elapsed_in_quarter


def american_to_implied_probability(american_odds: int) -> float:
    if american_odds > 0:
        return 100 / (american_odds + 100)
    return abs(american_odds) / (abs(american_odds) + 100)


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def read_tracker(inputs: TrackerInput) -> str:
    current_total = inputs.rebounds + inputs.assists
    needed_to_clear = max(0, int(inputs.target) + 1 - current_total)
    elapsed = game_seconds_elapsed(inputs.quarter, inputs.seconds_left_in_quarter)
    remaining = max(0, 2400 - elapsed)
    pace_total = current_total / elapsed * 2400 if elapsed > 0 else 0

    if needed_to_clear == 0:
        status = "CLEARED"
        recommendation = "Leg cleared. Cash-out decision now depends on remaining legs only."
    elif remaining <= 0:
        status = "MISSED"
        recommendation = "No time remaining."
    elif needed_to_clear == 1:
        status = "LIVE"
        recommendation = "One stat away. Lean ride unless cash-out is strong relative to remaining-leg fair value."
    elif needed_to_clear == 2:
        status = "NEEDS WORK"
        recommendation = "Needs two more events. Cash out becomes reasonable if offer is not heavily discounted."
    else:
        status = "LONG SHOT"
        recommendation = "Needs a late spike. Strongly consider cashing if offer is meaningful."

    lines = [
        f"{inputs.player} live tracker",
        "-" * 32,
        f"Target: over {inputs.target:g} rebounds + assists",
        f"Current: {inputs.rebounds} REB + {inputs.assists} AST = {current_total}",
        f"Needed to clear: {needed_to_clear}",
        f"Quarter/time: Q{inputs.quarter}, {inputs.seconds_left_in_quarter // 60}:{inputs.seconds_left_in_quarter % 60:02d} left",
        f"Full-game pace: {pace_total:.1f} R+A",
        f"Status: {status}",
        f"Read: {recommendation}",
    ]

    if inputs.payout is not None and inputs.cashout_offer is not None:
        lines.extend(["", f"Full payout: {format_money(inputs.payout)}", f"Cash-out offer: {format_money(inputs.cashout_offer)}"])
        if inputs.remaining_leg_american_odds is not None:
            fair_probability = american_to_implied_probability(inputs.remaining_leg_american_odds)
            fair_value = inputs.payout * fair_probability
            lines.append(f"Remaining-leg fair value estimate: {format_money(fair_value)}")
            if inputs.cashout_offer >= fair_value * 0.90:
                lines.append("Cash-out grade: STRONG OFFER")
            elif inputs.cashout_offer >= fair_value * 0.70:
                lines.append("Cash-out grade: FAIR OFFER")
            else:
                lines.append("Cash-out grade: LOW OFFER")

    return "\n".join(lines)


def parse_clock(clock: str) -> int:
    if ":" not in clock:
        return int(clock)
    minutes, seconds = clock.split(":", 1)
    return (int(minutes) * 60) + int(seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track a live rebounds+assists prop manually.")
    parser.add_argument("--player", default="Gabby Williams")
    parser.add_argument("--target", type=float, default=8.5)
    parser.add_argument("--rebounds", type=int, required=True)
    parser.add_argument("--assists", type=int, required=True)
    parser.add_argument("--quarter", type=int, required=True)
    parser.add_argument("--clock", required=True, help="Time left in quarter, e.g. 7:32.")
    parser.add_argument("--payout", type=float)
    parser.add_argument("--cashout-offer", type=float)
    parser.add_argument("--remaining-leg-odds", type=int, help="American odds of the only remaining leg, if known.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inputs = TrackerInput(
        player=args.player,
        target=args.target,
        rebounds=args.rebounds,
        assists=args.assists,
        quarter=args.quarter,
        seconds_left_in_quarter=parse_clock(args.clock),
        payout=args.payout,
        cashout_offer=args.cashout_offer,
        remaining_leg_american_odds=args.remaining_leg_odds,
    )
    print(read_tracker(inputs))


if __name__ == "__main__":
    main()
