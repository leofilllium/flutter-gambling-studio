# Repository Guidelines — Flutter Gambling Studio

## Codex CLI Instructions

This is a **gambling-only** game studio: every concept must fall into one of six categories (C1 social casino, C2 casino originals, C3 spin-to-progress hybrids, C4 gacha/loot-box, C5 casino roguelike, C6 coin pusher/plinko) and declare a verifiable math model (M1-M6). Puzzles, runners, shooters and clickers are out of scope.

Every generated game is **mobile-first**, with touch-first phone UI/UX as its canonical design
baseline. It must also fill and adapt to tablet, landscape, desktop, and Web viewports without a
fixed-width phone canvas or fake device frame. Follow `.claude/docs/mobile-first-contract.md`,
including both its phone-baseline and expanded-viewport verification gates.

All generated game art must use polished cartoon 2.5D casual-game illustration with bold
silhouettes, rounded/exaggerated forms, saturated theme-aware color, smooth modeled
gradients, glossy highlights, restrained star glints, and one consistent top-left light.
Derive the visual world, shapes, materials, details, and palette independently from each
game's concept and Design DNA. Inspect matching `examples-games/` previews by default and
generate original assets with relevant shared qualities. Read `.claude/docs/visual-context.md`
and `.claude/docs/game-concept-examples.md`. Photorealistic/product-render assets, flat vector clipart, and emoji/sticker
styling are out of scope.

All store screenshot sets use casino-grade marketing composition: lead with the decisive
wager/reveal/drop/collect moment, premium depth and tactility, controlled anticipation and reward
focus, with real active gameplay large and readable. This is composition—not a mandatory
black/neon/gold skin; every palette, material, character and type choice still comes from the
current game's Design DNA. Never use cropping or device chrome to hide a weak gameplay layout.
Record `lead_kind: character | object | mechanic` before composing. Zeus, Joker and chicken games
default to a large character on the first panel. Object/mechanic games such as crown slots and
Plinko need no invented mascot or character-only opening. For characters, left/lower edge crops
are allowed; protect heads/headwear with 2% top headroom and keep attached forms clear of the first
seam. Animal framing fits the species. Real game objects form the cropped bottom frame
and fall through the picture, while the far background stays broad, smooth, and subordinate so
those subjects lead. Store grading is restrained and theme-led by default: preserve the Design DNA's
exposure and add only enough saturation for the game objects to read cleanly. Brightness lifts, bloom,
blown light sources, and aggressively saturated treatments are opt-in art direction, never universal
delivery requirements. Generic stage furniture does not count as game objects, and a dark,
hyper-detailed far plane can still fail the readability contract. The Google Play feature graphic
uses its own horizontal composition.
A left-heavy 3/5–2/5 split is optional; object/mechanic scenes may use the full width. Keep the real
object frame across the lower edge and no reserved device-shaped zone. The shipped feature graphic
is text-free — the scene plus one framed phone on the right with a real capture, and no title,
tagline, logo or copy on the left or anywhere else.
Across both formats, place decisive gameplay wherever it reads best, with many real sprite assets in a spill
across the full lower edge, varied in scale, height, rotation, overlap, and depth rather than arranged
as a tidy row or a lower-left pile.
Gameplay may appear on any panel, span the right two, or span all three. Noncritical board
structure may cross seams; protect faces, inscriptions and decisive symbols/outcomes from gaps.
A narrower field is valid when its proportions or readability require it. Preserve the
bottom spill and add recognizable flying/falling game objects at varied depths above it. Choose
an expressive marketing background when the theme benefits, with the far plane subordinate.
Matching `examples-games/` previews are default references; other relevant `examples/` images may also guide composition;
record what is borrowed and keep the actual game's assets, mechanics and Design DNA authoritative.
Store-screenshot generation preserves the actual game's existing menu, gameplay, splash, and shared
background assets and wiring. A runtime-background redesign is a separate, explicit opt-in; never
replace the game's background merely to make it match newly generated marketing art.

