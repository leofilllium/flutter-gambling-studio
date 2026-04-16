---
name: code-review
description: "Комплексное ревью кода мини-игры: архитектура, game integrity, Flame API, тесты и риски."
argument-hint: "[путь или область]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /code-review

Запуск: пользователь вызывает `/code-review [путь или область]`

## Цель

Комплексное ревью кода мини-игры. Проверяет:
- Gambling-специфичные критические требования (RNG, State integrity)
- Архитектуру Flame 1.18.x (правильное использование API)
- Качество кода (паттерны, читаемость, тесты)
- Безопасность (нет math.Random, нет захардкоженных вероятностей)
- Производительность (нет аллокаций в update/render)

## Агенты

- `lead-programmer` — архитектура, паттерны, Dart качество
- `mechanics-programmer` — gambling логика, RNG безопасность, Flame API
- `qa-tester` — покрытие тестами, edge cases

## Порядок выполнения

### Шаг 1: Определить область ревью

Если передан путь (например `lib/systems/weighted_rng.dart`) — ревью этого файла.
Если не передан — ревью всей директории `lib/`.

### Шаг 2: lead-programmer — Архитектурное ревью

Агент `lead-programmer` проверяет:

**Структура проекта:**
- [ ] `lib/game/slot_config.dart` существует и содержит ТОЛЬКО константы
- [ ] `lib/systems/weighted_rng.dart` использует `Random.secure()`
- [ ] `lib/models/game_state.dart` содержит sealed class
- [ ] Нет бизнес-логики в `screens/` (только UI)
- [ ] Нет `BuildContext` в Flame компонентах

**Паттерны Dart:**
- [ ] Нет `dynamic` вне JSON-границ
- [ ] Нет `print()` в production коде
- [ ] Нет `await` в `update()` / `render()`
- [ ] Используется `final` где возможно
- [ ] Нет магических чисел вне SlotConfig

**Flame 1.18.x API:**
- [ ] `HasCollisionDetection` на `World`, не на `FlameGame`
- [ ] `CameraComponent(world: world)` — новый API
- [ ] Нет `isPaused = true` — используется `GameState`
- [ ] Прединициализированные Vector2/Rect/Paint в `update()`

### Шаг 3: mechanics-programmer — Game Integrity

Агент `mechanics-programmer` проверяет:

**КРИТИЧЕСКИЕ gambling требования:**
- [ ] `Random.secure()` — единственный источник случайности
- [ ] Нет захардкоженных вероятностей (`if (rng.nextDouble() < 0.1)`)
- [ ] Результат спина вычислен ДО начала анимации (Stateless Outcomes)
- [ ] Двойной клик Spin заблокирован во время спина
- [ ] Баланс обновляется только ПОСЛЕ завершения спина и подтверждения результата
- [ ] Нет State Leakage между спинами

**RTP и математика:**
- [ ] Веса символов читаются из `SlotConfig` / `rtp-config.json`
- [ ] Метод `PaylineEvaluator.evaluate()` — чистая функция без состояния
- [ ] Wild символ заменяет только нужные символы
- [ ] Scatter не привязан к payline

**Free Spins / Бонусы (если есть):**
- [ ] Счётчик Free Spins не может стать отрицательным
- [ ] Мультипликатор применяется корректно
- [ ] Повторный триггер Free Spins обрабатывается

### Шаг 4: qa-tester — Покрытие тестами

Агент `qa-tester` проверяет:

**Наличие тестов:**
- [ ] `test/systems/weighted_rng_test.dart` — дистрибуционный тест
- [ ] `test/systems/payline_evaluator_test.dart` — все комбинации
- [ ] Тест: недостаточный баланс блокирует спин
- [ ] Тест: двойной клик не запускает два спина
- [ ] Тест: GameState возвращается в Idle после спина
- [ ] Тест: баланс корректен после N спинов

**Качество тестов:**
- [ ] Используется `Random.secure()` или seed-based mock, не `Random()`
- [ ] Нет пустых тестов без assertions
- [ ] Следование AAA (Arrange-Act-Assert)

### Шаг 5: Формирование отчёта

Создать файл `docs/review-YYYY-MM-DD.md` со структурой:

```markdown
# Code Review — [Дата]
## Область: [путь или "весь проект"]

## 🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (блокируют релиз)
- Список критических находок

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ (требуют исправления)
- Список важных проблем

## 💡 РЕКОМЕНДАЦИИ (улучшения)
- Список рекомендаций

## ✅ ХОРОШО СДЕЛАНО
- Список того, что сделано правильно

## Итог
- Статус: APPROVED / NEEDS WORK / BLOCKED
- Следующие шаги: [список действий]
```

## Аргументы

- Без аргументов: полное ревью `lib/`
- `lib/systems/` — ревью только systems
- `lib/game/` — ревью game layer
- `--quick` — только gambling-критические проверки (без архитектуры)
- `--rng` — только RNG безопасность

## Инструменты

```
Read, Glob, Grep, Bash(grep*), Bash(dart analyze*)
```

## Пример вывода

```
🔍 Начинаю code review мини-игры...

📋 Проверяю RNG безопасность...
   ✅ Random.secure() используется в weighted_rng.dart
   🚨 math.Random() найден в lib/components/test_helper.dart:42

📋 Проверяю Stateless Outcomes...
   ✅ Результат спина вычисляется до анимации

📋 Проверяю SlotConfig...
   ⚠️  Найдены магические числа в reel_component.dart:78: `if (multiplier > 20)`
   → Перенести в SlotConfig.bigWinMultiplier

📋 Проверяю тестовое покрытие...
   ❌ Отсутствует тест: двойной клик Spin

Итог: NEEDS WORK (1 критическая, 2 важных, 0 блокирующих)
Отчёт сохранён: docs/review-2026-03-24.md
```
