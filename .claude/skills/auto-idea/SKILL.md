---
name: auto-idea
description: "Autonomously generates a ready-made concept for a gambling game (without asking the user). Selects from 32 A-AF archetypes in six categories (social casino, casino originals, spin-to-progress, gacha, casino roguelike, coin pusher/plinko) or comes up with a unique gambling mechanic. Scrolls through Variety Dimensions (setting/mood/palette/brightness/layout/style art) so that games are not repeated. Includes Classification (category + mathematical model + compliance), Design DNA, Layout Archetype, full map of MVP screens (12+), UX flow and craft-level tokens."
argument-hint: "[--list] | [--archetype A-AF] | [--category C1-C6]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# Auto-Idea - Automatic Gambling Game Idea Generator

Don't ask the user questions! Create `design/gdd/game-concept.md` completely autonomously.

> **GAMBLING ONLY.** The studio does not make puzzles, runners, shooters or clickers. Any idea must
> fall into one of six categories and have a declared mathematical model.
> Canonical reference: `.claude/docs/gambling-categories.md`.
>
> **ANTI-SLOP**: Read `.claude/rules/anti-slop-design.md` (principle + Craft Fundamentals)
> and `.claude/docs/layout-archetypes.md` before generation.
> The concept MUST include a unique visual identity (Design DNA) and the selected Layout
> Archetype. “Gambling” ≠ “dark neon and gold”: bingo can be warm and papery,
> gashapon can be pastel, while a roguelike can use strict typography. Vary both style and composition.

## Catalog of Archetypes (A–AF)

### 🎰 C1 – Social Casino (A–H) · M1 model · RTP 95–97%

**A – Classic 3x3 slot “Neon Spin”**
> 3 reels, fixed lines. Low volatility, frequent wins. Feature: controlled Near Miss (slowing down the 3rd reel) - honest, reflecting the real outcome.

**B – 5x3 video slot with Free Spins “Fruit Storm”**
> 5 reels, 10–25 lines, bonus scatter trigger. Cascading wins (Avalanche): symbols explode, the top ones fall down with a growing multiplier.

**C – Scatter-pays / cluster slot “Sugar Explosion”**
> Slot without lines: pays for the NUMBER of symbols (8+ identical anywhere). Tumble cascade, bomb multipliers. Feature: increasing tumble multiplier.

**D — Hold & Spin (Link & Win) “Golden Connection”**
> Respins with sticky coin symbols, 3 jackpot tiers. Each new coin resets the re-spin counter to 3. Feature: “one more coin” tension.

**E — Video poker “Poker Express”**
> Deal 5 cards, Hold, second draw. RTP is calculated taking into account the optimal strategy. Feature: Double-up - doubling on guessing the suit.

**F — Blackjack “Table 21”**
> Hit/Stand/Double/Split against the dealer. Feature: a readable dealer's hand and an unobtrusive hint of the basic strategy for a beginner.

**G – Cyber ​​Spin Roulette**
> European roulette (one zero), inside and outside bets. Feature: physically reliable ball bounce across the cells.

**H – Social Bingo “Bingo Blitz”**
> 75-ball rooms, auto-dub, patterns. Feature: power-ups (extra ball, instant dub) and collectible cards, XP room progress.

### ⚡ C2 — Casino Originals / Instant-Win (I–P) · M2 model · RTP 96–99%

**I — Crash “Space Takeoff”**
> The multiplier grows along a curve while the object is flying; cash-out until the crash. Flame Particles form a dynamic tail. Feature: visualized physical acceleration + history of recent rounds.

**J - Mines “Minefield”**
> The player opens cells, the multiplier grows geometrically with each safe one. Feature: tense hover sound effects, silence before opening.

**K — Dice roll-under “Quantum Dice”**
> The player sets a threshold; throw below threshold = win. Honest 2D physics of rotation and rebound from the sides (Forge2D). Feature: the threshold slider quickly changes the multiplier.

**L - Hi-Lo “Higher-Lower”**
> Guess whether the next card is higher or lower. Streak multipliers, cash-out at any time. Feature: card flip with a risk meter that grows with streak.

**M - Tower Climb “Dragon Tower”**
> Climbing by floors, choosing 1 of N cells per floor. Multiplier growth versus immediate reset. Feature: each floor is a “take or higher” decision.

**N – Keno “Numbers Lottery”**
> The player selects numbers on the grid, then the draw selects the winning ones. Feature: bouncing draw balls with clear match highlighting.

**O – Deluxe Gold Scratch Cards**
> The player “erases” 9 fields with his finger. 3 identical symbols = win. Feature: erasable foil particles, tactility of erasing.