Unspecified classic slots use 3 reels × 3 visible rows (3×3), not 4×4. Preserve explicit or existing
variants. Joker defaults to a mischievous, slightly vicious theatrical trickster, playful rather than
an elegant courtier or horror character. Prefer x5/x10 reward coins where the actual game config and
theme support them; never invent multipliers or change balance solely for promotional art.

All agent responses must be in English, and every artifact the pipeline writes — design documents, concepts, reports, session state and commit messages — must be in English as well. Dart/Flutter code, file paths, class names and CLI commands are English by definition.

The generated game ships in English too: every player-facing string (menus, buttons, HUD, rules/paytable, win messages, empty states, disclaimer, responsible-play block) plus store metadata and screenshot captions. The only exception is an explicit user request for a different language — then the player-facing copy uses that language, the choice is recorded in `design/gdd/game-concept.md`, and everything else (identifiers, file names, comments, design docs, reports) stays English. Do not switch the game's language on your own initiative and do not infer it from the language the user is typing in. Before writing code, read `CLAUDE.md`, `.claude/docs/gambling-categories.md`, `.claude/docs/math-models.md`, `.claude/rules/responsible-gaming.md`, `.claude/rules/game-code.md`, `.claude/rules/engine-code.md`, `.claude/rules/ui-code.md`, `.claude/rules/anti-slop-design.md`, `.claude/docs/mobile-first-contract.md`, `.claude/docs/gameplay-screen-contract.md`, `.claude/rules/test-standards.md`, `.claude/rules/data-files.md`, `.claude/rules/design-docs.md`, `.claude/docs/technical-preferences.md`, `.claude/docs/coding-standards.md`, `.claude/docs/directory-structure.md`, and `.claude/docs/coordination-rules.md`.

Treat slash commands as manual runbooks. When a user types `/brainstorm`, `/autocreate`, `/team-dev`, `/code-review`, `/ui-audit`, `/emulator-test`, `/balance-check`, `/release-package`, `/release-checklist`, or another studio command, open the matching file in `.claude/skills/*/SKILL.md` and follow it. For specialized roles, use the persona briefs in `.claude/agents/*.md`. If needed, run helper checks with `bash tools/codex-hooks.sh <hook-name>`.

Note on `/autocreate`: it is the full Zero-to-Production pipeline, split across three sessions. It MUST run every phase without skipping:

1. Session 1 — pre-production: concept, classification (category C1-C6 + math model M1-M6), Production Plan, `flutter create --platforms android,ios,web`, assets and audio.
2. Session 2 (`autocreate-implement`, Phases 4 → 10) — implementation: code plus meta systems, content wiring, integration, `dart analyze lib/` looped until 0 errors, `flutter test` all green, feel pass, UI audit, curve-based balancing, crash prevention.
3. Session 3 (`autocreate-finalize`, Phases 10.5 → 12) — runtime and soak verification via Chrome CDP with auto-fix, `/playtest`, session state, release-engineering PREP (icons, splash, versioning, store metadata, CI — WITHOUT building the AAB/APK and without a keystore) and the final report.

`/autocreate` leaves the project release-ready but does NOT produce the downloadable archive. Building the release artifact is an explicit user action: `/release-package` takes the screenshots, runs `flutter build apk --release`, runs `flutter clean` and archives the whole project into a **`.zip`** in `project_zip/`.

Final deliverable of `/release-package`: `project_zip/<name>-<ts>.zip`, containing `source/`, `apk/app-release.apk`, `screenshots/` and `RELEASE_INFO.md`. The archive format is strictly `.zip` — the web service picks up `project_zip/*.zip` and registers it as the downloadable chat artifact.

Runtime verification runs on Chrome/Web by default and needs no emulator. The Android path is a fallback: if there is no Android device, `/emulator-test` tries to auto-start the first available AVD (`emulator -list-avds | head -1`). The final report mentions these commands as re-run options after manual edits.

If Codex CLI does not detect this project or local skills, run:

- `bash tools/setup-codex-cli.sh link`
- `bash tools/codex-doctor.sh`

Then restart Codex CLI.

## Automatic learning during studio work

