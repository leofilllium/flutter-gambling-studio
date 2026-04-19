# Session State — Flutter Game Studio

<!-- STATUS -->
Epic: Studio Setup
Feature: Infrastructure
Task: Universal multi-genre studio complete
<!-- /STATUS -->

## Статус

Студия настроена и готова к разработке игр любого жанра.

## Новые возможности (добавлены 2026-04-04)

- Студия расширена до универсальной: поддержка 6 жанров (gambling, puzzle, arcade, physics, casual, card/board)
- 24 архетипа мини-игр A–X (было 12, только gambling)
- `/team-dev` — универсальная оркестрация (заменяет устаревший `/team-gambling`)
- Агенты переименованы: `mechanics-programmer`, `game-designer`, `game-mathematician`
- `GameConfig` — единственный источник констант для всех жанров
- Gambling-специфичные правила (RNG, RTP) теперь условные — применяются только к gambling жанру

## Команды студии

```
/start              — Ориентация: с чего начать
/brainstorm         — Концепт любого жанра
/autocreate         — Zero-to-playable без вопросов
/team-dev           — Оркестрация разработки
/balance-check      — RTP (gambling) или difficulty (другие жанры)
/release-checklist  — Финальный контроль качества
```

## Чтобы начать работу

Запусти `/start` или `/brainstorm` для новой игры.
Запусти `/continue-project` если есть незавершённый проект.

Последнее обновление: 2026-04-04

Последнее сжатие: 2026-04-19 23:55
