# Coding standards — Flutter Game Studio

All production standards are specialised for mini-games on Flame 1.18.x.

---

## 1. Dart style guide

### Import order

```dart
// 1. dart: SDK (alphabetical)
import 'dart:async';
import 'dart:math';

// 2. package: (alphabetical)
import 'package:flame/components.dart';
import 'package:flutter/material.dart';
import 'package:my_slot/game/slot_config.dart';

// 3. Relative (inside the package only)
import '../components/reel_component.dart';
```

### Class file — member order

1. Static constants and fields
2. Instance fields (`final` before mutable, public before private)
3. Constructors
4. Static methods
5. Lifecycle methods (onLoad → onMount → update → render → onRemove)
6. Public methods (alphabetical)
7. Private methods (alphabetical)

### `final` vs `var` vs `const`

| Keyword | When to use it |
|---------|----------------|
| `const` | Compile-time constants — always preferred |
| `final` | Assigned once at runtime — the default for fields and locals |
| `var` | Only when the variable is reassigned — requires a comment explaining why |

### Null safety

- No bare `!` without an inline comment explaining why the value is guaranteed non-null
- Prefer `??` for default values
- Use pattern matching for complex null checks
- `late final` only when initialisation cannot happen in the constructor

---

## 2. Flame component standards

### The required lifecycle method order

```dart
class ReelComponent extends PositionComponent with HasGameRef<SlotMachineGame> {
  // Fields
  final _tempPos = Vector2.zero(); // Pre-initialised!

  // Constructor

  @override
  Future<void> onLoad() async { ... }

  @override
  void onMount() { ... }

  @override
  void onGameResize(Vector2 size) {
    if (!isMounted) return; // The check is mandatory!
    super.onGameResize(size);
  }

  @override
  void update(double dt) { ... } // SYNCHRONOUS only!

  @override
  void render(Canvas canvas) { ... } // SYNCHRONOUS only!

  @override
  void onRemove() { ... }
}
```

### No allocation in the hot path

```dart
// ❌ Creates objects every frame — FORBIDDEN
void update(double dt) {
  position = Vector2(x, y + scrollOffset); // allocation!
  final paint = Paint()..color = Colors.red; // allocation!
}

// ✅ Pre-initialised
final _tempPos = Vector2.zero();
late final Paint _symbolPaint;

@override
Future<void> onLoad() async {
  _symbolPaint = Paint()..color = Colors.amber;
}

@override
void update(double dt) {
  _tempPos.setValues(x, y + scrollOffset);
  position.setFrom(_tempPos);
}
```

### Component limits

- Maximum lines in a component: 300 — otherwise decompose it
- Maximum direct children in onLoad: 10
- Maximum constructor parameters: 8 (otherwise use a config data class)
- Maximum inheritance depth: 3 below Component

---

## 3. Game-specific standards

### WeightedRNG — the single source of randomness (gambling)

```dart
/// Weighted random number generator using cryptographically secure Random.
/// See design/gdd/rtp-math-model.md for weight specifications.
class WeightedRNG {
  // One instance for the whole game
  final _rng = Random.secure();

  /// Picks a symbol index based on weights.
  /// [weights] must correspond to SlotConfig.reelWeights.
  int pickSymbol(List<int> weights) {
    assert(weights.isNotEmpty);
    final total = weights.reduce((a, b) => a + b);
    var roll = _rng.nextInt(total);
    for (var i = 0; i < weights.length; i++) {
      roll -= weights[i];
      if (roll < 0) return i;
    }
    return weights.length - 1;
  }
}
```

### PaylineEvaluator — a pure function (gambling)

```dart
/// Evaluates winning combinations on a slot result grid.
/// Pure function — no side effects, no state.
/// See design/gdd/payline-system.md, AC-1 through AC-5.
class PaylineEvaluator {
  /// Evaluates all paylines and returns win results.
  /// [grid] is a List<List<int>> — reels × visible rows.
  static WinResult evaluate(List<List<int>> grid, List<List<int>> paylines) {
    // Pure logic, no RNG, no state
  }
}
```

### GameState — a sealed class is mandatory

```dart
/// Represents all possible states of the slot machine.
/// Transitions: Idle → Spinning → Evaluating → Win|Idle
///              Idle → Spinning → Evaluating → FreeSpins → Spinning...
sealed class GameState {
  const GameState();
}

final class IdleState extends GameState { const IdleState(); }
final class SpinningState extends GameState {
  const SpinningState({required this.outcome});
  final SpinOutcome outcome; // The result is KNOWN before the animation!
}
final class EvaluatingState extends GameState { const EvaluatingState(); }
final class WinState extends GameState {
  const WinState({required this.result});
  final WinResult result;
}
final class FreeSpinsState extends GameState {
  const FreeSpinsState({required this.remaining, required this.multiplier});
  final int remaining;
  final int multiplier;
}
```

---

## 4. Flutter UI standards (HUD / screens)

### Separating state

```dart
// ✅ Correct — the HUD only reads
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> balance;     // From SlotMachineGame
  final ValueNotifier<int> bet;         // From SlotMachineGame
  final ValueNotifier<bool> isSpinning; // From SlotMachineGame

  const HudWidget({
    required this.balance,
    required this.bet,
    required this.isSpinning,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<int>(
      valueListenable: balance,
      builder: (context, bal, _) => Text('$bal', style: ...),
    );
  }
}
```

