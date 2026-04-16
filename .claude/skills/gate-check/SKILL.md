---
name: gate-check
description: "Проверяет готовность проекта к переходу между этапами (concept/design/code/qa/release) и выдает вердикт PASS/CONCERNS/FAIL."
argument-hint: "[concept|design|code|qa|release]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash, Agent
---

# /gate-check [этап]

Запуск: пользователь вызывает `/gate-check [concept|design|code|qa|release]`

## Цель

Проверяет готовность проекта к переходу между этапами разработки.
Выдаёт вердикт: **PASS / CONCERNS / FAIL** с конкретными блокерами.

## Этапы разработки мини-игры

```
Concept → Design → Code → QA → Release
   ↑         ↑       ↑      ↑       ↑
  gate      gate    gate   gate    gate
```

## Ворота по этапам

### gate-check concept → design
Проверяет готовность концепта для перехода к дизайну:

**Обязательные артефакты:**
- [ ] `design/gdd/game-concept.md` существует
- [ ] Elevator pitch (1-2 предложения)
- [ ] Жанр определён (gambling/puzzle/arcade/physics/casual/card)
- [ ] Уникальная механика ("сочность") описана
- [ ] Архетип выбран (A–X)
- [ ] Для gambling: целевой RTP указан (95–97%), волатильность выбрана, хотя бы 3 символа описаны

**Ворота:**
- PASS: все пункты выполнены
- CONCERNS: 1–2 пункта отсутствуют, но некритичны
- FAIL: концепт не задокументирован или RTP не определён

### gate-check design → code
Проверяет готовность дизайна для передачи программисту:

**Обязательные артефакты:**
- [ ] GDD документ с 8 секциями (см. rules/design-docs.md)
- [ ] `design/balance/rtp-config.json` существует и валиден
- [ ] Таблица выплат завершена (все символы × все комбинации)
- [ ] Paylines определены и пронумерованы
- [ ] Wild/Scatter поведение задокументировано (если есть)
- [ ] Free Spins условия описаны (если есть)
- [ ] GDD статус: `Status: Approved`
- [ ] `game-mathematician` подписал математику
- [ ] `design/balance/rtp-config.json` → `simulation.last_run_rtp` в диапазоне 95–97%

### gate-check code → qa
Проверяет готовность кода для QA:

**Критические gambling требования:**
- [ ] `lib/systems/weighted_rng.dart` использует `Random.secure()`
- [ ] Нет `math.Random()` в production коде
- [ ] Нет захардкоженных вероятностей
- [ ] `GameState` — sealed class (не boolean флаги)
- [ ] Результат спина вычислен до анимации
- [ ] Двойной клик Spin заблокирован
- [ ] `lib/game/slot_config.dart` содержит все настраиваемые значения

**Архитектура Flame 1.18.x:**
- [ ] `HasCollisionDetection` на `World` (не `FlameGame`)
- [ ] `CameraComponent(world: world)` — новый API

**Базовые требования кода:**
- [ ] `dart analyze` — 0 ошибок
- [ ] `flutter test` — все тесты зелёные
- [ ] Нет `print()` в production коде

### gate-check qa → release
Проверяет готовность к релизу:

**RTP и математика:**
- [ ] `/balance-check` запущен с 1М+ спинов
- [ ] Simulated RTP в диапазоне 95.0–97.0%
- [ ] Hit rate в диапазоне 20–40%
- [ ] Нет infinite win loop (>1000 Free Spins подряд невозможно)

**Тестовое покрытие:**
- [ ] `weighted_rng` — дистрибуционный тест есть
- [ ] `payline_evaluator` — все комбинации протестированы
- [ ] Edge case: баланс = 0 → спин заблокирован
- [ ] Edge case: двойной клик не запускает 2 спина
- [ ] 100 спинов без state leakage

**UX и визуал:**
- [ ] Win оверлей показывается корректно
- [ ] Анимации барабанов < 3 секунд
- [ ] Партикли не превышают 200 одновременно
- [ ] Нет артефактов после Free Spins

**Сборка:**
- [ ] `flutter build apk --release` — успешно
- [ ] Нет debug ассертов в release

## Формат вывода

```
🔍 Gate Check: [concept|design|code|qa|release]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Выполнено (N/M):
   ✅ rtp-config.json существует и валиден
   ✅ Random.secure() используется

❌ Блокеры (N):
   ❌ GDD отсутствует секция "Edge Cases"
   ❌ Simulated RTP = 94.2% (ниже 95%)

⚠️  Замечания (N):
   ⚠️  Нет теста на двойной клик

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Вердикт: FAIL ← NEEDS WORK ← PASS
         ^^^
Причина: Simulated RTP вне допустимого диапазона.
Следующий шаг: Вызовите game-mathematician для корректировки весов.
```

## Аргументы

- `concept` — ворота концепт→дизайн
- `design` — ворота дизайн→код
- `code` — ворота код→QA
- `qa` — ворота QA→релиз
- `release` — финальные ворота перед деплоем
- Без аргументов — автоопределение текущего этапа
