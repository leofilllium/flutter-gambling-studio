---
name: team-dev
description: "Оркеструет разработку механик мини-игры любого жанра с участием нескольких специалистов. Координирует геймдизайнера, программиста механик, художника VFX и звукового дизайнера."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Agent
argument-hint: "<описание фичи/системы> (например: 'Анимация победы в match-3' или 'Механика spawn врагов' или 'Каскадные барабаны с Free Spins')"
---

# `team-dev` — Оркестрация Студии

Запускает агентов в правильном порядке для реализации сложной фичи любого жанра.

## Инструкция

1. Уточните задачу у пользователя: какая фича, жанр игры, есть ли готовый GDD?

2. Если GDD нет — вызовите `game-designer` для его написания.
   - Для gambling: `game-designer` консультируется с `game-mathematician` по математике
   - Для других жанров: `game-mathematician` помогает с balance/difficulty curves

3. Если нужна математика или балансировка:
   - **Gambling**: `game-mathematician` (RTP, веса символов)
   - **Puzzle**: `game-mathematician` (difficulty curve, scoring)
   - **Arcade**: `game-mathematician` (spawn rates, difficulty scaling)

4. Для реализации вызовите `mechanics-programmer` (Core Logic) и `juice-artist` (VFX анимации) в нужном порядке. Обязательно передайте им ссылки на GDD.

5. При необходимости подключите `sound-designer` для аудио-событий.

6. Предложите пользователю проверить результат когда всё готово.
