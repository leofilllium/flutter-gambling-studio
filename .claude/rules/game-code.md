---
description: Gambling game Dart/Flame code rules — RNG integrity, stateless outcomes, math-model config, state integrity, forbidden patterns. Unconditional across all six gambling categories.
globs: ["lib/**/*.dart"]
---

# Game Code Rules — gambling games

## CRITICAL RULES (violation = PR blocked)

> These apply to all six categories C1–C6, without exception.

### GameConfig — the single source of game constants
- ALL game constants live in `lib/game/game_config.dart` (or `slot_config.dart` for slots)
- Bets, multipliers, timings, limits, board dimensions — only from the config
- The math model's numbers live in JSON (`design/balance/*.json`) and are loaded into the
  config; they are never re-typed by hand in two places
- Numeric literals for gameplay values outside the config are not allowed

```dart
// ✅ CORRECT
class GameConfig {
  static const int minBet = 1;
  static const int maxBet = 100;
  static const int startingBalance = 1000;
  static const int bigWinMultiplier = 10;
  static const int maxParticles = 200;
  static const Duration roundAnimation = Duration(milliseconds: 2000);
}

// ❌ FORBIDDEN
if (win > 1000) {              // Where did 1000 come from?
  triggerParticles(count: 50); // And 50?
}
```

### GameState — a sealed class is mandatory
- Use a sealed class for every round state
- No boolean flags (`isSpinning`, `isPaused`, `isGameOver`)
- Each state carries its own data, including the already-computed outcome

```dart
sealed class GameState {}
class IdleState extends GameState {}
/// Outcome is already resolved — the animation only plays it back.
class ResolvingState extends GameState { final RoundOutcome outcome; }
class RevealingState extends GameState { final RoundOutcome outcome; }
class WinState extends GameState { final int payout; final WinTier tier; }
class PausedState extends GameState { final GameState previousState; }
class OutOfFundsState extends GameState {}
```

### Protect the main action from double taps
- The main action button (Spin/Play/Start) MUST be locked while the round runs
- A debounce of at least 300 ms

### Stateless outcomes (deterministic results)
- The round result MUST be computed BEFORE the animation starts
- The animation only "plays back" a predetermined result
- Without this the RTP cannot be verified, and cash-out in C2 is mathematically incorrect

## RNG AND MATHEMATICAL INTEGRITY

> Unconditional rules: they apply to ALL categories C1–C6.

### RNG safety
- **NEVER** use `math.Random()` or `Random()` — ONLY `Random.secure()`
- **NEVER** hardcode a probability: `if (rng.nextDouble() < 0.1) win!`
- **ALWAYS** read weights from `GameConfig` or the math model's JSON config
- The RNG is initialised ONCE, inside `WeightedRNG`
- **The single exception**: seeded run determinism in casino roguelikes (C5, model M5).
  There `Random(seed)` is mandatory — the run has to be reproducible. The exception is
  recorded in an ADR, otherwise `/code-review` treats it as a violation.

```dart
// ✅ CORRECT (GAMBLING)
class WeightedRNG {
  final _rng = Random.secure();

  int pickSymbol(List<int> weights) {
    final total = weights.reduce((a, b) => a + b);
    var roll = _rng.nextInt(total);
    for (var i = 0; i < weights.length; i++) {
      roll -= weights[i];
      if (roll < 0) return i;
    }
    return weights.length - 1;
  }
}

// ❌ FORBIDDEN
final rng = Random(); // Not secure!
if (Random().nextDouble() < 0.15) triggerBonus(); // Hardcoded probability!
```

### The math model's target window

The window depends on the game's category — the full table is in `.claude/docs/math-models.md`:

| Category | Model | Target window |
|----------|-------|---------------|
| C1 | M1 | RTP 95–97%, hit rate 20–35% |
| C2 | M2 | RTP 96–99%, house edge declared, multiplier capped |
| C3 | M3 | source/sink 0.90–1.15, pace of 2–5 sessions per unlock |
| C4 | M4 | base rate 0.5–2%, hard pity 50–90, pity fires 100% of the time |
| C5 | M5 | run win-rate 25–40%, determinism by seed |
| C6 | M6 | RTP 95–97%, fixed timestep, reproducibility |

- If `/balance-check` returns FAIL, production stops.
- Only `game-mathematician` changes the model's numbers, and only in the JSON config.
- Changing a target metric (RTP, pity, win-rate) requires an ADR, not a silent edit.

## FORBIDDEN PATTERNS

1. **`isPaused = true`** — use the `GameState` sealed class
2. **`BuildContext` in Flame components** — use callbacks or a service locator
3. **`print()` in production code** — use `Logger`
4. **`await` in `update()` or `render()`** — these methods MUST be synchronous
5. **Object allocation in `update()`** — pre-initialise Vector2, Rect, Paint
6. **`math.Random()` / `Random()`** — only `Random.secure()` (exception: seeded C5 + ADR)
7. **Hardcoded gameplay parameters** outside GameConfig
8. **Changing state during an animation** — check the GameState
9. **Computing the outcome inside the animation** — breaks stateless outcomes and the RTP
10. **Duplicating the model's numbers** in JSON and in Dart — one source of truth
11. **Real-currency symbols next to the game balance** — see responsible-gaming.md §1
12. **Player-facing copy in a language other than English**, unless the user explicitly asked
    for a different language — see CLAUDE.md → Language

## REQUIRED ARCHITECTURE

```
lib/
├── game/
│   ├── [game_name]_game.dart   # extends FlameGame — the entry point
│   ├── [game_name]_world.dart  # extends World with HasCollisionDetection
│   └── game_config.dart        # ONLY constants, no logic
├── systems/
│   ├── weighted_rng.dart       # Random.secure() — the ONLY source of randomness
│   ├── [outcome]_resolver.dart # The round outcome, computed BEFORE the animation
│   └── [evaluator].dart        # A pure result-evaluation function (no RNG, no state)
├── models/
│   └── game_state.dart         # sealed class
```
