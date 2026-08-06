---
name: balance-check
description: "Verifies a gambling game's mathematical model through tools/simulate_math.py. Picks the model M1-M6 from the game's category (slot RTP, an original's house edge, a hybrid's economy, gacha pity, a roguelike's run win-rate, plinko's physical RTP) and checks it against the thresholds. Supports full-curve validation across every bet tier, level and banner."
user-invocable: true
allowed-tools: Bash, Read, Write
argument-hint: "[trial count, defaults to the model's own]"
---

# `balance-check` — the mathematical model verifier

Mathematics in this studio is a verifiable contract, not a "feeling of balance".
Every game has exactly one declared model, one config and one run.

## 1. Determine the model

Read `design/gdd/game-concept.md`, the **Classification** block. It contains the category,
the model and the path to the config. If the block is missing, the concept is a FAIL — go back
to `/gate-check concept`.

| Category | Model | Default config | PASS threshold |
|----------|-------|----------------|----------------|
| C1 🎰 Social Casino | **M1** | `design/balance/rtp-config.json` | RTP 95–97%, hit rate 20–35% |
| C2 ⚡ Originals | **M2** | `design/balance/rtp-config.json` | RTP 96–99%, the cap declared |
| C3 🏰 Spin-to-Progress | **M3** | `design/balance/economy-config.json` | source/sink 0.90–1.15, pace 2–5 |
| C4 🎁 Gacha | **M4** | `design/balance/gacha-config.json` | rate 0.5–2%, pity 50–90, 0 misses |
| C5 🃏 Roguelike | **M5** | `design/balance/run-config.json` | win-rate 25–40%, determinism |
| C6 ⚙️ Physics | **M6** | `design/balance/physics-config.json` | RTP 95–97%, fixed timestep |

The complete thresholds and formulas are in `.claude/docs/math-models.md`.

## 2. The run

```bash
python3 tools/simulate_math.py \
  --model [m1-m6] \
  --config design/balance/[file].json \
  --trials [defaults to the model's own] \
  --report design/balance/simulation-report.md
```

Exit codes: `0` = PASS, `1` = CONCERNS, `2` = FAIL — you can hang a hook or CI off that.

If the config does not exist yet, take the reference from `.claude/docs/templates/math-configs/`
(all six pass a run out of the box) and adapt it to the game without breaking the schema.
To check the tool is alive: `python3 tools/simulate_math.py --selftest`.

## 3. Reading the result

1. The report is always written to `design/balance/simulation-report.md` — a run without a
   report does not count as having happened.
2. **PASS** → the pipeline continues.
3. **CONCERNS** → record the risk in the report and decide with the user whether to proceed.
4. **FAIL** → production stops. Call `game-mathematician`; they edit **only the numbers in the
   JSON**, never the code. Then run it again.
5. Update `simulation.last_run_date` in the config — a commit without it is rejected by the hook.

## 4. Full-curve validation (ALL the content, not one point)

> A complete game means a volume of content. You verify the whole surface, not the default setting.

What is additionally run, by category:

- **C1/C2** — every **bet tier** separately: the RTP must not drift with the bet size.
  Plus the bonus mode: its share of the overall RTP (typically 30–40%) is stated in the report.
- **C2** — every depth / cash-out target: the RTP must be identical across strategies.
  A spread above 0.001 means a leak in the multiplier formula or the cap.
- **C3** — the whole `unlock_prices` ladder: monotonicity, no "wall" (step ≤ 1.6×), and the
  final unlock reachable within the simulated number of sessions.
- **C4** — every banner: the rates sum to 1.0, pity fires on all of them, and the 90th
  percentile of pulls ≤ hard pity.
- **C5** — the whole `round_targets` ladder (step ≤ 2×) and every modifier in `modifiers[]`:
  none dominant and none dead relative to the set's median.
- **C6** — the distribution across ALL buckets: not one "dead" bucket (< 0.1% of hits).
  For a coin pusher, measure in the steady state, after ≥10,000 warm-up coins.

The curve report: a "point → key parameter → metric → verdict" table in
`design/balance/curve-report.md`.

## 5. Cross-checking against what the player sees

The numbers shown to the player must match the config (`responsible-gaming.md` §5):

- paytable / rules ↔ the payouts and weights in the config;
- the "Odds" screen ↔ the base rates and pity in the config;
- the declared house edge and maximum multiplier ↔ the config.

A discrepancy is not cosmetic — it misleads the player: FAIL.
