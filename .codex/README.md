# Codex Compatibility Layer

This directory makes `flutter-gambling-studio` a first-class repository for OpenAI Codex
without breaking the original Claude-oriented structure.

## What lives here

- `commands.md` — the full registry of slash commands and how they map to `.claude/skills/*/SKILL.md`
- `agents.md` — the studio's agent roles and the rules for using them in Codex
- `hooks.md` — how to use the Claude hooks manually or through the `tools/codex-hooks.sh` wrapper

## How Codex should work in this repository

1. Read `AGENTS.md` (at the repository root) first — it defines the **execution model**:
   how to run the Claude mechanics (Agent tool → inline persona passes, Skill tool →
   runbook, hooks → `tools/codex-hooks.sh`).
2. Then read `CLAUDE.md` and the required rules in `.claude/rules/` and `.claude/docs/`.
3. If the user types a slash command (`$name` or `/name`), open the matching `SKILL.md`
   from `.claude/skills/` and follow its instructions as a runbook (the registry is in
   `commands.md`).
4. If a task needs a specialised role, adopt the persona from the table in `agents.md`
   (files in `.claude/agents/*.md`).
5. If a Claude hook is needed, run it manually with `bash tools/codex-hooks.sh <hook-name>`.

## Setup on a new machine

```bash
bash tools/setup-codex-cli.sh        # trusted project + sandbox defaults + skills (symlink)
bash tools/codex-doctor.sh           # environment self-diagnosis
```

## The compatibility principle

`.claude/` remains the canonical source of rules, skills and roles.
`.codex/` does not duplicate domain logic — it indexes and adapts it for Codex.
