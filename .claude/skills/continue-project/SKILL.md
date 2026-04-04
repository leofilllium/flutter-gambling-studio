---
name: continue-project
description: "Анализирует текущее состояние проекта и предлагает следующие логические шаги разработки. Запускайте при возвращении к работе над игрой."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: ""
---

# `continue-project` — Вход в проект

Автоматически восстанавливает контекст разработки и направляет в нужную стадию.

## Алгоритм

1. Прочитайте `design/gdd/game-concept.md` (если есть).
2. Прочитайте `pubspec.yaml` (если есть).
3. Прочитайте `production/session-state/active.md` (если есть).
4. Определите стадию проекта:
   - **Нет ничего**: предложите `/start` или `/brainstorm`
   - **Есть только GDD**: предложите `/design-system rtp-weights` или `/generate-asset symbols`
   - **Есть Flutter проект, но нет логики слота**: предложите вызов `mechanics-programmer`
   - **Есть готовый слот без звука/VFX**: предложите `juice-artist` и `sound-designer`
   - **Проект выглядит готовым**: предложите `/release-checklist`

5. Выведите статус красивым блоком с 3-мя рекомендованными командами для продолжения.
