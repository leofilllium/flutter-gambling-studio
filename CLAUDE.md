# Flutter Gambling Studio

> A specialised studio for building **gambling mini-games** on Flutter + Flame
> through coordinated Claude Code agents.
>
> For OpenAI Codex, use `AGENTS.md` and `.codex/` as a compatibility layer over these same rules.

## What the studio specialises in

**The studio builds gambling games only.** This is not a general-purpose mini-game studio:
puzzles, runners, shooters, tetris clones and clickers are out of scope. Every concept must
fall into one of the six gambling categories below and must have a **declared mathematical
model** that can be verified by a simulation run.

**Always virtual.** No game accepts or pays out real money. Virtual currency never converts
back. This is not a "safety feature" — it is the frame the whole studio exists inside. See
`.claude/rules/responsible-gaming.md`.

## Visual standard for assets

All game imagery uses a polished cartoon 2.5D casual-game language: bold readable silhouettes,
rounded or slightly exaggerated forms, a saturated theme-aware palette, smooth modelled
gradients, clean colour or gold edging, glossy highlights, restrained star glints and one
consistent light from the top left.

The theme, characters, objects, materials, shapes, details and colours are all derived
independently from the concept and Design DNA of the specific game. Do not depend on a
reference folder and do not copy symbols from other games. Photorealism, product-shot
rendering, flat vector clipart and emoji/sticker styling are not allowed.

## Technology stack

- **Engine**: Flutter 3.27+ / Flame 1.18+
- **Language**: Dart 3.6+ (null-safe, sealed classes, pattern matching)
- **Specialisation**: mobile-first gambling mini-games with responsive full-viewport layouts
- **Product platforms**: Android, iOS/iPadOS, and Web; phone UI/UX is the design baseline
- **Rendering**: Flutter Impeller (Android/iOS), CanvasKit/Skia for Web
- **Mathematics**: `tools/simulate_math.py` — the verifier for all six models

> **You are the creative director and producer.** The agents implement your idea.
> Run `/start` to begin.

## Language

**ALL work is produced in English.** This is a hard requirement for every agent.

That covers agent responses and questions, design documents, concepts, GDDs, reports,
session state and commit messages — as well as Dart/Flutter code, file paths, class names
and CLI commands, which are English by definition.

**The game itself ships in English too.** Every string the player sees — menus, buttons,
HUD labels, rules and paytable, win messages, empty states, achievement names, the age gate,
the disclaimer and the whole responsible-play block, plus store metadata and screenshot
captions — is written in English by default.

**The single exception is an explicit user request.** If the user asks for the game in another
language, produce the player-facing copy in that language and record the choice in
`design/gdd/game-concept.md`. Even then, everything else stays English: code identifiers,
file and asset names, comments, design documents, reports and session state. Never switch the
game's language on your own initiative, and never infer it from the language the user happens
to be typing in — only an explicit request counts.

## The six gambling categories

| ID | Category | Icon | Core | Balance metric | Archetypes |
|----|----------|------|------|----------------|------------|
| **C1** | Social Casino | 🎰 | A casino floor simulated with virtual chips | RTP 95–97% | A–H |
| **C2** | Casino Originals / Instant-Win | ⚡ | Instant round, live multiplier, cash-out | RTP 96–99% | I–P |
| **C3** | Spin-to-Progress Hybrids | 🏰 | The spin is the energy source for a casual meta game | Source/sink economy | Q–U |
| **C4** | Gacha & Loot-Box | 🎁 | Pulls from a banner with rarities and pity | Rates + pity | V–Y |
| **C5** | Casino Roguelike & Strategy | 🃏 | Casino mechanics as a roguelike's combat system | Run win-rate 25–40% | Z–AC |
| **C6** | Coin Pusher & Plinko | ⚙️ | Physics as the outcome generator | Empirical RTP 95–97% | AD–AF |

A full description of every category, its required systems, its compliance profile and its
archetypes lives in `.claude/docs/gambling-categories.md`. That is the canonical reference —
it outranks memory.

@.claude/docs/gambling-categories.md

## Archetypes A–AF (short index)