**P – Bonus Pick “Fortune Chests”**
> Select from N hidden objects, each revealing a multiplier or a collect result. Feature: a delayed dramatic reveal that increases tension.

### 🏰 C3 - Spin-to-Progress Hybrids (Q–U) · M3 model · economy

**Q — Build-and-Raid slot “Kingdom of Coins”**
> Spin gives coins / shield / attack / raid; coins build a village. Feature: raid on an opponent's base with excavation of 1 of 4 points.

**R — Board-move dice “Roll of Fate”**
> Rolling a dice moves a piece across the board, tile = event. Feature: season board - a full circle opens a new thematic board.

**S — Prize-wheel energy hub “Wheel of Fortune”**
> The wheel gives out energy/boosters/currency; Wait timers are hidden behind the wheel animation. Feature: jackpot sector with a progress bar growing between the spins.

**T — Sticker album “Collector's Album”**
> Spin gives out packs of stickers; the album is collected into sets. Feature: duplicates → exchange currency, completion of set = large reward.

**U — Raid & Shield ladder “Shield and Sword”**
> Spin gives attacks and shields; PvP light against rival bots. Feature: revenge - a list of those who attacked you, with a response window.

### 🎁 C4 – Gacha & Loot-Box (V–Y) · model M4 · rates + pity

**V — Banner pull “Summon Legends”**
> x1/x10 pulls by banner, rarity, hard + soft pity. Feature: visible pity counter and guarantor on the 10th pull - honesty as part of the UX.

**W — Mystery card packs “Deck of Champions”**
> Opening card packs, assembling the composition/deck. Feature: duplicates increase the level of the card, rather than turning into garbage.

**X — Case opener “Case Roulette”**
> The horizontal spinner spins objects and stops when they fall out. Feature: slowdown with near-miss on a rare item (fair - the item has already been determined).

**Y – Gashapon “Capsule Machine”**
> Physical metaphor: turn the handle, the capsule rolls out along the chute, and opens. Feature: two-stage opening - capsule, then contents.

### 🃏 C5 — Casino Roguelike & Strategy (Z–AC) · M5 model · run win-rate 25–40%

**Z — Poker deckbuilder “Joker”**
> Poker hands score against progressive round goals. Feature: joker modifiers that change the very rules of hand counting.

**AA — Slot-reel roguelike “Own Drum”**
> The player himself assembles a reel of symbols; spin = income, you need to pay “rent”. Feature: symbol synergies - proximity changes the payout.

**AB — Dice-builder “Dice Forge”**
> Dice are a combat resource; their faces improve between rounds. Feature: reforging replaces one face with a new effect.

**AC — Push-your-luck bag “Alchemist’s Bag”**
> You pull chips from the bag until you “go over” the threshold. Feature: the bust threshold is visible, but the composition of the bag changes every round.

### ⚙️ C6 — Coin Pusher & Plinko (AD–AF) · M6 model · empirical RTP

**AD – Coin Pusher “Golden Bulldozer”**
> 2D physics of pushing coins (rigid bodies), coins interact geometrically. Feature: the accumulation of a “canopy” at the edge is a visual promise of an avalanche.

**AE – Plinko “Neon Cascade”**
> Drop balls through pegs (Forge2D) into baskets with multipliers. Feature: choice of risk profile - number of rows and layout of baskets.

**AF – Pachinko “Silver Rain”**
> Vertical field, balls go into traps, hitting the gate starts the jackpot round. Feature: the jackpot gate opens a separate slot round.

## Procedural Unique Generation (Unique Mode)

If the `--archetype` flag is not passed or the user has explicitly requested a "unique idea", you
**MUST** invent new mechanics that do not coincide with A-AF - but it **must stay
gambling mechanics** and fall into one of six categories.

The best unique ideas live at the intersection of two categories:
- “Plinko, where baskets are poker hands” (C6 × C5)
- “Crash with pity counter: the longer you are unlucky, the higher the guaranteed minimum” (C2 × C4)
- “Coin pusher, where the knocked down coins are pulls from the banner” (C6 × C4)
- "A slot whose reels the player rearranges between village sessions" (C1 × C3 × C5)
- “Scratch map with layer destruction physics” (C2 × C6)

It is prohibited to invent a puzzle, runner, shooter, Tetris clone, clicker, or match-3—even with
a wager layered on top. A wager attached to a non-gambling mechanic does not make it gambling;
the core must be a wager on a random outcome.

**The category and mathematical model are recorded in the “Classification” block BEFORE the other sections.**

