# Codex Command Registry

Если пользователь пишет slash-команду (`$name` или `/name`), Codex обязан трактовать её как
вызов соответствующего runbook из `.claude/skills/`. Адаптация Claude-механик (Agent tool,
Skill tool, hooks, vision, image generation) — см. `AGENTS.md` → «Execution Model».

## Конвейер производства игры

| Команда | Skill file | Назначение |
|---------|------------|------------|
| `/start` | `.claude/skills/start/SKILL.md` | Онбординг, маршрутизация, выбор следующего шага |
| `/brainstorm` | `.claude/skills/brainstorm/SKILL.md` | Интерактивный концепт мини-игры |
| `/auto-idea` | `.claude/skills/auto-idea/SKILL.md` | Автогенерация идеи из 30+ архетипов A–AF (вкл. Reference Bar, Design DNA, Production Plan) |
| `/autocreate` | `.claude/skills/autocreate/SKILL.md` | **Zero-to-Production конвейер.** В Codex три «сессии» выполняются как три чекпоинта ОДНОЙ сессии: Фазы 1–3.8 → handoff-1 → `autocreate-implement` (Фазы 4–10.7) → handoff → `autocreate-finalize` (Фазы 10.5–12). «5 параллельных агентов» Фазы 4 = последовательные persona-проходы A→E→D→B→C. Ассеты — PNG через GPT Images 2.0 → GPT Images/default fallback; простые ассеты на белом фоне + rembg |
| `/autocreate-implement` | `.claude/skills/autocreate-implement/SKILL.md` | Сессия 2 (имплементация, Фазы 4–10.7) — также ручной перезапуск после сбоя (`--resume`) |
| `/autocreate-finalize` | `.claude/skills/autocreate-finalize/SKILL.md` | Сессия 3 (runtime+soak, playtest, release-eng PREP, отчёт) — также ручной перезапуск |
| `/continue-project` | `.claude/skills/continue-project/SKILL.md` | Возобновление работы по текущему состоянию |
| `/map-systems` | `.claude/skills/map-systems/SKILL.md` | Декомпозиция концепта на системы |
| `/design-system` | `.claude/skills/design-system/SKILL.md` | GDD для отдельной механики |
| `/prototype` | `.claude/skills/prototype/SKILL.md` | Быстрый прототип ощущения и juiciness |
| `/team-dev` | `.claude/skills/team-dev/SKILL.md` | Оркестрация мультидисциплинарной команды (в Codex — последовательные persona-проходы) |
| `/add-feature` | `.claude/skills/add-feature/SKILL.md` | Добавление новой фичи в существующую игру |

## Ассеты

| Команда | Skill file | Назначение |
|---------|------------|------------|
| `/generate-asset` | `.claude/skills/generate-asset/SKILL.md` | SVG по умолчанию; PNG только по явному запросу |
| `/generate-png-asset` | `.claude/skills/generate-png-asset/SKILL.md` | В Codex растровые ассеты через GPT Images 2.0 → GPT Images/default fallback; белый фон + rembg для простых ассетов |
| `/svg-to-png` | `.claude/skills/svg-to-png/SKILL.md` | В Codex конвертация SVG в PNG через GPT Images 2.0 → GPT Images/default fallback |
| `/asset-review` | `.claude/skills/asset-review/SKILL.md` | **Vision-ревью набора ассетов** (контактные листы, критерии AR1–AR10, перегенерация бракованных). Фаза 3.6 в `/autocreate` |

## Качество и верификация

| Команда | Skill file | Назначение |
|---------|------------|------------|
| `/gate-check` | `.claude/skills/gate-check/SKILL.md` | Quality gate для стадии проекта |
| `/design-review` | `.claude/skills/design-review/SKILL.md` | Ревью GDD и полноты спецификации |
| `/code-review` | `.claude/skills/code-review/SKILL.md` | Архитектурное и геймплейное ревью |
| `/ui-audit` | `.claude/skills/ui-audit/SKILL.md` | Anti-slop аудит (100+ проверок) + автофикс; меряет по `.claude/docs/quality-bar.md` |
| `/emulator-test` | `.claude/skills/emulator-test/SKILL.md` | Runtime-верификация. **Default platform: Chrome/Web** (headless, `tools/web_verify.mjs`, без эмулятора). Android ADB — только явный fallback `--platform android` |
| `/playtest` | `.claude/skills/playtest/SKILL.md` | **Глубокая игровая верификация**: реально играет через CDP, проверки P1–P10 (числа меняются, win/lose пути, живое поле, прогрессия, утечки). Фаза 10.6 в finalize |
| `/balance-check` | `.claude/skills/balance-check/SKILL.md` | RTP, difficulty curve, full-curve валидация контента |
| `/perf-profile` | `.claude/skills/perf-profile/SKILL.md` | FPS, память, particles, audio |
| `/tech-debt` | `.claude/skills/tech-debt/SKILL.md` | Реестр технического долга |
| `/hotfix` | `.claude/skills/hotfix/SKILL.md` | Срочное исправление критической проблемы |
| `/architecture-decision` | `.claude/skills/architecture-decision/SKILL.md` | ADR и архитектурный выбор |

## Релиз

| Команда | Skill file | Назначение |
|---------|------------|------------|
| `/release-checklist` | `.claude/skills/release-checklist/SKILL.md` | GO/NO-GO чеклист (persona release-manager; учитывает playtest и asset-review вердикты) |
| `/release-engineering` | `.claude/skills/release-engineering/SKILL.md` | Иконки/splash/версия/signed AAB/store-metadata/CI. В конвейере — только `--prep-only --no-keystore` |
| `/release-package` | `.claude/skills/release-package/SKILL.md` | Скриншоты + release APK/AAB + `flutter clean` + архив в `project_zip/`. **Явный запуск пользователя**, НЕ авто-вызов из конвейера |
| `/store-screenshots` | `.claude/skills/store-screenshots/SKILL.md` | Маркетинговые скрины (фоны через GPT Images 2.0, композитинг ImageMagick) → `project_zip/` |

## Устаревшее

| Команда | Замена |
|---------|--------|
| `/team-gambling` | `/team-dev` |

## Правило исполнения

1. Открыть указанный `SKILL.md`.
2. Выполнить шаги в порядке, указанном в skill, соблюдая критерии выхода фаз.
3. Если skill требует нескольких ролей — использовать persona-проходы по `.claude/agents/*.md`
   (см. `agents.md`).
4. Claude-specific шаг → ближайший эквивалент по таблице Execution Model в `AGENTS.md`:
   - Claude Agent tool → инлайн persona-проход / продолжение в этой же сессии
   - Claude Skill tool → открыть SKILL.md как runbook
   - Claude hook → `bash tools/codex-hooks.sh ...`
   - Vision-анализ → встроенный vision Codex; PNG-генерация → GPT Images 2.0, затем GPT Images/default fallback при сбое
