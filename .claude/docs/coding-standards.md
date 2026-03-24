# Стандарты кода — Flutter Gambling Studio

Все производственные стандарты специализированы под гемблинг игры на Flame 1.18.x.

---

## 1. Dart Style Guide

### Порядок импортов

```dart
// 1. dart: SDK (алфавитный порядок)
import 'dart:async';
import 'dart:math';

// 2. package: (алфавитный порядок)
import 'package:flame/components.dart';
import 'package:flutter/material.dart';
import 'package:my_slot/game/slot_config.dart';

// 3. Относительные (только внутри package)
import '../components/reel_component.dart';
```

### Файл класса — порядок членов

1. Статические константы и поля
2. Поля экземпляра (`final` перед изменяемыми, public перед private)
3. Конструкторы
4. Статические методы
5. Lifecycle методы (onLoad → onMount → update → render → onRemove)
6. Публичные методы (алфавитный порядок)
7. Приватные методы (алфавитный порядок)

### `final` vs `var` vs `const`

| Ключевое слово | Когда использовать |
|----------------|-------------------|
| `const` | Константы времени компиляции — всегда предпочтительно |
| `final` | Присваивается один раз в runtime — по умолчанию для полей и локальных переменных |
| `var` | Только когда переменная переприсваивается — требует комментария о причине |

### Null Safety

- Нет голого `!` без inline комментария — почему значение гарантировано non-null
- Предпочитай `??` для default значений
- Используй pattern matching для сложных null проверок
- `late final` только когда инициализация не может быть в конструкторе

---

## 2. Flame Component Standards

### Обязательный порядок lifecycle методов

```dart
class ReelComponent extends PositionComponent with HasGameRef<SlotMachineGame> {
  // Поля
  final _tempPos = Vector2.zero(); // Прединициализация!

  // Конструктор

  @override
  Future<void> onLoad() async { ... }

  @override
  void onMount() { ... }

  @override
  void onGameResize(Vector2 size) {
    if (!isMounted) return; // Проверка обязательна!
    super.onGameResize(size);
  }

  @override
  void update(double dt) { ... } // ТОЛЬКО синхронный!

  @override
  void render(Canvas canvas) { ... } // ТОЛЬКО синхронный!

  @override
  void onRemove() { ... }
}
```

### Нет аллокаций в hot path

```dart
// ❌ Каждый кадр создаёт объекты — ЗАПРЕЩЕНО
void update(double dt) {
  position = Vector2(x, y + scrollOffset); // аллокация!
  final paint = Paint()..color = Colors.red; // аллокация!
}

// ✅ Прединициализация
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

### Лимиты компонентов

- Максимум строк в компоненте: 300 — иначе декомпозировать
- Максимум прямых children в onLoad: 10
- Максимум параметров конструктора: 8 (иначе config data class)
- Максимум уровней наследования: 3 ниже Component

---

## 3. Gambling-Specific Standards

### WeightedRNG — единственный источник случайности

```dart
/// Weighted random number generator using cryptographically secure Random.
/// See design/gdd/rtp-math-model.md for weight specifications.
class WeightedRNG {
  // Один экземпляр на всю игру
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

### PaylineEvaluator — чистая функция

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

### GameState — sealed class обязателен

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
  final SpinOutcome outcome; // Результат ИЗВЕСТЕН до анимации!
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

## 4. Flutter UI Standards (HUD / Screens)

### Разделение состояний

```dart
// ✅ Правильно — HUD только читает
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> balance;     // Из SlotMachineGame
  final ValueNotifier<int> bet;         // Из SlotMachineGame
  final ValueNotifier<bool> isSpinning; // Из SlotMachineGame

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

### Spin Button — защита от двойного клика

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
      return; // Дебаунс
    }
    _lastTap = now;
    if (!widget.isSpinning.value) {
      widget.onSpin();
    }
  }
}
```

---

## 5. Audio Standards

### AudioService — максимум 3 параллельных

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

## 6. Error Handling

```dart
// ✅ Всегда указывай тип исключения
try {
  await loadRtpConfig();
} on FileSystemException catch (e, stack) {
  logger.severe('RTP config load failed', e, stack);
  // Fallback to SlotConfig.defaults
}

// ❌ Запрещено — глотать ошибки
try {
  await loadRtpConfig();
} catch (e) {
  // молчание
}
```

---

## 7. Documentation

### Doc comments — обязательны для public API

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

### TODO формат

```dart
// TODO(agent-name): Описание [ЗАДАЧА-NNN]
// Пример:
// TODO(slot-programmer): Add Near Miss detection [SLOT-42]
```

---

## 8. Testing Standards

### AAA структура — обязательна

```dart
test('PaylineEvaluator determines 3-match horizontal win', () {
  // Arrange
  final grid = [[0, 0, 0], [1, 2, 3], [4, 5, 6]]; // Row 0: три вишни
  final paylines = [[0, 0, 0]]; // Верхняя линия

  // Act
  final result = PaylineEvaluator.evaluate(grid, paylines);

  // Assert
  expect(result.winLines, hasLength(1));
  expect(result.totalMultiplier, equals(SlotConfig.cherry3Multiplier));
});
```

### Минимальное покрытие

| Файл | Минимум |
|------|---------|
| weighted_rng.dart | 95% |
| payline_evaluator.dart | 95% |
| slot_config.dart | 90% |
| game_state.dart | 85% |
| Screens / widgets | 70% |

---

## 9. Git Standards

### Формат коммитов

```
<тип>(<область>): <описание>

Примеры:
feat(slot): add Wild symbol substitution [SLOT-42]
fix(rng): replace math.Random() with Random.secure() [BUG-7]
test(payline): add scatter position tests [QA-12]
```

Типы: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
Области: `slot`, `rng`, `ui`, `audio`, `vfx`, `balance`, `qa`

### PR чеклист

- [ ] dart analyze — 0 ошибок
- [ ] flutter test — все зелёные
- [ ] Нет `math.Random()` в production коде
- [ ] Нет захардкоженных вероятностей
- [ ] Все игровые константы в SlotConfig
- [ ] GDD ссылка в doc comment (если новая механика)
- [ ] Нет аллокаций в update()/render()

---

## 10. Запрещённые паттерны

1. **`math.Random()` или `Random()`** — только `Random.secure()`
2. **Захардкоженные вероятности** вне SlotConfig
3. **`isPaused = true`** — используй `GameState` + `pauseEngine()`
4. **`await` в `update()` / `render()`** — должны быть синхронными
5. **`BuildContext` в Flame компонентах** — используй колбэки
6. **`print()`** — используй `Logger`
7. **Аллокация в `update()` / `render()`** — прединициализируй
8. **`dynamic`** вне JSON-границ
9. **Наследование > 3 уровней** ниже Component
10. **Изменение RTP весов** вне `rtp-config.json` + подтверждения rtp-mathematician
