<p align="center">
  <h1 align="center">Flutter Gambling Studio</h1>
  <p align="center">
Studio of gambling mini-games on Flutter + Flame.<br/>
From concept to release - correct architecture, verifiable mathematics, rich UI.
    <br /><br />
<strong>14 agents · 32 skills · 8 hooks · 8 rules · 32 archetypes · 6 categories</strong>
  </p>
</p>

<p align="center">
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/agents-14-blueviolet" alt="14 agents">
<img src="https://img.shields.io/badge/skills-32-green" alt="32 skills">
<img src="https://img.shields.io/badge/archetypes-32-orange" alt="32 archetypes">
<img src="https://img.shields.io/badge/categories-6-yellow" alt="6 categories">
  <img src="https://img.shields.io/badge/Flutter-3.27+-blue?logo=flutter" alt="Flutter 3.27+">
  <img src="https://img.shields.io/badge/Flame-1.18+-red" alt="Flame 1.18+">
<a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/compatible-Claude%20Code-f5f5f5?logo=anthropic" alt="Claude Code Compatible"></a>
<img src="https://img.shields.io/badge/compatible-OpenAI%20Codex-111111" alt="OpenAI Codex Compatible">
</p>

---

## Why is this needed

Gambling games are more difficult than they seem - and a mistake here costs more than in a regular mini-game:

- **Wrong weights** = unfair RTP that no one will notice until release
- **`math.Random()`** instead of `Random.secure()` = predictable outcome
- **Outcome calculated during animation** = RTP cannot be verified, cash-out is incorrect
- **Multiplier cap or payout rounding** = silent interest drain
- **Pity counter that does not survive restart** = pity becomes a fiction
- **Lack of age-gate and disclaimer** = store will reject the game
- **Plus general**: allocations in `update()` = junk; weak UI = game looks cheap

**Flutter Gambling Studio** solves all this through a system of specialized agents -
the mathematician owns the model and verifies it by running it, the designer writes GDD, the programmer
the mechanic implements the logic, the VFX artist adds “juiciness”, the release-manager checks
compliance. Hooks protect against rule violations when committing. The quality gates won't let you in
bad code for the next stage.

The math is not “by eye”: each game has exactly one declared model (M1–M6), one
JSON config and one run that either passes the threshold or blocks the release:

```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
# exit 0 = PASS · 1 = CONCERNS · 2 = FAIL
```

The repository is now configured in dual-mode:

- `CLAUDE.md` and `.claude/` remain the canonical source of studio rules
- `AGENTS.md` and `.codex/` give a Codex-compliant execution layer for the same skills, roles and hooks

You control the strategy. The team implements.

---

## Six categories of gambling

The studio makes **only** gambling games. Puzzles, runners, shooters and clickers are out of scope.

| ID | Category | Examples | Balance model |
|----|-----------|---------|----------------|
| **C1** 🎰 | Social Casino | Slots, video poker, blackjack, roulette, bingo | **M1**: RTP 95–97%, hit rate 20–35% |
| **C2** ⚡ | Casino Originals | Crash, mines, dice, hi-lo, tower, keno, scratch | **M2**: RTP 96–99%, multiplier cap |
| **C3** 🏰 | Spin-to-Progress | Build-and-raid, board-dice, prize wheel, album | **M3**: source/sink 0.90–1.15 |
| **C4** 🎁 | Gacha & Loot-Box | Banners, card packs, cases, gashapon | **M4**: rates 0.5–2%, pity 50–90 |
| **C5** 🃏 | Casino Roguelike | Poker deckbuilder, reel roguelike, dice-builder | **M5**: run win-rate 25–40% |
| **C6** ⚙️ | Coin Pusher & Plinko | Dozer, plinko, pachinko | **M6**: Empirical RTP 95-97% |

Full reference: [`.claude/docs/gambling-categories.md`](.claude/docs/gambling-categories.md).
Verification thresholds: [`.claude/docs/math-models.md`](.claude/docs/math-models.md).

> **Always virtual.** No game accepts or pays real money.
> Compliance layer (age-gate, disclaimer, responsible-play, revealing chances) - release blocker:
> [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md).

---

## Codex Quick Start

If you are working in OpenAI Codex:

1. Open `AGENTS.md`.
2. Then read `.codex/README.md`.
3. Execute any slash command (`/brainstorm`, `/autocreate`, `/team-dev`) through mapping in `.codex/commands.md`.
4. To manually run hook scripts, use `bash tools/codex-hooks.sh <hook-name>`.

