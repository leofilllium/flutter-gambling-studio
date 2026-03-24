---
description: Gambling-specific Dart/Flame code rules — RNG safety, state integrity, forbidden patterns
globs: ["lib/**/*.dart"]
---

# Gambling Code Rules

## КРИТИЧЕСКИЕ ПРАВИЛА (нарушение = блокировка PR)

### RNG Безопасность
- **НИКОГДА** не используй `math.Random()` или `Random()` — ТОЛЬКО `Random.secure()`
- **НИКОГДА** не захардкодируй вероятности: `if (rng.nextDouble() < 0.1) win!`
- **ВСЕГДА** читай веса из `SlotConfig` или `rtp-config.json`, никогда не пиши их в коде
- RNG должен быть инициализирован ОДИН РАЗ в `WeightedRNG` — не пересоздавай на каждом спине

```dart
// ✅ ПРАВИЛЬНО
class WeightedRNG {
  final _rng = Random.secure(); // Единственный источник случайности

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

// ❌ ЗАПРЕЩЕНО
final rng = Random(); // Не secure!
if (Random().nextDouble() < 0.15) { // Захардкоженная вероятность!
  triggerBonus();
}
```

### Stateless Outcomes (Детерминированные результаты)
- Результат спина ДОЛЖЕН быть вычислен ДО начала анимации
- Анимация только "проигрывает" предопределённый результат
- Никакого изменения результата во время анимации

```dart
// ✅ ПРАВИЛЬНО — результат известен до анимации
Future<void> spin() async {
  final outcome = _rng.computeOutcome(SlotConfig.reelWeights); // Сначала результат
  setState(GameState.spinning);
  await _animateReels(targetSymbols: outcome.symbols);      // Потом анимация
  await _evaluateAndShowWin(outcome);
}

// ❌ ЗАПРЕЩЕНО — результат определяется во время анимации
Future<void> spin() async {
  await _animateReels();        // Анимируем
  final won = Random().nextBool(); // Потом решаем
}
```

### Конфигурация в SlotConfig
- ВСЕ игровые константы — в `lib/game/slot_config.dart`
- Веса символов, множители, шансы бонуса — только из конфига
- Нельзя иметь числовые литералы вроде `0.95`, `3`, `5` для игровых значений вне конфига

```dart
// ✅ ПРАВИЛЬНО
class SlotConfig {
  static const List<int> reelWeights = [10, 8, 6, 4, 3, 2, 1]; // Веса из конфига
  static const double targetRtp = 0.96;
  static const int reelCount = 3;
  static const int symbolsPerReel = 3;
  static const int freeSpinsCount = 10;
}

// ❌ ЗАПРЕЩЕНО
if (winMultiplier > 20) { // Откуда взялось 20?
  triggerParticles(count: 50); // И 50?
}
```

## ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ

1. **`math.Random()` вне тестов** — только `Random.secure()`
2. **Захардкоженные вероятности** вне `SlotConfig` / `rtp-config.json`
3. **`isPaused = true`** — используй `GameState` enum
4. **`BuildContext` в Flame компонентах** — используй колбэки или service locator
5. **`print()` в production коде** — используй `Logger`
6. **`await` в `update()` или `render()`** — эти методы ОБЯЗАНЫ быть синхронными
7. **Изменение баланса/ставки во время спина** — проверяй `GameState.isSpinning`
8. **Аллокация объектов в `update()`** — прединициализируй Vector2, Rect, Paint

## ОБЯЗАТЕЛЬНАЯ АРХИТЕКТУРА

```
lib/
├── game/
│   ├── slot_machine_game.dart  # extends FlameGame — только точка входа
│   ├── slot_machine_world.dart # extends World with HasCollisionDetection
│   └── slot_config.dart        # ТОЛЬКО константы, никакой логики
├── systems/
│   ├── weighted_rng.dart       # Random.secure() — ЕДИНСТВЕННЫЙ RNG
│   └── payline_evaluator.dart  # Чистая функция, без состояния
├── models/
│   └── game_state.dart         # sealed class {Idle, Spinning, Evaluating, Win, FreeSpins}
```

## GameState — Обязательный sealed class

```dart
sealed class GameState {}
class IdleState extends GameState {}
class SpinningState extends GameState {
  final List<List<int>> targetSymbols;
  SpinningState(this.targetSymbols);
}
class EvaluatingState extends GameState {}
class WinState extends GameState {
  final int amount;
  final List<int> winLines;
  WinState(this.amount, this.winLines);
}
class FreeSpinsState extends GameState {
  final int remaining;
  FreeSpinsState(this.remaining);
}
```

## RTP Окно
- Целевой RTP: 95–97%
- Если `/balance-check` показывает RTP вне диапазона — игра останавливается
- Только `rtp-mathematician` может менять веса символов
