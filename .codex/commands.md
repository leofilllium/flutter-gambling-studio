# Codex Command Registry

When the user types a slash command (`$name` or `/name`), Codex must treat it as a call to the
matching runbook in `.claude/skills/`. For how the Claude mechanics (Agent tool, Skill tool,
hooks, vision, image generation) are adapted, see `AGENTS.md` → "Execution Model".

All commands inherit `.claude/docs/mobile-first-contract.md`: games begin with touch-first phone
UI/UX and responsively fill landscape, tablet, desktop, and Web viewports without a phone frame.

## The game production pipeline

| Command | Skill file | Purpose |
|---------|------------|---------|
| `/start` | `.claude/skills/start/SKILL.md` | Onboarding, routing, choosing the next step |
| `/brainstorm` | `.claude/skills/brainstorm/SKILL.md` | Interactive mini-game concept |
| `/auto-idea` | `.claude/skills/auto-idea/SKILL.md` | Auto-generate an idea from the 32 archetypes A–AF across 6 categories (incl. Classification, Reference Bar, Design DNA, Production Plan) |
| `/autocreate` | `.claude/skills/autocreate/SKILL.md` | **The Zero-to-Production pipeline.** In Codex the three "sessions" run as three checkpoints of ONE session: Phases 1–3.8 → handoff-1 → `autocreate-implement` (Phases 4–10.7) → handoff → `autocreate-finalize` (Phases 10.5–12). The "5 parallel agents" of Phase 4 become sequential persona passes A→E→D→B→C. Assets are PNG via GPT Image 2: the built-in tool, or `tools/gpt_image.py` in the headless CLI; simple assets go on a flat chroma-key background + `tools/cutout.py` |
| `/autocreate-implement` | `.claude/skills/autocreate-implement/SKILL.md` | Session 2 (implementation, Phases 4–10.7) — also the manual restart after a failure (`--resume`) |
| `/autocreate-finalize` | `.claude/skills/autocreate-finalize/SKILL.md` | Session 3 (runtime + soak, playtest, release-eng PREP, report) — also a manual restart |
| `/continue-project` | `.claude/skills/continue-project/SKILL.md` | Resume work from the current state |
| `/map-systems` | `.claude/skills/map-systems/SKILL.md` | Decompose the concept into systems |
| `/design-system` | `.claude/skills/design-system/SKILL.md` | A GDD for one individual mechanic |
| `/prototype` | `.claude/skills/prototype/SKILL.md` | A quick prototype of feel and juiciness |
| `/team-dev` | `.claude/skills/team-dev/SKILL.md` | Orchestrate a multi-disciplinary team (in Codex: sequential persona passes) |
| `/team-gambling` | `.claude/skills/team-gambling/SKILL.md` | Alias of `/team-dev` |
| `/add-feature` | `.claude/skills/add-feature/SKILL.md` | Add a new feature to an existing game |

## Assets

| Command | Skill file | Purpose |
|---------|------------|---------|
| `/generate-asset` | `.claude/skills/generate-asset/SKILL.md` | SVG by default; PNG only on explicit request |
| `/generate-png-asset` | `.claude/skills/generate-png-asset/SKILL.md` | In Codex, raster assets via GPT Image 2: the built-in tool, or `tools/gpt_image.py` in the headless CLI; flat chroma-key background + `tools/cutout.py` |
| `/svg-to-png` | `.claude/skills/svg-to-png/SKILL.md` | In Codex, SVG→PNG conversion via GPT Images 2.0 → GPT Images/default fallback |
| `/asset-review` | `.claude/skills/asset-review/SKILL.md` | **Vision review of the asset set** (contact sheets, criteria AR1–AR10, regeneration of rejects). Phase 3.6 in `/autocreate` |

## Quality and verification

