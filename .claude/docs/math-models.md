# Mathematical models — what is verified, and how

> In a gambling studio the mathematics is not "balancing by eye" — it is a **verifiable
> contract**. Every game has exactly one declared mathematical model (out of six), one config
> file and one simulation run that either clears the threshold or blocks the release.
>
> The model is determined by the game's category — see `.claude/docs/gambling-categories.md`.
> The owner of every model is the `game-mathematician` agent. Only they change it.

## Summary table

| Model | Categories | Config | Simulation | PASS threshold |
|-------|-----------|--------|------------|----------------|
| **M1 — Paytable RTP** | C1 | `design/balance/rtp-config.json` | 1,000,000 rounds | RTP 95–97%, hit rate 20–35% |
| **M2 — Instant-Win RTP** | C2 | `design/balance/rtp-config.json` | 1,000,000 rounds | RTP 96–99%, multiplier cap respected |
| **M3 — Economy** | C3 | `design/balance/economy-config.json` | 10,000 sessions | Source/sink 0.9–1.15, pace 2–5 sessions per unlock |
| **M4 — Gacha** | C4 | `design/balance/gacha-config.json` | 1,000,000 pulls | Effective rate = declared ±0.1 pp, pity fires 100% |
| **M5 — Run Win-Rate** | C5 | `design/balance/run-config.json` | 100,000 runs | Win-rate 25–40%, determinism by seed |
| **M6 — Physics RTP** | C6 | `design/balance/physics-config.json` | 1,000,000 launches | RTP 95–97%, reproducible by seed |

Running any model takes one entry point:

```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json --trials 1000000
```

The report is always written to `design/balance/simulation-report.md`.

---

## M1 — Paytable RTP (C1: slots, poker, blackjack, roulette, bingo)

**What we verify.** The return to player across the full payout table at honest weights.

**Formula:**
```
RTP = Σ(combination_probability × combination_payout) / bet
hit_rate = rounds_with_a_win / total_rounds
volatility = std(payouts) / mean_payout
```

**Thresholds:**

| Metric | PASS | CONCERNS | FAIL |
|--------|------|----------|------|
| RTP | 95.0–97.0% | 94.0–95.0 or 97.0–98.0% | < 94% or > 98% |
| Hit rate | 20–35% | 15–20 or 35–45% | outside 15–45% |
| Volatility | matches what was declared | ±20% deviation | does not match |
| Max win | reachable within 1M rounds | reachable within 10M | unreachable |

**Also mandatory:**
- Every bet tier is checked separately — the RTP must not drift with the bet size.
- The bonus mode (free spins) counts towards **the overall RTP**, not separately; the report
  states the share of RTP from base play and from the bonus (typically 60/40 or 70/30).
- A symbol weight of 0 is forbidden — delete the symbol instead.

---

## M2 — Instant-Win RTP (C2: crash, mines, dice, hi-lo, tower, keno, scratch, pick)

**What we verify.** The house edge of instant rounds and the correctness of the multiplier formula.

**Formula (common to the "originals"):**
```
multiplier(step) = (1 - house_edge) / probability_of_surviving_to_step
RTP = 1 - house_edge
```

An example for mines with `n` cells and `m` mines, after `k` reveals:
```
P(k) = C(n-m, k) / C(n, k)
multiplier(k) = (1 - house_edge) / P(k)
```

**Thresholds:**

| Metric | PASS | FAIL |
|--------|------|------|
| RTP | 96.0–99.0% | outside the range |
| House edge declared in the rules | yes | no |
| Maximum multiplier | declared and enforced by the cap | not capped |
| The round is predetermined at the start | yes (stateless outcome) | computed during the animation |

**Round determinism (mandatory for C2).** The round's outcome is computed before the animation
from the triple `serverSeed + clientSeed + nonce`. The test must prove that the same triple
gives the same outcome, and that changing any component changes the outcome.

```dart
/// Round outcome is derived once, before any animation frame.
/// See design/gdd/rtp-math-model.md.
final outcome = RoundResolver.resolve(
  serverSeed: seed.server,
  clientSeed: seed.client,
  nonce: seed.nonce,
);
```

**Cash-out correctness.** The test: the payout on a cash-out at step `k` is exactly
`bet × multiplier(k)`, not a cent more — a classic source of RTP leakage.

---

## M3 — Economy (C3: spin-to-progress hybrids)

**What we verify.** Not RTP, but whether the economy converges: the player should feel constant
progress without finishing the content in one evening.

**Metrics:**

| Metric | Definition | PASS |
|--------|------------|------|
| **Source/sink ratio** | currency in / currency spent on unlocks per 100 spins | 0.90–1.15 |
| **Progress pace** | sessions until the next meaningful unlock | 2–5 |
| **Session length** | until the energy runs out | 3–7 minutes |
| **Regeneration** | energy per hour | covers 2–3 sessions a day |
| **Price step** | price of unlock N+1 / price of unlock N | ≤ 1.6 |
| **Dead-end rate** | share of sessions where the player got nowhere | < 10% |

**Simulation.** 10,000 virtual sessions with an "average player policy" (spends energy to zero,
invests in everything available in ascending price order). The report is a "session → cumulative
progress" curve, which must be monotonic with no plateau longer than 5 sessions.

**The spin event table** is part of the model too: the event weights (coins / shield / attack /
raid / jackpot) are declared in the config and sum to 100%. If spins can be paid for, these
probabilities are **disclosed to the player** (see compliance).

