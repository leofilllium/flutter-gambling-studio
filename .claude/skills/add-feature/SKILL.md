---
name: add-feature
description: "Добавление новой фичи в готовую мини-игру любого жанра. Gambling: Wild символы, Free Spins, джекпот. Puzzle: новый тип тайлов, бустер. Arcade: пауэрап, новый тип врага."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<название-фичи>"
---

# `add-feature` — Добавление фичи

Правильное добавление новой механики в готовую игру.

## Инструкция

1. Прочитайте `design/gdd/game-concept.md` чтобы понять жанр и текущую архитектуру.

2. Спросите пользователя:
   - Как работает фича?
   - Как часто она должна появляться/срабатывать?
   - Насколько она влияет на баланс (выигрыш / сложность)?

3. **Для gambling-фич**:
   - Внесите изменения в `design/balance/rtp-config.json`.
   - Запустите `game-mathematician` для пересчёта RTP (целевой: 95–97%).
   - Запустите `/balance-check` для подтверждения.
   - Вызовите `mechanics-programmer` для реализации в `PaylineEvaluator`.

4. **Для puzzle-фич**:
   - Обновите `design/balance/level-config.json`.
   - Запустите `game-mathematician` для проверки difficulty curve.
   - Вызовите `mechanics-programmer` для реализации логики.

5. **Для arcade-фич**:
   - Обновите `design/balance/difficulty-curve.json`.
   - Вызовите `mechanics-programmer` для реализации SpawnManager/PowerupSystem.

6. Создайте Issue в `production/session-state/` и вызовите `/team-dev` для полной реализации.

7. После кода — `/balance-check` для проверки, `/code-review` для ревью.
