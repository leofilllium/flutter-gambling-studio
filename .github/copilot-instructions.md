# GitHub Copilot Instructions — Flutter Gambling Studio

Respond in Russian. Code in English (Dart/Flutter).

This is a gambling game studio using Flutter 3.27+ and Flame 1.18+.

## Critical Rules

- RNG: ONLY `Random.secure()` — never `math.Random()` or `Random()`
- Spin result must be computed BEFORE animation (stateless outcomes)
- All game constants in `slot_config.dart` — no magic numbers in logic
- GameState must be a sealed class, not boolean flags
- No `await` in `update()` or `render()` — synchronous only
- No object allocation in hot path (`update`/`render`) — pre-initialize Vector2, Paint, Rect
- Max 3 concurrent audio channels (BGM + Spin + Effect)
- HasCollisionDetection goes on World, not FlameGame
- Use new CameraComponent API (Flame 1.18)

## UI Rules (Anti-Slop)

- No bare `ThemeData.dark()` — custom themes only
- No `CircularProgressIndicator` — themed loaders only
- No default `MaterialPageRoute` — custom transitions
- Minimum 2 custom fonts per game
- Every interactive element needs tactile feedback (scale/glow/sound)
- All animation durations centralized in `lib/theme/animations.dart`

## Full Documentation

See `agents.md`, `CLAUDE.md`, and `.claude/rules/` for complete rules.