## Variety Dimensions - why the same archetype ≠ the same game

The archetype sets the MECHANICS. To make two games of the same archetype look and feel different,
**scroll these axes and select values ​​that are different from the last game**. Record your choice in the concept.

| Axis | Examples of meanings (choose varied) |
|-----|------------------------------------------|
| **Setting/world** | underwater, space, ancient Egypt, cyberpunk Tokyo, enchanted forest, candy land, noir city, wild west, zen garden, steampunk, myths, coffee shop |
| **Mood/mood** | intense, cozy, epic, ironic, mystical, upbeat, meditative |
| **Palette family** | warm earthy, cool neon, pastel, monochrome+1 accent, jewel tones, burnt retro |
| **Brightness** | light / dark / twilight - NOT always dark |
| **Layout Archetype** | L1–L6 (see Section 3.5) - vary the composition |
| **Cartoon 2.5D treatment** | glossy arcade, soft storybook, clay-like, candy-like, hand-drawn adventure, retro cartoon—always with volume, clean silhouettes, and consistent light |
| **Audience/tone** | hardcore casual, children's, premium elegant, retro nostalgia |

> Goal: even two "A" slots should look like DIFFERENT games - one warm Egyptian light,
> another cold cosmic dark one, with different layout archetypes. Setting + palette + layout
> together they give a huge range of dissimilar results.
>
> **Separately against “casino-slop”**: neon + black + gold IS a default, not a style.
> If the game comes out dark neon gold for no reason in Setting, scroll the axis again.

## Work algorithm

1. Read the flag:
   - `--list` — display a table of archetypes A–AF, grouped into categories C1–C6.
   - `--category C1..C6` - choose an archetype randomly INSIDE this category.
   - `--archetype A..AF` - take a specific one.
2. Otherwise, choose an archetype pseudo-randomly, **without repeating the previous one**:
   ```python
   import time
   ARCHETYPES = ["A","B","C","D","E","F","G","H",      # C1
                 "I","J","K","L","M","N","O","P",      # C2
                 "Q","R","S","T","U",                  # C3
                 "V","W","X","Y",                      # C4
                 "Z","AA","AB","AC",                   # C5
                 "AD","AE","AF"]                       # C6
   archetype = ARCHETYPES[int(time.time()) % len(ARCHETYPES)]
   ```
3. **Define the category and mathematical model** of the archetype by
   `.claude/docs/gambling-categories.md`. This is the first thing that will be included in the concept.
4. **Scroll Variety Dimensions**: setting / mood / palette / brightness /
   Layout Archetype (L1–L6) / art style - unlike the previous game.
5. Create a detailed GDD in `design/gdd/game-concept.md`.

## Required sections of GDD

### Section 0: Classification (FIRST, mandatory)

> Without this block `/gate-check concept` returns FAIL, and downstream `/autocreate` phases
> cannot select the correct math implementation. Fill it out literally in machine-readable form.

```markdown
## Classification
- **Category**: [C1 | C2 | C3 | C4 | C5 | C6] - [category name]
- **Archetype**: [A–AF | UNIQUE] - [name]
- **Mathematical model**: [M1 | M2 | M3 | M4 | M5 | M6] - [name]
- **Target Metric**: ["RTP 96.0% ±1%" | "hard pity 70, SSR 1.2%" | “run win-rate 32%” | …]
- **Model config**: design/balance/[file].json
- **Compliance profile**: [full | reduced C5 - justification]
```

### Section 1: Overview
- Title, category, archetype, one sentence
- Target audience
- Unique Selling Proposition (USP)

### Section 1.5: Reference Bar (quality bar calibration)

> The game competes with REAL games in the store, not with other demos.
> See `.claude/docs/quality-bar.md`.

- **2–3 named real category hits**:
  - C1 → Slotomania, Heart of Vegas, Zynga Poker, Bingo Blitz
  - C2 → crash/mines/dice-originals, Hi-Lo
  - C3 → Monopoly GO!, Coin Master, Dice Dreams
  - C4 → Genshin Impact, Honkai: Star Rail, RAID: Shadow Legends
  - C5 → Balatro, Luck be a Landlord, Dicey Dungeons
  - C6 → Coin Dozer, Plinko, pachinko machines
- For each: what do we borrow **IN FEELING** (timing of stopping the reels, weight of the cascade,
  nerve before cash-out, rhythm of pull opening, responsiveness) - not in the content and not in the visuals
- **Hook**: one line - how OUR game differs from the references

### Section 2: Math/Balance Profile

Filled in according to the model from Section 0. Thresholds - `.claude/docs/math-models.md`.

