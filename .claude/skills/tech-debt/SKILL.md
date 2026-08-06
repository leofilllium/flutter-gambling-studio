---
name: tech-debt
description: "Scans for and maintains a register of technical debt, and builds a plan to pay it down."
argument-hint: "[scan|add|show|plan]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# /tech-debt [area]

Invocation: the user runs `/tech-debt [scan|add|show|plan]`

## Goal

Tracks, categorises and prioritises the technical debt in a gambling game.
Scans the code for debt indicators, maintains the register, and recommends a paydown order.

## Technical debt categories

| Category | Symbol | Examples |
|----------|--------|----------|
| CRITICAL (gambling) | 🚨 | math.Random(), hardcoded RTP |
| Architecture | 🏗️ | the wrong Flame API, architectural violations |
| Performance | ⚡ | allocations in update(), no SpriteBatch |
| Testing | 🧪 | no tests for critical logic |
| Documentation | 📝 | no GDD, no comments |
| Code quality | 🔧 | TODOs with no ticket, magic numbers |

## Commands

### /tech-debt scan

The `lead-programmer` agent scans all of `lib/`:

```bash
# TODOs with no ticket
grep -rn "TODO\|FIXME\|HACK\|XXX" lib/ --include="*.dart"

# Magic numbers (outside the config)
grep -rn "[^a-zA-Z][0-9]\{2,\}[^0-9]" lib/ --include="*.dart" | grep -v "slot_config\|_test"

# print() statements
grep -rn "^\s*print(" lib/ --include="*.dart" | grep -v "_test"

# Deprecated Flame API
grep -rn "isPaused\s*=\|HasCollisionDetection" lib/game/ --include="*.dart"

# Missing tests for critical files
for f in lib/systems/*.dart lib/game/slot_config.dart; do
  test_f="test/$(basename ${f%.dart}_test.dart)"
  [ ! -f "$test_f" ] && echo "❌ No test: $f"
done
```

The result is a list of findings with files and line numbers.

### /tech-debt add

Add an entry to the debt register at `docs/tech-debt-register.md`:
```
/tech-debt add "Description of the debt"
```

### /tech-debt show

Show the current `docs/tech-debt-register.md`, grouped by priority.

### /tech-debt plan

Create a paydown plan — what to start with and why.

## The debt register

The register lives in `docs/tech-debt-register.md`:

```markdown
# Tech Debt Register — [date]

## 🚨 CRITICAL (gambling integrity)
| ID | File | Description | Cost | Risk |
|----|------|-------------|------|------|
| TD-001 | lib/game/old_component.dart:45 | math.Random() instead of Random.secure() | 30min | CRITICAL |

## 🏗️ Architecture
| ID | File | Description | Cost | Risk |
|----|------|-------------|------|------|
| TD-002 | lib/game/game.dart | HasCollisionDetection on FlameGame | 2h | HIGH |

## ⚡ Performance
...

## 🧪 Testing
...

## Summary
- Critical: N (pay down IMMEDIATELY)
- High: N (next sprint)
- Medium: N (the next 2 sprints)
- Low: N (backlog)
```

## Prioritisation rules

1. **CRITICAL gambling** — always paid down first; they affect the integrity of the game
2. **Architecture** — paid down before new features are added
3. **Performance** — paid down when the game slows below its thresholds
4. **Testing** — paid down before a release
5. **Documentation** — paid down when a task is handed to another agent
6. **Code quality** — paid down opportunistically, along the way

## Arguments

- `scan` — automatic code scan (the default)
- `show` — show the current register
- `add "description"` — add an entry by hand
- `plan` — build a paydown plan
- `--critical-only` — only the critical integrity problems (RNG, math model, compliance)