This allows you to use the same agents/skills/workflows as in Claude Code, but without the hidden Claude-specific magic.

---

## Technology stack

| Component | Technology |
|-----------|-----------|
| **Engine** | Flutter 3.27+ / Flame 1.18+ |
| **Language** | Dart 3.6+ (null-safe, sealed classes, pattern matching) |
| **Product target** | Android phones + iPhone, portrait-only |
| **Rendering** | Impeller (Android/iPhone); Web/CanvasKit only for preview and automated verification |
| **Audio** | flame_audio ^2.1.0 |
| **SVG** | flame_svg ^1.10.0 |
| **Physics** | forge2d (pinball, plinko, physics games) |
| **RNG** | `Random.secure()` for gambling; `Random()` for non-critical elements |

---

## Studio hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ Tier 1 — Directors (strategic decisions) │
│    creative-director    technical-director               │
└─────────────────────────────────────────────────────────┘
              ↓                    ↓
┌─────────────────────────────────────────────────────────┐
│ Tier 2 — Game mechanics specialists │
│    game-mathematician     game-designer                  │
│    mechanics-programmer   juice-artist                   │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│ Tier 3 — Basic specialists (implementation and quality) │
│    lead-programmer        performance-analyst            │
│    ui-programmer          sound-designer                 │
│    qa-tester              release-manager                │
└─────────────────────────────────────────────────────────┘
```

### Agent table

| Agent | Role | Area of ​​responsibility |
|-------|------|---------------------|
| `creative-director` | Creative Director | Game vision, concept, creative conflict resolution |
| `technical-director` | Technical Director | ADR, architectural solutions, technical conflict resolution |
| `game-mathematician` | Owner of the mathematical model | RTP, house edge, pity, economy, run win-rate - and their verification |
| `game-designer` | Game designer | GDD: round, bets, bonuses, progression, compliance screens |
| `mechanics-programmer` | Programmer mechanic | RNG, physics, collisions, match detection, spawning |
| `juice-artist` | VFX Artist | Anticipation, near-miss, win-celebration, particles |
| `art-director` | Art director | Vision review of a set of assets for visual integrity |
| `meta-systems-programmer` | Meta-systems | Save, economy, progression, achievements, ads/iap abstractions |
| `lead-programmer` | Lead Programmer | Architecture, code review, Flame 1.18.x standards |
| `performance-analyst` | Performance Analyst | FPS, memory, SpriteBatch, texture leaks |
| `ui-programmer` | Flutter UI | Screens, HUD, Win overlays, anti-slop design |
| `sound-designer` | Sound designer | Bet, spin, stop, cash-out, reveal, pitch scaling |
| `qa-tester` | QA engineer | Test cases, edge cases, RNG distribution, state leakage |
| `release-manager` | Release Manager | Final check before deployment + compliance audit |

> **Language**: all agents communicate in **English**. Generated games, store metadata,
> screenshot captions, design documents, reports, and session artifacts are English too,
> unless the user explicitly requests a different player-facing language.

---

## Development roadmap

```
IDEA CONCEPT DESIGN CODE QA RELEASE
    │               │               │              │             │             │
/brainstorm    /gate-check    /design-system   /team-       /code-       /release-
/auto-idea      concept       /design-review   dev          review       checklist
/autocreate                   /map-systems     /gate-check  /balance-
               /gate-check    /balance-check    code        check
                design                         /gate-check  /gate-check
                                                            qa
