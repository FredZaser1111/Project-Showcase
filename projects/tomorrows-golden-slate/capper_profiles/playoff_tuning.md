# Playoff Tuning Parameters

These parameters are applied before turning a stat profile into a +EV betting or
DFS opinion. They are designed for second-round-and-later playoff basketball,
where rotations tighten, pace slows, and defenses lower shot quality.

## Rotation weighting

- Boost projected minutes for top-seven rotation players by **+15-20%**.
- Current implementation uses **+17.5%** for top-seven roles.
- Discount fragile bench roles with a **0.82 bench impact factor**.
- Treat deep bench production as less predictive than star usage or trusted
  playoff role-player minutes.

## Possession-based efficiency

- Shift away from raw per-game averages.
- Apply a **-5% pace adjustment** to non-Denver series.
- Denver-linked series are exempt because Denver environments can preserve
  offensive structure and pace differently.
- Prefer rates per possession, per minute, touch, rebound chance, or shot
  attempt over plain season averages.

## Defensive intensity and shot quality

- Apply a projected **-2.3% true-shooting drop**.
- Apply a projected **-4.3 offensive-rating drop per 100 possessions**.
- Upgrade legs with cleaner shot quality:
  - rim attempts,
  - catch-and-shoot threes from role clarity,
  - rebounding chances,
  - assists from double-team pressure.
- Downgrade legs relying on contested pull-ups, cold first-option isolation, or
  low-value late-clock looks.

## Clutch context and must-win factors

- Increase clutch weighting in Game 6/7 and elimination scenarios.
- In those games, veteran poise and floor spacing should matter more than
  regular-season hot streaks.
- The module can apply a small urgency multiplier for:
  - veteran poise,
  - floor spacing,
  - elimination or Game 6/7 context.

## Matchup persistence

- Prioritize series-to-date trends over season-long data.
- Current rate blend when series data exists:
  - **60% series trend**
  - **25% last-10 form**
  - **15% full-season baseline**
- Without series data:
  - **60% last-10 form**
  - **40% full-season baseline**

## Practical build rules

Use these tuning rules to find gaps where books have not adjusted for playoff
efficiency declines:

1. Prefer top-seven rotation players.
2. Prefer star multi-category anchors over isolated scoring.
3. Prefer role-player rebounds/activity over role-player points unless the line
   is discounted.
4. Use one uncomfortable payout expander max.
5. Penalize underdog role-player overs in blowout-risk games.
6. Treat series Game 1/2 data as live evidence, but confirm it with role and
   minutes before chasing.

## Utility

`playoff_tuning.py` provides a small standard-library calculator for these
adjustments:

```bash
python3 playoff_tuning.py \
  --season-rate 0.55 \
  --last10-rate 0.65 \
  --series-rate 0.70 \
  --base-minutes 34 \
  --rotation-rank 4 \
  --shot-quality 0.02
```

Use the output `adjusted_probability` as the modeled probability to compare
against bookmaker implied probability.

