# Flutter Game Studio — Instructions for AI Assistants

> This file provides instructions for OpenAI Codex and other GPT-based agents.
> The canonical source of truth is `CLAUDE.md` and files in `.claude/`.

## Language

ALL interactions MUST be in Russian. Exceptions: Dart/Flutter code, file paths, class names, CLI commands.

## Tech Stack

- Flutter 3.27+ / Flame 1.18+
- Dart 3.6+ (null-safe, sealed classes, pattern matching)
- Supported genres: Gambling (slots, roulette, crash, dice), Puzzle (match-3, tetris, sokoban),
  Action/Arcade (runner, shooter, breakout), Physics (pinball, plinko), Casual (clicker, idle), Card/Board

## Critical Rules (All Genres)

1. **GameState**: sealed class — no boolean flags
2. **GameConfig**: all game constants in `game_config.dart` — no magic numbers in logic
3. **Double-click protection**: main action button locked during animation (300ms debounce)
4. **Stateless Outcomes**: result is computed BEFORE animation starts
5. **No `await` in `update()` / `render()`**: synchronous only
6. **No allocation in hot path**: pre-initialize Vector2, Paint, Rect

## Critical Rules (Gambling Genre Only)

1. **RNG**: ONLY `Random.secure()` — never `math.Random()` or `Random()`
2. **RTP range**: 95–97% validated via 1M spin simulation
3. **No hardcoded probability**: no `if (rng < 0.1) win!`
4. **Weights from config**: always read from `game_config.dart` or `rtp-config.json`

## Required Reading

Before writing any code, read the following files:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full project instructions, agent roles, command reference |
| `.claude/rules/game-code.md` | Game logic rules (all genres + gambling-conditional) |
| `.claude/rules/engine-code.md` | Flame 1.18.x API rules and required patterns |
| `.claude/rules/ui-code.md` | Flutter UI/HUD rules, state separation |
| `.claude/rules/anti-slop-design.md` | Anti-AI-slop UI/UX design rules |
| `.claude/rules/test-standards.md` | Testing requirements |
| `.claude/rules/data-files.md` | rtp-config.json schema, GameConfig rules |
| `.claude/rules/design-docs.md` | GDD document standards (8 mandatory sections) |
| `.claude/docs/technical-preferences.md` | Flame API, audio, SVG asset standards |
| `.claude/docs/coding-standards.md` | Dart style, component limits, error handling |
| `.claude/docs/directory-structure.md` | Project directory layout |
| `.claude/docs/coordination-rules.md` | Agent collaboration and conflict resolution |

## Slash Commands (manual execution)

GPT Codex does not natively support Claude Code skills. To replicate them, read the corresponding skill file and follow its instructions:

| Command | Skill file |
|---------|-----------|
| `/brainstorm` | `.claude/skills/brainstorm/SKILL.md` |
| `/auto-idea` | `.claude/skills/auto-idea/SKILL.md` |
| `/autocreate` | `.claude/skills/autocreate/SKILL.md` |
| `/team-dev` | `.claude/skills/team-dev/SKILL.md` |
| `/generate-asset` | `.claude/skills/generate-asset/SKILL.md` |
| `/code-review` | `.claude/skills/code-review/SKILL.md` |
| `/ui-audit` | `.claude/skills/ui-audit/SKILL.md` |
| `/balance-check` | `.claude/skills/balance-check/SKILL.md` |

When a user types a slash command, read the corresponding SKILL.md and execute the instructions within it.

## Agent Roles

The project uses specialized agent roles. When working as a GPT agent, adopt the appropriate role based on the task:

- **game-mathematician**: RTP calculations (gambling), difficulty curves (puzzle), scoring (arcade)
- **game-designer**: GDD for any genre — reels, paylines, levels, bonuses, progression
- **mechanics-programmer**: Core game logic — RNG, match detection, spawning, physics (Flame 1.18.x)
- **juice-artist**: VFX, particles, animations — making the game feel "juicy"
- **lead-programmer**: Architecture, code review
- **ui-programmer**: Flutter screens, HUD, control panels
- **sound-designer**: Audio effects, BGM, flame_audio integration
- **qa-tester**: Test cases, edge cases, RNG verification

## Forbidden Patterns (All Genres)

1. `isPaused = true` — use `GameState` sealed class
2. `await` in `update()` / `render()` — must be synchronous
3. `BuildContext` in Flame components — use callbacks
4. `print()` — use `Logger`
5. Object allocation in `update()` / `render()` — pre-initialize
6. `dynamic` outside JSON boundaries
7. Inheritance > 3 levels below Component
8. Hardcoded game parameters outside GameConfig

## Forbidden Patterns (Gambling Only)

1. `math.Random()` or `Random()` — only `Random.secure()`
2. Hardcoded probabilities outside GameConfig / rtp-config.json
3. Modifying RTP weights outside `rtp-config.json` + game-mathematician approval