```

### Quality gate (`/gate-check`)

| Team | What checks | Blockers |
|---------|--------------|---------|
| `/gate-check concept` | Is the concept ready for design? | No GDD, no block Classification (category + model + compliance) |
| `/gate-check design` | Is GDD ready for implementation? | No 8 sections, no balance config |
| `/gate-check code` | Is the code ready for QA? | `math.Random()`, hardcoded probabilities, outcome inside animation |
| `/gate-check qa` | Are you ready for release? | The mathematical model is out of the window, there are no compliance screens, no edge case tests |

---

## All commands

### Game creation

| Team | Description |
|---------|----------|
| `/start` | Onboarding and routing - where to start |
| `/brainstorm [hint]` | Interactive gambling game concept |
| `/auto-idea` | Autonomous concept of 32 archetypes without question |
| `/auto-idea --list` | Show all 32 archetypes (A–AF) by category |
| `/auto-idea --archetype [A-AF]` | Expand a specific archetype |
| `/auto-idea --category [C1-C6]` | Random archetype within a category |
| `/autocreate` | Zero-to-playable: concept + assets + standalone code |
| `/autocreate --from-concept` | Implement an already saved concept |

### Design and architecture

| Team | Description |
|---------|----------|
| `/map-systems` | Decomposition of the concept into Flame systems |
| `/design-system [system]` | GDD for one mechanic |
| `/prototype [mechanics]` | Isolated prototype for testing juiciness |
| `/architecture-decision [decision]` | Architecture Decision Record (ADR) |

### Assets

| Team | Description |
|---------|----------|
| `/generate-asset [type] [name]` | SVG by default; PNG only by explicit request |
| `/generate-png-asset [description]` | PNG via GPT Image 2: built-in tool or `tools/gpt_image.py` in headless Codex CLI; background of simple assets is cut out locally |
| `/svg-to-png [path]` | Convert SVG → PNG via Codex GPT Images 2.0 |

### Review and gate

| Team | Description |
|---------|----------|
| `/code-review` | Full review: RNG, Stateless Outcomes, Flame API, State, tests |
| `/design-review` | Review of GDD: 8 sections, mathematics, edge cases |
| `/ui-audit` | Automatic UI audit for anti-slop quality |
| `/gate-check [stage]` | Transition gate with verdict PASS / CONCERNS / FAIL |

### Balance and mathematics

| Team | Description |
|---------|----------|
| `/balance-check` | Verification of the mathematical model M1–M6 through `tools/simulate_math.py` (1M tests, full-curve) |

### Diagnostics

| Team | Description |
|---------|----------|
| `/perf-profile [region]` | Profiling FPS/memory/particles/audio |
| `/tech-debt` | Technical Debt Scanning and Registry |
| `/hotfix [description]` | Emergency fix with audit trail |

### Teamwork

| Team | Description |
|---------|----------|
| `/team-dev [description]` | Orchestration: game-designer → game-mathematician → mechanics-programmer → juice-artist |

### Working with an existing project

| Team | Description |
|---------|----------|
| `/continue-project` | Restore context and continue from breakpoint |
| `/add-feature [feature]` | Add a feature to a finished game (with balance recalculation) |
| `/release-checklist` | Final checklist before deployment |

---

## Gambling Game Archetypes (A–AF)

### 🎰 C1 – Social Casino (A–H) · model M1

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| A | Neon Spin | Classic 3x3 slot | Near Miss system, cascade stop |
| B | Fruit Storm | Video slot 5×3 + Free Spins | Avalanche: cascading symbols, growing multiplier |
| C | Sugar Explosion | Scatter-pays/cluster slot | Payout per number of symbols, tumble multipliers |
| D | Golden Connection | Hold & Spin (Link & Win) | Sticky coins, 3 jackpot tiers |
| E | Poker Express | Video poker | 5 cards, Hold, Double-up per suit |
| F | Table 21 | Blackjack | Hit/Stand/Double/Split, basic strategy hint |
| G | Cyber ​​Spin | European Roulette | Physically reliable ball bounce |
| H | Bingo Blitz | Social bingo 75 balls | Power-ups, trading cards, room XP |

### ⚡ C2 — Casino Originals (I–P) · model M2

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| I | Space Takeoff | Crash | Acceleration curve, particle tail, round history |
| J | Minefield | Mines | Geometric growth of the multiplier, silence before disclosure |
| K | Quantum Dice | Dice roll-under | Honest 2D throwing physics, live threshold slider |
| L | Above-Below | Hi-Lo | Streak multipliers, risk meter, cash-out at any time |
| M | Dragon Tower | Tower Climb | Risk/Reward, choice of 1 of N cells per floor |
| N | Numbers Lottery | Keno | Number selection + circulation with ball physics |
| O | Deluxe Gold | Scratch cards | Erasable foil particles, tactile erasing |
| P | Fortune Chests | Bonus Pick | Delayed dramatic reveal |

### 🏰 C3 - Spin-to-Progress (Q–U) · M3 model

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| Q | Kingdom of Coins | Build-and-Raid slot | Raid with excavation 1 of 4 points |
| R | Throw of Fate | Board-move dice | Season board: circle opens new board |
| S | Wheel of Fortune | Prize-wheel energy hub | Jackpot sector with progress bar between spins |
| T | Collector's Album | Stickers from packs | Duplicates → exchange currency, recruitment reward |
| U | Shield and Sword | Raid & Shield ladder | Revenge: a window of response to those who attacked |

### 🎁 C4 – Gacha & Loot-Box (V–Y) · model M4

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| V | Summon Legends | Banner pull | Visible pity counter, guarantor on the 10th pull |
| W | Champions Deck | Mystery card packs | Duplicates increase card level |
| X | Case Roulette | Case opener | Braking spinner with near-miss on rare |
| Y | Capsule Machine | Gashapon | Two-stage opening: capsule → contents |

### 🃏 C5 – Casino Roguelike (Z–AC) · M5 model

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| Z | Joker | Poker deckbuilder | Jokers change the very rules of hand counting |
| AA | Own Drum | Slot-reel roguelike | Symbol Synergies: Neighborhood Changes Payout |
| AB | Dice Forge | Dice-builder | Reforging: replacing one face with an effect |
| AC | Alchemist's Bag | Push-your-luck bag | The bust threshold is visible, the composition of the bag changes |

### ⚙️ C6 — Coin Pusher & Plinko (AD–AF) · model M6

| ID | Title | Mechanics | Unique feature |
|----|----------|----------|-----------------|
| AD | Golden Bulldozer | Coin Pusher | Accumulation of "canopy" at the edge - the promise of an avalanche |
| AE | Neon Cascade | Plinko | Selecting a risk profile (rows + basket layout) |
| AF | Silver Rain | Pachinko | Jackpot gate launches separate slot round |

```bash
/auto-idea --archetype A # Neon Spin (slot, C1)
/auto-idea --archetype I # Space Takeoff (crash, C2)
/auto-idea --archetype V # Summon Legends (gacha, C4)
/auto-idea --category C5 # Casino roguelike
/auto-idea --list # Show all 32 archetypes by category
/auto-idea # Random unique gambling mechanics
```

> Archetype = MECHANICS. To prevent games of the same archetype from being repeated, they scroll on top of it
> **Layout Archetype L1–L6** (screen composition) and **Design DNA** (palette/fonts/shapes).
> “Gambling” ≠ “dark neon and gold”: bingo can be warm and papery, gashapon -
> pastel, while a roguelike can use strict typography.

---

## Critical rules of the game

Apply to all six categories **absolutely** - there are no "categories they do not apply to".

```dart
// ✅ Random.secure() ONLY
class WeightedRNG {
final _rng = Random.secure(); // Not Random()!
}