**M1 (C1) — Paytable RTP:**
- Suggested RTP (95–97%) and volatility
- Symbol table with weights, payout table
- Hit rate (20–35%), winning formula
- Bet-tiers and the share of RTP attributable to the bonus

**M2 (C2) — Instant-Win RTP:**
- House edge (1–4%) and resulting RTP (96–99%)
- Multiplier formula in steps, maximum multiplier (cap is required)
- Round determinism scheme: `serverSeed + clientSeed + nonce`
- Cash-out rule: payout at step k strictly = bet × multiplier(k)

**M3 (C3) — Economy:**
- Energy cap, regeneration per hour, spin cost
- Spin event table with weights (sum = 100%)
- Unlock price ladder, price step ≤ 1.6×
- Source/sink 0.90–1.15, pace 2–5 sessions per unlock, session 3–7 minutes

**M4 (C4) — Gacha:**
- Rarity table with base rates (SSR 0.5–2%), amount = 1.0
- Hard pity (50–90), soft pity (start and step)
- E[pulls to rarest] and 90th percentile
- Duplicate value for EACH rarity

**M5 (C5) — Run Win-Rate:**
- Round thresholds (step ≤ 2×), target run win-rate 25–40%
- Run economics: income per round versus store prices
- List of modifiers (≥3) with strength - neither dominant nor dead
- Seed determinism scheme + note about ADR on `Random(seed)`

**M6 (C6) — Physics RTP:**
- Field geometry, basket multipliers, target RTP 95–97%
- Fixed timestep and deterministic start seed
- Expected distribution by baskets (without “dead”)
- For coin pusher - how the steady state is measured

### Section 2.5: Production Plan (which makes the game FULL and not a mini-demo)

> **This is the key section for the "full game".** One game loop = mini demo. The full game is
> loop + content (many levels/modes) + meta-loop (progression/economy/achievements) +
> monetization/telemetry points + compliance layer. Describe them SPECIFICALLY - downstream
> phases `/autocreate` (3.5 audio, 4 meta-systems agent, 4.5 content) build exactly this.

```markdown
## Production Plan

### Content Plan (volume of content - NOT one level)
- **Content model**: [levels | endless-stages | bet-tiers+bonus | waves] - what suits the mechanics
- **Number**: [for example, 24 levels in 3 worlds | 8 progressive stages | 5 bet-tiers + 2 bonus games]
- **Parameters per content unit** (which changes from level to level): [speed/density/target/weights]
- **Progression curve**: [how rates/targets/prices grow; link to category content config]
- **Condition for passing / stars**: [how success is counted, 1–3 stars according to thresholds]

### Game Modes (2-3 modes - replayability)
- **Mode 1 (main)**: [Classic / Campaign - completing content in order]
- **Mode 2**: [High-Roller (high stakes) / Turbo / Survival series / Daily Run - suitable category]
- **Mode 3 (optional)**: [Daily Challenge - deterministic seed by date, separate leaderboard]

### Progression Model (meta-loop retention)
- **What unlocks**: [levels/worlds/skins/themes/modes as you progress]
- **Player level / XP**: [yes/no; if so, what is XP for and what does it give]
- **Stored progress**: [stars, best scores, open levels, statistics]

### Economy Model (virtual - for retention)
- **Currency**: [name, e.g. “coins”/“crystals”] - what is awarded for
- **Where is it spent**: [store: skins/themes/boosters/level sets/remove-ads]
- **Starting balance and prices**: [numbers → will go to GameConfig / economy-config.json]
- ⚠️ The currency is strictly VIRTUAL: does not buy the outcome, is not converted into money, is not withdrawn.
  Real currency symbols next to the game balance are prohibited (responsible-gaming.md §1).

### Achievements & Daily (retention hooks)
- **Achievements**: [5–12 pieces: id + condition + reward]
- **Daily Bonus**: [streak mechanics that gives]
- **Missions (optional)**: [daily/weekly goals]

### Monetization Placements (integration points - implemented as abstractions/no-op)
- **Rewarded**: [continue after losing | double your reward | bonus spin] - where exactly
- **Interstitial**: [between sessions, frequency cap N]
- **IAP catalog**: [coin sets, remove-ads, premium skins - product id list]
- **Banner**: [yes/no; default off]

### Telemetry Events (taxonomy - implemented via AnalyticsService no-op)
- Key events: app_open, session_start/end, screen_view, level_start/complete/fail,
  game_action, purchase, ad_shown/reward, achievement_unlocked, daily_bonus_claimed
- **Remote-config keys** (live-tuning): [advertising frequency, prices, RTP/pity profile, energy regen]

### Compliance (MANDATORY - see `.claude/rules/responsible-gaming.md`)
- **Age-gate**: screen on first launch, result in SharedPreferences
- **Disclaimer**: “Gaming with virtual chips. Real money is not accepted or paid.
  Success in this game does not mean success in gambling for real money." - splash + rules
- **Responsible-play**: block in settings (session reminder, “take a break”, help contacts)
- **Odds disclosure**: [required for C4 and paid spins C3 | covered by paytable for C1/C2/C6]
- **Age rating**: [18+ Google Play / 17+ App Store; C5 without purchases - usually 12+]
- **Weakened Profile**: [none | yes - only C5 without IAP and without currency bets, justification]
```

