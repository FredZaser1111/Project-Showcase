# 2026-05-07 Tuned Slip Build

Status: results review started

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

## Results captured from screenshots

### Lakers at Thunder

Final: Thunder 125, Lakers 107.

| Leg | Result seen | Outcome | Lesson |
| --- | ---: | --- | --- |
| Lakers +15.5 | Lakers lost by 18 | Miss | The spread protection did not survive the final margin; blowout risk was real. |
| Rui Hachimura 13+ points | did not clear 12.5 | Miss | Lakers secondary scoring read failed; avoid over-trusting role scoring in huge underdog spots. |
| LeBron James 21+ points | did not clear 20.5 | Miss | Star usage anchor failed under OKC defensive pressure/game script. |
| Luguentz Dort 2+ made threes | did not clear 1.5 | Miss | Role-player spacing can still disappear; do not stack too many scoring/shooting legs in one SGP. |
| Austin Reaves 10+ rebounds + assists | did not clear 9.5 | Miss | Safer multi-category Lakers role leg still failed in the blowout environment. |
| Chet Holmgren 2+ blocks | 2 blocks | Hit | Defensive category edge translated cleanly. |
| Chet Holmgren 2+ threes | 3 made threes | Hit | Big-man spacing expander hit; this was the best moonshot add. |
| Chet Holmgren 12+ points | hit in shared 10-leg screenshot | Hit | Lower Chet points alt was viable in OKC-control script. |
| Shai Gilgeous-Alexander 30+ points | hit in shared 10-leg screenshot | Hit | OKC scoring engine worked; SGA was better than Lakers-side scoring legs. |

### Cavaliers at Pistons

Final: Pistons 107, Cavaliers 97.

| Leg | Result seen | Outcome | Lesson |
| --- | ---: | --- | --- |
| Evan Mobley 9+ rebounds | 1 rebound | Miss | Biggest model miss; series weighting overreacted to the prior path and ignored role/game-flow risk. |
| Jalen Duren 3+ assists | 1 assist | Miss | Big-man passing expander was too fragile; teammate conversion/touch role did not hold. |
| Evan Mobley 4+ assists | 4 assists | Hit | Mobley connector role did show up even while rebounds collapsed. |

### Cavaliers at Pistons diversion slip

Final: Pistons 107, Cavaliers 97.

| Leg | Result seen | Outcome | Lesson |
| --- | ---: | --- | --- |
| Donovan Mitchell 25+ points | cleared 25 | Hit | Primary scorer response angle was correct. |
| James Harden 7+ assists | did not clear 7 | Miss | Main-line assist ladder was too optimistic; one-game series confirmation over-weighted the Game 1 path. |
| Evan Mobley 2+ blocks | cleared 2 | Hit | Mobley defensive activity was a better category than Mobley rebounds. |
| Jalen Duren 12+ rebounds | did not clear 12 | Miss | Duren board ceiling did not carry over; physical big-man props need clearer role/rebound-chance confirmation. |
| Donovan Mitchell 3+ made threes | did not clear 3 | Miss | Do not pair Mitchell points with threes unless the threes price is clearly mispriced; the scoring path can come inside the arc/FT line. |

## Model adjustment after May 7

- The playoff tuning layer over-weighted one-game series confirmation for several legs. Series data should be capped until at least two games exist.
- In large-spread games, underdog scoring and secondary usage should be penalized harder than the current model did.
- Defensive/big-man spacing legs were better than Lakers scoring legs:
  - Chet blocks hit.
  - Chet threes hit.
  - SGA points hit.
- Role-player or secondary-scorer points in the large-underdog game were poor:
  - Rui points missed.
  - LeBron points missed.
  - Dort threes missed.
  - Reaves R+A missed.
- Big-man assists should remain expander-only. Duren missed while Mobley hit, showing this market is highly role-specific.
- Rebounds are not automatically safer if the player can be schemed away or pulled from the primary board path; Mobley 9+ rebounds was a major miss.
- Primary scorer points can still work in a loss. Mitchell 25+ hit even while the Cavs lost by 10.
- Avoid same-player scorer + threes correlation unless both legs are independently mispriced. Mitchell points hit while Mitchell threes missed.
- Harden assists should be downgraded from "strong add" to "price-sensitive only" until a second series game confirms 7+ facilitation.

