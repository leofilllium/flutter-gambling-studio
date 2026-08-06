# Codex Hook Mapping

Claude Code runs hooks automatically through `.claude/settings.json`. Codex does not, so in
this repository the hooks are used manually or through the `tools/codex-hooks.sh` wrapper.

## Hook script registry

| Hook | Script | When to run it in Codex |
|------|--------|-------------------------|
| `session-start` | `.claude/hooks/session-start.sh` | At the start of a new session |
| `detect-gaps` | `.claude/hooks/detect-gaps.sh` | After reviewing the structure, or before starting work |
| `validate-assets` | `.claude/hooks/validate-assets.sh` | After changing assets or `pubspec.yaml` |
| `validate-commit` | `.claude/hooks/validate-commit.sh` | Before a commit or a code freeze |
| `validate-push` | `.claude/hooks/validate-push.sh` | Before pushing to a protected branch |
| `pre-compact` | `.claude/hooks/pre-compact.sh` | Before a long context switch, or when finishing a chunk of work |
| `session-stop` | `.claude/hooks/session-stop.sh` | At the end of a session |
| `log-agent` | `.claude/hooks/log-agent.sh` | When manually recording the use of a specialised role |

## The standard cycle in Codex

```bash
bash tools/codex-hooks.sh session-start
bash tools/codex-hooks.sh detect-gaps
```

After notable changes:

```bash
bash tools/codex-hooks.sh validate-assets
bash tools/codex-hooks.sh pre-compact
```

Before a commit or a release:

```bash
bash tools/codex-hooks.sh validate-commit
bash tools/codex-hooks.sh validate-push
```

At the end of the work:

```bash
bash tools/codex-hooks.sh session-stop
```

## Limitation

Some Claude hooks read `CLAUDE_*` environment variables. The `tools/codex-hooks.sh` wrapper
substitutes safe defaults so that the scripts remain executable under Codex too.