> Keep the volume realistic for auto-generation: content is DATA (JSON + parameters in
> GameConfig), rather than N handwritten screens. 8 bet-tiers + 3 banners = one GameScreen + config
> with records. This is the “full game” at the low cost of context.

### Section 3: Design DNA (Contextual Visual Identity)

**Each visual decision MUST be justified within the context of THAT SPECIFIC game.**
Not a template. Not "always neon + trapezoid." Design flows from theme, mood and mechanics.

Read `.claude/rules/anti-slop-design.md` - the principle is explained there.

```markdown
## Design DNA: [Game Name]

### Emotional Core
[1-2 sentences: how does the player FEEL while playing THIS PARTICULAR game?]
[Example: “Increasing tension and euphoria when winning” / “Quiet satisfaction from a solved puzzle” / “Adrenaline from speed and reflexes”]

### Visual World
[What visual world does this game exist in? This determines EVERYTHING else.]
[Example: "Underwater world with soft glow of jellyfish" / "Neon Tokyo 2080s" / "Cozy coffee shop with paper textures"]

### Shape Language (derived from Visual World)
- Primary action button: [form + WHY for this game]
  [Example for an underwater game: "smooth drop - organic shape, like a jellyfish"]
  [Example for a mechanical game: “a grooved rectangle is like an industrial lever”]
  [Example for a cozy game: “soft rounded - like a pillow”]
- Info panels: [form + WHY]
- Decorative elements: [shape + WHY]

### Color Palette (5 colors - EACH justified by the context of the game)
- Background: #XXXXXX - [WHY this color for THIS game]
- Surface: #XXXXXX - [WHY]
- Primary: #XXXXXX - [WHY - connection with the theme/world of the game]
- Win/Success: #XXXXXX — [WHY]
- Danger/Loss: #XXXXXX — [WHY]
[Note: if the game is about a forest, the green palette is LOGICAL, and not prohibited.
If the game is about space, blue is LOGICAL. Color is only prohibited if it is RANDOM.]

### Typography (derived from world and mood)
- Display font: [specific Google Font] - [WHY this font suits this game]
  [Example: "Press Start 2P - Retro Slot Hall" / "Playfair Display - Elegant Casino" / "Nunito - Friendly Social Bingo"]
- Body font: [specific Google Font] - [WHY readable and fits the mood]

### Motion Character (derived from emotional core)
- Button feedback: [WHAT and WHY]
  [Heavy mechanical game: deep pressing with delay]
  [Light Casual: Springy Rebound]
  [Elegant: subtle glow]
- Win celebration: [WHAT exactly and WHY corresponds to the level of winning]
- Screen transitions: [WHAT and WHY - connection with the game metaphor]
  [Card game: card flip. Slot: doors. Gachapon: capsule opens.]
  [Or: quick cut for quick play. Intentional simplicity is also a design decision.]
- Idle state: [WHAT animates the screen when the player is not interacting]

### Depth & Effects Strategy
[NOT "always glassmorphism." A: What technique for creating depth is appropriate for THIS game?]
- [Example: "Paper layers with shadows" for a board game]
- [Example: "Holographic overlays" for sci-fi]
- [Example: “No depth - flat minimalism” for a strict roguelike]
- [Example: "Glassmorphism" for a futuristic theme]
- Effects: [what effects are used, why, and where NOT used]

### What Makes This Design UNIQUE to This Game
[If you transfer this UI to another game, will it look out of place? If yes, the design was a success.]
[1-2 sentences: what would NOT be possible to transfer to another game]
```

### Section 3.5: Layout & Composition Direction (MANDATORY)

**Select Layout Archetype** from `.claude/docs/layout-archetypes.md` (L1–L6) and apply
`.claude/docs/gameplay-screen-contract.md`. The archetype defines
COMPOSITION of screens regardless of Design DNA (which determines the look). **Vary the archetype
from the last game** - this is the main lever against “all screens are the same”.

