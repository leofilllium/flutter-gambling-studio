You are Antigravity / Gemini CLI working on Flutter Game Studio — a universal mini-game studio supporting all genres (Gambling, Puzzle, Action/Arcade, Physics, Casual, Card/Board) built with Flutter 3.27+ and Flame 1.18+.

Respond in Russian. Write code in English (Dart/Flutter).

BEFORE writing any code, read the relevant rule files in `.claude/rules/` and `.claude/docs/` (which serve as the universal studio ground truth):
- Game logic (all genres): .claude/rules/game-code.md
- Flame engine: .claude/rules/engine-code.md
- UI/HUD: .claude/rules/ui-code.md
- Anti-slop design: .claude/rules/anti-slop-design.md
- Testing: .claude/rules/test-standards.md
- Full reference: AGENTS.md, GEMINI.md and CLAUDE.md

If the user types a slash command like `/brainstorm`, `/team-dev`, `/autocreate`, `/code-review`, `/ui-audit`, etc., you MUST act as the specified agent or runbook. Open the matching file in `.claude/skills/*/SKILL.md` or `.gemini/skills/*/SKILL.md` (using the `view_file` tool) and follow the instructions exactly. For specialized roles, consult the persona briefs in `.claude/agents/*.md`.

CRITICAL RULES (ALL GENRES):
- GameState = sealed class, no boolean flags
- All game constants in game_config.dart only (no magic numbers)
- Main action button locked during animation — 300ms debounce
- Result computed BEFORE animation starts (stateless outcomes)
- No await in update()/render() — synchronous only
- No allocation in update()/render() — pre-initialize Vector2, Paint, Rect
- HasCollisionDetection on World, not FlameGame
- CameraComponent (new Flame 1.18 API), not Camera()

CRITICAL RULES (GAMBLING GENRE ONLY):
- RNG: ONLY Random.secure() — NEVER math.Random() or Random()
- No hardcoded probabilities outside game_config.dart / rtp-config.json
- RTP must be 95–97% (validated via /balance-check)

UI RULES (ANTI-SLOP):
- No bare ThemeData.dark() — custom themes only
- No CircularProgressIndicator — themed loaders
- Minimum 2 custom fonts, custom shaped buttons
- All animation durations in lib/theme/animations.dart
- Minimum 10 screens/overlays in MVP

Your goal is to be fully runnable in the Gemini CLI environment.
Use your tools effectively (view_file to read SKILL.md rules, grep_search to inspect mechanics, run_command to run flutter tools or helper scripts like `bash tools/codex-hooks.sh`).
