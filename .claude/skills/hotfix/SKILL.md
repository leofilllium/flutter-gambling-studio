---
name: hotfix
description: "An emergency fix for a critical problem, with a minimal diff and mandatory verification."
argument-hint: "[a short description of the critical problem]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# /hotfix [problem description]

Invocation: the user runs `/hotfix [a short description of the critical problem]`

## Goal

An emergency fix for a critical problem in the mini-game. It bypasses the normal development
process while keeping a full audit trail. Use it for:
- Critical RNG bugs (an incorrect distribution)
- The RTP falling outside 90–98%
- State leakage (an incorrect balance)
- A crash during a spin
- A critical UI bug (spinning is impossible)

## When NOT to use it

- Ordinary bugs → use the standard process
- New features → `/add-feature`
- Refactoring → a normal PR

## Order of work

### Step 1: assessing severity

The `lead-programmer` agent assesses:
- Does it touch the RNG or the balance? → CRITICAL
- Can the player lose coins? → CRITICAL
- Purely a visual bug? → NOT A HOTFIX

### Step 2: diagnosis

```bash
# Check dart analyze
dart analyze lib/

# Look for the obvious cause
grep -rn "TODO\|FIXME\|HACK" lib/ --include="*.dart"

# Check the tests
flutter test --name "broken_mechanic"
```

The `mechanics-programmer` agent analyses the gambling-specific files:
- `lib/systems/weighted_rng.dart` — checking the RNG
- `lib/systems/payline_evaluator.dart` — checking the logic
- `lib/game/slot_config.dart` — checking the config
- `lib/models/game_state.dart` — checking the state machine

### Step 3: creating the hotfix branch

```bash
DATE=$(date '+%Y%m%d')
git checkout -b hotfix/$DATE-short-description
```

### Step 4: the fix

- Fix ONLY the identified problem
- No opportunistic improvements
- The smallest possible diff

### Step 5: verification

```bash
# Mandatory after the fix
flutter test
dart analyze lib/
python3 tools/simulate_math.py --model [m1-m6] --config design/balance/[file].json --trials 100000
```

The verification checklist:
- [ ] The fix does not break existing tests
- [ ] The RTP is still within 95–97% (or it was outside and is now back in range)
- [ ] No new `math.Random()` was introduced
- [ ] No state leakage appeared

### Step 6: the audit trail

Create `production/session-logs/hotfix-YYYY-MM-DD.md`:
```markdown
# Hotfix — [date and time]

## Problem
[A description of the critical problem]

## Diagnosis
[The root cause]

## The fix
[What was changed and why]

## Files changed
- path/to/file.dart — [what changed]

## Verification
- flutter test: [PASS/FAIL]
- dart analyze: [0 issues / N issues]
- Math simulation (100K): [XX.X%]

## Approved
- Technically: [lead-programmer / technical-director]
- Mathematically: [game-mathematician — if the RTP was affected]
```

### Step 7: merging

```bash
git add [only the changed files]
git commit -m "hotfix: [a short description of the problem]

Problem: [what was wrong]
Fix: [what changed]
Verification: tests GREEN, RTP XX.X%"
```

## Arguments

- `[description]` — a short description of the problem (required)
- `--rng` — focus on the RNG/probabilities
- `--balance` — focus on the player's balance
- `--crash` — focus on the crash/error
