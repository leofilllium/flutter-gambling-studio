# Codex Compatibility Layer

Этот каталог делает `flutter-game-studio` first-class репозиторием для OpenAI Codex,
не ломая исходную Claude-ориентированную структуру.

## Что здесь находится

- `commands.md` — полный реестр slash-команд и их маппинг на `.claude/skills/*/SKILL.md`
- `agents.md` — роли агентов студии и правила их использования в Codex
- `hooks.md` — как использовать Claude hooks вручную или через обёртку `tools/codex-hooks.sh`

## Как Codex должен работать в этом репозитории

1. Сначала читать `AGENTS.md` (корень репозитория) — он задаёт **Execution Model**:
   как исполнять Claude-механики (Agent tool → инлайн persona-проходы, Skill tool →
   runbook, hooks → `tools/codex-hooks.sh`).
2. Затем читать `CLAUDE.md` и обязательные правила из `.claude/rules/` и `.claude/docs/`.
3. Если пользователь пишет slash-команду (`$name` или `/name`), открыть соответствующий
   `SKILL.md` из `.claude/skills/` и выполнить его инструкцию как runbook (реестр —
   `commands.md`).
4. Если задача требует специализированной роли, принять нужную persona по таблице из
   `agents.md` (файлы `.claude/agents/*.md`).
5. Если нужен Claude hook, запускать его вручную через `bash tools/codex-hooks.sh <hook-name>`.

## Setup на новой машине

```bash
bash tools/setup-codex-cli.sh        # trusted project + sandbox defaults + skills (symlink)
bash tools/codex-doctor.sh           # самодиагностика окружения
```

## Принцип совместимости

`.claude/` остаётся каноническим источником правил, навыков и ролей.
`.codex/` не дублирует доменную логику, а индексирует и адаптирует её для Codex.