| ID | Archetype | The essence of the composition |
|----|---------|-----------------|
| L1 | Classic Stack | Top HUD bar, field in the center, controls+action below |
| L2 | Bottom Command Deck | Edge-to-edge top, tight bottom console |
| L3 | Floating Corners | Full-bleed field, floating chips in the corners, floating button |
| L4 | Side Rail | Side Vertical Control Rail/HUD |
| L5 | Split Panel | Dominant ≈65–75% field / compact core-control zone |
| L6 | Card/Sheet Stack | Full-viewport field with structural layered sheets; never a nested mini-game card |

```markdown
## Layout & Composition Direction

### Selected Archetype: [L1–L6] - [name]
[1 sentence: why this composition fits this mechanic and category]

### Applying to key screens
- Main Menu: [as assembled by archetype + dressed in DNA]
- Game Screen + HUD: [where is the HUD, where is the main action, like a field]
- Full-viewport proof: [how field reaches ≥55% usable portrait area and normally ≥88% width at
  390×844 and 430×932; how core field/HUD/stake/action stay visible without scrolling]
- Overlays: [toast position, modal entry style]
- Transitions: [a family of transitions from an archetype, colored by the game's metaphor]
```

> Archetype = composition (HOW it is arranged). DNA = appearance (WHAT it looks like). Don't default
> "HUD on top + button on bottom center" layout for every game. Description of screens below -
> MUST follow the chosen archetype.

### Section 4: MVP Screen Map

**NECESSARILY. Minimum 10 screens with description and UX flow. The composition of each is according to the selected Layout Archetype.**

```markdown
## Screen Map

### Screen 1: Splash Screen
- What it shows: [animated game logo/symbol]
- Duration: 1.5-2 sec
- Go to: Main Menu
- Entrance animation: [specific effect]

### Screen 2: Main Menu
- Elements: title (with glow), PLAY button (pulsating), settings, help
- Background: [description of atmospheric background]
- Entry animation: staggered appearance of elements
- Transitions: → Game Screen, → Settings, → Help

### Screen 3: Game Screen + HUD
- Playing field: [reels/table/mine grid/multiplier curve/banner/board/pegs field]
- HUD elements: account/balance (animated counter), controls, action button
- Viewport composition: [dominant integrated field; compact control attachment; no nested window,
  large competing info card, or page-scrolling core loop]
- Overlays: Win/Score (3 levels), Game Over, level passed

### Screen 4: Paytable
- Content: rules, payouts or combinations
- Navigation: swipe or tabs
- Go back: → Game Screen

### Screen 5: Settings
- Elements: BGM volume, SFX volume, vibration, fast mode/skip animation,
  **Responsible Play block** (session reminder, break, help contacts)
- Toggle style: [description of custom toggles]

### Screen 6: Help / How to play
- Format: step-by-step guide with illustrations

### Screen 7: Win/Score Overlays (3 levels)
- Small (basic): toast from below, animated counter, auto-dismiss 2s
- Big (medium): half-screen, confetti particles, 3s
- Mega (maximum): full screen, explosion, camera shake

### Screen 8: Game Over / Insufficient Funds
- Stylized modal (NOT AlertDialog)
- Repeat / reduce bet / continue

### Screen 9: Bonus/Special Mode (if available)
- Bonus category mode: free spins / hold&spin / jackpot gate / bonus pick

### Screen 10: Daily Bonus
- Player retention mechanics
- Go back: → Main Menu

### Screen 11: Leaderboard / Stats
- Top results, player progress

### Screen 12: Player Profile
- Avatar, nickname, statistics

### Screen 13: Level / Mode Select (if content = levels/modes)
- Level grid/map with status (locked/open/stars) or mode selection
- Go to: → Game Screen (selected level/mode)

### Screen 14: Shop (Economy)
- List of items purchased for currency (skins/themes/boosters/sets/remove-ads), currency balance at the top
- Conditions: available / not enough currency / purchased

### Screen 15: Achievements
- List of achievements with progress (unlocked/in progress), awards
```

**UX Flow (navigation):**
```
Splash → Menu → Game ←→ Paytable/Rules
                 ↓  ←→ Settings
                 ↓  ←→ Help
                 ↓
          Win Overlay → Game (auto)
          Bonus Mode → Game (auto)
          Game Over → Menu / Retry

          Menu ←→ Daily Bonus
          Menu ←→ Leaderboard
          Menu ←→ Player Profile
```

