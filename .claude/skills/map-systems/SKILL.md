---
name: map-systems
description: "Decomposes a gambling game concept into technical systems. Builds a dependency graph and an implementation plan for the programmer, working from the category C1-C6 and the mathematical model M1-M6."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
---

# `map-systems` — the game build plan

Breaks the game from `design/gdd/game-concept.md` down into structural components for Flame.

## Behaviour

Do not ask the user anything. Read the concept (the **Classification** block), determine the
category and the mathematical model, and generate `design/gdd/systems-map.md`.

## Output template

```markdown
# Systems map: [Game name]

**Category**: [C1-C6] — [name]
**Archetype**: [A-AF]
**Mathematical model**: [M1-M6] → `design/balance/[file].json`

## 1. Core logic
- `GameConfig` (every tuning knob; the model's numbers are loaded from JSON, never duplicated)
- `GameState` (sealed class: Idle / Resolving / Revealing / Win / OutOfFunds / Paused)
- `WeightedRNG` (`Random.secure()` — the ONLY source of randomness)
- `[Outcome]Resolver` (the round outcome is computed BEFORE the animation — stateless outcomes)
- `[Evaluator]` (a pure evaluation function: no RNG, no state)

## 2. Flame components (presentation)
- `[MainComponent]` (reel / table / minefield / curve / peg field)
- `[ElementComponent]` (symbols, cards, chips, balls, capsules)
- `WinAnimationComponent` (VFX scaled to the significance of the win)
- `AmbientParticles` (a living field — the screen is never static)

## 3. Flutter UI
- `GameScreen` (full-viewport integrated composition from
  `.claude/docs/mobile-phone-contract.md` and `.claude/docs/gameplay-screen-contract.md`; phone
  portrait only, no nested window or core-loop scrolling)
- `HudWidget` (compact balance/bet/multiplier through a ValueNotifier)
- `BetPanel` (bet selection, locked during a round)
- `ActionButton` (a 300 ms debounce + disabled/pressed states + ≥48 wide/56 high primary target)
- Stable layout keys: `gameplaySurface`, `primaryAction`, and `controlDeck` for geometry tests
- `MainMenuScreen`, `PaytableScreen`, every MVP screen

## 4. Compliance (the mandatory layer)
- `AgeGateScreen` (once, before the menu; the result in SharedPreferences)
- `ComplianceCopy` (disclaimer, responsible play, contacts — constants in one place)
- `OddsScreen` (mandatory for C4 and for paid spins in C3)

## 5. Meta & audio
- `SaveService`, `EconomyService`, `ProgressionService`, `AchievementService`
- `AudioService` (at most 3 concurrent sounds)

## Development order (the plan)
1. The mathematical model → `/design-system [system]` → `/balance-check`
2. Core logic (RNG + Resolver + Evaluator) → `/design-system`
3. Flame components → `/prototype [mechanic]`
4. Flutter UI (every screen) + the compliance layer
5. Meta systems and content
6. Integration → `/balance-check` → `/ui-audit` → testing
```

## Key systems by category

| Category | The mechanic's core |
|----------|---------------------|
| **C1** 🎰 slot | `WeightedRNG` + `PaylineEvaluator` + `ReelComponent` + `SymbolComponent` |
| **C1** 🎰 table | `WeightedRNG` + `HandEvaluator`/`WheelResolver` + `CardComponent`/`WheelComponent` |
| **C2** ⚡ | `RoundResolver` (seed+nonce) + `MultiplierCurve` + `CashoutController` + `RoundHistory` |
| **C3** 🏰 | `SpinEventTable` + `EnergyService` + `MetaProgressService` + `RaidResolver` |
| **C4** 🎁 | `BannerResolver` + `PityCounter` (persistent!) + `DuplicateConverter` + `PullReveal` |
| **C5** 🃏 | `RunRng(seed)` + `HandEvaluator` + `ModifierRegistry` + `ShopController` + `RunState` |
| **C6** ⚙️ | `PhysicsWorld` (fixed timestep) + `LaunchResolver` + `BucketDetector` + `BodyLimiter` |

The document must include the `Development order` section and the list of classes.
