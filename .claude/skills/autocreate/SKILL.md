---
name: autocreate
description: "Zero-to-Production factory for complete C1-C6 gambling games. Produces an English game concept and production plan, polished concept-derived 2.5D PNG assets in Codex, synthesized WAV audio, structured content/economy data, complete Flutter/Flame implementation, tests, compliance, math verification, runtime verification, and release preparation. The result is a complete publishable game, not a mini-demo."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Production Complete Game Factory

Build a complete production-ready gambling game. Do not ask the user questions: derive reasonable choices from the concept and record them.

All conversation, design documents, reports, prompts, code comments, generated game copy, store metadata, and screenshot captions must be in English. Use another player-facing language only when the user explicitly requests it and record that choice in the concept.

## Mandatory execution contract

The pipeline is split into three context sessions:

1. **Session 1 — pre-production (this skill, Phases 1–3.8):** concept, project bootstrap, structure and layout, assets, audio, content/economy data, then a handoff to Session 2.
2. **Session 2 — implementation (`autocreate-implement`, Phases 4–10):** game code, meta systems, content wiring, integration, build fixes, feel pass, tests, UI/compliance audit, balance, and crash prevention.
3. **Session 3 — finalize (`autocreate-finalize`, Phases 10.5–12):** runtime/soak verification, playtest, session state, release-engineering preparation, and final report.

Every session must hand control to the next one with the Agent tool. If Agent is unavailable, write the handoff and continue in the same session by reading the next skill. Do not copy full history into a phase agent; give it only the handoff path, skill path, and exit criterion.

The product target is Android phones and iPhone in portrait only. Chrome/Web is the primary
runtime **verification harness**, not a desktop product target. This pipeline prepares release
metadata and native branding but does not build an AAB/APK or upload keystore.
`/release-package` and the full `/release-engineering` run are explicit user actions.

Session 1 must produce:

- `design/gdd/game-concept.md` with classification, production plan, Design DNA, layout direction, screen map, data flow, complete loop, and edge cases.
- A Flutter project created for Web verification plus Android phones and iPhone, with the
  phone-only portrait target recorded in design artifacts.
- `design/structure.md` and `design/art-direction.md`.
- A budgeted, validated asset set and `design/asset-manifest.md`.
- Eight real sound-effect WAV files created by `tools/synth_sfx.py` (no background music).
- `design/asset-review.md` with an asset-cohesion verdict.
- Category-appropriate JSON content and economy data under `assets/data/` and `design/balance/`.
- `production/session-state/autocreate-handoff-1.md`, followed by Session 2.

Session 1 must not write gameplay code, screens, services, stubs, or TODO implementations. It must not claim that the game is complete.

## Asset policy

In Codex, create PNG assets with the built-in image-generation tool. In headless Codex where that tool is unavailable, use `python3 tools/gpt_image.py` with `gpt-image-2`. A missing built-in tool is not a reason to fall back to SVG. If both GPT Image 2 transports fail technically, retry through the default Codex image-generation path with the same prompt. SVG is allowed only outside Codex, after an explicit `--svg`, or after all PNG paths fail and the user approves the fallback.

The required visual profile is polished cartoon 2.5D casual-game art derived from the concept and Design DNA: clear bold silhouettes, rounded or slightly exaggerated forms, saturated theme-aware colors, smooth modeled gradients, glossy highlights, restrained star glints, and one consistent top-left light. Do not copy a reference set. Photorealistic product renders, flat clipart, and emoji/sticker art are forbidden.

Use `design/asset-manifest.md` as the budget ledger: at most 12 unique generated PNG sources plus 2 technical recovery calls. Generate only unique game silhouettes and scenes. Build UI, typography, icons, VFX, and safe variants in code or derive/reuse them locally.

## Phase 1 — concept

Run the logic from `.claude/skills/auto-idea/SKILL.md`, unless `--from-concept` was supplied. Save the result to `design/gdd/game-concept.md`.

The concept must include:

- Category C1–C6, math model M1–M6, archetype, compliance obligations, and English game language.
- A reference bar naming 2–3 successful games in the category, the specific feel/timing lesson from each, and the new game's differentiating hook. Never copy their content or art.
- A complete production plan with content volume, 2–3 modes, progression, virtual economy, achievements/daily loop, service abstractions, telemetry, and compliance.
- Context-derived Design DNA and layout archetype L1–L6.
- At least 12 connected screens, their data flow, the complete game loop, and all failure/edge states.
- A phone-only portrait declaration following `.claude/docs/mobile-phone-contract.md`; no
  tablet/iPad, desktop, wide-screen, or landscape layout plan.

