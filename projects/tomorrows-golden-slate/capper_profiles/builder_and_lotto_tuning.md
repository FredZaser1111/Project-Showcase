# Builder and Lotto Tuning Profile

Real slips drive this split: **Builders** prioritize **strike rate / bankroll continuity**;
**Lottos** prioritize ** correlated script + payout** while still following guardrails.

Use this alongside `golden_ticket_style.md`, `playoff_tuning.md`, `playoff_tuning.py`,
and near-miss rules in tracking summaries.

---

## Definitions

### Builder lane

**Goal:** Compound roll with **+300 to +1200** (order-of-magnitude) same-game combos
that still feel like **priced-in star production** plus **modest ladders**.

**Shape signals**

- Mostly **single game** when possible — one pace, whistle, foul pattern.
- **Points-heavy** clears when **market total + game flow** scream **competitive shootout**.
- **Soft superstar floors** beside **thin star ceilings** (e.g. one **elite 30+** leg next
  to role **12–17** ladders).
- Optional **Bet Protect / no-sweat / insurance fees** acceptable as **mental EV** —
  modeling usually treats stake as gross of fee unless explicitly adjusted.

### Lotto lane

**Goal:** **SGP/SGP+** with **four to eight legs** (+1500+) where **everything must
travel together** — assists + boards + quarterly micro legs + occasional **cross-game
“free square” peg**.

**Shape signals**

- **Same-game stacking** across **both sides** OR **heavy one-side team stack** plus
  **one diversifier** from another game (low-floor star or alt).
- **Assists ladders** beside **glass** beside **shooting spikes** — high **single-game
 correlation**, high **half-to-half volatility**.
- **Quarter props** (**1Q** 2+, 4+ points): many **builders** taped into one card become
  a **compound lotto**.
- Profit boosts amplify **display odds** — track **boosted EV** separately from raw book
  probabilities.

---

## Example slips (how the model should read them)

### A. DET @ CLE — four-leg points builder (+977, settled win)

Legs were **PTS-only** Overs on **both teams** — **Harris**, **Cade**, **Mitchell**,
**Mobley**.

**Tune**

| Factor | Allocation |
| --- | --- |
| Game environment | Heavy weight on **projected pace + closing total** vs regular-season norms. Competitive EC playoff game favors this profile. |
| Star ceiling vs floor | Treat **elite scorer line** (**Mitchell 32.5**) as **script anchor** requiring **shooting variance** clearance; softer **Mobley 12.5** as **path B** clearing on volume not hero ball. |
| Multiplier | **Builders** skip `low_margin_activity_combo`; apply **moderate playoff efficiency penalty** (`playoff_tuning.py`) to **shooting-heavy** slips when defense tightens unexpectedly. |

**Avoid** cloning this blindly when total **< ~210** or **one elite defense** suddenly
whole without injury news.

---

### B. DET @ CLE — high-odds SGP (**Mitchell 6+ AST**, **Mobley 2+ AST**, **Cade 10+ REB**)

**Tune**

| Factor | Allocation |
| --- | --- |
| Assist ladders | Prefer **tiered ladders**: **2+ AST** behaves like a **cheap connector** vs **6+** on a scorer — model should **discount** naive correlation between two Cavs assists without minutes overlap math. |
| Live sweat | **`assists`** need **half-to-half pacing** monitoring (halftime drift); document as **cash-out zone** heuristic. |
| Rebound hero | **Cade 10+ REB** is **heavy tail** vs assist legs — tune with **positional rebound-share** snapshot, **not season average** alone. |

**Flag** `--rookie_primary_scorer_points` does **not** apply — use **positional**
**rebounding stress** heuristic from near-miss doc instead.

---

### C. DET @ CLE — six-leg **first-quarter** scorer stack (boosted, **+1585** class)

Ultra-low **1Q** ladders (**4+**, **2+** points).

**Tune**

