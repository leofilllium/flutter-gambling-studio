---
name: design-system
description: "Проектирование отдельной игровой механики для любого жанра. Gambling: веса символов, барабаны, выплаты, бонусы. Puzzle: уровни, scoring. Arcade: spawn, difficulty. Генерирует GDD документ с участием game-mathematician и game-designer."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: "<название-системы> (например: rtp-weights, free-spins, match-cascade, spawn-system)"
---

# `design-system` — Детализация игровых систем

Интерактивно проектирует одну систему мини-игры любого жанра.

## Рабочий процесс

1. **Контекст**: Прочитайте `design/gdd/game-concept.md` (или `gambling-concept.md`)
2. **Тип системы**: Определите жанр и о какой системе идет речь:

   **Gambling**:
   - **Математика/Веса**: `game-mathematician` (RTP, Payload, Weights)
   - **Механика/Бонусы**: `game-designer` (Scatter, Free Spins, Bonus Round)
   - **Audio/VFX**: `juice-artist` / `sound-designer` (Near Miss, Cascade)

   **Puzzle**:
   - **Уровни/Сложность**: `game-mathematician` (difficulty curve, move targets)
   - **Механики**: `game-designer` (special tiles, cascades, boosters)

   **Arcade**:
   - **Spawning/Difficulty**: `game-mathematician` (spawn rates, scaling)
   - **Gameplay**: `game-designer` (powerups, wave patterns)

3. **Интерактив (Вопросы)**:
   Для gambling "rtp-weights":
   - Спрашиваем список базовых символов.
   - Спрашиваем желаемый множитель для самого редкого (x100? x1000?).
   - Спрашиваем распределение "пустых" спинов (частота проигрышей около 70-80%).

   Для puzzle "match-cascade":
   - Спрашиваем размер сетки.
   - Спрашиваем количество типов тайлов.
   - Спрашиваем правила каскада (гравитация, случайное заполнение).

4. **Генерация черновика**:
   Запишите в `design/gdd/[system-name].md`.
   Обязательные поля:
   - *Balance Impact* (как влияет на общую математику/сложность)
   - *Visual Feedback* (какой фидбек у игрока на срабатывание)
   - *Edge Cases* (граничные ситуации)

5. **Дальнейшие шаги**:
   - `/balance-check` (если меняли веса/сложность)
   - Вызвать `/team-dev` для программирования этой системы
