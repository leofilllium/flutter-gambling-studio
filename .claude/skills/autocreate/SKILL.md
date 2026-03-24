---
name: autocreate
description: "Фабрика производства гемблинг-игр Zero-to-Playable. Создает концепт, рисует SVG ассеты, пишет код на Flutter/Flame 1.18.x, настраивает pubspec.yaml и проверяет работоспособность. Всё автономно."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Playable Gambling Game Factory

Выполняет полный цикл разработки мини-игр без участия пользователя.
**ЗАПРЕЩАЕТСЯ задавать вопросы (кроме критических багов).**

## Фаза 1 — Идея (Auto-Concept)
Вызов логики `/auto-idea` для генерации концепции (пропустить если `--from-concept`).
Сохранение в `design/gdd/gambling-concept.md`.

## Фаза 2 — Flutter Project Bootstrap
`flutter create . --project-name gambling_app --platforms android,ios,web`
Обновление `pubspec.yaml`:
```yaml
dependencies:
  flame: ^1.18.0
  flame_audio: ^2.1.0
  flame_svg: ^1.10.0
```

## Фаза 3 — Asset Planner & Generation
Автоматическая генерация простых SVG (в основном плоские объекты, символы) 
в `assets/images/sprites/`, `assets/images/ui/`.
В гемблинге минимальный набор символов (Вишня, Лимон, Семёрка и т.д.)
Важно сгенерировать Particle-референсы для эффектов выигрыша.

## Фаза 4 — Parallel Game Implementation
Запуск ДВУХ агентов ПАРАЛЛЕЛЬНО для написания Dart кода:

**Agent A (slot-programmer):**
- WeightedRng система (строго `Random.secure()`)
- Механика вращения (ReelComponent)
- FlameWorld и HasCollisionDetection
- Обработка выигрышных линий

**Agent B (ui-programmer):**
- Flutter HUD через ValueNotifiers
- Панель ставок: Bet+, Bet-, Max Bet
- BalanceCounter
- Оверлеи Win / Mega Win

## Фаза 5 — Сборка кода
Создать `lib/assets.dart` с типизированными SVG константами.
Обновить все пути в `pubspec.yaml`.

## Фаза 6 — Верификация
Выполнить:
`flutter pub get`
`dart analyze lib/`
Исправить ошибки компиляции (до 5 попыток).

Вывести отчет `AUTOCREATE COMPLETE` с рекомендацией запустить `flutter run`.
