# Codex Command Registry

Если пользователь пишет slash-команду, Codex обязан трактовать её как вызов соответствующего runbook из `.claude/skills/`.

| Команда | Skill file | Назначение |
|---------|------------|------------|
| `/start` | `.claude/skills/start/SKILL.md` | Онбординг, маршрутизация, выбор следующего шага |
| `/brainstorm` | `.claude/skills/brainstorm/SKILL.md` | Интерактивный концепт мини-игры |
| `/auto-idea` | `.claude/skills/auto-idea/SKILL.md` | Автогенерация идеи из архетипов |
| `/autocreate` | `.claude/skills/autocreate/SKILL.md` | Zero-to-playable конвейер. **АВТОМАТИЧЕСКИ** запускает `/emulator-test --quick` в Фазе 10.5 и `/release-package` в Фазе 10.6 — не оставляет их пользователю. В финальном отчёте эти же команды упоминаются как рекомендации для повторного перезапуска. |
| `/continue-project` | `.claude/skills/continue-project/SKILL.md` | Возобновление работы по текущему состоянию |
| `/map-systems` | `.claude/skills/map-systems/SKILL.md` | Декомпозиция концепта на системы |
| `/design-system` | `.claude/skills/design-system/SKILL.md` | GDD для отдельной механики |
| `/prototype` | `.claude/skills/prototype/SKILL.md` | Быстрый прототип ощущения и juiciness |
| `/generate-asset` | `.claude/skills/generate-asset/SKILL.md` | SVG/PNG ассеты по задаче |
| `/generate-png-asset` | `.claude/skills/generate-png-asset/SKILL.md` | Растровые ассеты через AI pipeline |
| `/svg-to-png` | `.claude/skills/svg-to-png/SKILL.md` | Конвертация SVG в PNG |
| `/design-review` | `.claude/skills/design-review/SKILL.md` | Ревью GDD и полноты спецификации |
| `/code-review` | `.claude/skills/code-review/SKILL.md` | Архитектурное и геймплейное ревью |
| `/ui-audit` | `.claude/skills/ui-audit/SKILL.md` | Anti-slop аудит и UI автоисправления |
| `/emulator-test` | `.claude/skills/emulator-test/SKILL.md` | Runtime-верификация на ADB/эмуляторе с автофиксом. **Default platform: Android** через ADB. Скриншоты снимаются через `flutter screenshot` (Impeller-safe) с fallback на `adb screencap` + валидация PNG-сигнатуры. Флаг `--no-impeller` если кадры невалидны. |
| `/balance-check` | `.claude/skills/balance-check/SKILL.md` | RTP, difficulty curve, scoring balance |
| `/gate-check` | `.claude/skills/gate-check/SKILL.md` | Quality gate для стадии проекта |
| `/perf-profile` | `.claude/skills/perf-profile/SKILL.md` | FPS, память, particles, audio |
| `/tech-debt` | `.claude/skills/tech-debt/SKILL.md` | Реестр технического долга |
| `/hotfix` | `.claude/skills/hotfix/SKILL.md` | Срочное исправление критической проблемы |
| `/architecture-decision` | `.claude/skills/architecture-decision/SKILL.md` | ADR и архитектурный выбор |
| `/team-dev` | `.claude/skills/team-dev/SKILL.md` | Оркестрация мультидисциплинарной команды |
| `/team-gambling` | `.claude/skills/team-gambling/SKILL.md` | Оркестрация команды для gambling жанра |
| `/add-feature` | `.claude/skills/add-feature/SKILL.md` | Добавление новой фичи в существующую игру |
| `/release-checklist` | `.claude/skills/release-checklist/SKILL.md` | Финальный GO/NO-GO чеклист перед релизом (делегирует release-manager агенту) |
| `/release-package` | `.claude/skills/release-package/SKILL.md` | Финальная упаковка релиза: скриншоты всех экранов через ADB/simctl, `flutter build apk --release` (+ AAB + split-per-abi), `flutter clean`, архивация всего проекта со скринами и APK в `project_zip/<name>-<ts>.zip` с SHA256. Автоматически запускается из `/autocreate` Фаза 10.6. |

## Правило исполнения

1. Открыть указанный `SKILL.md`.
2. Выполнить шаги в порядке, указанном в skill.
3. Если skill требует нескольких ролей, использовать роли из `.claude/agents/*.md` и таблицы в `agents.md`.
4. Если Claude-specific шаг не поддерживается нативно в Codex, использовать ближайший эквивалент:
   - Claude agent → sub-agent Codex или локальная persona
   - Claude hook → `bash tools/codex-hooks.sh ...`
   - Slash routing → ручное выполнение по этому реестру
