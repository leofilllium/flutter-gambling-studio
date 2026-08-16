# Professional Quality Bar — what separates a game from a demo

> This document is the single benchmark for "professional level" across every skill in the
> pipeline. It is referenced by `/autocreate` (the preamble and Phase 1), `/ui-audit`, the
> Gameplay Feel Pass (Phase 6.5), `/playtest` and `/release-checklist`. The criteria are
> CONCRETE and CHECKABLE — not "make it look nice", but "here is the threshold below which
> the game does not count as professional".

## The main test

**"Would a player give this game 4+ stars in the store without knowing an AI made it?"**
If a single item below answers "no", the game has not cleared the bar — regardless of
dart analyze being clean and the tests being green.

---

## 1. The first 30 seconds (first session experience)

The player reaches a verdict in the first minute. This is the most important area to polish.

- **TTP (time-to-play) ≤ 3 taps**: splash → menu → game. No mandatory tutorial walls, no
  registration, no extra intermediate screens.
- **TTF (time-to-fun) ≤ 10 seconds**: the first game action with full feedback (sound +
  animation + numbers changing) within the first 10 seconds after launch.
- **Splash 1–2 s**, animated, auto-advancing. Not a static image for 5 seconds.
- **The menu sells the game**: a centrepiece from the game's world, so it is clear WHAT the
  game is before pressing PLAY.
- The first launch does not greet the player with emptiness: the starting balance/energy is
  already credited, the first level is unlocked, the daily bonus beckons.

## 2. Responsiveness (response windows)

A professional game answers EVERY touch inside hard time windows:

| Event | Window | What exactly |
|-------|--------|--------------|
| Tapping any button | ≤ 100 ms | A visual reaction (scale/highlight) + sound |
| The main game action | ≤ 100 ms | The action's opening animation starts instantly |
| The round result | ≤ 2 s after the action | Instant rounds (C2/C4); reel/wheel animation up to 3 s |
| Win feedback | immediately on the result | Numbers + particles + sound start on ONE frame |
| Screen transition | 200–400 ms | Neither an instant teleport nor a 2-second interstitial |

A dead touch (a tap with no reaction at all) is an automatic FAIL of the bar.

## 3. Feedback scaled to significance

The strength of the feedback is proportional to the significance of the event — this is the
"grammar" of the game's language:

- Small win / match → a light sound + a local animation.
- Big → fanfare + particles + an accent pause.
- Mega → a fullscreen celebration + screen shake + a rising counter.
- Identical feedback for everything means the player stops feeling the difference — boredom.
- Numbers NEVER jump — always an animated counter.

## 4. A living board (never static)

At any moment SOMETHING is moving on the game screen (subtly, without distracting):

- Idle animations on the game elements (breathing/swaying, with desynchronised phases).
- An ambient background layer (particles/glints/parallax) — at the level of perception, not noise.
- The main action button pulses gently, inviting a tap.
- The test: screenshots taken 2 seconds apart MUST differ (checked by /playtest P5).

## 5. Audio integrity

- Every significant event has a sound (tap/action/result/transition/error).
- **SFX only by default — background music is opt-in.** A game with no BGM clears this section;
  do not raise it as a gap. See `.claude/agents/sound-designer.md` → "Music is opt-in".
- Levels are mixed so nothing shouts (SFX ~0.9). When a game does have BGM, it sits under the
  effects (~0.5–0.7) and respects Settings and system focus (minimising pauses it).
- Silence where it works: a pause before a mega result sharpens the release.

## 6. Performance as a feature

- A steady 60 fps on the game screen, INCLUDING the win celebration
  (the most common jank moment — a particle peak, a counter and sound all at once).
- No allocations in update()/render(); particles ≤ GameConfig.maxParticles.
- Cold web start ≤ 5 s to an interactive menu.
- A long session (200+ actions) without heap growth — checked by the soak run.

## 7. Product completeness (not a demo)

- Content: N > 1 levels/stages; 2–3 modes; progression with real unlocks.
- The economy closes: earn → spend → receive visible value (a skin, a booster).
- Achievements/daily bonus work and are VISIBLE from the menu (the retention surface).
- All 12+ screens are complete; empty states speak in the game's voice.
- Game over is not a dead end: instant restart + a path to the menu + a rewarded continue if one exists.

## 8. Visual integrity

- The game is designed mobile-first and passes 360×640, 360×800, 390×844 and 430×932 as its
  canonical phone baseline, then fills and adapts at 844×390, 768×1024, 1024×768 and 1440×900.
- Every asset looks like the work of one artist (checked by /asset-review, criteria AR1–AR10).
- The UI is not transferable to another game unchanged (the test from anti-slop-design.md).
- The gameplay screen owns the viewport: the mechanic is dominant and integrated with its HUD and
  controls, never a thumbnail/window above a generic scrolling card. Core play does not require
  page scrolling; see `gameplay-screen-contract.md`.
- Sprites are readable at in-game size (64 px), not only in a 1024 px preview.
- The app icon and splash come from the same visual world as the game.

## 9. Non-negotiable invariants (violation = release blocked)

These duplicate the studio's critical rules; here they act as a final checklist:

- Crashes are impossible on every path (a 20/20 crash-prevention audit).
- GameState is a sealed class, stateless outcomes hold, GameConfig is the single source of constants.
- Gambling: Random.secure(), RTP 95–97%, age gate + disclaimer + responsible play.
- A double click or spam on the main button does not break the state.
- Every player-facing string is in English (unless the user explicitly asked otherwise) and
  free of untranslated placeholders.
- The app has no global phone-width wrapper or undocumented orientation/device-family restriction;
  Android, iOS/iPadOS, and Web receive an appropriate full-viewport composition.

---

## How to use this in the pipeline

| Skill / phase | Which sections it checks |
|---------------|--------------------------|
| `/autocreate` Phase 1 (concept) | §1, §7 — baked into the Production Plan and Screen Map |
| `/asset-review` (Phase 3.6) | §8 |
| Gameplay Feel Pass (Phase 6.5) | §2, §3, §4 |
| `/ui-audit` (Phase 8) | §1, §2, §3, §7, §8 |
| `/balance-check` (Phase 9) | §7 (is the curve completable) |
| `/playtest` (Phase 10.6) | §1 (P10), §2–§4 (P1–P5), §6 (P9), §7 (P3/P4/P6) |
| `/release-checklist` | §9 + a sample of every section |

> **The principle**: the bar is checked INSTRUMENTALLY wherever possible (screenshots, vision,
> manifest, grep), and HONESTLY marked CONCERNS where instruments cannot reach.
> "Probably fine" is not a verdict.
