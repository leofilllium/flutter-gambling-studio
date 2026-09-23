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
- **TTF (time-to-fun) ≤ 10 seconds**: the first game action and its complete, readable state
  feedback occur within the first 10 seconds after launch.
- **Opening state ≤ 2 s**, auto-advancing. It may be animated or deliberately direct according to
  the Design Signature; it must not hold the player on an inert branding image.
- **The menu sells the game**: it implements the recorded memorable interface idea and M/O/R
  recipe, so the player understands the world and route to play before acting. A character,
  object, mechanic, scene, path, machine facade, shelf, or typographic/poster composition can
  lead. Do not invent a mascot or force a centered one-third-height centerpiece. V19 checks the
  documented attention order and intentional composition, not a universal subject placement.
- The first launch does not greet the player with emptiness: starting resources are credited, the
  first playable path is available, and the next optional reward/progression route is discoverable
  without forcing a daily-bonus badge into every menu composition.

## 2. Responsiveness (response windows)

A professional game answers EVERY touch inside hard time windows:

| Event | Window | What exactly |
|-------|--------|--------------|
| Activating any control | ≤ 100 ms | Immediate visible/tactile acknowledgement from the control's documented feedback role |
| The main game action | ≤ 100 ms | Commitment feedback starts instantly; the resolved outcome remains predetermined |
| The round result | ≤ 2 s after the action | Instant rounds (C2/C4); reel/wheel animation up to 3 s |
| Result feedback | immediately on the result | Field, HUD, audio/haptics, and overlays change coherently where each is applicable |
| Ordinary screen transition | 0–400 ms | Direct/standard is valid; longer sequences are reserved for recorded dramatic states and remain skippable/reduced-motion safe |

A dead touch (a tap with no reaction at all) is an automatic FAIL of the bar.

## 3. Feedback scaled to significance

The strength of feedback is proportional to event significance, expressed through this game's
recorded motion, sound, haptic, depth, and overlay vocabulary:

- routine events usually stay local to the object or value that changed;
- notable events may change field emphasis, cadence, or a contextual HUD region;
- major events may take over more of the scene when interruption is justified, but full-screen
  overlays, particles, shake, fanfares, and counters are options rather than required ingredients;
- event tiers must be distinguishable without relying only on color, volume, or flashing.
- Meaningful reward/risk/progression changes communicate magnitude; stable utility values may
  update directly when animation would add delay or noise.

## 4. A responsive, stateful board

The game must visibly respond to input and state changes. Continuous ambient motion is optional:

- idle motion belongs on elements whose world/material supports it;
- particles, glints, parallax, and pulsing controls are techniques, not baseline requirements;
- a deliberately still setup state can improve tension, precision, readability, or battery use;
- `/playtest` P5 verifies that an active round produces meaningful frame change. It must not fail
  a deliberately still idle state merely because two idle screenshots match.

## 5. Audio integrity

- Significant events have an intentional audio policy: an appropriate cue, a purposeful quiet
  beat, or silence where repetition/accessibility makes sound harmful. Do not sonify every route.
- **SFX only by default — background music is opt-in.** A game with no BGM clears this section;
  do not raise it as a gap. See `.claude/agents/sound-designer.md` → "Music is opt-in".
- Levels are mixed so nothing shouts (SFX ~0.9). When a game does have BGM, it sits under the
  effects (~0.5–0.7) and respects Settings and system focus (minimising pauses it).
- Silence where it works: a pause before a mega result sharpens the release.

## 6. Performance as a feature

- A steady 60 fps on the game screen, including the highest-cost recorded result treatment.
- No allocations in update()/render(); particles ≤ GameConfig.maxParticles.
- Cold web start ≤ 5 s to an interactive menu.
- A long session (200+ actions) without heap growth — checked by the soak run.

## 7. Product completeness (not a demo)

- Content: N > 1 levels/stages; 2–3 modes; progression with real unlocks.
- The economy closes: earn → spend → receive visible value (a skin, a booster).
- Achievements/daily bonus work and are discoverable from the menu or its documented hub/navigation
  model; they do not require a universal icon row.
- All 12+ screens are complete; empty states speak in the game's voice.
- Game over is not a dead end: instant restart + a path to the menu + a rewarded continue if one exists.

## 8. Visual integrity

- The game is designed mobile-first and passes 360×640, 360×800, 390×844 and 430×932 as its
  canonical phone baseline, then fills and adapts at 844×390, 768×1024, 1024×768 and 1440×900.
- Every asset looks like the work of one artist (checked by /asset-review, criteria AR1–AR11).
- The UI passes the recorded Similarity Check and remains distinctive in wireframe/grayscale;
  changing only palette and art would not produce the same game.
- The gameplay screen owns the viewport: the mechanic is dominant and integrated with its HUD and
  controls, never a thumbnail/window above a generic scrolling card. Core play does not require
  page scrolling; see `gameplay-screen-contract.md`.
- Sprites are readable at in-game size (64 px), not only in a 1024 px preview.
- The app icon and splash come from the same visual world as the game.

## 9. Non-negotiable invariants (violation = release blocked)

These duplicate the studio's critical rules; here they act as a final checklist:

- Crashes are impossible on every path (a 20/20 crash-prevention audit).
- GameState is a sealed class, stateless outcomes hold, GameConfig is the single source of constants.
- Gambling: Random.secure(), RTP 95–97%, disclaimer + responsible play.
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
