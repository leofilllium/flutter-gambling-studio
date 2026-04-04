---
name: map-systems
description: "Декомпозиция концепта мини-игры любого жанра на технические системы. Строит граф зависимостей и план реализации для программиста."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
---

# `map-systems` — План сборки игры

Разбирает игру из `design/gdd/game-concept.md` на структурные компоненты для Flame.

## Поведение

Не спрашивайте пользователя. Прочитайте концепт, определите жанр и сгенерируйте `design/gdd/systems-map.md`.

## Шаблон вывода

```markdown
# Карта систем: [Имя Игры]

**Жанр**: [gambling / puzzle / arcade / physics / casual / card]

## 1. Core Logic (Ядро)
- `GameConfig` (Все тюнинги и параметры)
- `GameState` (sealed class: Idle/Playing/Paused/GameOver)
- `[MainLogic]` (основная механика — зависит от жанра)
- `[Evaluator]` (чистая функция оценки результата)

## 2. Flame Components (Представление)
- `[MainComponent]` (основной игровой объект)
- `[ElementComponent]` (элементы игры)
- `WinAnimationComponent` (VFX эффекты)

## 3. Flutter UI (Интерфейс)
- `HudWidget` (основной HUD с ValueNotifiers)
- `ActionButton` (основная кнопка действия)
- `MainMenuScreen` (вход в игру)

## 4. Audio (Звук)
- `AudioService` (play() / loop())

## Порядок разработки (План)
1. Core Logic -> `/design-system [система]`
2. Flame Components -> `/prototype [механика]`
3. Flutter UI (все экраны)
4. Интеграция
5. `/balance-check` + тестирование
```

## Примеры по жанрам

**Gambling (слот)**: WeightedRNG + PaylineEvaluator + ReelComponent
**Puzzle (match-3)**: MatchDetector + CascadeSystem + GridComponent + TileComponent
**Arcade (runner)**: SpawnManager + CollisionHandler + PlayerComponent + ObstacleComponent
**Physics (pinball)**: Forge2DWorld + BallComponent + BumperComponent + FlipperComponent

Обязательно включите в документ `Порядок разработки` и список классов.
