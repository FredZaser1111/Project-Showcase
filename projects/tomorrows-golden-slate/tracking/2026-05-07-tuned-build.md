# 2026-05-07 Tuned Slip Build

Status: tuned model build

## Tuning applied

- Top-seven rotation boost.
- Non-Denver playoff pace drag.
- Playoff TS% and offensive-rating efficiency drag.
- Series-to-date priority from Game 1.
- Role-player points treated with more skepticism.
- Rebounds/blocks/activity upgraded when the Game 1 path confirmed.

Important: the tuned probabilities are used for **ranking and gap detection**.
Because many series inputs are currently only one game, they should not be read
as perfectly calibrated true probabilities.

## Major changes from the initial May 7 preview

- Jarrett Allen 2+ blocks was downgraded because the new series-weighted layer
  penalized the Game 1 miss.
- Jalen Duren 3+ assists was upgraded as a capper-style big-man passing
  expander after Game 1 confirmed the path.
- Chet Holmgren 2+ blocks and Dort 2+ threes remained strong.
- Rui Hachimura 13+ points and LeBron James 21+ points remained the best Lakers
  usage legs with Luka sidelined.
- Evan Mobley 9+ rebounds remained the cleanest Cavs category leg.

## Safer 5-leg

| Leg | Price checked | Tuned model read | Why it fits |
| --- | ---: | ---: | --- |
| Rui Hachimura 13+ points | -122 | Strong | Lakers need non-LeBron scoring with Luka out. |
| LeBron James 21+ points | -125 | Strong | Star usage anchor in high-urgency underdog script. |
| Evan Mobley 9+ rebounds | -112 | Strong | Rebound category edge after playoff efficiency drag. |
| Luguentz Dort 2+ threes | -138 | Strong | Trusted role spacing and Game 1 path. |
| Chet Holmgren 2+ blocks | -146 | Strong | Stable rim-protection leg. |

Approximate odds: +1702.

## Primary Golden Ticket 6-leg

| Leg | Price checked | Tuned model read | Why it fits |
| --- | ---: | ---: | --- |
| Rui Hachimura 13+ points | -122 | Strong | Usage and scoring need with Luka out. |
| LeBron James 21+ points | -125 | Strong | Star anchor. |
| Evan Mobley 9+ rebounds | -112 | Strong | Role/category fit. |
| Luguentz Dort 2+ threes | -138 | Strong | Role-player spacing edge. |
| Chet Holmgren 2+ blocks | -146 | Strong | Defensive category edge. |
| Jalen Duren 3+ assists | +130 | Expander | Big-man passing leg; Game 1 path confirmed. |

Approximate odds: +4044.

## Balanced 6-leg alternative

Use this if the Duren assist expander feels too uncomfortable:

| Leg | Price checked |
| --- | ---: |
| Rui Hachimura 13+ points | -122 |
| LeBron James 21+ points | -125 |
| Evan Mobley 9+ rebounds | -112 |
| Luguentz Dort 2+ threes | -138 |
| Chet Holmgren 2+ blocks | -146 |
| Austin Reaves 10+ rebounds + assists | -120 |

Approximate odds: +3203.

## Moonshot 8-leg

| Leg | Price checked | Role |
| --- | ---: | --- |
| Rui Hachimura 13+ points | -122 | Usage leg |
| LeBron James 21+ points | -125 | Star anchor |
| Evan Mobley 9+ rebounds | -112 | Category edge |
| Luguentz Dort 2+ threes | -138 | Role-player spacing |
| Chet Holmgren 2+ blocks | -146 | Defensive edge |
| Jalen Duren 3+ assists | +130 | Big-man passing expander |
| Evan Mobley 4+ assists | +134 | Star/big passing expander |
| Chet Holmgren 2+ threes | +126 | Big-man spacing expander |

Approximate odds: +21814.

## Final placement guidance

- Best main ticket: **Primary Golden Ticket 6-leg**.
- Best safer ticket: **Safer 5-leg**.
- Use the moonshot only with a small stake or boost.
- Do not add Jarrett Allen blocks unless live odds or pregame news creates a
  much better reason than the current Game 1 trend.
- Avoid adding more Lakers underdog role-player points; blowout risk is still
  the main slate risk.

