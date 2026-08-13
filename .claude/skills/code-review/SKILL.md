---
name: code-review
description: "A comprehensive code review of the mini-game: architecture, game integrity, the Flame API, tests and risks."
argument-hint: "[path or area]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /code-review

Invocation: the user runs `/code-review [path or area]`

## Goal

A comprehensive code review of the mini-game. It checks:
- The gambling-specific critical requirements (RNG, state integrity)
- The Flame 1.18.x architecture (correct API usage)
- Code quality (patterns, readability, tests)
- Safety (no math.Random, no hardcoded probabilities)
- Performance (no allocations in update/render)

## Agents

- `lead-programmer` — architecture, patterns, Dart quality
- `mechanics-programmer` — gambling logic, RNG safety, the Flame API
- `qa-tester` — test coverage, edge cases

## Order of work

### Step 1: determine the review scope

If a path is given (for example `lib/systems/weighted_rng.dart`), review that file.
If not, review the whole `lib/` directory.

### Step 2: lead-programmer — the architectural review

The `lead-programmer` agent checks:

**Project structure:**
- [ ] `lib/game/slot_config.dart` exists and contains ONLY constants
- [ ] `lib/systems/weighted_rng.dart` uses `Random.secure()`
- [ ] `lib/models/game_state.dart` contains a sealed class
- [ ] No business logic in `screens/` (UI only)
- [ ] No `BuildContext` in Flame components

**Phone target:**
- [ ] `main.dart` locks `DeviceOrientation.portraitUp` before `runApp`
- [ ] Android is portrait; iOS is portrait and iPhone-only
- [ ] No tablet/iPad, desktop, wide-screen, landscape, hover-only, or keyboard-only layout branch
- [ ] A wide Web host retains the centered phone canvas capped at 430 logical pixels

**Dart patterns:**
- [ ] No `dynamic` outside JSON boundaries
- [ ] No `print()` in production code
- [ ] No `await` in `update()` / `render()`
- [ ] `final` is used wherever possible
- [ ] No magic numbers outside SlotConfig

**The Flame 1.18.x API:**
- [ ] `HasCollisionDetection` on the `World`, not on `FlameGame`
- [ ] `CameraComponent(world: world)` — the new API
- [ ] No `isPaused = true` — `GameState` is used
- [ ] Pre-initialised Vector2/Rect/Paint in `update()`

### Step 3: mechanics-programmer — game integrity

The `mechanics-programmer` agent checks:

**CRITICAL gambling requirements:**
- [ ] `Random.secure()` is the only source of randomness
- [ ] No hardcoded probabilities (`if (rng.nextDouble() < 0.1)`)
- [ ] The spin result is computed BEFORE the animation starts (stateless outcomes)
- [ ] Double-clicking Spin is blocked while a spin runs
- [ ] The balance updates only AFTER the spin finishes and the result is confirmed
- [ ] No state leakage between spins

**RTP and mathematics:**
- [ ] Symbol weights are read from `SlotConfig` / `rtp-config.json`
- [ ] `PaylineEvaluator.evaluate()` is a pure function with no state
- [ ] The Wild symbol substitutes only for the symbols it should
- [ ] Scatter is not tied to a payline

**Free spins / bonuses (if there are any):**
- [ ] The free spins counter cannot go negative
- [ ] The multiplier is applied correctly
- [ ] A re-trigger of free spins is handled

### Step 4: qa-tester — test coverage

The `qa-tester` agent checks:

**Tests present:**
- [ ] `test/systems/weighted_rng_test.dart` — a distribution test
- [ ] `test/systems/payline_evaluator_test.dart` — every combination
- [ ] Test: an insufficient balance blocks the spin
- [ ] Test: a double click does not start two spins
- [ ] Test: GameState returns to Idle after a spin
- [ ] Test: the balance is correct after N spins
- [ ] `game_screen_layout_test.dart` covers 360×640, 360×800, 390×844 and 430×932

**Test quality:**
- [ ] `Random.secure()` or a seed-based mock is used, not `Random()`
- [ ] No empty tests without assertions
- [ ] AAA (Arrange-Act-Assert) is followed

### Step 5: producing the report

Create `docs/review-YYYY-MM-DD.md` with this structure:

```markdown
# Code Review — [date]
## Scope: [path or "the whole project"]

## 🚨 CRITICAL PROBLEMS (they block the release)
- The list of critical findings

## ⚠️ IMPORTANT OBSERVATIONS (they need fixing)
- The list of important problems

## 💡 RECOMMENDATIONS (improvements)
- The list of recommendations

## ✅ WELL DONE
- The list of what was done right

## Summary
- Status: APPROVED / NEEDS WORK / BLOCKED
- Next steps: [the list of actions]
```

## Arguments

- No arguments: a full review of `lib/`
- `lib/systems/` — review systems only
- `lib/game/` — review the game layer
- `--quick` — only the critical integrity checks (RNG, stateless outcomes, config), no architecture
- `--rng` — RNG safety only

## Tools

```
Read, Glob, Grep, Bash(grep*), Bash(dart analyze*)
```

## Example output

```
🔍 Starting the mini-game code review...

📋 Checking RNG safety...
   ✅ Random.secure() is used in weighted_rng.dart
   🚨 math.Random() found in lib/components/test_helper.dart:42

📋 Checking stateless outcomes...
   ✅ The spin result is computed before the animation

📋 Checking SlotConfig...
   ⚠️  Magic numbers found in reel_component.dart:78: `if (multiplier > 20)`
   → Move it into SlotConfig.bigWinMultiplier

📋 Checking test coverage...
   ❌ Missing test: a double click on Spin

Summary: NEEDS WORK (1 critical, 2 important, 0 blocking)
Report saved: docs/review-2026-03-24.md
```
