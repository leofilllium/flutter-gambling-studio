---
name: team-dev
description: "Orchestrates development of a gambling game mechanic across several specialists. Coordinates the game designer, the mathematician, the mechanics programmer, the VFX artist and the sound designer."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<feature/system description> (e.g. 'Cascading reels with free spins', 'Cash-out with round history', 'A pity counter and an odds screen')"
---

# `team-dev` — studio orchestration

Runs the agents in the right order to implement a complex feature.

## Instructions

1. Clarify the task with the user: which feature, and is there already a GDD?
   Read the **Classification** block in `design/gdd/game-concept.md` — the category (C1–C6)
   and the mathematical model (M1–M6) determine who to call and in what order.

2. If there is no GDD, call `game-designer` to write one.
   They must consult `game-mathematician` on anything involving the model's numbers.

3. **The mathematics comes BEFORE the code.** If the feature touches the numbers:
   - `game-mathematician` edits the model's JSON config
   - run it: `python3 tools/simulate_math.py --model [m1-m6] --config design/balance/[file].json`
   - only a green run opens the road to implementation

   | Category | What the mathematician computes |
   |----------|--------------------------------|
   | C1 | symbol weights, payouts, RTP, hit rate |
   | C2 | house edge, the multiplier formula, the cap |
   | C3 | spin event weights, unlock prices, energy regeneration |
   | C4 | base rates, soft/hard pity |
   | C5 | round thresholds, modifier strength, income |
   | C6 | bucket multipliers, the hit distribution |

4. For the implementation call `mechanics-programmer` (core logic) and `juice-artist` (VFX
   animation) in the right order. Always pass them the links to the GDD and to the model config.
   Remind them: `Random.secure()`, stateless outcomes, and not one model number as a Dart literal.

5. Where needed, bring in `sound-designer` for the audio events
   (bet, spin, stop, near-miss, cash-out, reveal, wins by tier).

6. If the feature adds a random award in exchange for currency, bring in `ui-programmer`
   to update the odds disclosure screen (`.claude/rules/responsible-gaming.md` §2.4).

7. All player-facing copy the feature introduces is written in English (unless the user
   explicitly asked for the game in another language).

8. When everything is done, suggest the user verify the result: `/balance-check`, `/ui-audit`.