After every concrete reusable failure, user correction, or verified faster approach, invoke
`.claude/skills/auto-learn/SKILL.md` and the `.claude/agents/auto-learner.md` role. Record evidence,
deduplicate by cause/remedy, implement a bounded improvement in an isolated worktree, validate
it, and push a `learning/*` proposal branch using `tools/auto_learn.py`. The owner has authorized
these proposal pushes in `.claude/auto-learning.json`; do not ask again. Only the owner approves
or merges. Never merge, force-push, publish unrelated work, or silently adopt unmerged rules.
Suggest or implement new skills, agents, scripts or rules only when the observed gap warrants
them; prefer correcting existing guidance. Keep RNG/math/compliance and quality gates intact.
Process pending findings during agent sessions; this is not an always-running background service.
An explicit pause or narrower user request overrides automatic learning. See
`.claude/docs/auto-learning.md` for commands, evidence requirements and recovery.

## Project Structure & Module Organization

This repository is a Flutter + Flame **gambling** game studio template. Core guidance lives in [`CLAUDE.md`](CLAUDE.md), with canonical rules in [`.claude/rules/`](.claude/rules), role briefs in [`.claude/agents/`](.claude/agents), reusable runbooks in [`.claude/skills/`](.claude/skills), and helper scripts in [`.claude/hooks/`](.claude/hooks). Codex compatibility docs live in [`.codex/`](.codex). Store design docs in `design/`, process notes in [`docs/`](docs), and session artifacts in [`production/`](production). Generated game apps should use `lib/game/`, `lib/components/`, `lib/systems/`, `lib/models/`, `lib/screens/`, `assets/`, and `test/`.

## Build, Test, and Development Commands

Use these commands after initializing or opening a Flutter app in this repo:

- `flutter create . --project-name game_app`: scaffold the Flutter project.
- `flutter pub get`: install dependencies.
- `dart format .`: format Dart files.
- `dart analyze` or `flutter analyze`: run static analysis.
- `flutter test`: run unit and widget tests.
- `bash tools/codex-hooks.sh detect-gaps`: check for missing required files.

## Coding Style & Naming Conventions

Use Dart 3.6+ with null safety, sealed classes, and pattern matching. Indent with 2 spaces. Prefer `const` and `final`; use `var` only when reassignment is required. Name files in `snake_case.dart`, classes in `PascalCase`, and fields or methods in `camelCase`. Keep gameplay constants in `lib/game/game_config.dart`; keep math-model numbers in the category's JSON config under `design/balance/` and load them — never duplicate a number in both. Use a logger instead of `print()`.

## Testing Guidelines

Place tests under `test/` and name them `*_test.dart`, for example `test/systems/weighted_rng_test.dart`. Cover pure game logic, state transitions, and edge cases. Every game must verify `Random.secure()` (the only sanctioned exception is C5's seeded run, which needs an ADR), stateless outcomes, exact payout arithmetic, and the category's math-model assumptions. Verify the model with `python3 tools/simulate_math.py --model [m1-m6] --config design/balance/<file>.json` — exit code 0 means PASS. Run `flutter test` before opening a pull request.

## Commit & Pull Request Guidelines

The repository does not yet have commit history, so follow the documented convention: use focused conventional commits such as `feat: add free spins overlay` or `fix: move reel speed constants into game config`. Pull requests should state the purpose, affected areas, test status, linked issues, and include screenshots or recordings for UI changes.

## Architecture & Safety Notes

Follow [`.claude/rules/game-code.md`](.claude/rules/game-code.md), [`.claude/rules/engine-code.md`](.claude/rules/engine-code.md), [`.claude/rules/ui-code.md`](.claude/rules/ui-code.md), and [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md). Do not `await` inside `update()` or `render()`, avoid allocations in hot paths, never use `Random()` for anything affecting an outcome, resolve the round outcome BEFORE the animation starts, and keep gameplay values out of inline magic numbers.

The compliance layer is a release blocker, not a nice-to-have: disclaimer ("virtual chips, no real money; success here does not imply success at real-money gambling"), responsible-play block in settings, and odds disclosure where the category requires it. No real-currency symbols next to a virtual balance.
