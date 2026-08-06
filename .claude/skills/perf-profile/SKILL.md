---
name: perf-profile
description: "Profiles the mini-game's performance and returns prioritised optimisation recommendations."
argument-hint: "[reels|particles|audio|memory|full]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /perf-profile [area]

Invocation: the user runs `/perf-profile [reels|particles|audio|memory|full]`

## Goal

Structured performance profiling of a gambling game.
Finds bottlenecks in the game loop, analyses the frame budget and returns prioritised
optimisation recommendations.

## Agents

- `performance-analyst` — the primary analyst
- `lead-programmer` — architectural recommendations

## Order of work

### Step 1: performance-analyst — the baseline audit

Static code analysis, without running the game:

**Checking for allocations in the hot path:**
```bash
# Look for allocations in update() / render()
grep -n "Vector2(" lib/components/*.dart
grep -n "Paint()" lib/components/*.dart
grep -n "Rect.from" lib/components/*.dart
grep -n "List<" lib/systems/*.dart
```

**Checking SpriteBatch:**
- Is SpriteBatch used for the reel symbols?
- More than 9 symbols on screen without SpriteBatch is a bottleneck

**Checking particles:**
```bash
# How many particles can be created?
grep -n "count:" lib/components/*.dart
grep -n "Particle.generate" lib/components/*.dart
```

**Checking audio:**
- How many AudioPlayer instances are created?
- Is a pool used, or a new one every time?

### Step 2: static analysis — known patterns

| Pattern | Finding | Recommendation | Priority |
|---------|---------|----------------|----------|
| `Vector2()` in update() | An allocation every frame | Pre-initialise it as a field | HIGH |
| `Paint()` in render() | An allocation every frame | Pre-initialise it as a field | HIGH |
| N×SpriteComponent without SpriteBatch | N draw calls | Use SpriteBatch | HIGH |
| `Particle.generate(count: >200)` | Budget overflow | Cap it at 200 | MEDIUM |
| `FlameAudio.play()` every frame | Audio flood | Debounce + AudioPool | MEDIUM |
| `setState()` every frame | A Flutter rebuild | Use a ValueNotifier | MEDIUM |
| `onGameResize()` without isMounted | A potential crash | Add the check | LOW |

### Step 3: profiling (if the game is running)

```bash
# Run in profile mode
flutter run --profile

# Commands for DevTools:
# 1. CPU Profiler → Record → 10 spins → Stop → find the top methods
# 2. Memory → Take snapshot → before and after free spins
# 3. Performance → look at the worst frames
```

**Target metrics:**
| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| FPS | > 58 | 45–57 | < 45 |
| Worst frame | < 25ms | 25–50ms | > 50ms |
| Memory | < 150MB | 150–250MB | > 250MB |

### Step 4: recommendations

The `performance-analyst` agent produces a prioritised list:

```markdown
## HIGH priority (affects gameplay)
1. ReelComponent: a Vector2 allocation in update() → pre-initialise it
   Expected effect: -2ms per frame
   File: lib/components/reel_component.dart:45

## MEDIUM priority (affects UX)
2. WinAnimation: 300 particles exceed the budget → cap at 200
   File: lib/components/win_animation.dart:78

## LOW priority (cosmetic)
3. HudWidget: redundant rebuilds on every frame
   File: lib/screens/hud_widget.dart:23
```

### Step 5: the report

Create `docs/perf-report-YYYY-MM-DD.md`:
```markdown
# Performance Report — [date]

## Baseline (before optimisation)
- FPS: XX
- Worst frame: XXms
- Memory: XXmb

## Problems found
[the findings table]

## Recommendations
[the prioritised list]

## After applying the recommendations (projected)
- Expected FPS improvement: +N
- Expected worst-frame reduction: -Nms
```

## Arguments

- `reels` — focus on reel performance
- `particles` — focus on particles and VFX
- `audio` — focus on the audio system
- `memory` — focus on memory and leaks
- `full` — a full profile (the default)
- `--quick` — static analysis only, with no run-time recommendations
