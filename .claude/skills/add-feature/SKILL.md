---
name: add-feature
description: "Adds a new feature to a finished gambling game. C1: Wild symbols, free spins, a jackpot. C2: auto-bet, a new risk profile. C3: a new spin event type, a board season. C4: a guarantee on an x10, a new rarity. C5: a new modifier. C6: a special bucket, a jackpot gate."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<feature-name>"
---

# `add-feature` — adding a feature

The correct way to add a new mechanic to a finished game.

## Instructions

1. Read `design/gdd/game-concept.md`, the **Classification** block — the category (C1–C6),
   the mathematical model (M1–M6) and the path to its config.

2. Ask the user:
   - How does the feature work?
   - How often should it appear or fire?
   - How much does it affect the model's target metric?

3. **Update the mathematical model's config** — a feature almost always changes the numbers:

   | Category | Config | What typically changes |
   |----------|--------|------------------------|
   | C1 | `design/balance/rtp-config.json` | weights, payouts, the `bonus` block |
   | C2 | `design/balance/rtp-config.json` | house edge, the multiplier formula, the cap |
   | C3 | `design/balance/economy-config.json` | `spin_events[]`, `unlock_prices[]`, regeneration |
   | C4 | `design/balance/gacha-config.json` | `rarities[]`, `hard_pity`, soft pity |
   | C5 | `design/balance/run-config.json` | `modifiers[]`, `round_targets[]`, income |
   | C6 | `design/balance/physics-config.json` | `bucket_multipliers[]`, geometry |

4. **Recompute the mathematics** — before writing the code, not after:
   ```bash
   python3 tools/simulate_math.py --model [m1-m6] --config design/balance/[file].json
   ```
   - Call `game-mathematician` to bring the metric back into its target window.
   - Run `/balance-check` to confirm it and write the report.
   - A feature that knocks the metric out of its window does not reach the code until it is balanced.

5. **Implementation**: call `mechanics-programmer`. They read the new values from the config —
   not one of the feature's numbers appears as a Dart literal.

6. **Check the compliance consequences** (`.claude/rules/responsible-gaming.md`):
   - The feature adds a new random award for currency → update the odds disclosure screen.
   - The feature changes payouts → update the paytable/rules so what is shown matches the config.
   - The feature adds a purchase → for C5 the relaxed profile automatically becomes the full one.

7. Any new player-facing copy is written in English (unless the user explicitly asked for the
   game in another language).

8. Create an issue in `production/session-state/` and call `/team-dev` for the full implementation.

9. After the code: `/balance-check` to verify, `/code-review` for the review.
