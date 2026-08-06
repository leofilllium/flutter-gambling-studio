# Quick start

Welcome to **Flutter Gambling Studio** — a studio for gambling mini-games:
slots, poker, roulette, bingo, crash, mines, plinko, gacha, casino roguelikes,
coin pushers and spin-to-progress hybrids.

Here you act as the **studio director**, and the AI agents are your team.
Your job is to make the decisions; the team handles the rest.

> **IMPORTANT**: all work in the studio is produced in **English** — the conversation, the
> design documents, the code and the game's own copy. If you want the game itself in another
> language, say so explicitly and the player-facing text will use it.
>
> **Always virtual.** The studio's games do not accept or pay out real money —
> see `.claude/rules/responsible-gaming.md`.

## The six categories the studio works in

| ID | Category | Examples |
|----|----------|----------|
| C1 🎰 | Social Casino | slot, video poker, blackjack, roulette, bingo |
| C2 ⚡ | Casino Originals | crash, mines, dice, hi-lo, tower, keno, scratch |
| C3 🏰 | Spin-to-Progress | build-and-raid slot, board-dice, prize wheel |
| C4 🎁 | Gacha & Loot-Box | banner pull, card packs, case opener, gashapon |
| C5 🃏 | Casino Roguelike | poker deckbuilder, slot-reel roguelike |
| C6 ⚙️ | Coin Pusher & Plinko | dozer, plinko, pachinko |

The full reference is `.claude/docs/gambling-categories.md`.

## 🚀 How do I start a new game?

There are two paths:

### Path 1: automatic (I want a finished game)
Just type:
```bash
/autocreate
```
The studio picks an archetype out of 32 (A–AF across the six categories), declares a
mathematical model, writes the design, draws the assets, writes the code, runs the balance
simulation and sets up `pubspec.yaml`.

### Path 2: manual (I want to build a unique game)

**Step 1. Idea and category**
```bash
/brainstorm
```
Together with the agent you choose the category, the archetype, the theme and the unique
piece of "juice".

**Step 2. Break it into components**
```bash
/map-systems
```
The studio produces a build plan with a map of systems.

**Step 3. Detailed mechanic design**
```bash
/design-system rtp-weights        # C1: symbol weights and the payout table
/design-system multiplier-curve   # C2: the multiplier formula from the house edge
/design-system pity-system        # C4: soft/hard pity and odds disclosure
/design-system energy-economy     # C3: regeneration, cap, source/sink
```
`game-mathematician` and `game-designer` step in and compute the model for your category.

**Step 4. Write the code**
```bash
/team-dev "Implement the game core from our concept"
```
This orchestrates `mechanics-programmer` (logic and RNG) and `juice-artist` (animation).

---

## 👥 Your team (the agents)

| Specialist | Who to call | What they do |
|------------|-------------|--------------|
| Mathematician | `@game-mathematician` | Owner of the math model: RTP, house edge, pity, economy, run win-rate |
| Game designer | `@game-designer` | GDD: the round, bets, bonuses, progression, compliance screens |
| Mechanics programmer | `@mechanics-programmer` | `Random.secure()`, stateless outcomes, paylines, multipliers, Forge2D |
| Meta systems | `@meta-systems-programmer` | Save, economy, progression, achievements, ads/iap abstractions |
| VFX artist | `@juice-artist` | Anticipation, near-miss, win celebration, particles |
| UI/UX | `@ui-programmer` | Every Flutter screen, HUD, bet panel, anti-slop design |
| Sound | `@sound-designer` | Bet, spin, stop, win, cash-out |

---

## 🛠 Useful commands along the way

Generating assets:
```bash
/generate-asset symbol cherry     # a reel symbol
/generate-asset sprite chip-gold  # a chip / ball / capsule
```

Check the game's mathematics:
```bash
/balance-check                    # picks the model M1–M6 from the game's category
```

Directly, when you need it quickly:
```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
python3 tools/simulate_math.py --selftest   # the reference configs for all six models
```

Add a feature to a finished game:
```bash
/add-feature "Add a free spins round"           # C1
/add-feature "Add auto-bet with limits"         # C2
/add-feature "Add a guarantee on the 10th pull" # C4
```

Take a break and continue tomorrow:
```bash
/continue-project
```

Ready to start? Type `/start` right now.
