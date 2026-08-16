# Technical standards of the Gambling Studio

## Product platform

- Design for touch-first phone UI/UX first, then adapt to the full available viewport on Android,
  iOS/iPadOS, and Web.
- Web is a supported runtime target and the primary Chrome/CDP verification environment.
- Essential interaction must never depend on hover or a keyboard. Expanded tablet/desktop
  layouts preserve the mobile hierarchy while using the additional space intentionally. Follow
  `.claude/docs/mobile-first-contract.md`.

## Flutter + Flame 1.18.x

### Mathematics and RNG

- **CRITICAL**: NEVER use `math.Random()`. ONLY `Random.secure()` for any outcome that
  affects a payout:
  - Picking symbols on the reels, dealing cards, stopping the wheel or the ball
  - The crash point in crash, the placement of mines, a dice roll
  - A keno draw, revealing a scratch field, choosing a chest
  - Bonus mechanic triggers and pity pulls in gacha
  - The starting conditions of a physical launch in plinko/pachinko
- **The single exception** is seeded run determinism in casino roguelikes (category C5,
  model M5): there `Random(seed)` is mandatory, because the run has to be reproducible.
  The exception is recorded in an ADR, otherwise `/code-review` treats it as a violation.
- `Random()` is acceptable ONLY for purely visual elements that do not affect the outcome
  (particle scatter, idle animation phases). Never for game logic.
- **Stateless outcomes**: the round result is computed BEFORE the animation starts. The
  animation simply "plays back" a predetermined script. Without this the RTP is not
  verifiable, and cash-out in C2 is mathematically incorrect.
- **Balance tuning**: all game parameters live in `game_config.dart`; the math model's numbers
  live in the model's JSON config (`design/balance/*.json`), which `tools/simulate_math.py`
  reads. One source of truth, with no duplication between JSON and code.

### Flame API (1.18.x)

- Derive the main class from `FlameGame`.
- Always declare collisions on the `World`, not on the `FlameGame`:
  `class GameWorld extends World with HasCollisionDetection {}`
- Use the updated `CameraComponent`:
  `camera = CameraComponent(world: _world);`
- No `.isPaused = true`. Use `GameState` (a sealed class: Idle, Playing, Paused, GameOver).

### Visualisers and particles

For the juiciness of a round we use *ParticleSystemComponent* effects.
- On key events (a win, a near-miss, a cash-out, a rare pull, a jackpot) spawn thematic
  particles:
  `ParticleSystemComponent(particle: Particle.generate(count: 50, generator: ...))`
- The strength of the effect scales with the significance of the event (see quality-bar.md §3):
  a small win gets a local flash, a mega win gets fullscreen. Identical feedback for
  everything kills the game's grammar.
- Effect settings (glow, drop shadow) are implemented through a Flutter Overlay on top of
  Flame, because complex filters inside Flame are expensive.

### Sound
- Use the `flame_audio` package, `^2.1.0`.
- Limit concurrent playback: at most 3 overlapping sounds (for example 1 BGM loop, 1 action
  sound loop, 1 effect overlay).
- For rising effects use pitch scaling: `playbackRate` 1.0 → 1.5.

### Graphical assets
- For `/autocreate` under Codex the default graphics path is **PNG via GPT Images 2.0**, and
  if GPT Images 2.0 fails, a retry through **GPT Images / the default Codex image generation**,
  straight from the concept and Design DNA. Do not generate SVG first and convert it to PNG
  afterwards: that loses the material, the light, the style and the tie to the game's world.
- SVG remains the fallback mode for non-Codex environments or an explicit `--svg`.
- The chosen format is recorded in `design/asset-format.md`.
- If `format: png`, the UI uses `Image.asset(...)` and real `.png` paths.
- If `format: svg`, the UI uses `SvgPicture.asset(...)` / `flame_svg`.
- `/svg-to-png` exists only for legacy SVG or an explicit user request — it is not the normal
  `/autocreate` path.
- For simple PNG assets the prompt must ask for a flat key background (chroma key: by default
  `pure magenta #FF00FF`, or `pure green #00FF00` if the palette contains magenta/pink) with no
  shadows, gradients or scene, and the background is then cut out with
  `python3 tools/cutout.py <file> --type sprite`.
  A white background is forbidden for objects with light or white areas — they merge into it.
  A manual `magick -fuzz -transparent white` is forbidden: it tears the alpha and leaves a halo.
  For background images the background is not removed.
- Naming pattern:
  `background_X` (backgrounds)
  `sprite_X` (game elements: reel symbols, cards, chips, balls, mines, capsules)
  `ui_X` (buttons, bet panels, decks)
  `icon_X` (badges, interface icons)
