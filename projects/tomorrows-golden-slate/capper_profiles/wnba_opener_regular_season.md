# WNBA Opener Regular-Season Model

This profile adapts the Golden Ticket workflow for WNBA opening-week regular
season slates. It should not use NBA playoff assumptions like series trend
dominance, elimination urgency, or playoff-only defensive drag.

## Core identity

Opening-week WNBA edges usually come from market lag:

- last-season lines not reflecting new roles,
- offseason roster movement,
- injuries creating usage,
- rookies or returners changing rotations,
- coaches testing but still leaning on compact WNBA rotations.

The goal is to find props where the book is pricing the old role while the
current roster points to a new minutes, usage, rebound, or assist path.

## Primary inputs

### 1. Role continuity

Grade whether the player is returning to the same role:

| Grade | Meaning |
| --- | --- |
| A | Same team, same starter role, stable usage. |
| B | Same team, role slightly expanded or compressed. |
| C | New team, new coach, or uncertain rotation. |
| D | Rookie/deep bench without confirmed minutes. |

High continuity improves floor. Low continuity creates upside only when the new
role is confirmed by news, preseason, or depth chart.

### 2. Minutes confidence

WNBA rotations are often compact, but opening games still carry role uncertainty.

| Grade | Projected minutes |
| --- | --- |
| A | 30+ minutes, locked starter/closer. |
| B | 24-30 minutes, clear rotation role. |
| C | 18-24 minutes, bench or matchup-dependent. |
| D | Under 18 minutes or unclear role. |

Avoid building around D-grade minutes unless it is a tiny moonshot.

### 3. Usage change

Upgrade players when:

- a high-usage teammate left,
- a starter is injured,
- the player moved into the starting lineup,
- the team lost a primary ball-handler,
- preseason role matched the projected regular-season role.

Downgrade when a new star or ball-handler reduces touches.

### 4. Market lag

This is the opener model's main edge.

Look for lines that appear based on last season:

- points line below new starter usage,
- assists line below new ball-handling role,
- rebounds line below new frontcourt minutes,
- threes line below expanded catch-and-shoot volume.

### 5. Preseason signal

Use preseason lightly:

- minutes role: useful,
- starting lineup: useful,
- usage/touch pattern: useful,
- raw shooting percentage: weak signal.

Preseason should confirm role, not drive the pick by itself.

## Tuning rules

- Apply an early-season shooting penalty to points and threes.
- Prefer rebounds, assists, and minutes-based props before shooting overs.
- Do not apply NBA playoff pace drag by default.
- Do not use series-to-date weighting; there is no series yet.
- Use last-season baseline plus projected role adjustment.
- Penalize rookies and new-team players unless role confidence is high.

## Preferred leg types

- Rebounds for frontcourt players with new minutes.
- Assists for new primary or secondary handlers.
- Points for players with confirmed usage expansion.
- Threes only when attempt volume is role-based, not hot-hand based.
- Unders when public hype outruns role certainty.

## Avoid

- High points overs for players on new teams without stable usage.
- Rookie overs without confirmed starter minutes.
- Bench scorers who need shooting efficiency.
- Lines based only on preseason box-score production.
- Parlaying multiple players whose usage cannibalizes each other.

## Golden Ticket structure

Use one of these builds:

### Balanced 4-5 leg

- 1 stable star anchor
- 2 role/market-lag edges
- 1 rebound or assist floor leg
- optional 1 plus-money expander

### Moonshot 6-8 leg

- 2 market-lag edges
- 2 role/minutes confirmation legs
- 1 under or defensive/activity leg
- 1 uncomfortable expander

Never add a player only because the payout improves.

## Example-derived opener slip pattern

The Fever/Aces example showed a strong WNBA opener construction:

- Lexie Hull 6+ rebounds
- A'ja Wilson 8+ rebounds
- Aliyah Boston 8+ rebounds
- Chelsea Gray 6+ assists
- Jackie Young 4+ rebounds
- Odyssey Sims 10+ points
- Kelsey Mitchell 15+ points
- Jackie Young over 16.5 points

What it did well:

1. **Stable-role concentration**
   - It leaned on players with defined starter/closing roles.
   - The ticket avoided unknown bench pieces and uncertain rookies.

2. **Alt lines below ceiling**
   - The thresholds were attainable: 6+ assists, 8+ rebounds, 10+ points,
     15+ points, 4+ rebounds.
   - These are not main-line maxes; they are alternate lines that a normal good
     game can clear.

3. **Category resilience**
   - Four legs were rebounds.
   - One leg was assists.
   - Only three legs were points.
   - The slip did not depend on made threes or pure shooting variance.

4. **Team-role balance**
   - The slip used both teams.
   - Aces legs captured star/guard control through A'ja Wilson, Chelsea Gray,
     and Jackie Young.
   - Fever legs captured frontcourt activity and scoring need through Aliyah
     Boston, Lexie Hull, Odyssey Sims, and Kelsey Mitchell.

5. **Same-game correlation without cannibalization**
   - Rebounds and assists can rise together in a competitive, high-possession
     game.
   - Multiple players can clear modest alt lines without needing one player to
     dominate every possession.

6. **One star-plus-role-player spine**
   - A'ja Wilson and Jackie Young gave the ticket elite usage.
   - Role-player alt lines supplied payout while staying role-based.

## WNBA opener replication rules

When copying this style for a new WNBA opener slate:

- Build around 1-2 star anchors.
- Add 2-4 trusted starter/closing-role activity legs.
- Prefer rebounds, assists, and combo lines before threes.
- Use points only for players with clear usage or market-lag value.
- Avoid stacking multiple high points overs from teammates whose usage can
  cannibalize.
- Require every role-player leg to have a minutes case.
- Use one game environment only if the game is projected competitive enough for
  both teams' starters to close.

Best opener categories:

| Category | Opener strength | Why |
| --- | --- | --- |
| Rebounds | High | Less shooting-efficiency dependent. |
| Assists | High for primary guards | Captures role/touch stability. |
| Points | Medium | Good only with usage confirmation. |
| Threes | Low-medium | Need attempt volume, not just shooting talent. |
| Steals/blocks | Expander only | High variance unless role/matchup is obvious. |

## Live checklist

Before locking a WNBA opener slip, confirm:

1. Is the player starting or first off bench?
2. Is minutes projection stable?
3. Did offseason movement create new usage?
4. Is the book still pricing last season?
5. Is the line tied to role, not just shooting luck?
6. Are any teammates returning who reduce usage?
7. Is the prop category resilient if shooting efficiency is low?

