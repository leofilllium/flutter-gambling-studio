# Gemini CLI / Antigravity Guide for Flutter Gambling Studio

> Drive the gambling studio through the Gemini / Antigravity agent.
> The studio builds ONLY gambling games: six categories C1–C6, 32 archetypes A–AF.
> This file adapts the studio's commands for use in the `gemini` CLI.
>
> For Claude: `CLAUDE.md` and `.claude/`
> For Codex: `AGENTS.md` and `.codex/`
> For Cursor: `.cursorrules`

## Installation and integration (Gemini CLI)

To make the skills and agents show up in Gemini / Antigravity:
```bash
./tools/setup-gemini-cli.sh link
```
This adds the studio's project plugin to `~/.gemini/antigravity/plugins/flutter-gambling-studio/skills`.

## Usage

Your bot (Antigravity, for example) is trained to run commands as "manual runbooks" or as
full skills. Just type the command you want in the chat (`/brainstorm`, for instance) or
mention the agent.

### Available commands

| Command | Description |
|---------|-------------|
| `/brainstorm` | Interactive concept generator |
| `/auto-idea` | Autonomous concept (32 archetypes A–AF across 6 categories + Variety Dimensions + Layout Archetype) |
| `/autocreate` | The full game creation cycle |
| `/team-dev` | Developer team orchestration |
| `/ui-audit` | Find anti-slop design problems |
| `/emulator-test` | Runtime testing — Chrome/Web by default, with a real Android emulator over ADB as the fallback. Screenshots come from `flutter screenshot`, falling back to `adb screencap`, with PNG validation. Use `--no-impeller` if the frames come out invalid. |
| `/code-review` | Review of the Flame and Flutter architecture |
| `/balance-check` | Math model verification M1–M6 via `tools/simulate_math.py` |

For the full list see [CLAUDE.md](CLAUDE.md).

## Language

Everything produced in this repository is in English: agent responses, design documents,
reports and code. The generated game ships in English too — every player-facing string plus
store metadata. The only exception is an explicit user request for a different language: then
the player-facing copy uses it and everything else stays English. Never switch the game's
language on your own initiative or because of the language the user types in.

## Coding rules

When writing code, the Gemini bot follows the standards described in:
- `.claude/rules/game-code.md`
- `.claude/rules/engine-code.md`
- `.claude/rules/ui-code.md`

Always pay attention to the `Random.secure()` and "stateless outcomes" requirements, and
avoid magic numbers outside `game_config.dart`.

Required reading before starting work:
- `.claude/docs/gambling-categories.md` — the six categories and 32 archetypes
- `.claude/docs/math-models.md` — models M1–M6 and their verification thresholds
- `.claude/rules/responsible-gaming.md` — the compliance layer (a release blocker)
