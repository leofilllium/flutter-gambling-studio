# Repository Guidelines — Flutter Gambling Studio

## Codex CLI Instructions

This is a **gambling-only** game studio: every concept must fall into one of six categories (C1 social casino, C2 casino originals, C3 spin-to-progress hybrids, C4 gacha/loot-box, C5 casino roguelike, C6 coin pusher/plinko) and declare a verifiable math model (M1-M6). Puzzles, runners, shooters and clickers are out of scope.

All generated game art must use polished cartoon 2.5D casual-game illustration with bold
silhouettes, rounded/exaggerated forms, saturated theme-aware color, smooth modeled
gradients, glossy highlights, restrained star glints, and one consistent top-left light.
Derive the visual world, shapes, materials, details, and palette independently from each
game's concept and Design DNA. Do not depend on a reference folder or copy symbols from
other games. Photorealistic/product-render assets, flat vector clipart, and emoji/sticker
styling are out of scope.

All agent responses must be in Russian. Keep Dart/Flutter code, file paths, class names, and CLI commands in English. Before writing code, read `CLAUDE.md`, `.claude/docs/gambling-categories.md`, `.claude/docs/math-models.md`, `.claude/rules/responsible-gaming.md`, `.claude/rules/game-code.md`, `.claude/rules/engine-code.md`, `.claude/rules/ui-code.md`, `.claude/rules/anti-slop-design.md`, `.claude/rules/test-standards.md`, `.claude/rules/data-files.md`, `.claude/rules/design-docs.md`, `.claude/docs/technical-preferences.md`, `.claude/docs/coding-standards.md`, `.claude/docs/directory-structure.md`, and `.claude/docs/coordination-rules.md`.

Treat slash commands as manual runbooks. When a user types `/brainstorm`, `/autocreate`, `/team-dev`, `/code-review`, `/ui-audit`, `/emulator-test`, `/balance-check`, `/release-package`, `/release-checklist`, or another studio command, open the matching file in `.claude/skills/*/SKILL.md` and follow it. For specialized roles, use the persona briefs in `.claude/agents/*.md`. If needed, run helper checks with `bash tools/codex-hooks.sh <hook-name>`.

Note on `/autocreate`: это полный конвейер Zero-to-Android-APK. Он ОБЯЗАН выполнить ВСЕ 12 фаз без пропусков:
1. `flutter create --platforms android,ios,web` (Android — primary)
2. Сгенерировать ассеты
3. Написать код (4 параллельных агента)
4. `dart analyze lib/` → цикл исправлений до 0 errors
5. `flutter test` → все зелёные
6. **Фаза 10.5**: автоматически запустить AVD (если не запущен) и `/emulator-test --quick` — скриншоты, vision-анализ, auto-fix
7. **Фаза 10.6**: автоматически запустить `/release-package` — финальные скриншоты + `flutter build apk --release` + `flutter clean` + архивирование в **`.tar.gz`** в `project_zip/`

Финальный deliverable: `project_zip/<name>-<ts>.tar.gz` должен содержать `source/`, `apk/app-release.apk`, `screenshots/`, `RELEASE_INFO.md`. Формат архива — строго `.tar.gz` (НЕ `.zip`).

Эти фазы **НЕ** оставляются пользователю — они часть конвейера. Если нет Android-девайса, `/autocreate` пытается автозапустить первый доступный AVD (`emulator -list-avds | head -1`). В финальном отчёте эти команды упоминаются также как опции повторного запуска после ручных правок.

If Codex CLI does not detect this project or local skills, run:

- `bash tools/setup-codex-cli.sh link`
- `bash tools/codex-doctor.sh`

Then restart Codex CLI.

## Project Structure & Module Organization

This repository is a Flutter + Flame **gambling** game studio template. Core guidance lives in [`CLAUDE.md`](/Users/leofillium/codex-game/CLAUDE.md), with canonical rules in [`.claude/rules/`](/Users/leofillium/codex-game/.claude/rules), role briefs in [`.claude/agents/`](/Users/leofillium/codex-game/.claude/agents), reusable runbooks in [`.claude/skills/`](/Users/leofillium/codex-game/.claude/skills), and helper scripts in [`.claude/hooks/`](/Users/leofillium/codex-game/.claude/hooks). Codex compatibility docs live in [`.codex/`](/Users/leofillium/codex-game/.codex). Store design docs in [`design/`](/Users/leofillium/codex-game/design), process notes in [`docs/`](/Users/leofillium/codex-game/docs), and session artifacts in [`production/`](/Users/leofillium/codex-game/production). Generated game apps should use `lib/game/`, `lib/components/`, `lib/systems/`, `lib/models/`, `lib/screens/`, `assets/`, and `test/`.

## Build, Test, and Development Commands

Use these commands after initializing or opening a Flutter app in this repo:

- `flutter create . --project-name game_app`: scaffold the Flutter project.
- `flutter pub get`: install dependencies.
- `dart format .`: format Dart files.
- `dart analyze` or `flutter analyze`: run static analysis.
- `flutter test`: run unit and widget tests.
- `flutter run`: launch the game locally.
- `bash tools/codex-hooks.sh detect-gaps`: check for missing required files.

## Coding Style & Naming Conventions

Use Dart 3.6+ with null safety, sealed classes, and pattern matching. Indent with 2 spaces. Prefer `const` and `final`; use `var` only when reassignment is required. Name files in `snake_case.dart`, classes in `PascalCase`, and fields or methods in `camelCase`. Keep gameplay constants in `lib/game/game_config.dart`; keep math-model numbers in the category's JSON config under `design/balance/` and load them — never duplicate a number in both. Use a logger instead of `print()`.

## Testing Guidelines

Place tests under `test/` and name them `*_test.dart`, for example `test/systems/weighted_rng_test.dart`. Cover pure game logic, state transitions, and edge cases. Every game must verify `Random.secure()` (the only sanctioned exception is C5's seeded run, which needs an ADR), stateless outcomes, exact payout arithmetic, and the category's math-model assumptions. Verify the model with `python3 tools/simulate_math.py --model [m1-m6] --config design/balance/<file>.json` — exit code 0 means PASS. Run `flutter test` before opening a pull request.

## Commit & Pull Request Guidelines

The repository does not yet have commit history, so follow the documented convention: use focused conventional commits such as `feat: add free spins overlay` or `fix: move reel speed constants into game config`. Pull requests should state the purpose, affected areas, test status, linked issues, and include screenshots or recordings for UI changes.

## Architecture & Safety Notes

Follow [`.claude/rules/game-code.md`](.claude/rules/game-code.md), [`.claude/rules/engine-code.md`](.claude/rules/engine-code.md), [`.claude/rules/ui-code.md`](.claude/rules/ui-code.md), and [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md). Do not `await` inside `update()` or `render()`, avoid allocations in hot paths, never use `Random()` for anything affecting an outcome, resolve the round outcome BEFORE the animation starts, and keep gameplay values out of inline magic numbers.

The compliance layer is a release blocker, not a nice-to-have: age gate, disclaimer ("virtual chips, no real money; success here does not imply success at real-money gambling"), responsible-play block in settings, and odds disclosure where the category requires it. No real-currency symbols next to a virtual balance.