### Section 5: Asset Manifest (FULL, format-aware)
```markdown
## Asset Manifest

**Default for Codex `/autocreate`: PNG via GPT Images 2.0 → GPT Images/default fallback.**
SVG is only valid as a fallback outside of Codex or with an explicit `--svg`. In concept, DO NOT call
assets `.svg`, if the game will be played through `/autocreate` in Codex: downstream agents read this
manifesto literally.

### Shared Visual Style Anchor
- Render style: polished cartoon 2.5D casual-game art; [how the concept determines the forms,
  materials, details and character of this cartoon world]
- Lighting: [single source, for example soft top-left key + subtle rim]
- Palette: [3-5 colors from Design DNA]
- Camera/composition: single centered hero object for sprites/icons; 9:16 layered scene for backgrounds
- Cutout policy: sprites/icons/tiles/items = generate on a flat solid chroma-key background
  (default pure magenta #FF00FF; pure green #00FF00 if the palette contains magenta/pink/purple),
  then cut with `tools/cutout.py`; backgrounds = full scene, no alpha removal
- Negative prompt: no photorealism, no product photography, no flat vector icon,
  no emoji/sticker, no logo, no text, no sprite sheet,
  no generic casino/neon unless this is explicitly in Design DNA

### Sprites (assets/images/sprites/)
- sprite_[name].png — [subject identity from the game world; material/texture; role in gameplay; readable at 64px]
- ... (minimum 5-8 elements)

### UI Elements (assets/images/ui/)
- ui_action_button.png — action button; shape from shape language DNA
- ui_frame.png — frame of the playing field
- ui_panel.png - control panel / rates / resources
- ui_separator.png — decorative separator
- ui_icon_sound.png — sound icon
- ui_icon_settings.png — settings icon
- ui_icon_info.png — help icon

### Backgrounds (assets/images/backgrounds/)
- background_menu.png — 9:16 background of the main menu; peace, depth and brightness from DNA
- background_game.png — 9:16 background of the game screen; quiet center area, does not argue with the field

### Audio (assets/audio/) — sound effects only, no background music
- assets/audio/sfx/sfx_action.wav - main action (spin/tap/move)
- assets/audio/sfx/sfx_coin.wav — currency accrual / counter
- assets/audio/sfx/sfx_error.wav - failure / error / insufficient resources
- assets/audio/sfx/sfx_win_small.wav - small win / success
- assets/audio/sfx/sfx_win_big.wav - big win / success
- assets/audio/sfx/sfx_win_mega.wav - mega win / exceptional success
- assets/audio/sfx/sfx_button.wav — pressing the UI button
- assets/audio/sfx/sfx_navigate.wav — transition between screens
```

### Section 6: Code Architecture (FULL with Data Flow)
```markdown
## Dart Classes

### Game Core
- [GameName]Game extends FlameGame - entry point, controls ValueNotifiers
- [GameName]World extends World with HasCollisionDetection - game world
- GameConfig - ALL numerical constants (bet rates, speeds, multipliers, timings)
- GameState (sealed) — Idle, Playing, Animating, Win, GameOver, Paused

### Systems
- [GameLogic] - basic mechanics (WeightedRNG/MatchDetector/SpawnManager)
- [Evaluator] - pure function for calculating the result

### Components
- [MainComponent] - main game object
- [ElementComponent] - game elements
- WinAnimationComponent - VFX wins
- AmbientParticles - background particles

### UI
- GameApp (MaterialApp) → named routes
- SplashScreen → MainMenu → GameScreen (GameWidget + HUD overlay)
- HudWidget - ValueListenableBuilder for balance/account/status
- WinOverlay - 3 levels
- All other screens (12+)

## ValueNotifier Contracts (between Flame Game and Flutter UI)
| Notifier | Type | Writes | Reads |
|----------|------|--------|-------|
| balance | ValueNotifier<int> | Game | HUD, Bet selector, InsufficientFunds |
| bet | ValueNotifier<int> | HUD (Bet+/-) | Game (on action) |
| isPlaying | ValueNotifier<bool> | Game | HUD (button lock) |
| currentState | ValueNotifier<GameState> | Game | HUD, Overlays |
| score | ValueNotifier<int> | Game | HUD, Leaderboard |
| lastWin | ValueNotifier<int> | Game | WinOverlay |

## Complete Game Loop
1. User taps Action button → check isPlaying (false) + check balance >= bet
2. Set isPlaying = true, deduct bet from balance
3. Compute outcome (BEFORE animation)
4. Play action animation (reels spin / tiles move / etc.)
5. Animation complete → evaluate result
6. If win: update balance, show WinOverlay (level based on multiplier), play sound
7. If loss: brief feedback
8. Set isPlaying = false → return to Idle state
9. Update leaderboard if score > highScore

## Edge Cases (FULL list)
- Balance = 0 → show InsufficientFunds dialog
- Balance < minBet → show InsufficientFunds
- Double-click Action → second click ignored (isPlaying check)
- App pause during animation → complete animation, return to Idle
- Back button on GameScreen → confirm exit dialog
- Settings changed mid-game → apply immediately (audio volume)
- Daily Bonus already claimed today → show "come back tomorrow"
- First launch → show tutorial/help overlay
```