| Category | Archetypes |
|----------|------------|
| **C1** 🎰 | **A** 3×3 slot · **B** 5×3 video slot + free spins · **C** scatter-pays/cluster · **D** Hold & Spin · **E** video poker · **F** blackjack · **G** roulette · **H** bingo |
| **C2** ⚡ | **I** crash · **J** mines · **K** dice · **L** hi-lo · **M** tower climb · **N** keno · **O** scratch · **P** bonus pick |
| **C3** 🏰 | **Q** build-and-raid slot · **R** board-move dice · **S** prize-wheel hub · **T** sticker album · **U** raid & shield |
| **C4** 🎁 | **V** banner pull · **W** card packs · **X** case opener · **Y** gashapon |
| **C5** 🃏 | **Z** poker deckbuilder · **AA** slot-reel roguelike · **AB** dice-builder · **AC** push-your-luck |
| **C6** ⚙️ | **AD** coin pusher · **AE** plinko · **AF** pachinko |

## Quick start

```
/start             — Orientation: where to begin right now
/brainstorm        — Interactive gambling game concept generation
/auto-idea         — Autonomous generation of a finished idea (no questions)
/autocreate        — Zero-to-Production: a complete working game from one command
                     (concept + math model + assets + code + tests + audit + balancing)
```

## The full path to a finished game

```
Idea → Concept → Math model → Design → Gate → Code → UI audit → Runtime → Gate → QA → Gate → Release
  │       │          │          │       │      │      │           │        │      │      │       │
/start /brain-   /balance-  /design-  /gate  /team- /ui-      /emulator- /code- /balance /gate /release-
       storm     check      system    check  dev    audit     test       review  check   check checklist
```

## Studio commands (skills)

### Building a game (in order)

| Command | Description | When to use |
|---------|-------------|-------------|
| `/start` | Onboarding and routing | At the start of every session |
| `/brainstorm [hint]` | Interactive gambling game concept | No idea yet, or one that needs shaping |
| `/auto-idea` | Autonomous concept (32 archetypes A–AF across 6 categories + Variety Dimensions) | Fast generation with no questions |
| `/auto-idea --list` | Show every archetype A–AF by category | Choosing an archetype by hand |
| `/auto-idea --archetype [A-AF]` | Expand one specific archetype | You already have a preference |
| `/auto-idea --category [C1-C6]` | A random archetype inside one category | You know the category, not the mechanic |
| `/autocreate` | Zero-to-Production: a complete working game, no questions | You want a fully working game |
| `/autocreate --from-concept` | Implement a saved idea | After `/auto-idea` |
| `/map-systems` | Decompose into technical systems | After the concept |
| `/design-system [system]` | A GDD for one game system | One system at a time |
| `/prototype [mechanic]` | A juiciness / feel prototype | Before full implementation |
| `/generate-asset [type] [name]` | SVG assets by default, no format question | Before writing code |
| `/generate-asset [type] [name] --png` | PNG/image generation; GPT Image 2 built-in, or `tools/gpt_image.py` in headless Codex CLI | When you need raster |
| `/generate-png-asset [description]` | PNG via GPT Image 2; the headless bridge uses the per-user API key, and simple assets go through a local cutout | High-quality raster, fast |
| `/generate-png-asset --batch "items"` | Batch-generate several PNGs at once | Generating all assets |
| `/generate-png-asset --from-concept` | Generate every PNG from the concept | After design |
| `/svg-to-png [path]` | Convert SVG to PNG via Codex GPT Images 2.0 → GPT Images/default fallback | You have SVG, you need raster |

### Quality gates (pass one before every transition)

| Command | Description | When |
|---------|-------------|------|
| `/gate-check concept` | Is the concept ready (category + math model + compliance)? | After brainstorm |
| `/gate-check design` | Is the GDD ready for implementation? | Before the programming team |
| `/gate-check code` | Is the code ready for QA? | After coding is finished |
| `/gate-check qa` | Is it ready for release? | After all tests |

### Review and quality

