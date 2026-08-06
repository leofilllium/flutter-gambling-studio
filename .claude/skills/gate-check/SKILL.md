---
name: gate-check
description: "Checks whether the project is ready to move between stages (concept/design/code/qa/release) and returns a PASS/CONCERNS/FAIL verdict."
argument-hint: "[concept|design|code|qa|release]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /gate-check [stage]

Invocation: the user runs `/gate-check [concept|design|code|qa|release]`

## Goal

Checks whether the project is ready to move between development stages.
Returns a verdict: **PASS / CONCERNS / FAIL**, with the specific blockers.

## The mini-game's development stages

```
Concept → Design → Code → QA → Release
   ↑         ↑       ↑      ↑       ↑
  gate      gate    gate   gate    gate
```

## The gates, stage by stage

### gate-check concept → design
Checks that the concept is ready to move into design:

**Required artifacts:**
- [ ] `design/gdd/game-concept.md` exists
- [ ] An elevator pitch (1-2 sentences)
- [ ] The **Classification** block is filled in: category C1–C6, archetype A–AF, math model
      M1–M6, target metric, the path to the config, the compliance profile
- [ ] The unique mechanic (the "juice") is described
- [ ] The archetype is chosen (A–AF / Unique)
- [ ] The Design DNA is described (palette/fonts/shapes/motion, justified by the theme; not default neon)
- [ ] The Layout & Composition Direction is stated (Layout Archetype L1–L6)
- [ ] The math model's target metric is stated and sits inside the window for that model
      (M1 RTP 95–97% + volatility + ≥3 symbols | M2 house edge + cap | M3 regeneration + source/sink |
      M4 rates + hard pity | M5 win-rate + thresholds | M6 bucket multipliers)
- [ ] The compliance profile is chosen and justified (full, or relaxed C5)
- [ ] The game's language is recorded (English by default)

**The gate:**
- PASS: every item is done
- CONCERNS: 1–2 items are missing but not critical
- FAIL: the concept is undocumented, or the RTP is undefined

### gate-check design → code
Checks that the design is ready to hand to the programmer:

**Required artifacts:**
- [ ] A GDD document with its 8 sections (see rules/design-docs.md)
- [ ] `design/balance/rtp-config.json` exists and is valid
- [ ] The payout table is complete (every symbol × every combination)
- [ ] The paylines are defined and numbered
- [ ] Wild/Scatter behaviour is documented (if there is any)
- [ ] The free spins conditions are described (if there are any)
- [ ] The GDD status: `Status: Approved`
- [ ] `game-mathematician` has signed off on the mathematics
- [ ] `design/balance/rtp-config.json` → `simulation.last_run_rtp` is within 95–97%

### gate-check code → qa
Checks that the code is ready for QA:

**Critical gambling requirements:**
- [ ] `lib/systems/weighted_rng.dart` uses `Random.secure()`
- [ ] No `math.Random()` in production code
- [ ] No hardcoded probabilities
- [ ] `GameState` is a sealed class (not boolean flags)
- [ ] The spin result is computed before the animation
- [ ] Double-clicking Spin is blocked
- [ ] `lib/game/slot_config.dart` contains every tunable value

**Flame 1.18.x architecture:**
- [ ] `HasCollisionDetection` on the `World` (not on `FlameGame`)
- [ ] `CameraComponent(world: world)` — the new API

**Baseline code requirements:**
- [ ] `dart analyze` — 0 errors
- [ ] `flutter test` — every test green
- [ ] No `print()` in production code
- [ ] Every player-facing string is in English (or in the language the user explicitly requested)

### gate-check qa → release
Checks readiness for release:

**RTP and mathematics:**
- [ ] `/balance-check` has been run with 1M+ spins
- [ ] The simulated RTP is within 95.0–97.0%
- [ ] The hit rate is within 20–40%
- [ ] No infinite win loop (>1000 free spins in a row is impossible)

**Test coverage:**
- [ ] `weighted_rng` — a distribution test exists
- [ ] `payline_evaluator` — every combination is tested
- [ ] Edge case: balance = 0 → the spin is blocked
- [ ] Edge case: a double click does not start 2 spins
- [ ] 100 spins with no state leakage

**UX and visuals:**
- [ ] The win overlay displays correctly
- [ ] Reel animations are under 3 seconds
- [ ] Particles never exceed 200 at once
- [ ] No artefacts after free spins

**Build:**
- [ ] `flutter build apk --release` — succeeds
- [ ] No debug asserts in the release

## Output format

```
🔍 Gate Check: [concept|design|code|qa|release]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Done (N/M):
   ✅ rtp-config.json exists and is valid
   ✅ Random.secure() is used

❌ Blockers (N):
   ❌ The GDD is missing its "Edge Cases" section
   ❌ Simulated RTP = 94.2% (below 95%)

⚠️  Observations (N):
   ⚠️  No test for the double click

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verdict: FAIL ← NEEDS WORK ← PASS
         ^^^
Reason: the simulated RTP is outside the permitted range.
Next step: call game-mathematician to adjust the weights.
```

## Arguments

- `concept` — the concept→design gate
- `design` — the design→code gate
- `code` — the code→QA gate
- `qa` — the QA→release gate
- `release` — the final gate before deployment
- No argument — auto-detect the current stage
