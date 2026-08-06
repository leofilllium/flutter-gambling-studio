---
name: start
description: "The introductory skill. Presents the gambling studio, its six categories and 32 archetypes, and points the user in the right direction. Run it at the beginning of any new project."
user-invocable: true
allowed-tools: Bash, Read
---

# `flutter-gambling-studio` — meet the studio

Hello! You are in a studio that specialises in building **gambling mini-games** with
**Flutter + Flame**.

We only make gambling: slots, poker, roulette, bingo, crash, mines, plinko, gacha, casino
roguelikes, coin pushers and spin-to-progress hybrids. Puzzles, runners, shooters and clickers
are outside the studio's scope.

> **Rule 1**: everything here is produced in **English** — the conversation, the design
> documents, the code and the game's own copy. If you want the game itself in another language,
> say so explicitly and the player-facing text will use it.
>
> **Rule 2**: every game runs on **virtual chips**. Real money is neither accepted nor paid out
> (`.claude/rules/responsible-gaming.md`).

### The main commands to get started

| Command | What it does |
|---------|--------------|
| `/brainstorm` | Step-by-step idea generation. Together we pick the category, the archetype, the mathematics, the theme and the "juice". |
| `/auto-idea` | Instantly generates a complete concept (no questions) from the 32 archetypes A–AF, cycling the Variety Dimensions and choosing a Layout Archetype. |
| `/autocreate` | Builds the game from concept to a finished Flutter project in one session. |
| `/continue-project` | Continue an existing game from where you stopped. Your usual entry point. |

### The six gambling categories

| ID | Category | What it is | Balance metric |
|----|----------|------------|----------------|
| **C1** 🎰 | Social Casino | A casino floor simulated with virtual chips | RTP 95–97% |
| **C2** ⚡ | Casino Originals | An instant round, a live multiplier, cash-out | RTP 96–99% |
| **C3** 🏰 | Spin-to-Progress | The spin is fuel for a casual meta game | A source/sink economy |
| **C4** 🎁 | Gacha & Loot-Box | Pulls with rarities and pity | Rates + pity |
| **C5** 🃏 | Casino Roguelike | Casino mechanics as a roguelike's combat system | Run win-rate 25–40% |
| **C6** ⚙️ | Coin Pusher & Plinko | Physics as the outcome generator | Empirical RTP 95–97% |

### The archetype catalogue (A–AF)

| ID | Name | Mechanic | Cat. |
|----|------|----------|------|
| A | Neon Spin | A classic 3×3 slot | C1 |
| B | Fruit Storm | A 5×3 video slot + free spins, avalanche | C1 |
| C | Sugar Blast | A scatter-pays / cluster slot, tumble | C1 |
| D | Golden Link | Hold & Spin (Link & Win), jackpot tiers | C1 |
| E | Poker Express | Video poker, hold + double-up | C1 |
| F | Table 21 | Blackjack against the dealer | C1 |
| G | Cyber Spin | European roulette | C1 |
| H | Bingo Blitz | Social 75-ball bingo, power-ups | C1 |
| I | Cosmic Ascent | Crash, a multiplier + cash-out | C2 |
| J | Minefield | Mines, a geometric multiplier | C2 |
| K | Quantum Dice | Dice roll-under, roll physics | C2 |
| L | Higher-Lower | Hi-Lo, a streak of multipliers | C2 |
| M | Dragon Tower | Tower climb, risk/reward per floor | C2 |
| N | Number Lottery | Keno, picking numbers + the draw | C2 |
| O | Deluxe Gold | Scratch cards | C2 |
| P | Chests of Fortune | Bonus pick, a dramatic reveal | C2 |
| Q | Coin Kingdom | A build-and-raid slot | C3 |
| R | Roll of Fate | Board-move dice, tile events | C3 |
| S | Wheel of Luck | A prize-wheel energy hub | C3 |
| T | Collector's Album | Stickers and sets from packs | C3 |
| U | Shield and Sword | A raid & shield ladder | C3 |
| V | Summon of Legends | Banner pull, soft/hard pity | C4 |
| W | Deck of Champions | Mystery card packs | C4 |
| X | Case Roulette | A case opener with a spinner | C4 |
| Y | Capsule Machine | Gashapon, a two-stage reveal | C4 |
| Z | Joker | A poker deckbuilder | C5 |
| AA | Build Your Reel | A slot-reel roguelike | C5 |
| AB | Dice Forge | A dice-builder | C5 |
| AC | The Alchemist's Bag | A push-your-luck bag | C5 |
| AD | Golden Dozer | Coin pusher | C6 |
| AE | Neon Cascade | Plinko | C6 |
| AF | Silver Rain | Pachinko + a jackpot gate | C6 |

> Screen composition is a separate axis: the **Layout Archetype L1–L6**
> (`.claude/docs/layout-archetypes.md`). The look comes from the **Design DNA**.
> One archetype + different DNA/Layout = different games.
>
> The full category reference: `.claude/docs/gambling-categories.md`.

### The team of specialists

You are served by specialised agents:
- **`game-mathematician`** — owner of the mathematical model: RTP, house edge, pity, the economy, run win-rate.
- **`game-designer`** — designs the round, the bets, bonuses, progression and the compliance screens.
- **`mechanics-programmer`** — writes the logic: `Random.secure()`, stateless outcomes, physics on Flame `1.18.x`.
- **`juice-artist`** — makes anticipation, near-miss and win celebration feel juicy.

***

**Where shall we start?** Type `/brainstorm` to build a game interactively,
`/auto-idea` to generate a concept instantly, or `/autocreate` for a fast start.