| Command | Description |
|---------|-------------|
| `/code-review` | Full code review (architecture, Flame API, RNG integrity, state, tests) |
| `/ui-audit` | Automatic UI/UX audit for anti-slop quality + compliance screens + auto-fix |
| `/asset-review` | Vision review of the asset set for consistency (style/light/palette/readability, AR1–AR10) + regeneration of rejects (art-director agent) |
| `/emulator-test` | Runtime verification on Chrome/Web (primary) or ADB/emulator: launch, screenshots, vision analysis, log parsing, automatic bug fixes |
| `/playtest` | Deep GAMEPLAY verification via CDP: actually plays N rounds, checks that the balance changes, that win/lose paths work, that cash-out is honest, that the board is alive (P1–P10) |
| `/design-review` | GDD review for completeness and mathematical correctness |
| `/balance-check` | Math model verification: `tools/simulate_math.py` against the category's model M1–M6 |
| `/release-checklist` | Final GO/NO-GO checklist before release, including compliance (release-manager agent) |
| `/release-engineering` | Ship engineering: app icons (adaptive + iOS) + native splash + versioning + **signed AAB** + iOS scaffold + store metadata (with the mandatory compliance fields) + CI |
| `/release-package` | Release packaging: screenshots of every screen + release APK/AAB + `flutter clean` + a `.zip` in `project_zip/` |
| `/store-screenshots` | A casino-grade store showcase: mechanic-first tension/reveal/celebration composition in the current game's Design DNA, never a generic neon reskin. Includes a text-free concept panorama sliced into panels + real round frames inside a secondary phone frame + feature graphic + applied app icon and emblem. **Storefront ↔ game continuity is a blocking gate**: the game's real sprites and its real play field (`boardplate`, stood up in perspective) are placed into a layout draft and then handed back to the image model as reference images, so the panorama is **one rendered picture** whose objects are the app's own — never a flat paste-up and never a symbol the model invented — and that panorama is wired into the app as its background *before* frames are captured, so the listing and the app show one world. Panel 1 is composed as a berth for a large protagonist whose complete silhouette, including held props, stays inside the first panel; real game objects form a cropped foreground band across the bottom and the remainder fall through the full picture. The far background stays bright, broad and smooth so the subjects lead, while saturation and controlled overexposure are measured. A strict final-art gate blocks dark or hyper-detailed panoramas, generic furniture standing in for game objects, weak bottom framing, missing glare, and hero bounds that cross a seam. **The panels reassemble into the whole picture**: the cuts are butt-joined, so nothing is discarded between them, no panel ends mid-object, and laying them side by side gives the panorama back exactly. What protects a seam is where it falls — the tiling slides until the cuts land on the picture's quietest columns, and the art is asked for a calm corridor at each boundary. A seam allowance that throws a strip away at each cut is opt-in (`--gutter`), for a publisher who asks the panels to line up across the store's carousel gap. Two sets: **1320×2868** for App Store Connect (iPhone 6.9″) and **1080×1920** 9:16 for Google Play. Compliance and gameplay-layout gates → a `.zip` in `project_zip/` |

### Diagnostics and debt

| Command | Description |
|---------|-------------|
| `/perf-profile [area]` | FPS / memory / particle profiling |
| `/tech-debt` | Technical debt scan and register |
| `/hotfix [description]` | Emergency fix for critical bugs |
| `/architecture-decision [decision]` | Create an ADR for a significant decision (including a change of math model) |

### Teamwork

| Command | What it orchestrates |
|---------|----------------------|
| `/team-dev [description]` | game-designer + mechanics-programmer + juice-artist + sound-designer + qa |
| `/team-gambling [description]` | Alias of `/team-dev` |

### Working with an existing project

| Command | Description |
|---------|-------------|
| `/continue-project` | Continue from where work stopped |
| `/add-feature [feature]` | Add a feature to a finished game |

## Studio agents

### Tier 1 — Directors (high-level decisions)

| Agent | Role |
|-------|------|
| `creative-director` | Overall vision, concept, game category, creative decisions |
| `technical-director` | Architectural decisions, ADRs, resolving technical conflicts |

### Tier 2 — Gambling mechanics specialists

| Agent | Role |
|-------|------|
| `game-mathematician` | **Owner of the math model**: RTP, weights, house edge, pity, economy, run win-rate. The only agent who changes the model's numbers |
| `game-designer` | GDD: round mechanics, bets, bonuses, progression, compliance screens |
| `mechanics-programmer` | Implementation: WeightedRNG on `Random.secure()`, stateless outcomes, paylines, multipliers, physics |
| `meta-systems-programmer` | Meta systems: SaveService, Economy, Progression, Achievements + Analytics/Ads/IAP/RemoteConfig abstractions (no-op). Turns one round into a full game |
| `art-director` | Visual consistency of the asset set: vision review (uniform style/light/palette, readability at 64px, AR1–AR10), regeneration of rejects |
| `juice-artist` | VFX, particles, anticipation / near-miss / win-celebration animations — what makes a round feel "juicy" |

