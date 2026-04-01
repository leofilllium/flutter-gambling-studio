# Flutter Gambling Studio — Instructions for AI Assistants

> This file provides instructions for OpenAI Codex and other GPT-based agents.
> The canonical source of truth is `CLAUDE.md` and files in `.claude/`.

## Language

ALL interactions MUST be in Russian. Exceptions: Dart/Flutter code, file paths, class names, CLI commands.

## Tech Stack

- Flutter 3.27+ / Flame 1.18+
- Dart 3.6+ (null-safe, sealed classes, pattern matching)
- Specialization: mini-gambling games (slots, roulette, card games)

## Critical Rules (gambling integrity)

1. **RNG**: ONLY `Random.secure()` — never `math.Random()` or `Random()`
2. **Stateless Outcomes**: spin result is computed BEFORE animation starts
3. **SlotConfig**: all game constants live in `slot_config.dart` only
4. **RTP range**: 95–97% validated via 1M spin simulation
5. **GameState**: sealed class — no boolean flags
6. **Double-click protection**: Spin button locked during spin
7. **No hardcoded probability**: no `if (rng < 0.1) win!`

## Required Reading

Before writing any code, read the following files:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full project instructions, agent roles, command reference |
| `.claude/rules/gambling-code.md` | RNG rules, stateless outcomes, forbidden patterns |
| `.claude/rules/engine-code.md` | Flame 1.18.x API rules and required patterns |
| `.claude/rules/ui-code.md` | Flutter UI/HUD rules, state separation |
| `.claude/rules/anti-slop-design.md` | Anti-AI-slop UI/UX design rules |
| `.claude/rules/test-standards.md` | Testing requirements for gambling games |
| `.claude/rules/data-files.md` | rtp-config.json schema, SlotConfig rules |
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
| `/generate-asset` | `.claude/skills/generate-asset/SKILL.md` |
| `/code-review` | `.claude/skills/code-review/SKILL.md` |
| `/ui-audit` | `.claude/skills/ui-audit/SKILL.md` |
| `/balance-check` | `.claude/skills/balance-check/SKILL.md` |

When a user types a slash command, read the corresponding SKILL.md and execute the instructions within it.

## Agent Roles

The project uses specialized agent roles. When working as a GPT agent, adopt the appropriate role based on the task:

- **rtp-mathematician**: RTP calculations, symbol weights, probability simulation
- **gambling-game-designer**: GDD for slots — reels, paylines, bonuses, symbols
- **slot-programmer**: Spin logic, RNG, winning combinations (Flame 1.18.x)
- **juice-artist**: VFX, particles, animations — making the game feel "juicy"
- **lead-programmer**: Architecture, code review
- **ui-programmer**: Flutter screens, HUD, bet panel
- **qa-tester**: Test cases, edge cases, RNG verification

## Forbidden Patterns

1. `math.Random()` or `Random()` — only `Random.secure()`
2. Hardcoded probabilities outside SlotConfig
3. `isPaused = true` — use `GameState` sealed class
4. `await` in `update()` / `render()` — must be synchronous
5. `BuildContext` in Flame components — use callbacks
6. `print()` — use `Logger`
7. Object allocation in `update()` / `render()` — pre-initialize
8. `dynamic` outside JSON boundaries
9. Inheritance > 3 levels below Component
10. Modifying RTP weights outside `rtp-config.json`
