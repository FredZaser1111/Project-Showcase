# Tomorrow's Golden Slate

Tomorrow's Golden Slate is a 3-point prop research workspace for building
lotto-style parlays from high-volume shooters whose ceiling appears
underpriced by the market.

The betting rule is strict: a leg only survives if the model projects at least a
50% hit probability and that probability is higher than the bookmaker's
implied probability after vig is considered.

## Core betting thesis

Look for high-volume 3-point shooters in spots where books may be shading the
line too low because the player is an underdog, volatile shooter, bench scorer,
or matchup-dependent ceiling play.

This project prioritizes +EV selection over narratives:

1. Estimate the player's true probability of clearing the 3PM line.
2. Convert the sportsbook price into implied probability.
3. Keep only legs where:
   - model probability >= 50%
   - model probability > implied probability
   - expected value is positive
   - recent and season hit-rate signals support the projection

## Statistical measures to use

Use these measures before adding any leg to the slate:

| Measure | Why it matters |
| --- | --- |
| Season 3PA and recent 3PA | Volume is the base of every 3PM ceiling projection. |
| Season 3P% and recent 3P% | Captures long-term skill and current form. |
| Season hit rate and recent hit rate | Checks how often the player clears this exact line. |
| Weighted model probability | Combines baseline projection, form, matchup, volume, and role. |
| Sportsbook implied probability | Converts American odds into the book's required break-even rate. |
| No-vig market probability | Removes the book's hold when over and under prices are both available. |
| Edge | Model probability minus implied probability. |
| Expected value per $1 | Profit expectation at the offered price. |
| Underdog boost | Optional signal for players whose ceiling may be discounted by game spread. |
| Opponent 3PA allowed index | Matchup factor for defenses allowing more/fewer 3-point attempts. |
| Minutes and usage trend | Confirms the shooter has enough court time and role stability. |

## Included screener

`screen_three_point_legs.py` is a dependency-free Python tool that reads a CSV of
candidate 3PM prop legs, scores each player, and prints only legs that pass the
+EV filters.

## Model profiles

The workspace supports multiple slate types:

| Slate type | Profile | Utility |
| --- | --- | --- |
| NBA playoffs | `capper_profiles/golden_ticket_style.md` and `capper_profiles/playoff_tuning.md` | `playoff_tuning.py` |
| WNBA opener regular season | `capper_profiles/wnba_opener_regular_season.md` | `wnba_tuning.py` |

Use the NBA playoff model for series-based adjustments, rotation tightening, and
defensive intensity. Use the WNBA opener model for roster continuity, offseason
role changes, market lag, and early-season shooting volatility.

## Use it ASAP in your browser

This project now includes a no-install local web app. From this folder, run:

```bash
python3 app.py
```

Then open:

```text
http://localhost:8000
```

Fastest workflow:

1. Copy tomorrow's 3PM prop slate into CSV format.
2. Paste it into the text box, or upload a CSV file.
3. Adjust filters for minimum probability, edge, EV, no-vig edge, 3PA, and parlay size.
4. Click **Screen Slate**.
5. Review the ranked +EV legs and parlay combinations.

Use `example_candidates.csv` if you want to test the app before entering a real slate.
Use `slate_template.csv` as the fillable sheet for tomorrow's real slate.

Run the included example:

```bash
python3 screen_three_point_legs.py example_candidates.csv
```

Useful options:

```bash
# Require a larger book edge before a leg qualifies.
python3 screen_three_point_legs.py example_candidates.csv --min-edge 0.05

# Require a larger no-vig market edge when under odds are present.
python3 screen_three_point_legs.py example_candidates.csv --min-no-vig-edge 0.05

# Build a shorter lotto card from the top ranked legs.
python3 screen_three_point_legs.py example_candidates.csv --top 3

# Export the filtered slate for tracking.
python3 screen_three_point_legs.py example_candidates.csv --write-csv slate.csv
```

## Candidate CSV columns

