---
description: Game-specific Dart/Flame code rules — state integrity, config management, forbidden patterns. Includes gambling-specific RNG rules when applicable.
globs: ["lib/**/*.dart"]
---

# Game Code Rules

## КРИТИЧЕСКИЕ ПРАВИЛА ДЛЯ ВСЕХ ЖАНРОВ (нарушение = блокировка PR)

### GameConfig — единственный источник игровых констант
- ВСЕ игровые константы — в `lib/game/game_config.dart` (или `slot_config.dart` для gambling)
- Множители, скорости, размеры сетки, тайминги — только из конфига
- Нельзя иметь числовые литералы для игровых значений вне конфига

```dart
// ✅ ПРАВИЛЬНО
class GameConfig {
  static const int gridWidth = 8;
  static const int gridHeight = 8;
  static const double playerSpeed = 200.0;
  static const int maxLives = 3;
  static const Duration comboTimeout = Duration(seconds: 2);
}

// ❌ ЗАПРЕЩЕНО
if (score > 1000) { // Откуда взялось 1000?
  triggerParticles(count: 50); // И 50?
}
```

### GameState — sealed class обязателен
- Используй sealed class для всех состояний игры
- Нет boolean флагов (`isPlaying`, `isPaused`, `isGameOver`)
- Каждое состояние содержит свои данные

```dart
sealed class GameState {}
class IdleState extends GameState {}
class PlayingState extends GameState { final LevelData level; }
class PausedState extends GameState { final GameState previousState; }
class GameOverState extends GameState { final int score; }
class VictoryState extends GameState { final int score; final int stars; }
```

### Защита основного действия от двойного клика
- Основная кнопка действия (Spin/Play/Start) ОБЯЗАНА быть заблокирована во время выполнения
- Дебаунс минимум 300мс

### Stateless Outcomes (Детерминированные результаты)
- Результат действия ДОЛЖЕН быть вычислен ДО начала анимации
- Анимация только "проигрывает" предопределённый результат
- Это важно для gambling (спин), но полезно для всех жанров (match-3 каскады, и т.д.)

## ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА ДЛЯ GAMBLING ЖАНРА

> Эти правила применяются только если игра относится к жанру gambling (слоты, рулетка, карты, crash, dice)

### RNG Безопасность
- **НИКОГДА** не используй `math.Random()` или `Random()` — ТОЛЬКО `Random.secure()`
- **НИКОГДА** не захардкодируй вероятности: `if (rng.nextDouble() < 0.1) win!`
- **ВСЕГДА** читай веса из `GameConfig` или `rtp-config.json`
- RNG должен быть инициализирован ОДИН РАЗ в `WeightedRNG`

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

// ❌ ЗАПРЕЩЕНО (GAMBLING)
final rng = Random(); // Не secure!
if (Random().nextDouble() < 0.15) triggerBonus(); // Захардкоженная вероятность!
```

### RTP Окно (только gambling)
- Целевой RTP: 95–97%
- Если `/balance-check` показывает RTP вне диапазона — игра останавливается
- Только `game-mathematician` может менять веса символов

## ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ (ВСЕ ЖАНРЫ)

1. **`isPaused = true`** — используй `GameState` sealed class
2. **`BuildContext` в Flame компонентах** — используй колбэки или service locator
3. **`print()` в production коде** — используй `Logger`
4. **`await` в `update()` или `render()`** — эти методы ОБЯЗАНЫ быть синхронными
5. **Аллокация объектов в `update()`** — прединициализируй Vector2, Rect, Paint
6. **`math.Random()` в gambling коде** — только `Random.secure()`
7. **Захардкоженные игровые параметры** вне GameConfig
8. **Изменение состояния во время анимации** — проверяй GameState

## ОБЯЗАТЕЛЬНАЯ АРХИТЕКТУРА

```
lib/
├── game/
│   ├── [game_name]_game.dart   # extends FlameGame — точка входа
│   ├── [game_name]_world.dart  # extends World with HasCollisionDetection
│   └── game_config.dart        # ТОЛЬКО константы, никакой логики
├── systems/
│   ├── [game_logic].dart       # Основная логика (RNG для gambling, match detector для puzzle, и т.д.)
│   └── [evaluator].dart        # Чистая функция оценки результата
├── models/
│   └── game_state.dart         # sealed class
```
