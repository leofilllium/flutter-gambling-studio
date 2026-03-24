---
name: map-systems
description: "Декомпозиция концепта слота/карт на технические системы. Строит граф зависимостей и план реализации для программиста."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
---

# `map-systems` — План сборки игры

Разбирает игру из `design/gdd/gambling-concept.md` на структурные компоненты для Flame.

## Поведение

Не спрашивайте пользователя. Прочитайте концепт и сгенерируйте `design/gdd/systems-map.md`.

## Типичная структура слота (Пример вывода)

```markdown
# Карта систем: [Имя Игры]

## 1. Core Logic (Ядро)
- `WeightedRng` (Генератор шансов)
- `SlotConfig` (Все тюнинги и RTP)
- `GameState` (ValueNotifiers баланса/ставки)
- `PaylineEvaluator` (Поиск выигрышных линий)

## 2. Flame Components (Представление)
- `ReelComponent` (Вращающийся барабан)
- `SymbolComponent` (Объект с графикой)
- `WinAnimationComponent` (Particle-система выигрышей)

## 3. Flutter UI (Интерфейс)
- `HudWidget` (Нижняя панель с кнопкой Spin)
- `BetSelector` (+ / - ставка)
- `MainMenuScreen` (Вход в игру)

## 4. Audio (Звук)
- `AudioService` (play() / loop())

## Порядок разработки (План)
1. Core Logic (RNG + Config) -> `/design-system rtp-weights`
2. Flame Components -> `/prototype spin-feel`
3. Flutter UI
4. Соединение (Integration)
5. `/balance-check` + Поиск багов
```

Обязательно включите в документ `Порядок разработки` и список классов.