// ✅ Stateless Outcomes - result BEFORE animation
Future<void> spin() async {
final outcome = _rng.computeOutcome(); // Result first
await _animateReels(outcome.symbols);  // Then animation
}

// ❌ Hardcoded probabilities - prohibited
if (Random().nextDouble() < 0.15) triggerBonus();

// ✅ GameState - sealed class is required
sealed class GameState {}
class IdleState extends GameState {}
class ResolvingState extends GameState { final RoundOutcome outcome; }
class WinState extends GameState { final int payout; final WinTier tier; }
class OutOfFundsState extends GameState {}

// ✅ All parameters in GameConfig; model numbers are from JSON, not duplicated
class GameConfig {
  static const int minBet = 1;
  static const int maxBet = 100;
  static const Duration roundAnimation = Duration(milliseconds: 2000);
}

// ❌ Prohibited - magic numbers
if (win > 1000) triggerJackpot(); // Where did 1000 come from?
```

**The only exception to `Random.secure()`** is the seeded determinism of the run in roguelike casinos
(C5): the race must be played based on the seed. Requires ADR.

**Model verification is required** before `/gate-check qa`:

```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json --trials 1000000
python3 tools/simulate_math.py --selftest # reference configs of all six models
```

### Compliance - release blocker

Age-gate at first launch · disclaimer on splash and in the rules · responsible-play in settings ·
odds reveal (C4 and paid spins C3) · no real currency symbols in the game balance ·
no promises of winnings. Full: [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md).

---

## Automation and hooks

| Hook | When | What does |
|-----|-------|-----------|
| `session-start.sh` | Start of session | Shows project status, GDD, latest commits |
| `detect-gaps.sh` | Start of session | Searches for violations (gambling: `math.Random()`), missing files |
| `validate-commit.sh` | Before `git commit` | Gambling: blocks `math.Random()`, hardcoded RTP. All: invalid JSON, `print()` |
| `validate-push.sh` | Before `git push` | Warns when pushing into main without a gate |
| `validate-assets.sh` | After Write/Edit | Checks asset naming (`sprite_X`, `sfx_X`) |
| `pre-compact.sh` | Before context compression | Saves the checkpoint to `production/session-state/active.md` |
| `session-stop.sh` | Ending the session | Logs changes to `production/session-logs/` |
| `log-agent.sh` | Launching a subagent | Audit trail of all agent calls |

### Code rules (path-based)

| Rule | Applies to | Contents |
|---------|--------------|-----------|
| `game-code.md` | `lib/**/*.dart` | GameConfig, GameState sealed class, double click protection |
| `engine-code.md` | `lib/game/**/*.dart` | Flame 1.18.x API (World, CameraComponent, HasTimeScale) |
| `ui-code.md` | `lib/screens/**/*.dart` | ValueNotifier, Win overlays, anti-slop requirements |
| `test-standards.md` | `test/**/*.dart` | AAA structure, RNG distribution (gambling), edge cases |
| `data-files.md` | `design/balance/**/*.json` | Scheme rtp-config.json (gambling), balance configs |
| `design-docs.md` | `design/**/*.md` | 8 Required Sections of GDD Document Status |

---

## Project structure

```
flutter-game-studio/
├── CLAUDE.md # Main studio configuration
├── .claude/
│ ├── settings.json # Rights, hooks, statusline
│ ├── agents/ # 12 specialized agents
│   │   ├── creative-director.md
│   │   ├── technical-director.md
│ │ ├── game-mathematician.md # owner of the mathematical model M1–M6 + verification
│ │ ├── game-designer.md # GDD: round, bets, bonuses, compliance
│ │ ├── mechanics-programmer.md # RNG, Stateless Outcomes, cash-out, pity, physics
│   │   ├── juice-artist.md
│   │   ├── lead-programmer.md
│   │   ├── performance-analyst.md
│   │   ├── ui-programmer.md
│   │   ├── sound-designer.md
│   │   ├── qa-tester.md
│   │   └── release-manager.md
│ ├── skills/ # 24 slash commands
│   │   ├── start/  brainstorm/  auto-idea/  autocreate/
│   │   ├── map-systems/  design-system/  prototype/
│   │   ├── generate-asset/  generate-png-asset/  svg-to-png/
│   │   ├── team-dev/  balance-check/  add-feature/
│   │   ├── code-review/  design-review/  ui-audit/
│   │   ├── gate-check/  release-checklist/  continue-project/
│   │   ├── hotfix/  perf-profile/  tech-debt/  architecture-decision/
│ │ └── [team-gambling/ - deprecated, replaced by team-dev/]
│ ├── hooks/ # 8 automatic scripts
│ ├── rules/ # 6 path-based rules
│   │   ├── game-code.md  engine-code.md  ui-code.md
│   │   ├── test-standards.md  data-files.md  design-docs.md
│ └── docs/ # Studio documentation
├── production/
│ ├── session-state/active.md # Current checkpoint (gitignored)
│ └── session-logs/ # Audit log (gitignored)
└── [game projects are created here]
├── lib/game/game_config.dart # All game constants
├── lib/models/game_state.dart # sealed state class
    ├── assets/
    ├── design/gdd/
    ├── design/balance/
    └── tools/simulate_balance.py
```

---

## Quick start

### Requirements

- [Flutter SDK](https://docs.flutter.dev/get-started/install) 3.27+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`)
- OpenAI Codex with `AGENTS.md` support
- Python 3 (for balance simulation)

### Installation

```bash
git clone https://github.com/leofillium/flutter-gambling-studio.git
cd flutter-gambling-studio
claude
```

### Paths

**I want a game right now (any of six categories):**
```
/autocreate
```
Autonomous pipeline: concept + mathematical model → assets → Flutter code → balance verification
→ `pubspec.yaml`. No questions asked.

**I want to control every step:**
```
/brainstorm # Select category C1–C6 and create a concept together
/gate-check concept # Check concept readiness
/design-system # Write GDD for mechanics
/gate-check design # Check GDD readiness
/team-dev # Pass to the programming team
/code-review # Review written code
/balance-check # Balance simulation
/gate-check qa # Final gate
/release-checklist # Ready for release
```

---

## License

MIT License. Details in [LICENSE](LICENSE).
