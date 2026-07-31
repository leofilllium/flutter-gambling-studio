---
name: map-systems
description: "Декомпозиция концепта гемблинг-игры на технические системы. Строит граф зависимостей и план реализации для программиста, отталкиваясь от категории C1-C6 и математической модели M1-M6."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
---

# `map-systems` — План сборки игры

Разбирает игру из `design/gdd/game-concept.md` на структурные компоненты для Flame.

## Поведение

Не спрашивайте пользователя. Прочитайте концепт (блок **Классификация**), определите
категорию и математическую модель, сгенерируйте `design/gdd/systems-map.md`.

## Шаблон вывода

```markdown
# Карта систем: [Имя Игры]

**Категория**: [C1-C6] — [название]
**Архетип**: [A-AF]
**Математическая модель**: [M1-M6] → `design/balance/[файл].json`

## 1. Core Logic (Ядро)
- `GameConfig` (все тюнинги; числа модели загружаются из JSON, не дублируются)
- `GameState` (sealed class: Idle / Resolving / Revealing / Win / OutOfFunds / Paused)
- `WeightedRNG` (`Random.secure()` — ЕДИНСТВЕННЫЙ источник случайности)
- `[Outcome]Resolver` (исход раунда вычисляется ДО анимации — Stateless Outcomes)
- `[Evaluator]` (чистая функция оценки: без RNG, без состояния)

## 2. Flame Components (Представление)
- `[MainComponent]` (барабан / стол / поле мин / кривая / поле pegs)
- `[ElementComponent]` (символы, карты, фишки, шары, капсулы)
- `WinAnimationComponent` (VFX, масштабированные по значимости выигрыша)
- `AmbientParticles` (живое поле — экран никогда не статичен)

## 3. Flutter UI (Интерфейс)
- `HudWidget` (баланс/ставка/множитель через ValueNotifier)
- `BetPanel` (выбор ставки, заблокирован во время раунда)
- `ActionButton` (дебаунс 300 мс + disabled state + press-анимация)
- `MainMenuScreen`, `PaytableScreen`, все экраны MVP

## 4. Compliance (обязательный слой)
- `AgeGateScreen` (один раз до меню, результат в SharedPreferences)
- `ComplianceCopy` (дисклеймер, responsible-play, контакты — константы в одном месте)
- `OddsScreen` (обязателен для C4 и платных спинов C3)

## 5. Meta & Audio
- `SaveService`, `EconomyService`, `ProgressionService`, `AchievementService`
- `AudioService` (max 3 параллельных звука)

## Порядок разработки (План)
1. Математическая модель → `/design-system [система]` → `/balance-check`
2. Core Logic (RNG + Resolver + Evaluator) → `/design-system`
3. Flame Components → `/prototype [механика]`
4. Flutter UI (все экраны) + compliance-слой
5. Мета-системы и контент
6. Интеграция → `/balance-check` → `/ui-audit` → тестирование
```

## Ключевые системы по категориям

| Категория | Ядро механики |
|-----------|---------------|
| **C1** 🎰 слот | `WeightedRNG` + `PaylineEvaluator` + `ReelComponent` + `SymbolComponent` |
| **C1** 🎰 стол | `WeightedRNG` + `HandEvaluator`/`WheelResolver` + `CardComponent`/`WheelComponent` |
| **C2** ⚡ | `RoundResolver` (seed+nonce) + `MultiplierCurve` + `CashoutController` + `RoundHistory` |
| **C3** 🏰 | `SpinEventTable` + `EnergyService` + `MetaProgressService` + `RaidResolver` |
| **C4** 🎁 | `BannerResolver` + `PityCounter` (персистентный!) + `DuplicateConverter` + `PullReveal` |
| **C5** 🃏 | `RunRng(seed)` + `HandEvaluator` + `ModifierRegistry` + `ShopController` + `RunState` |
| **C6** ⚙️ | `PhysicsWorld` (fixed timestep) + `LaunchResolver` + `BucketDetector` + `BodyLimiter` |

Обязательно включите в документ `Порядок разработки` и список классов.