---

## M4 — Gacha (C4)

**What we verify.** That the declared percentages are true, and that pity really does rescue the player.

**Key concepts:**
- **Base rate** — the declared chance of a rarity on a single pull.
- **Soft pity** — the point from which the chance starts to rise linearly.
- **Hard pity** — the pull at which the rarity is guaranteed (100%).
- **Effective rate** — the actual chance including pity over a long distance. This is the number
  disclosed to the player alongside the base rate.

```
effective_rate = total_SSR_dropped / total_pulls   (a 1M pull simulation)
E[pulls to SSR] = 1 / effective_rate
```

**Thresholds:**

| Metric | PASS | FAIL |
|--------|------|------|
| SSR base rate | 0.5–2.0% | outside the range |
| Hard pity | 50–90 pulls | > 90 or absent |
| Effective rate = the computed one | ±0.1 pp | a larger divergence |
| Pity fires | in 100% of cases at hard pity | even one miss |
| 90th percentile of pulls to an SSR | ≤ hard pity | above hard pity (pity is broken) |
| Sum of all rarity probabilities | exactly 1.0 | anything else |
| The odds disclosure screen | exists and is reachable BEFORE a pull | absent |

**Duplicates must have value** — conversion into shards or levels. A pull that gives "nothing"
is a design failure, not a mathematical one.

---

## M5 — Run Win-Rate (C5: casino roguelikes)

**What we verify.** That the run is winnable but not free, and that the seed is reproducible.

**Simulation.** 100,000 runs by an "average player" bot: a greedy heuristic (always takes the
modifier with the highest expected score gain, buys while it can afford to).

**Thresholds:**

| Metric | PASS | FAIL |
|--------|------|------|
| Run win-rate (average player) | 25–40% | < 15% (hopeless) or > 55% (no challenge) |
| Monotonicity of round targets | step ≤ ×2 | a "wall" larger than ×2 |
| Strength of a single modifier | none gives a win-rate > 80% | there is a dominant one |
| Dead modifiers | none gives < 5% benefit | there are useless ones |
| Seed determinism | one seed → an identical run | divergence |
| Average run length | 8–20 minutes | outside the range |

**The determinism test is mandatory:**
```dart
test('the same seed produces an identical run', () {
  final a = RunSimulator(seed: 12345).playToEnd();
  final b = RunSimulator(seed: 12345).playToEnd();
  expect(a.eventLog, equals(b.eventLog));
});
```

> C5 is the only model where `Random.secure()` is **not** required: determinism by seed matters
> more than cryptographic strength, so a seeded `Random(seed)` is used. This must be explicitly
> recorded in an ADR. In every other category: `Random.secure()` only.

---

## M6 — Physics RTP (C6: coin pusher, plinko, pachinko)

**What we verify.** That the physics pays out, on average, what was declared. This cannot be
computed analytically — only by running it.

**Simulation requirements:**
- A fixed timestep (`1/60`), not tied to the real fps.
- A fixed seed for the starting conditions (position, impulse, angle).
- 1,000,000 launches headless, without rendering.
- Measure the distribution across buckets, not just the mean.

**Thresholds:**

| Metric | PASS | FAIL |
|--------|------|------|
| RTP | 95.0–97.0% | outside the range |
| Reproducibility | one seed → an identical trajectory | divergence |
| Bucket distribution | no bucket below 0.5% of hits | there is a "dead" bucket |
| Stability under fps drops | RTP does not change (fixed timestep) | RTP drifts |
| Active body limit | the GameConfig cap is respected | it is exceeded |

**The coin pusher trap.** Coins accumulating on the shelf make the RTP **non-stationary** — it
depends on the state of the field. RTP must be measured in the steady state (after 10,000
"warm-up" coins), not from an empty field.

---

## Rules common to every model

1. **One source of truth.** The numbers live in the JSON config; Dart reads them into
   `GameConfig`. Duplicating a value in JSON and in code is a violation.
2. **Stateless outcomes.** The outcome is computed BEFORE the animation in all six models.
   The animation only plays back a result that is already known.
3. **`Random.secure()`** everywhere except the seeded determinism in M5 (and the seed for the
   starting conditions in the M6 simulation, which does not ship in the production round).
4. **The report is mandatory.** A run that is not written to
   `design/balance/simulation-report.md` does not count as having happened.
5. **The run date.** The `simulation.last_run_date` field is updated by every run; a config
   commit without an updated date is rejected by the hook.
6. **Changing the model = an ADR.** Changing the target RTP, pity or win-rate requires
   `/architecture-decision`, not a silent JSON edit.

## Report format

```markdown
# Simulation Report — [Game name]

- **Model**: M[1-6] — [name]
- **Config**: design/balance/[file].json
- **Trials**: 1,000,000
- **Date**: YYYY-MM-DD
- **Seed**: [if applicable]

## Result

| Metric | Target | Measured | Verdict |
|--------|--------|----------|---------|
| RTP | 96.0% | 95.87% | ✅ PASS |
| Hit rate | 28% | 27.4% | ✅ PASS |
| ... | | | |

## Payout distribution
[a table or histogram by win tier]

## Verdict
✅ PASS — the model is inside the target window, we can continue.
⚠️ CONCERNS — [what exactly is borderline, and what we are risking].
❌ FAIL — [what is outside the window]; game-mathematician adjusts [specific parameters].
```