### Spin button — double-tap protection

```dart
class SpinButtonWidget extends StatefulWidget {
  final VoidCallback onSpin;
  final ValueNotifier<bool> isSpinning;

  @override
  State<SpinButtonWidget> createState() => _SpinButtonWidgetState();
}

class _SpinButtonWidgetState extends State<SpinButtonWidget> {
  DateTime? _lastTap;

  void _handleTap() {
    final now = DateTime.now();
    if (_lastTap != null &&
        now.difference(_lastTap!) < const Duration(milliseconds: 300)) {
      return; // Debounce
    }
    _lastTap = now;
    if (!widget.isSpinning.value) {
      widget.onSpin();
    }
  }
}
```

---

## 5. Audio standards

### AudioService — at most 3 concurrent

```dart
/// Manages game audio — max 3 concurrent sounds: BGM + Spin + Effect.
/// See .claude/docs/technical-preferences.md for audio spec.
class AudioService {
  static const int maxConcurrent = 3;

  AudioPlayer? _bgmPlayer;
  AudioPlayer? _spinPlayer;

  Future<void> startBgm() async {
    await _bgmPlayer?.stop();
    _bgmPlayer = await FlameAudio.loopLongAudio('bgm_main.ogg', volume: 0.7);
  }

  Future<void> playSpinStart() async {
    await _spinPlayer?.stop();
    _spinPlayer = await FlameAudio.loop('sfx_reel_spin.ogg', volume: 0.9);
  }

  Future<void> playSpinStop() async {
    await _spinPlayer?.stop();
    _spinPlayer = null;
    await FlameAudio.play('sfx_reel_stop.ogg');
  }
}
```

---

## 6. Error handling

```dart
// ✅ Always name the exception type
try {
  await loadRtpConfig();
} on FileSystemException catch (e, stack) {
  logger.severe('RTP config load failed', e, stack);
  // Fallback to SlotConfig.defaults
}

// ❌ Forbidden — swallowing errors
try {
  await loadRtpConfig();
} catch (e) {
  // silence
}
```

---

## 7. Documentation

### Doc comments — mandatory for public APIs

```dart
/// Computes the weighted random outcome for a spin.
///
/// Returns [SpinOutcome] with predetermined symbols for all [reelCount] reels.
/// The outcome is computed BEFORE animation starts (Stateless Outcomes pattern).
/// See design/gdd/rtp-math-model.md.
///
/// Throws [InsufficientBalanceException] if [bet] exceeds [balance].
SpinOutcome computeOutcome({required int bet, required int balance}) { ... }
```

### TODO format

```dart
// TODO(agent-name): Description [TASK-NNN]
// Example:
// TODO(mechanics-programmer): Add Near Miss detection [SLOT-42]
```

---

## 8. Testing standards

### The AAA structure — mandatory

```dart
test('PaylineEvaluator determines 3-match horizontal win', () {
  // Arrange
  final grid = [[0, 0, 0], [1, 2, 3], [4, 5, 6]]; // Row 0: three cherries
  final paylines = [[0, 0, 0]]; // The top line

  // Act
  final result = PaylineEvaluator.evaluate(grid, paylines);

  // Assert
  expect(result.winLines, hasLength(1));
  expect(result.totalMultiplier, equals(SlotConfig.cherry3Multiplier));
});
```

### Minimum coverage

| File | Minimum |
|------|---------|
| weighted_rng.dart | 95% |
| payline_evaluator.dart | 95% |
| slot_config.dart | 90% |
| game_state.dart | 85% |
| Screens / widgets | 70% |

---

## 9. Git standards

### Commit format

```
<type>(<scope>): <description>

Examples:
feat(slot): add Wild symbol substitution [SLOT-42]
fix(rng): replace math.Random() with Random.secure() [BUG-7]
test(payline): add scatter position tests [QA-12]
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
Scopes: `slot`, `rng`, `ui`, `audio`, `vfx`, `balance`, `qa`

### PR checklist

- [ ] dart analyze — 0 errors
- [ ] flutter test — all green
- [ ] No `math.Random()` in production code
- [ ] No hardcoded probabilities
- [ ] Every game constant in GameConfig / SlotConfig
- [ ] A GDD reference in the doc comment (for a new mechanic)
- [ ] No allocation in update()/render()

---

## 10. Forbidden patterns

1. **`math.Random()` or `Random()`** — only `Random.secure()`
2. **Hardcoded probabilities** outside GameConfig / SlotConfig
3. **`isPaused = true`** — use `GameState` + `pauseEngine()`
4. **`await` in `update()` / `render()`** — they must be synchronous
5. **`BuildContext` in Flame components** — use callbacks
6. **`print()`** — use `Logger`
7. **Allocation in `update()` / `render()`** — pre-initialise
8. **`dynamic`** outside JSON boundaries
9. **Inheritance more than 3 levels** below Component
10. **Changing RTP weights** outside `rtp-config.json` + game-mathematician's approval
