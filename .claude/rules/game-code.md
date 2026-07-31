---
description: Gambling game Dart/Flame code rules — RNG integrity, stateless outcomes, math-model config, state integrity, forbidden patterns. Unconditional across all six gambling categories.
globs: ["lib/**/*.dart"]
---

# Game Code Rules — гемблинг-игры

## КРИТИЧЕСКИЕ ПРАВИЛА (нарушение = блокировка PR)

> Применяются ко всем шести категориям C1–C6 без исключений.

### GameConfig — единственный источник игровых констант
- ВСЕ игровые константы — в `lib/game/game_config.dart` (или `slot_config.dart` для слотов)
- Ставки, множители, тайминги, лимиты, размеры поля — только из конфига
- Числа математической модели живут в JSON (`design/balance/*.json`) и загружаются в конфиг,
  а не переписываются руками в двух местах
- Нельзя иметь числовые литералы для игровых значений вне конфига

```dart
// ✅ ПРАВИЛЬНО
class GameConfig {
  static const int minBet = 1;
  static const int maxBet = 100;
  static const int startingBalance = 1000;
  static const int bigWinMultiplier = 10;
  static const int maxParticles = 200;
  static const Duration roundAnimation = Duration(milliseconds: 2000);
}

// ❌ ЗАПРЕЩЕНО
if (win > 1000) {          // Откуда взялось 1000?
  triggerParticles(count: 50); // И 50?
}
```

### GameState — sealed class обязателен
- Используй sealed class для всех состояний раунда
- Нет boolean флагов (`isSpinning`, `isPaused`, `isGameOver`)
- Каждое состояние содержит свои данные, включая уже вычисленный исход

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

### Защита основного действия от двойного клика
- Основная кнопка действия (Spin/Play/Start) ОБЯЗАНА быть заблокирована во время выполнения
- Дебаунс минимум 300мс

### Stateless Outcomes (Детерминированные результаты)
- Результат раунда ДОЛЖЕН быть вычислен ДО начала анимации
- Анимация только "проигрывает" предопределённый результат
- Без этого RTP невозможно верифицировать, а cash-out в C2 математически некорректен

## RNG И МАТЕМАТИЧЕСКАЯ ЦЕЛОСТНОСТЬ

> Безусловные правила: применяются ко ВСЕМ категориям C1–C6.

### RNG Безопасность
- **НИКОГДА** не используй `math.Random()` или `Random()` — ТОЛЬКО `Random.secure()`
- **НИКОГДА** не захардкодируй вероятности: `if (rng.nextDouble() < 0.1) win!`
- **ВСЕГДА** читай веса из `GameConfig` или JSON-конфига математической модели
- RNG должен быть инициализирован ОДИН РАЗ в `WeightedRNG`
- **Единственное исключение**: seeded-детерминизм забега в казино-рогаликах (C5, модель M5).
  Там `Random(seed)` обязателен — забег должен воспроизводиться по seed. Исключение
  фиксируется в ADR, иначе `/code-review` трактует его как нарушение.

```dart
// ✅ ПРАВИЛЬНО (GAMBLING)
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

// ❌ ЗАПРЕЩЕНО
final rng = Random(); // Не secure!
if (Random().nextDouble() < 0.15) triggerBonus(); // Захардкоженная вероятность!
```

### Целевое окно математической модели

Окно зависит от категории игры — полная таблица в `.claude/docs/math-models.md`:

| Категория | Модель | Целевое окно |
|-----------|--------|--------------|
| C1 | M1 | RTP 95–97%, hit rate 20–35% |
| C2 | M2 | RTP 96–99%, house edge объявлен, множитель капнут |
| C3 | M3 | source/sink 0.90–1.15, пейс 2–5 сессий на анлок |
| C4 | M4 | base rate 0.5–2%, hard pity 50–90, pity срабатывает 100% |
| C5 | M5 | run win-rate 25–40%, детерминизм по seed |
| C6 | M6 | RTP 95–97%, fixed timestep, воспроизводимость |

- Если `/balance-check` даёт FAIL — производство останавливается.
- Только `game-mathematician` меняет числа модели, и только в JSON-конфиге.
- Смена целевой метрики (RTP, pity, win-rate) требует ADR, а не молчаливой правки.

## ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ

1. **`isPaused = true`** — используй `GameState` sealed class
2. **`BuildContext` в Flame компонентах** — используй колбэки или service locator
3. **`print()` в production коде** — используй `Logger`
4. **`await` в `update()` или `render()`** — эти методы ОБЯЗАНЫ быть синхронными
5. **Аллокация объектов в `update()`** — прединициализируй Vector2, Rect, Paint
6. **`math.Random()` / `Random()`** — только `Random.secure()` (исключение: seeded C5 + ADR)
7. **Захардкоженные игровые параметры** вне GameConfig
8. **Изменение состояния во время анимации** — проверяй GameState
9. **Вычисление исхода внутри анимации** — нарушает Stateless Outcomes и ломает RTP
10. **Дублирование чисел модели** в JSON и в Dart — один источник правды
11. **Символы реальной валюты у игрового баланса** — см. responsible-gaming.md §1

## ОБЯЗАТЕЛЬНАЯ АРХИТЕКТУРА

```
lib/
├── game/
│   ├── [game_name]_game.dart   # extends FlameGame — точка входа
│   ├── [game_name]_world.dart  # extends World with HasCollisionDetection
│   └── game_config.dart        # ТОЛЬКО константы, никакой логики
├── systems/
│   ├── weighted_rng.dart       # Random.secure() — ЕДИНСТВЕННЫЙ источник случайности
│   ├── [outcome]_resolver.dart # Исход раунда, вычисленный ДО анимации
│   └── [evaluator].dart        # Чистая функция оценки результата (без RNG, без состояния)
├── models/
│   └── game_state.dart         # sealed class
```
