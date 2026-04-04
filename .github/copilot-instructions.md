# GitHub Copilot Instructions — Flutter Game Studio

Respond in Russian. Code in English (Dart/Flutter).

This is a universal mini-game studio using Flutter 3.27+ and Flame 1.18+.
Supported genres: Gambling (slots, roulette, crash, dice), Puzzle (match-3, tetris),
Action/Arcade (runner, shooter), Physics (pinball, plinko), Casual (clicker, idle), Card/Board.

## Critical Rules (All Genres)

- GameState must be a sealed class, not boolean flags
- All game constants in `game_config.dart` (or `slot_config.dart` for gambling) — no magic numbers
- Main action button (Spin/Play/Start) locked during animation — debounce 300ms
- Stateless Outcomes: result computed BEFORE animation starts
- No `await` in `update()` or `render()` — synchronous only
- No object allocation in hot path (`update`/`render`) — pre-initialize Vector2, Paint, Rect
- Max 3 concurrent audio channels (BGM + Action + Effect)
- HasCollisionDetection goes on World, not FlameGame
- Use new CameraComponent API (Flame 1.18)

## Critical Rules (Gambling Genre Only)

- RNG: ONLY `Random.secure()` — never `math.Random()` or `Random()`
- No hardcoded probabilities: no `if (rng < 0.1) win!`
- RTP range: 95–97% validated via 1M spin simulation

## UI Rules (Anti-Slop)

- No bare `ThemeData.dark()` — custom themes only
- No `CircularProgressIndicator` — themed loaders only
- No default `MaterialPageRoute` — custom transitions
- Minimum 2 custom fonts per game
- Every interactive element needs tactile feedback (scale/glow/sound)
- All animation durations centralized in `lib/theme/animations.dart`

## Full Documentation

See `agents.md`, `CLAUDE.md`, and `.claude/rules/` for complete rules.