If `--idea-only` is supplied, stop only after writing and reporting the concept.

## Phase 2 — Flutter project bootstrap

Web must be included as the preview/verification harness. Android phones and iPhone are the
shipping product targets; no desktop platform is created.

```bash
flutter create . --project-name game_app --platforms web,android,ios --org com.gamestudio

if [[ ! -f web/index.html ]]; then
  echo "Web project was not created; stopping."
  exit 1
fi
```

Immediately apply the native half of `.claude/docs/mobile-phone-contract.md` to the scaffold:
Android launcher portrait, iOS portrait-only orientations with no iPad block, and
`TARGETED_DEVICE_FAMILY = 1` in every Xcode build configuration. Session 2's UI pass must add the
Flutter `SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])` lock before
`runApp` and retain a centered unframed canvas capped at 430 logical pixels on wide Web hosts.

Use Flutter 3.27+, Dart 3.6+, Flame 1.18.x, `flame_audio`, `flame_svg`, `google_fonts`, and `shared_preferences`. Register these directories in `pubspec.yaml`:

```yaml
flutter:
  assets:
    - assets/images/sprites/
    - assets/images/ui/
    - assets/images/backgrounds/
    - assets/audio/sfx/
    - assets/data/
```

Do not hardcode studio-default fonts. Select display and body fonts from the game's Design DNA and use `google_fonts`.

Read `.claude/docs/directory-structure.md`, choose one V1–V5 structure, create the directories, and write the exact path map to `design/structure.md`. Read `.claude/docs/mobile-phone-contract.md`, `.claude/docs/layout-archetypes.md` and `.claude/docs/gameplay-screen-contract.md`, choose L1–L6 from the concept, and write screen-specific composition rules to `design/art-direction.md`. The art-direction file must specify a portrait-phone composition at 360×640, 360×800, 390×844 and 430×932; how the live field fills the viewport; where the integrated HUD/control deck sits; and how the 55% area / normal 88% width thresholds are met. It must not plan a nested mini-game, page-scrolling core loop, or tablet/desktop/landscape variant.

## Phase 3 — asset generation and validation

Detect the environment without asking the user. Write `design/asset-format.md`, `design/asset-prompts.md`, and `design/asset-manifest.md` before generating assets.

Each manifest row must include a logical ID, output path, dimensions, class (`generate`, `derive`, `code`, or `reuse`), source ID, generator, prompt/style anchor, attempt count, SHA-256, alpha requirement, and validation verdict.

In PNG mode:

- Generate sprites/symbols on a flat chroma-key background with no text, border, frame, UI, or baked shadow.
- Keep the full set consistent in light direction, materials, palette, perspective, and detail.
- Use one game background by default; derive menu variants locally unless a genuinely different world/composition is required.
- Build ordinary controls, panels, icons, typography, shadows, glows, and VFX in code.
- Remove backgrounds only with `python3 tools/cutout.py`; never use fuzz-based global color transparency.

```bash
python3 tools/cutout.py --dir assets/images/sprites --check
python3 tools/cutout.py --dir assets/images/ui --check
flutter pub get
```

Validate that every generated file is a real PNG, required sprites/icons have clean alpha, no accidental SVG files exist in PNG mode, every declared asset exists, and the prompt/manifest ledgers are complete.

Outside Codex, the SVG fallback must use valid `<svg>` documents with a `viewBox`, consistent Design DNA, and no baked text. Validate every referenced path with `flutter pub get`.

## Phase 3.5 — real audio synthesis

Derive the mood from the concept and synthesize playable 16-bit/44.1 kHz WAV files:

```bash
python3 tools/synth_sfx.py --from-concept --sfx-dir assets/audio/sfx

ls -1 assets/audio/sfx/*.wav 2>/dev/null | wc -l
```

Required names: `sfx_button`, `sfx_navigate`, `sfx_action`, `sfx_coin`, `sfx_error`, `sfx_win_small`, `sfx_win_big`, `sfx_win_mega`. Expect **8** files.

