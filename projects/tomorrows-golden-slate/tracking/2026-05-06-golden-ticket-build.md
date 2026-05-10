# 2026-05-06 Golden Ticket Build

Status: results review started

## Style source

Built from the `Golden Ticket Capper Style` profile, which emphasizes:

- correlated SGP/SGP+ clusters
- alt thresholds instead of main lines
- role-player playoff minutes
- one or two payout expanders with basketball context
- current second-round series adjustments

## Current slate context

- Philadelphia 76ers at New York Knicks
  - Knicks favored by 7.5.
  - 76ers underdog script supports high-usage perimeter attempts.
- Minnesota Timberwolves at San Antonio Spurs
  - Spurs favored by 9.5.
  - Timberwolves lead series 1-0 after a close Game 1.
  - Game 2 should create adjustment pressure and tighter playoff rotations.

## Primary Golden Ticket

| Leg | Price checked | Model probability | Grade | Why it fits |
| --- | ---: | ---: | --- | --- |
| Paul George 3+ made threes | +110 | 71.4% | A | Best first-game shooting edge; underdog perimeter script. |
| Jalen Brunson 3+ made threes | -102 | 55.7% | B+ | High-usage playoff guard, positive edge, strong minutes. |
| Stephon Castle 2+ made threes | +124 | 63.0% | A | Best second-game shooting edge; hit 3 threes in Game 1. |
| Julius Randle 7+ rebounds | +106 | 63.4% | A- | Game 1 board path was real; Spurs size creates rebound chances. |
| Jaden McDaniels 15+ points | -130 | 62.5% | B+ | Direct capper-style role-player points leg; hit 16 in Game 1. |
| Naz Reid 7+ rebounds | +104 | 61.6% | B+ | Role big alt-rebound leg; strong recent board profile. |

Approximate combined profile:

- Approximate parlay odds: +6826
- Model probability: 6.1%
- Implied probability: 1.4%
- Estimated edge: +4.7 percentage points

## Higher-payout expander variant

Swap:

- Julius Randle 7+ rebounds

For:

- Julius Randle 2+ made threes

Randle 2+ threes is a thinner leg:

- Model probability: 49.9%
- Price checked: +144
- Use only as the uncomfortable payout expander.

Approximate expander variant:

- Approximate parlay odds: +8104
- Model probability: 4.8%
- Implied probability: 1.2%

## Notes for placement

- Keep odds movement off if available.
- Do not add more legs unless a new leg has a clear playoff-context reason.
- If forced to reduce risk, remove Naz Reid 7+ rebounds first.
- If forced to increase payout, use the Randle 2+ threes expander instead of Randle 7+ rebounds.

## Results captured from screenshots

### 76ers at Knicks

Final: Knicks 108, 76ers 102.

| Leg | Result seen | Outcome | Lesson |
| --- | ---: | --- | --- |
| Philadelphia 76ers +10.5 | 76ers lost by 6 | Hit | Spread protection/context read was good. |
| Andre Drummond 8+ rebounds | 8 rebounds | Hit | Role big rebound floor was correctly identified. |
| VJ Edgecombe 20+ points | did not clear 20 | Miss | Points threshold was too aggressive for a volatile rookie in a playoff road spot. |
| Josh Hart 8+ rebounds | did not clear 8 | Miss | Hart rebound props are sensitive to game flow and role; do not treat season-average boards as automatic. |
| Karl-Anthony Towns 15.5+ rebounds + assists | 17 R+A | Hit | Star big multi-category angle translated well. |

### Timberwolves at Spurs

Live screenshot: Spurs 76, Timberwolves 52 with 5:37 left in the 3rd.

| Leg | Result seen | Outcome at screenshot | Lesson |
| --- | ---: | --- | --- |
| Anthony Edwards 2+ made threes | 1 made three | Pending/miss risk | Safer than 3+, but game script/injury/minutes can still suppress volume. |
| Jaden McDaniels 15+ points | 10 points | Miss risk | Role-player points legs need competitive game script or clear usage path. |
| Naz Reid 6.5+ rebounds | 5 rebounds | Miss risk | This was the correct first leg to cut when reducing risk. |
| Julius Randle 6.5+ rebounds | 4 rebounds | Miss risk | Randle rebound path weakened in a lopsided game. |
| Julius Randle 2+ made threes | 0 made threes | Miss risk | The expander remained thin; do not pair it with other correlated Randle outcomes. |

### Fresh-swap slip

Live screenshot: Spurs 76, Timberwolves 52 with 5:37 left in the 3rd.

| Leg | Result seen | Outcome at screenshot | Lesson |
| --- | ---: | --- | --- |
| Keldon Johnson 3.5+ rebounds | 9 rebounds | Hit | Strongest fresh swap; role-player rebound edge translated. |
| Devin Vassell 4.5+ rebounds | 5 rebounds | Hit | Plus-money rebound swap was a strong read. |
| Julian Champagnie 8.5+ points | 0 points | Miss risk | Role-player points can disappear even when minutes exist; points are less stable than rebounds. |
| Jaden McDaniels 15+ points | 10 points | Miss risk | Same role-player points issue. |
| Naz Reid 6.5+ rebounds | 5 rebounds | Miss risk | Rebound line was close but did not create enough margin. |

## Adjustment notes

- Rebounds beat points for role players in this slate. Keldon and Vassell boards were cleaner than Champagnie/Jaden point thresholds.
- Avoid stacking multiple legs from the same vulnerable game script. Minnesota falling behind hurt Edwards, Jaden, Naz, and Randle at the same time.
- Keep one uncomfortable expander maximum. Randle threes plus Randle rebounds created too much same-player dependence.
- For Round 2, role-player points should require either:
  - Game 1 usage plus strong shot volume, or
  - a line at least 2-4 points below season average, or
  - evidence the team needs that player's scoring specifically.
- Star multi-category legs remain valuable. KAT rebounds + assists hit because it had multiple paths.
- Future Golden Ticket builds should prefer:
  - star multi-category anchors,
  - role-player rebounds,
  - one activity combo,
  - one expander only if the price is meaningfully mispriced.