Core input columns:

| Column | Example | Notes |
| --- | --- | --- |
| `player` | `Sample Shooter A` | Player name. |
| `team` | `ABC` | Player team. |
| `opponent` | `XYZ` | Opponent team. |
| `line` | `2.5` | Sportsbook 3PM line. `line_3pm` is also accepted. |
| `american_odds` | `+135` | Price for the over leg. |
| `under_american_odds` | `-165` | Optional paired under price for no-vig market probability. `opposing_american_odds` is also accepted. |
| `model_probability` | `0.54` | Optional. If omitted, the script derives one from volume, accuracy, hit-rate, role, matchup, and spread inputs. |
| `season_3pa` | `7.8` | Season 3-point attempts per game. `three_pa_per_game` is also accepted. |
| `recent_3pa` | `9.4` | Recent 3-point attempts per game, usually last 5-10 games. `last_10_3pa` is also accepted. |
| `season_3p_pct` | `0.384` | Season 3-point percentage. |
| `recent_3p_pct` | `0.412` | Recent 3-point percentage. |
| `season_hit_rate` | `0.54` | Season rate clearing this 3PM line. |
| `recent_hit_rate` | `0.62` | Recent rate clearing this 3PM line. |
| `minutes` | `32` | Expected minutes. |
| `usage_rate` | `0.23` | Usage share as a decimal. |
| `team_is_underdog` | `true` | `true` if the player's team is an underdog. |
| `spread` | `5.5` | Positive values mean the player's team is an underdog. |
| `opponent_3pa_allowed_index` | `1.08` | `1.00` is league average; higher means more 3PA allowed. |

## Fillable slate template

Use `slate_template.csv` when you want me to generate cards for a real slate.
It is header-only on purpose: fill one row per player prop, then send the
completed CSV back here. Use `example_candidates.csv` only as a reference for
what filled rows look like.

Recommended minimum columns to fill:

- `player`
- `team`
- `opponent`
- `market`
- `line`
- `american_odds`
- `under_american_odds` when available
- `model_probability` if you already have a projection
- `season_hit_rate`
- `recent_hit_rate`
- `last5_hit_rate`
- `season_3pa`
- `recent_3pa`
- `season_3p_pct`
- `recent_3p_pct`
- `minutes`
- `team_is_underdog`
- `spread`

If `model_probability` is blank, the tool will try to derive one from volume,
shooting percentage, hit rates, minutes, usage, matchup, and underdog/spread
inputs. More filled columns produce better rankings.

## Model guardrails

- Do not include legs with model probability below 50%.
- Do not include legs with negative expected value.
- Do not chase long odds unless the model probability still beats the implied
  probability.
- When paired over/under odds are available, require the model probability to
  beat the no-vig market probability too.
- By default, the screener keeps plus-money legs, requires at least 6 current
  3PA per game, and rejects known hit-rate profiles below the probability floor.
- Prefer high-volume attempts and stable minutes over small-sample hot streaks.
- Treat the output as a shortlist for manual review, not guaranteed picks.

## Tomorrow workflow

1. Pull tomorrow's NBA 3PM prop lines and odds into a CSV.
2. Add season and recent shooting data for every candidate.
3. Run `python3 app.py` and paste/upload the slate.
4. Review the top +EV underdog/ceiling candidates in the browser.
5. Track final decisions and results so the probability model can be calibrated.

## Files

- `app.py` - local browser app for screening pasted or uploaded CSV slates.
- `playoff_tuning.py` - reusable playoff projection adjustment calculator.
- `wnba_tuning.py` - WNBA opener regular-season projection adjustment calculator.
- `screen_three_point_legs.py` - +EV three-point prop screener.
- `example_candidates.csv` - example slate input format.
- `slate_template.csv` - fillable CSV for real slates.
- `capper_profiles/` - reusable betting-style profiles and playoff tuning rules.
- `tracking/` - saved cards, outcomes, and notes for model adjustment.
