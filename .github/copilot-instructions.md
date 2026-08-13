# GitHub Copilot Instructions — Flutter Gambling Studio

Respond in English. Everything you produce is English: code (Dart/Flutter), design docs and
reports. The GAME itself also ships in English — every player-facing string, plus store
metadata. The only exception is an explicit user request for another language: then the
player-facing copy uses that language and everything else stays English. Never switch the
game's language on your own initiative or because of the language the user types in.

This is a **gambling-only** mini-game studio using Flutter 3.27+ and Flame 1.18+.
Puzzles, runners, shooters and clickers are out of scope.

Every game targets Android phones and iPhone in portrait only. Web exists solely for preview and
automated verification. Do not create tablet/iPad, desktop, wide-screen, or landscape layouts;
follow `.claude/docs/mobile-phone-contract.md`.

Six gambling categories (no other genres):
  C1 Social Casino        — slots, video poker, blackjack, roulette, bingo      → model M1 (RTP 95-97%)
  C2 Casino Originals     — crash, mines, dice, hi-lo, tower, keno, scratch     → model M2 (RTP 96-99%)
  C3 Spin-to-Progress     — build-and-raid, board-dice, prize wheel, album      → model M3 (economy)
  C4 Gacha & Loot-Box     — banner pulls, card packs, case openers, gashapon    → model M4 (rates + pity)
  C5 Casino Roguelike     — poker deckbuilder, reel roguelike, dice-builder     → model M5 (run win-rate)
  C6 Coin Pusher & Plinko — coin dozer, plinko, pachinko                        → model M6 (physics RTP)

## Critical Rules (all six categories — unconditional)

- RNG: ONLY `Random.secure()` — never `math.Random()` or `Random()`.
  Sole exception: seeded run RNG in C5 casino roguelikes, and only with an ADR.
- Stateless Outcomes: the round result is computed BEFORE the animation starts
- No hardcoded probabilities: no `if (rng < 0.1) win!` — weights come from the JSON math config
- GameState must be a sealed class, not boolean flags
- All game constants in `game_config.dart`; math-model numbers in `design/balance/*.json`
  (loaded, never duplicated as Dart literals)
- Main action button locked during the round — debounce 300ms
- No `await` in `update()` or `render()` — synchronous only
- No object allocation in hot path (`update`/`render`) — pre-initialize Vector2, Paint, Rect
- Max 3 concurrent audio channels (BGM + Action + Effect)
- HasCollisionDetection goes on World, not FlameGame
- Use new CameraComponent API (Flame 1.18)
- Verify the model: `python3 tools/simulate_math.py --model [m1-m6] --config design/balance/<file>.json`

## Compliance (release blocker)

Virtual chips only — no real money in or out. Age gate on first launch, disclaimer on splash
and in the rules, responsible-play block in settings, odds disclosure for C4 and paid spins in C3.
No real-currency symbols next to a virtual balance. See `.claude/rules/responsible-gaming.md`.

## UI Rules (Anti-Slop)

- Portrait phone canvas only; required gates: 360×640, 360×800, 390×844, 430×932
- No bare `ThemeData.dark()` — custom themes only
- No `CircularProgressIndicator` — themed loaders only
- No default `MaterialPageRoute` — custom transitions
- Minimum 2 custom fonts per game
- Every interactive element needs tactile feedback (scale/glow/sound)
- All animation durations centralized in `lib/theme/animations.dart`

## Full Documentation

See `AGENTS.md`, `CLAUDE.md`, `.claude/docs/gambling-categories.md`, `.claude/docs/math-models.md` and `.claude/rules/` for complete rules.
