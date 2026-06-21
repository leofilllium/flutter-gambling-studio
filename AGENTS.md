# Flutter Game Studio — Инструкции для OpenAI Codex

> Это главный entrypoint для **OpenAI Codex CLI** в этом репозитории. Codex читает этот файл
> автоматически. Канонический источник правил — `CLAUDE.md` + `.claude/` (rules/docs/skills/
> agents); этот файл НЕ дублирует их, а говорит, КАК их исполнять в Codex.

## Что это за репозиторий

Универсальная агентная студия для создания **полных, публикуемых мини-игр** (гемблинг, пазлы,
аркады, физика, казуальные, карточные) на **Flutter 3.27+ / Flame 1.18+**. Главный конвейер —
`/autocreate`: Zero-to-Production игра за один запуск (концепт → ассеты → аудио → код →
тесты → аудиты → playtest → release-ready).

## Язык

**Всё общение с пользователем — на русском.** На английском: код Dart, пути, имена классов, CLI.

## Порядок чтения при старте сессии

1. Этот файл (вы уже здесь).
2. `CLAUDE.md` — стек, жанры, команды, критические правила game integrity.
3. По мере необходимости: `.claude/rules/*` (game-code, ui-code, engine-code, data-files,
   test-standards, design-docs, anti-slop-design) и `.claude/docs/*` (coding-standards,
   technical-preferences, directory-structure, layout-archetypes, **quality-bar**).
4. `bash tools/codex-hooks.sh session-start` — покажет состояние проекта и `active.md`.

## Slash-команды (skills)

Пользователь вызывает команды как `$name` или `/name` (например `$autocreate --from-concept
"идея"`). Любая такая команда = **runbook** `.claude/skills/<name>/SKILL.md`:

1. Открыть SKILL.md, выполнить фазы по порядку, соблюдая критерии выхода каждой фазы.
2. Полный реестр команд — `.codex/commands.md`. Если команда не найдена — сказать об этом,
   не угадывать.
3. Frontmatter-поля `allowed-tools`/`user-invocable` — Claude-специфичны, игнорировать.

## Execution Model — адаптация Claude-механик к Codex

SKILL.md-файлы написаны для Claude Code и упоминают инструменты, которых в Codex нет.
Замены (ОБЯЗАТЕЛЬНЫЕ, конвейер никогда не останавливается из-за отсутствия инструмента):

| В SKILL.md написано | Что делает Codex |
|---------------------|------------------|
| `Agent(...)` — spawn субагента/сессии | **Продолжить инлайн в этой же сессии**: прочитать указанный в промпте SKILL.md / agent-файл и выполнить его самому, от лица этой роли |
| «5 параллельных агентов» (Фаза 4 autocreate) | **Последовательные persona-проходы** в порядке **A → E → D → B → C** (логика и сервисы раньше UI). Перед каждым проходом: прочитать `.claude/agents/<роль>.md` + `lib/contracts.md`; после — записать 3–5-строчное резюме в `production/session-state/active.md` |
| Skill tool / вызов `/команды` изнутри skill | Открыть соответствующий SKILL.md и выполнить как runbook |
| Claude hooks (session-start, validate-*) | `bash tools/codex-hooks.sh <hook>` (реестр: `.codex/hooks.md`) |
| Read с vision (анализ скриншотов/ассетов) | Встроенный vision Codex — прикладывать изображение и анализировать |
| Генерация PNG-ассетов | **GPT Images 2.0 → GPT Images/default fallback** (встроенная image generation) + белый фон простых ассетов + `rembg` для вырезания. PNG — режим по умолчанию в Codex (`design/asset-format.md: format: png`) |

### /autocreate в Codex: три «сессии» = три чекпоинта одной сессии

Конвейер `/autocreate` в Claude разбит на 3 context-сессии, связанные Agent tool. В Codex —
**один непрерывный прогон с теми же чекпоинтами**:

```
Фазы 1–3.8 (autocreate/SKILL.md)
  → записать autocreate-handoff-1.md           [чекпоинт 1]
  → прочитать autocreate-implement/SKILL.md и продолжить (Фазы 4–10.7)
  → записать autocreate-handoff.md             [чекпоинт 2]
  → прочитать autocreate-finalize/SKILL.md и продолжить (Фазы 10.5–12)
  → финальный отчёт
```

- Handoff-файлы ОБЯЗАТЕЛЬНЫ даже без spawn — это чекпоинты восстановления: если сессия
  оборвалась, новый запуск `$autocreate-implement` / `$autocreate-finalize` продолжает с них.
- `/compact` (если доступен) — на чекпоинтах; вся важная информация уже в файлах
  (`design/*`, `production/session-state/*`), разговор можно сжимать смело.

### Дисциплина контекста (в Codex критична — контекст один на весь конвейер)

- **Файлы — память, разговор — нет**: решения немедленно в `design/*` и
  `production/session-state/active.md` (см. `.claude/docs/context-management.md`).
- НЕ читать `lib/` массово: оперировать выводами `dart analyze` / `flutter test` /
  `grep`, точечный Read 1–2 файлов для диагностики.
- В persona-проходах держать в контексте только файлы СВОЕЙ зоны ответственности.

## Несгораемые правила (полный список — CLAUDE.md и .claude/rules/)

1. `GameState` — sealed class; все константы — только в `GameConfig`/JSON-конфигах.
2. Gambling: ТОЛЬКО `Random.secure()`; RTP 95–97%; Stateless Outcomes; age-gate/disclaimer.
3. Никаких stub-экранов и TODO-заглушек в результатах конвейера.
4. Дизайн — из Design DNA игры, не house-style (см. anti-slop-design.md).
5. Планка качества — `.claude/docs/quality-bar.md`: «поставил бы игрок 4+ звезды,
   не зная, что игру сделал ИИ?». Фазы 3.6 (asset-review), 6.5 (feel pass), 8 (ui-audit),
   10.6 (playtest) проверяют её инструментально — их нельзя пропускать или имитировать.
6. Отчитываться о результатах ЧЕСТНО: красный тест/упавшая фаза — называется красной,
   SKIPPED — называется SKIPPED. Не «в целом готово».

## Роли (агенты)

Реестр: `.codex/agents.md` → файлы `.claude/agents/*.md`. В Codex роль = persona-проход:
прочитать файл роли, выполнить её зону, вернуть короткое резюме. Ключевые:
`mechanics-programmer`, `ui-programmer`, `juice-artist`, `sound-designer`,
`meta-systems-programmer`, `art-director` (визуальная целостность ассетов),
`game-mathematician`, `qa-tester`, `lead-programmer`, `release-manager`.

## Верификация (web-first, без эмулятора)

Runtime-проверки идут через **headless Chrome + CDP**: `flutter run -d web-server` +
`node tools/web_verify.mjs` (тур по экранам, скриншоты, soak). Нужны `node` ≥21 и
Chrome/Chromium. Android/эмулятор — только явный fallback. Если node/Chrome нет —
фаза честно SKIPPED, конвейер продолжается.

## Setup (однократно на машине)

`bash tools/setup-codex-cli.sh` — добавит проект в trusted, выставит sandbox-дефолты
и установит skills в `~/.codex/skills` (symlink). После — перезапустить Codex CLI.
