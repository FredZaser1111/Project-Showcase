# Golden Ticket Capper Style

This profile captures the betting style inferred from example first-round
winning and near-winning slips. It is meant to guide future "golden ticket"
builds alongside the existing +EV three-point screener.

## Core identity

The style is an analytics-driven longshot SGP/SGP+ approach. It is not random
lotto construction. The tickets use alternate thresholds, playoff rotation
context, and correlated game scripts to create very large payouts without
relying only on extremely low-probability stat outcomes.

## Patterns from examples

### 1. Alt-line ladders, not standard lines

The slips prefer attainable alternate thresholds:

- points: 10+, 15+, 25+
- rebounds: 8+, 9+, 10+
- assists: 2+, 7+
- steals: 2+
- threes: 1+, 2+, 3+

The capper often avoids the sportsbook's main line and instead chooses a
threshold that is reachable if the game script breaks correctly.

### 2. Role-player stat floors create hidden payout

The examples lean into role players whose playoff minutes or matchup role can
beat the public perception:

- Julian Champagnie 10+ points
- Keldon Johnson 10+ points
- Mike Conley 10+ points
- Jaden McDaniels 15+ points
- Terrence Shannon Jr. 10+ points
- VJ Edgecombe 2+ steals
- Andre Drummond 2+ assists

These are not superstar-only tickets. The edge is often in role players with
clear paths to minutes, usage, defensive activity, or cleanup production.

### 3. Correlated same-game clusters

The tickets often build around a single game environment:

- Multiple players on both sides clearing modest point thresholds.
- One star accumulating across categories while role players cover smaller
  alternate lines.
- Game staying competitive enough for starters and key role players to receive
  full playoff minutes.

This is different from independent leg hunting. The slip asks: "If this game
plays out this way, which four to eight alt outcomes rise together?"

### 4. One or two uncomfortable legs create the payout

The best examples include at least one leg most casual bettors would avoid:

- Andre Drummond 1+ made three
- Andre Drummond 2+ assists
- VJ Edgecombe 2+ steals
- Role-player 10+ point ladders

These are not always strict-card legs. They are "payout expanders" that still
need a basketball reason: role, opponent scheme, minutes, previous matchup,
injury/rotation change, or specific matchup tendency.

### 5. Stars are used as anchors, not always as scorers

The capper does not only use star points:

- Jayson Tatum 7+ assists
- Jayson Tatum 10+ rebounds
- Jayson Tatum 2+ steals
- LeBron James 25+ points

Star legs are selected where playoff minutes plus role create multiple paths to
the stat, especially rebounds/assists/defense when the market is focused on
points.

## Build rules

### Strong ticket structure

Use one of these structures:

1. **4-leg SGP+**
   - 2 high-confidence alt anchors
   - 1 role-player edge
   - 1 payout expander with basketball context

2. **6-leg single-game stack**
   - 2 star/usage anchors
   - 2 role-player point or rebound thresholds
   - 1 defense/activity leg
   - 1 uncomfortable payout expander

3. **8-leg moonshot**
   - Only if every leg has a specific game-script reason.
   - Avoid stacking too many high-variance shooting legs unless volume is elite.

### Preferred leg types

- Alt points for role players with 28+ projected minutes.
- Alt rebounds for wings/bigs facing high-miss or pace-up environments.
- Alt assists for primary handlers against pressure/double-team schemes.
- Steals for active guards/wings against turnover-prone ball handlers.
- Threes only when volume or matchup supports it; avoid pure hot-hand chasing.

### Avoid

- Too many legs depending on the same player's shooting variance.
- Bench players without a clear rotation path.
- Blowout-sensitive overs unless the player benefits from garbage-time run.
- Main lines that are already fully priced by the market.
- Adding a leg only because the payout looks better.

## Scoring rubric

Grade each leg before adding it:

| Grade | Meaning |
| --- | --- |
| A | Clears model probability, role, minutes, and price checks. |
| B | Positive basketball context but thinner price or recent form. |
| C | Lotto-only expander; must be limited to one per ticket. |
| F | No clear role, minutes, matchup, or price edge. |

An A-level Golden Ticket should contain mostly A/B legs and at most one C-level
payout expander.

## Current second-round adjustment

Second-round playoff tickets should emphasize:

- tighter rotations
- stars playing extended minutes
- Game 2 adjustments after Game 1 data
- injured players changing shot distribution
- role players who already showed they can stay on the floor in the series
- home/away whistle and pace changes

The goal is not to copy the old slips exactly. The goal is to copy the logic:
find alt lines where playoff context makes the outcome more likely than the
public price implies.

## Playoff tuning overlay

Before finalizing a Golden Ticket, apply `playoff_tuning.md` and
`playoff_tuning.py`:

- top-seven rotation minutes receive a 15-20% boost,
- non-Denver series receive a 5% pace drag,
- scoring efficiency is penalized for playoff defensive intensity,
- series-to-date trends outrank full-season baselines,
- Game 6/7 or elimination spots get a clutch/veteran-poise review.

This overlay should make the model more skeptical of fragile role-player points
while preserving edges in star multi-category anchors, rebounding, defense, and
trusted rotation activity.

**Addendum (near-miss SGPs):** When a ticket clears **star rebound + assists**
but misses **by one combined counting stat** on a low **REB+AST** line, or **by
2–3 points** on a **rookie/volatile scorer** ladder, apply `playoff_tuning.md`
“Near-miss” rules and optional `--low-margin-activity-combo` /
`--rookie-primary-scorer-points` flags in `playoff_tuning.py` before trusting the
same structure on the next slate.
