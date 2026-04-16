# Codex Hook Mapping

Claude Code запускает hooks автоматически через `.claude/settings.json`. Codex этого не делает, поэтому в этом репозитории hooks используются вручную или через обёртку `tools/codex-hooks.sh`.

## Реестр hook-скриптов

| Hook | Скрипт | Когда запускать в Codex |
|------|--------|-------------------------|
| `session-start` | `.claude/hooks/session-start.sh` | В начале новой сессии |
| `detect-gaps` | `.claude/hooks/detect-gaps.sh` | После обзора структуры или перед стартом работ |
| `validate-assets` | `.claude/hooks/validate-assets.sh` | После изменения ассетов или `pubspec.yaml` |
| `validate-commit` | `.claude/hooks/validate-commit.sh` | Перед коммитом или code freeze |
| `validate-push` | `.claude/hooks/validate-push.sh` | Перед push в защищённую ветку |
| `pre-compact` | `.claude/hooks/pre-compact.sh` | Перед долгой сменой контекста или завершением части работы |
| `session-stop` | `.claude/hooks/session-stop.sh` | В конце сессии |
| `log-agent` | `.claude/hooks/log-agent.sh` | При ручной фиксации вызова специализированной роли |

## Стандартный цикл в Codex

```bash
bash tools/codex-hooks.sh session-start
bash tools/codex-hooks.sh detect-gaps
```

После заметных изменений:

```bash
bash tools/codex-hooks.sh validate-assets
bash tools/codex-hooks.sh pre-compact
```

Перед коммитом или релизом:

```bash
bash tools/codex-hooks.sh validate-commit
bash tools/codex-hooks.sh validate-push
```

В конце работы:

```bash
bash tools/codex-hooks.sh session-stop
```

## Ограничение

Некоторые Claude hooks читают переменные окружения `CLAUDE_*`. Обёртка `tools/codex-hooks.sh` подставляет безопасные значения по умолчанию, чтобы скрипты были исполнимы и в Codex.
