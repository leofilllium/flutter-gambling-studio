# Repository Guidelines

## Codex CLI Instructions

All agent responses must be in Russian. Keep Dart/Flutter code, file paths, class names, and CLI commands in English. Before writing code, read `CLAUDE.md`, `.claude/rules/game-code.md`, `.claude/rules/engine-code.md`, `.claude/rules/ui-code.md`, `.claude/rules/anti-slop-design.md`, `.claude/rules/test-standards.md`, `.claude/rules/data-files.md`, `.claude/rules/design-docs.md`, `.claude/docs/technical-preferences.md`, `.claude/docs/coding-standards.md`, `.claude/docs/directory-structure.md`, and `.claude/docs/coordination-rules.md`.

Treat slash commands as manual runbooks. When a user types `/brainstorm`, `/autocreate`, `/team-dev`, `/code-review`, `/ui-audit`, `/emulator-test`, `/balance-check`, or another studio command, open the matching file in `.claude/skills/*/SKILL.md` and follow it. For specialized roles, use the persona briefs in `.claude/agents/*.md`. If needed, run helper checks with `bash tools/codex-hooks.sh <hook-name>`.

If Codex CLI does not detect this project or local skills, run:

- `bash tools/setup-codex-cli.sh link`
- `bash tools/codex-doctor.sh`

Then restart Codex CLI.

## Project Structure & Module Organization

This repository is a Flutter + Flame game studio template. Core guidance lives in [`CLAUDE.md`](/Users/leofillium/codex-game/CLAUDE.md), with canonical rules in [`.claude/rules/`](/Users/leofillium/codex-game/.claude/rules), role briefs in [`.claude/agents/`](/Users/leofillium/codex-game/.claude/agents), reusable runbooks in [`.claude/skills/`](/Users/leofillium/codex-game/.claude/skills), and helper scripts in [`.claude/hooks/`](/Users/leofillium/codex-game/.claude/hooks). Codex compatibility docs live in [`.codex/`](/Users/leofillium/codex-game/.codex). Store design docs in [`design/`](/Users/leofillium/codex-game/design), process notes in [`docs/`](/Users/leofillium/codex-game/docs), and session artifacts in [`production/`](/Users/leofillium/codex-game/production). Generated game apps should use `lib/game/`, `lib/components/`, `lib/systems/`, `lib/models/`, `lib/screens/`, `assets/`, and `test/`.

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

Use Dart 3.6+ with null safety, sealed classes, and pattern matching. Indent with 2 spaces. Prefer `const` and `final`; use `var` only when reassignment is required. Name files in `snake_case.dart`, classes in `PascalCase`, and fields or methods in `camelCase`. Keep gameplay constants in `lib/game/game_config.dart` or a genre-specific config file. Use a logger instead of `print()`.

## Testing Guidelines

Place tests under `test/` and name them `*_test.dart`, for example `test/systems/weighted_rng_test.dart`. Cover pure game logic, state transitions, and edge cases. Gambling games must verify `Random.secure()`, stateless outcomes, and RTP assumptions. Run `flutter test` before opening a pull request.

## Commit & Pull Request Guidelines

The repository does not yet have commit history, so follow the documented convention: use focused conventional commits such as `feat: add free spins overlay` or `fix: move reel speed constants into game config`. Pull requests should state the purpose, affected areas, test status, linked issues, and include screenshots or recordings for UI changes.

## Architecture & Safety Notes

Follow [`.claude/rules/game-code.md`](/Users/leofillium/codex-game/.claude/rules/game-code.md), [`.claude/rules/engine-code.md`](/Users/leofillium/codex-game/.claude/rules/engine-code.md), and [`.claude/rules/ui-code.md`](/Users/leofillium/codex-game/.claude/rules/ui-code.md). Do not `await` inside `update()` or `render()`, avoid allocations in hot paths, never use `Random()` in gambling logic, and keep gameplay values out of inline magic numbers.
