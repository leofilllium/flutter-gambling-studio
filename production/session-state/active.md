# Session State — Flutter Gambling Studio

<!-- STATUS -->
Epic: Studio Setup
Feature: Infrastructure
Task: Gambling-only studio refocus complete
<!-- /STATUS -->

## Статус

Студия настроена и готова к разработке гемблинг-игр. Универсальная мульти-жанровая
конфигурация свёрнута: пазлы, раннеры, шутеры и кликеры больше не поддерживаются.

## Изменения (2026-07-31) — переход на гемблинг-специализацию

- **Шесть категорий вместо шести жанров**: C1 Social Casino · C2 Casino Originals ·
  C3 Spin-to-Progress · C4 Gacha & Loot-Box · C5 Casino Roguelike · C6 Coin Pusher & Plinko.
  Канонический справочник — `.claude/docs/gambling-categories.md`
- **32 архетипа A–AF**, все гемблинг (было 32 смешанных, из них 20 не-гемблинг)
- **Шесть математических моделей M1–M6** с проверяемыми порогами —
  `.claude/docs/math-models.md`
- **`tools/simulate_math.py`** — единый верификатор всех шести моделей
  (заменил `tools/simulate_rtp.py`, который был описан в документации, но не существовал).
  Точный расчёт там, где пространство исходов перечислимо; Monte Carlo — только для
  путезависимых моделей. Exit code: 0 = PASS, 1 = CONCERNS, 2 = FAIL
- **Эталонные конфиги** всех шести моделей — `.claude/docs/templates/math-configs/`,
  каждый проходит прогон «из коробки» (`python3 tools/simulate_math.py --selftest`)
- **`.claude/rules/responsible-gaming.md`** — compliance-слой стал release-блокером:
  age-gate, дисклеймер, responsible-play, раскрытие шансов, запрет символов реальной валюты
- **Правила RNG/Stateless Outcomes теперь безусловны** — были условными «только для gambling
  жанра». Единственное исключение: seeded-детерминизм забега в C5 (требует ADR)
- **Блок «Классификация»** обязателен в каждом концепте: категория, архетип, модель,
  целевая метрика, конфиг, compliance-профиль. Без него `/gate-check concept` даёт FAIL
- Все 32 навыка, 14 агентов и зеркальные слои (Codex / Gemini / Copilot / Cursor)
  переведены на гемблинг-таксономию

## Команды студии

```
/start              — Ориентация: с чего начать
/brainstorm         — Концепт гемблинг-игры (выбор категории C1–C6)
/auto-idea          — Автономный концепт из 32 архетипов A–AF
/autocreate         — Zero-to-playable без вопросов
/team-dev           — Оркестрация разработки
/balance-check      — Верификация матмодели M1–M6
/release-checklist  — Финальный контроль качества + compliance
```

## Чтобы начать работу

Запусти `/start` или `/brainstorm` для новой игры.
Запусти `/continue-project` если есть незавершённый проект.

Последнее обновление: 2026-07-31