| Factor | Allocation |
| --- | --- |
| Time window | Shrink effective minutes to **12** or less — volatility **↑**, **assist conversion** meaningless; **shooting bursts** dominate. |
| Rotation | Starter **opening stint length** matters more than full-game rotation rank. Penalize if coach historically **subs early** Game X. |
| UI / sanity | Confirm **players + teams match** — bad labels void model trust; halt allocation. |

**Model suggestion**: apply an extra **−4% to −8%** implicit haircut per **1Q-only**
leg versus full-game equivalents unless **hit-rate data** supplied for that bucket.

---

### D. Spurs @ Wolves + Sacramento — seven-leg (+500-ish) settled win

**Stack**: **Ant** scorer + rebounder ceilings, **Wemby**, **MIN role floors**,
plus **Fox 10+** away peg.

**Tune**

| Factor | Allocation |
| --- | --- |
| Team stacking | **Five MIN legs** implies **heavy blowout/cohesion** dependence — downgrade if **spread or foul risk** spikes. |
| Diversifier | **Fox soft floor** in **second game** reduces **pure** mono-game variance — good **SGP+** hygiene; tune **travel/rest** minimally unless back-to-back. |
| Boards + points same player | Ant **PTS + REB both** correlates tightly — counting one **premium** spike leg max unless lines **priced wrong**. |

---

## Where tuning applies by style

| Prop family | Builder allocation | Lotto allocation |
| --- | --- | --- |
| **Star PTS over (main-ish)** | Prefer **baseline playoff efficiency** penalties only; soften line over chasing juice. | Can accept **harder ladders** (**30+, 35+**) with **boost** iff script says elite usage. |
| **Role PTS soft ladder** | **Good** backbone for builders when total high. | Okay as **glue** legs; stack **fewer than three** correlated non-stars unless plus absurd. |
| **Assists (4+, 6+)** | Use **lighter** ladders or **combined P+A**. | Separate **tier** (**2+** vs **7+**) in model spreadsheet; halftime adjustment workflow. |
| **Rebounds (big)** | Prefer **solo glass path** clarity (board competition). | Allow **hero** big lines only with **explicit** matchup note. |
| **1Q micro points** | Group as **nano-builder** subsection with **minute shrink penalty**. | Stacking six = **compound lotto** — treat slip as **lotto correlation = 1 game × 6**. |
| **SGP+ away peg** | Rare; keep **minimum** **projected scorer** certainty. | **Classic** diversification — one **cheap** star PTS in second game. |
| **Insurance / Protect+** | User preference — annotate stake **inclusive of fee**. | Same; note boost / token interaction if book excludes from boost. |

---

## Integration with Python utilities

| Need | Tool / action |
| --- | --- |
| Playoff minutes + efficiency shading | `playoff_tuning.py` on **estimated hit rates** leg-by-leg |
| Thin combined activity | `--low-margin-activity-combo` |
| Volatile scorer points | `--rookie_primary_scorer_points` |
| 3PM screen | `screen_three_point_legs.py` (usually **lotto spikes**, not builders) |

**Builders** invoking `playoff_tuning.py` should pass **honest blended rates** — do
not inflate series hit rate after **single-game noise**.

---

## Process checklist before allocation label

Tag each slip **Builder**, **Lotto**, or **Hybrid** (`builder stack inflated to lotto odds`),

then verify:

1. **Single-game vs SGP+** — second game justified?
2. **Total + spread** narrative supports **PTS stack**?
3. **Duplicate player** correlations counted?
4. **Quarter legs** flagged for **minute shrink** haircut?
5. **Boost** separated in notes for reproducible retros?

Log outcomes in `tracking/` with slip type tags so regressions distinguish **builder**
**hit rate** from **lotto**.

---

## Bankroll guardrails

- **Separate stake budgets:** builders (larger tolerated) vs **lotto capped small** —
  treating them as **different experiments** avoids over-betting correlated moonshots.
- **Fixed lotto ceiling:** operational cap of **\$5 gross stake per single lotto SGP**
  preserves roll while preserving **+log** learning — note exact stake inclusive of bonus
  bet / Protect+ fee in each `tracking/` entry.