### Section 7: Juiciness Requirements - COMPLETE

```markdown
## Anticipation
- [Description of the effect of waiting before the result]
- [Slow down/delay/sound fade in]

## Near Miss / Almost Win (if applicable)
- [Description of visual effect when almost winning]

## Win Celebration (3 levels)
- Small (1-5x): [description - toast + confetti + ding]
- Big (5-20x): [description - half-screen + burst particles + fanfare]
- Mega (20x+): [description - fullscreen + explosion + camera shake + epic music]

## Idle Animations (when the player does not interact)
- Main element: [wiggle/flare/ripple]
- Background: [moving particles / ambient glow]
- Action button: [pulsating glow]

## Micro-Interactions
- Each button: scale 0.95 when pressed → 1.0 when released + shadow change
- Numbers: AnimatedCounter when changing (easeOutCubic)
- Navigation: thematic transition (not fade/slide)
- Switches: custom toggle with animation

## Sound Design Map
| Event | Sound | Character |
|---------|------|----------|
| Action start | sfx_action.wav | Growing |
| Action complete | (silence 200ms) | Pause for anticipation |
| Small win | sfx_win_small.wav | Melodious ding |
| Big win | sfx_win_big.wav | Fanfare |
| Mega win | sfx_win_mega.wav | Epic orchestra |
| Button tap | sfx_button.wav | Short click |
| Navigation | sfx_navigate.wav | Swoosh |
| Error/Fail | sfx_error.wav | Soft buzz |
```

### Section 8: Anti-Slop Checklist + Production Readiness
```markdown
## Anti-Slop (intent + craft, NOT imposed style)
- [ ] Palette based on the theme of the game (not random purple-blue by default)
- [ ] 2 fonts from DNA + typographic hierarchy (type scale 4–6 sizes)
- [ ] Basic indent step (4/8); button shape from shape language (rounded rectangle is OK if it fits)
- [ ] Layout Archetype selected and applied (composition NOT default “HUD on top + button on bottom”)
- [ ] Gameplay screen contract satisfied: dominant full-viewport field, integrated controls,
      core loop visible without scrolling, and usable button proportions at all four target sizes
- [ ] Transitions between screens are thematic (related to the game world)
- [ ] All 12+ screens are described with full content
- [ ] Micro-interactions on each interactive element
- [ ] Idle animations defined
- [ ] Loading - thematic widget (not CircularProgressIndicator)
- [ ] Depth strategy of DNA modals (glass / card / paper / flat - whatever suits the world)
- [ ] One clear focus on each screen; text contrast ≥ 4.5:1
- [ ] Centralized animation timings (animations.dart)
- [ ] The style is NOT transferable to another game (neon/dark theme - only if justified by the theme)

## Production Readiness
- [ ] Complete Game Loop described (step by step)
- [ ] ALL edge cases are listed with solutions
- [ ] Data Flow defined (ValueNotifier contracts)
- [ ] Asset Manifest full (Codex PNG + Audio WAV; SVG fallback only)
- [ ] Sound Design Map defined
- [ ] SharedPreferences for: Settings, Profile, Leaderboard, Daily Bonus
```

## Conclusion

Print the message:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTO-IDEA COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Game: [Name]
Category: [C1-C6] - [title]
Archetype: [A-AF | UNIQUE] - [name]
Mathematical model: [M1-M6] - target metric [...]
Setting / Mood: [world] / [mood]
Layout: [L1-L6] - [name of composition archetype]
Balance: [RTP XX% / Difficulty curve / Points system]
Content: [N levels/stages] | Modes: [Classic + Endless/Time-Attack/Daily]
Meta: [currency + store + progression + achievements]
Compliance: [full: age-gate + disclaimer + responsible-play + 18+ | reduced C5]
MVP screens: [N] screens
Design DNA: [key visual decisions]

Saved: design/gdd/game-concept.md

Next step:
  /autocreate --from-concept - implement as a game
  /map-systems - decompose into systems
  /design-review - concept review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