| Command | Skill file | Purpose |
|---------|------------|---------|
| `/gate-check` | `.claude/skills/gate-check/SKILL.md` | Quality gate for a project stage |
| `/design-review` | `.claude/skills/design-review/SKILL.md` | Review of the GDD and the completeness of the spec |
| `/code-review` | `.claude/skills/code-review/SKILL.md` | Architectural and gameplay review |
| `/ui-audit` | `.claude/skills/ui-audit/SKILL.md` | Anti-slop audit (100+ checks) + auto-fix; measured against `.claude/docs/quality-bar.md` |
| `/emulator-test` | `.claude/skills/emulator-test/SKILL.md` | Runtime verification. **Default platform: Chrome/Web** (headless, `tools/web_verify.mjs`, no emulator). Android ADB is an explicit fallback via `--platform android` |
| `/playtest` | `.claude/skills/playtest/SKILL.md` | **Deep gameplay verification**: actually plays through CDP, checks P1–P10 (numbers change, win/lose paths, living board, progression, leaks). Phase 10.6 in finalize |
| `/balance-check` | `.claude/skills/balance-check/SKILL.md` | RTP, difficulty curve, full-curve content validation |
| `/perf-profile` | `.claude/skills/perf-profile/SKILL.md` | FPS, memory, particles, audio |
| `/tech-debt` | `.claude/skills/tech-debt/SKILL.md` | The technical debt register |
| `/hotfix` | `.claude/skills/hotfix/SKILL.md` | Urgent fix for a critical problem |
| `/architecture-decision` | `.claude/skills/architecture-decision/SKILL.md` | ADRs and architectural choices |

## Release

| Command | Skill file | Purpose |
|---------|------------|---------|
| `/release-checklist` | `.claude/skills/release-checklist/SKILL.md` | GO/NO-GO checklist (release-manager persona; takes the playtest and asset-review verdicts into account) |
| `/release-engineering` | `.claude/skills/release-engineering/SKILL.md` | Icons/splash/version/signed AAB/store metadata/CI. Inside the pipeline: only `--prep-only --no-keystore` |
| `/release-package` | `.claude/skills/release-package/SKILL.md` | Screenshots + release APK/AAB + `flutter clean` + an archive in `project_zip/`. **An explicit user action**, NOT an automatic call from the pipeline |
| `/store-screenshots` | `.claude/skills/store-screenshots/SKILL.md` | The gambling game's store showcase: a concept triptych around the key moment of a round (one panorama across N panels, with NO text, cut with a ~100px seam allowance so the store's gutter cannot bisect an object) + round frames in a phone frame with captions + feature graphic + icon/emblem (generated AND applied). Continuity gate: the game's real sprites and its real play field (`boardplate`, with yaw/pitch/depth so it is an object and not a decal) are placed into a layout draft (`triptych --pano-only`), and the finished panorama is RENDERED from that draft with the same files passed as reference images (`gpt_image.py edit --fidelity high`) — one picture, not a composite, with the app's own objects in it. An identity gate checks every object against its source file before anything downstream reads the art, and the panorama goes into the app as its background (`backdrop`) before frames are captured. Panel 1 is drawn as an empty hero berth and the real protagonist goes into it. Two sets — 1320×2868 (App Store 6.9″) and 1080×1920 9:16 (Google Play). Compliance gate: no currency symbols, no payout promises. Art from GPT Images 2.0, compositing, grading and typography from `tools/store_compose.py` → `project_zip/` |

## Execution rule

1. Open the named `SKILL.md`.
2. Run the steps in the order the skill gives, respecting each phase's exit criteria.
3. If the skill needs several roles, use persona passes over `.claude/agents/*.md`
   (see `agents.md`).
4. A Claude-specific step maps to its nearest equivalent in the Execution Model table in
   `AGENTS.md`:
   - Claude Agent tool → an inline persona pass / continuing in the same session
   - Claude Skill tool → open the SKILL.md as a runbook
   - Claude hook → `bash tools/codex-hooks.sh ...`
   - Vision analysis → Codex's built-in vision; PNG generation → GPT Image 2 built-in or
     `tools/gpt_image.py`. The absence of a built-in tool does not license an SVG fallback.