**Sound effects only — do not synthesize background music.** The generator can
render a BGM bed behind `--with-bgm`, but the result is weak next to the rest of
the game, so a game ships with SFX and silence unless the user explicitly asks
for music. Do not add `assets/audio/bgm/` to the pubspec `assets:` list: an asset
directory that does not exist is a hard `flutter build` failure. Ship the settings
screen's music toggle anyway — it costs nothing and means adding music later is a
content change, not a UI change. Silence here is the intended result: never report
it as a missing asset, a gap, or a TODO.

## Phase 3.6 — asset cohesion review

Follow `.claude/skills/asset-review/SKILL.md` as the art director. Create contact sheets including a mandatory 64 px gameplay-size sheet, evaluate AR1–AR10, and write `design/asset-review.md`. Fix only failed assets. Spend a recovery call only when the generated source itself is defective.

Exit only when the review records PASS, or when every REGENERATE item has been corrected and re-reviewed.

## Phase 3.7 — content and economy data

Generate data before implementation so Session 2 builds against a stable schema. Keep all numeric content in JSON as the single source of truth.

- Always create the category's canonical math config in `design/balance/`, using `.claude/docs/templates/math-configs/` as the baseline.
- C1/C2: `assets/data/bet-tiers.json` with bet levels, limits, and bonus-mode parameters.
- C3: `assets/data/stage-config.json` with more than one unlock/season stage.
- C4: `assets/data/banners.json` with more than one banner, pools, rates, and rotation.
- C5: `assets/data/run-config.json` with round thresholds, at least three modifiers, and shop prices.
- C6: `assets/data/board-config.json` with more than one board/risk profile.
- Economy: `assets/data/economy-config.json` with starting balances, catalog prices, and progression/daily/achievement rewards.
- Record 2–3 modes in the concept and handoff.

Parse every JSON file before exit. Do not duplicate these values as inline constants in the future game code.

## Phase 3.8 — handoff to Session 2

Write `production/session-state/autocreate-handoff-1.md` with:

- Timestamp, game name, category, archetype, math model, package ID, structure variant, layout archetype, audio mood, and game language.
- Links to the concept, production plan, structure, art direction, asset format/prompts/manifest/review, balance configs, and content data.
- Counts and paths for generated/derived assets, WAV files, levels/stages/banners/boards, economy entries, and modes.
- A checklist confirming that Session 1 is complete and that gameplay implementation has not started.
- Session 2's required exit criteria: `dart analyze` with zero errors, green tests, complete content wiring, passed UI/compliance audit, a passed full-viewport gameplay-screen gate at the required sizes, verified balance, and 20/20 crash-prevention checks.
- A phone-contract checklist: native portrait/iPhone-only scaffold applied; Session 2 must verify
  the Flutter portrait lock and all four phone viewports with no non-phone layout branches.

Then start a clean-context agent with this instruction:

```text
You are Session 2 of /autocreate. First read:
1. production/session-state/autocreate-handoff-1.md
2. .claude/skills/autocreate-implement/SKILL.md
3. design/structure.md, design/art-direction.md, and design/gdd/game-concept.md

Execute Phases 4–10 exactly as specified by autocreate-implement. Preserve Session 1's concept, assets, audio, balance, and content data. Exit only with zero analyzer errors, green tests, completed content wiring, a passed UI/compliance audit, verified full-curve balance, and 20/20 crash prevention. Then write autocreate-handoff.md and start Session 3 with autocreate-finalize.
```

If Agent is unavailable, continue locally by reading `autocreate-implement/SKILL.md`. If Session 2 fails, report the exact failure and the manual restart command `/autocreate-implement`; never claim the game is ready.

## Final pipeline quality gates

The full pipeline succeeds only when:

- The complete game is playable in English and all screens, buttons, navigation, data, modes, progression, economy, audio, animation, and edge states work.
- `dart analyze` reports zero errors and `flutter test` is green.
- The declared M1–M6 model passes its verifier over the complete content curve.
- Runtime verification and playtest produce at least five screenshots plus `REPORT.md`, with no exceptions or severe layout defects. The 360×640, 360×800, 390×844 and 430×932 phone matrix must pass `.claude/docs/mobile-phone-contract.md`; idle and active gameplay captures must pass `.claude/docs/gameplay-screen-contract.md`: dominant integrated field, core controls visible without scrolling, and usable buttons.
- `production/session-state/active.md` contains the current runtime verdict.
- Icons, splash, version, store metadata, and CI preparation are complete.

Release artifacts remain an explicit next action: `/release-package` for the downloadable project archive/APK, or full `/release-engineering` for a signed AAB.