### Tier 3 — Core specialists

| Agent | Role |
|-------|------|
| `lead-programmer` | Architecture, code review |
| `performance-analyst` | FPS, memory, Flame optimisation, profiling |
| `ui-programmer` | Flutter screens, HUD, bet panels, compliance screens |
| `sound-designer` | Audio: bet, spin, stop, win, near-miss |
| `qa-tester` | Test cases, edge cases, RNG distribution, state leakage |
| `release-manager` | Release preparation, compliance audit |

## Critical rules (game integrity)

> Breaking these rules blocks the release. In a gambling studio they are **unconditional** —
> there are no "genres they don't apply to".

1. **RNG**: ONLY `Random.secure()` — no `math.Random()`, no `Random()`.
   The single exception is the seeded run determinism in C5 (model M5), and it must be
   recorded in an ADR.
2. **Stateless Outcomes**: the round result is computed BEFORE the animation starts.
   The animation only plays back an outcome that is already known.
3. **GameState**: a sealed class — no boolean flags.
4. **GameConfig**: every game constant lives in the config file (`game_config.dart`),
   and the math model's numbers live in the model's JSON config.
5. **No hardcoded probability**: no `if (rng < 0.1) win!`. Weights are read from the config.
6. **No magic numbers**: no hardcoded gameplay parameters outside the config.
7. **Double protection**: the main action button is locked during the animation (300 ms debounce).
8. **The math model is verified**: `tools/simulate_math.py` returns PASS for the category's model.
   A game without a green run does not ship.
9. **The compliance layer is in place**: age gate, disclaimer, responsible play, odds disclosure
   where required — see `.claude/rules/responsible-gaming.md`.

@.claude/docs/math-models.md

@.claude/rules/responsible-gaming.md

## Collaboration protocol

**User-directed collaboration, not autonomous execution.**

The pattern: **Question → Options → Decision → Draft → Approval**

- Agents MUST ask "May I write this to [path]?" before Write/Edit
- Exception: `/autocreate` and `/auto-idea` run autonomously — that is deliberate

## Contextual Design (human-crafted UI)

> Every visual decision follows from the context of THIS specific game — its theme, mood and
> mechanics. There is no single template. Neon trapezoids for EVERY game are just as much slop
> as purple gradients. **"Gambling" does not mean "dark neon and gold"**: a bingo room can be
> warm and papery, a gashapon pastel and toy-like, a roguelike strict and typographic.
> The test: if the UI could be moved to another game unchanged, the design failed.
>
> Variety rests on TWO independent axes:
> - **Design DNA** (the look: palette/fonts/shapes/motion) — from the game's theme. See anti-slop-design.md.
> - **Layout Archetype** (the composition: where the HUD and the action go, how the menu works) — L1–L6. See layout-archetypes.md.

@.claude/rules/anti-slop-design.md

@.claude/docs/layout-archetypes.md

### Gameplay-screen composition

The live game must own the viewport. The mechanic is a dominant, integrated surface—not a small
window floating above a generic scrolling card. Core play, essential HUD, stake/risk controls,
and the primary action remain visible together without page scrolling. The implementation and
runtime gates use the measurable contract below.

@.claude/docs/gameplay-screen-contract.md

### Mobile-first, full-viewport product target

Every screen starts from a touch-first phone composition, verified across the required phone
matrix. The same game must then fill and adapt to landscape, tablet, desktop, and Web viewports;
never place it in a capped phone canvas or artificial device frame.

@.claude/docs/mobile-first-contract.md

## Professional quality bar

> One shared benchmark for "professional level" across every skill in the pipeline. The main
> test: "would a player give this 4+ stars without knowing an AI made it?" With concrete,
> checkable thresholds: TTF ≤ 10 s, response ≤ 100 ms, scaled feedback, a living board,
> 60 fps during win celebration, product completeness.

@.claude/docs/quality-bar.md

## Code standards

@.claude/docs/technical-preferences.md

@.claude/docs/coding-standards.md

## Directory structure

@.claude/docs/directory-structure.md

## Coordination rules

@.claude/docs/coordination-rules.md

## Context management

@.claude/docs/context-management.md
