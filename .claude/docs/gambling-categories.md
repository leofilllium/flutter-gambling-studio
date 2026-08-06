# Gambling game categories — the studio's canonical reference

> **The studio builds ONLY gambling games.** This is not a general-purpose mini-game studio.
> Every concept, archetype and production decision must fall into one of the six categories
> below. If an idea fits none of them, it is not for this studio.
>
> This document is the single source of truth for the taxonomy. It is referenced by
> `CLAUDE.md`, `/auto-idea`, `/brainstorm`, `/autocreate`, `/balance-check`,
> `/design-system`, `/gate-check` and `/release-checklist`.

## What "a gambling game" means in this studio

A game belongs to our domain if its **core is a random-outcome mechanic with a stake**: the
player commits a resource (virtual chips, a spin, energy, premium currency, a card in hand),
the outcome is decided by a random number generator according to a declared mathematical model,
and the result creates a "risk → anticipation → reveal → reward" loop.

**Always virtual.** No game in the studio accepts or pays out real money. Virtual currency does
not convert back into money and cannot be withdrawn. See
`.claude/rules/responsible-gaming.md` — those rules block the release.

---

## The six categories

| ID | Category | Icon | Core | Balance metric | Archetypes |
|----|----------|------|------|----------------|------------|
| **C1** | Social Casino (casino simulation) | 🎰 | Recreating a real casino floor with virtual chips | RTP 95–97% | A–H |
| **C2** | Casino Originals / Instant-Win | ⚡ | "Originals": an instant round, a live multiplier, cash-out | RTP 96–99% | I–P |
| **C3** | Spin-to-Progress Hybrids | 🏰 | The spin/roll is the energy source for a casual meta game | Economy: source/sink | Q–U |
| **C4** | Gacha & Loot-Box | 🎁 | Pulls from a banner with rarities and pity | Pull rates + pity | V–Y |
| **C5** | Casino Roguelike & Strategy | 🃏 | Casino mechanics as the combat system of a single-player roguelike | Run win-rate 25–40% | Z–AC |
| **C6** | Coin Pusher & Plinko (arcade physics) | ⚙️ | Falling/pushing physics as the outcome generator | Empirical RTP 95–97% | AD–AF |

> **C2 is an extension of the base taxonomy.** The "originals" (crash, mines, dice, hi-lo,
> tower, keno, scratch, bonus-pick) are an independent and now the largest family of modern
> gambling mini-games. Formally they are simulated casino (C1), but their mathematics is
> different (an instant round with no reels, a multiplier curve, cash-out) and so is their UI,
> so the category is broken out separately.

---

## C1 — Social Casino (simulated casino) 🎰

**What it is.** A digital recreation of a real casino floor: slots, poker, blackjack, roulette,
bingo. Play is strictly with virtual chips; winning or withdrawing real money is impossible, but
extra chip bundles can be bought.

**Feel references:** Slotomania, Heart of Vegas, Zynga Poker, WSOP Mobile, Bingo Blitz.

**Core loop:** choose a bet → round → outcome reveal → payout → chips → the next bet.

**Required systems:** paytable, bet tiers (min/max/steps), chip balance, player XP/level, chip
bundles in the shop, a daily bonus (protection against "out of chips"), a leaderboard.

**Mathematical model:** RTP 95–97% over 1M rounds, hit rate 20–35%, declared volatility
(low/medium/high), a complete payout table. All weights live in `rtp-config.json`.

**Compliance profile:** age gate, a "virtual chips, not real money" disclaimer, a responsible
play block, an 18+ rating (Google Play: the Social Casino category).

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **A** | Classic 3×3 slot | 3 reels, fixed lines | A controlled near miss — the third reel slows down |
| **B** | 5×3 video slot with free spins | 5 reels, 10–25 lines, a scatter trigger | Avalanche: symbols explode, the ones above fall, the multiplier grows |
| **C** | Scatter-pays / cluster slot | Payouts for the NUMBER of symbols (8+), no lines | A tumble chain with bomb multipliers |
| **D** | Hold & Spin (Link & Win) | Respins with sticky coin symbols, 3 jackpot tiers | Every new coin resets the respin counter to 3 |
| **E** | Video poker | A 5-card deal, hold, a second draw | Double-up: doubling the win by guessing the suit |
| **F** | Blackjack | Hit / stand / double / split against the dealer | A readable dealer hand plus a basic-strategy hint |
| **G** | Roulette | European (single zero), inside and outside bets | A physically believable ball bounce across the pockets |
| **H** | Social bingo | 75-ball rooms, auto-daub, patterns | Power-ups (an extra ball, an instant daub) and collectible cards |

---

## C2 — Casino Originals / Instant-Win ⚡

**What it is.** Instant rounds with none of the casino-floor trappings: the multiplier climbs in
real time and the player decides when to take it. Maximally "readable" mathematics — the player
sees the probability and the current win right on screen.

**Feel references:** crash games, mines, dice, hi-lo, tower, keno, scratch.

**Core loop:** bet → the round unfolds step by step → the player either cashes out at any moment
OR loses everything → an instant restart.

**Required systems:** an explicit current multiplier, a cash-out button, a history of recent
rounds (in C2 this is a key element of trust), auto-bet with limits, a maximum win cap.

**Mathematical model:** RTP 96–99% (house edge 1–4%), an explicit multiplier formula, a
provably-fair-style deterministic round seed (`serverSeed + clientSeed + nonce`), a declared
maximum multiplier. Checked separately: **the multiplier is NEVER computed during the
animation** — the whole round is predetermined at the start.

**Compliance profile:** the same as C1, plus a mandatory visible round history and a house edge
declared in the rules.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **I** | Crash | The multiplier climbs along a curve while an object flies; cash out before the crash | Visualised physical acceleration plus a particle trail |
| **J** | Mines | A grid with mines; every safe cell multiplies the win | Geometric multiplier growth plus tension on hover |
| **K** | Dice (roll-under) | The player sets a threshold; a roll below it wins | Honest 2D roll and wall-bounce physics (Forge2D) |
| **L** | Hi-Lo | Guess whether the next card is higher or lower; a streak of multipliers | A risk meter that grows with the streak, cash out at any moment |
| **M** | Tower Climb | Climb the floors, choosing 1 of N cells per floor | Risk/reward: every floor is a "take it or go higher" decision |
| **N** | Keno / number lottery | Pick numbers on a grid, then the draw | A ball draw with physical bouncing |
| **O** | Scratch cards | Rub the fields with a finger, 3 matches wins | Peeling foil particles, tactile scratching |
| **P** | Bonus Pick | Choose from N closed objects, each a multiplier or "collect" | A dramatic reveal with a delay and rising tension |

---

## C3 — Spin-to-Progress Hybrids 🏰

**What it is.** A casual meta game (building, collecting, raiding rivals) where a slot machine or
a dice roll is the main source of energy and events. The gambling mechanic drives all the rest
of the progress.

**Feel references:** Monopoly GO!, Coin Master, Dice Dreams.

**Core loop:** spin (spends energy) → an event result (coins / shield / raid / attack) → invest
in the meta progress (building / collection) → an unlock → a new goal for spins. Energy refills
on a timer.

**Required systems:** energy with regeneration and a cap, a meta progress object
(village/album/board), a weighted spin event table, a card/sticker collection with duplicates,
shields and revenge (if there is a PvP layer), tournament events.

**Mathematical model:** this is **not RTP, it is an economy**. What is checked:
- energy regeneration (spins/hour) and the cap;
- source/sink balance — how many coins arrive per 100 spins against the price of the next unlock;
- **progress pace** — how many sessions until the next meaningful unlock (target: 2–5 sessions,
  not 40);
- an average session length of 3–7 minutes;
- the absence of a "grind wall": the price of unlock N+1 is no more than 1.6× the price of unlock N.

**Compliance profile:** age gate + disclaimer (spin mechanics = simulated gambling), plus
explicit disclosure of the spin event table's probabilities if spins can be paid for.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **Q** | Build-and-raid slot | The spin gives coins / a shield / an attack / a raid; coins build the village | Raiding a rival's base by digging 1 of 4 spots |
| **R** | Board-move dice | A dice roll moves the token round the board, each tile an event | A board season: a lap of the board unlocks a new themed board |
| **S** | Prize-wheel energy hub | The wheel dispenses energy/boosters/currency; timers hide behind the wheel | A jackpot sector with a progress bar that builds between spins |
| **T** | Sticker / card album | The spin awards sticker packs; the album fills up into sets | Duplicates → trade currency; completing a set is a major reward |
| **U** | Raid & shield ladder | The spin gives attacks and shields; PvP-lite against bot rivals | Revenge: a list of who attacked you, with a window to respond |

---

## C4 — Gacha & Loot-Box 🎁

**What it is.** Progression built on **pulls** — a mechanic modelled directly on Japanese capsule
machines and slot-machine drop rates. Formally this is an RPG/collection game, but the core is
randomised distribution in exchange for currency.

**Feel references:** Genshin Impact, Honkai: Star Rail, RAID: Shadow Legends, sports/anime games
that build a roster out of packs.

**Core loop:** earn/buy premium currency → pull (x1 / x10) → the reveal animation → rarity →
strengthen the collection → new content demands a stronger collection.

**Required systems:** a rarity table with explicit percentages, a **pity counter** (hard pity
mandatory, soft pity optional), an x10 pull with a guarantee, conversion of duplicates into
shards, banners on rotation, a collection showcase, an "odds" screen (rates disclosure).

**Mathematical model:**
- Rates by rarity (typically: SSR 0.5–2%, SR 5–12%, R the rest);
- Hard pity 50–90 pulls, soft pity — a rising chance starting at roughly 75% of hard pity;
- **Effective rate** including pity (a 1M pull simulation);
- E[pulls to the first SSR] and the 90th percentile (the realistic worst case);
- Cost: how many sessions/currency until a guaranteed SSR.

**Compliance profile:** **odds disclosure is mandatory and must be in-game** (a requirement of
the stores and of several jurisdictions) — the "Odds" screen is reachable BEFORE a pull. Plus an
age gate, a disclaimer, and the pity counter shown to the player.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **V** | Banner pull (collector) | x1/x10 pulls on a banner, rarities, hard + soft pity | A visible pity counter and a guarantee on the 10th pull |
| **W** | Mystery card packs | Opening card packs, building a roster/deck | Duplicates upgrade a card's level rather than becoming junk |
| **X** | Case / crate opener | A roulette spinner scrolls through items and slows to the drop | A decelerating spinner with a near-miss on a rare item |
| **Y** | Capsule machine (gashapon) | A physical metaphor: a handle, a capsule rolls out and cracks open | A two-stage reveal: capsule → contents |

---

## C5 — Casino Roguelike & Strategy 🃏

**What it is.** The premium/indie approach: casino mechanics (poker hands, dice rolls, reels)
turned into a **single-player tactical system**. There are no real-money stakes and no
microtransactions — here the gambling mechanic is the combat system.

**Feel references:** Balatro, Luck be a Landlord, Dicey Dungeons.

**Core loop:** a run → a round with a target score → the player assembles/upgrades their "engine"
(deck / reel / set of dice) → the target rises → the run ends in victory or defeat → a meta
unlock for the next run.

**Required systems:** seeded run determinism (one seed = one reproducible run), a shop between
rounds, modifiers ("jokers"/symbols/items), escalating targets, a run summary screen, meta
unlocks between runs, a daily run on a shared seed.

**Mathematical model:**
- **Run win-rate 25–40%** for an average player (simulating an "average player policy");
- monotonic round target thresholds (no jump larger than ×2);
- modifier strength: none may give a win-rate above 80% on its own;
- run economy: income per round against shop prices;
- **determinism**: one seed reproduces the run bit for bit (the test is mandatory).

**Compliance profile:** an age gate is **not required** if there are no purchases and no
simulated currency wagering. The disclaimer stays if it looks like a casino. The rating is
typically 12+. This is the only category with relaxed compliance — record that decision
explicitly in the concept.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **Z** | Poker deckbuilder | Poker hands deal "damage"/score points against rising targets | Joker modifiers that change how hands are scored |
| **AA** | Slot-reel roguelike | The player assembles the reel out of symbols; a spin is income | Symbol synergies: adjacency changes the payout |
| **AB** | Dice-builder | Dice are the resource; faces are upgraded between fights | Reforging a face: swapping one face for an effect |
| **AC** | Push-your-luck bag | Draw chips from a bag until you bust the threshold | The bust threshold is visible, but the bag's contents change each round |

---

## C6 — Coin Pusher & Plinko (arcade physics) ⚙️

**What it is.** Digital adaptations of fairground and arcade games of chance. The outcome is
decided by physics rather than a table — but the mathematics must still converge on the target RTP.

**Feel references:** Coin Dozer, Plinko, Japanese pachinko.

**Core loop:** spend a chip → launch an object → physics decides → a cascading reward → the field
accumulates potential for the next launch.

**Required systems:** a Forge2D world with a deterministic simulation step, an accumulating field
(that is where the pleasure lives), a bucket/pocket multiplier table, special prizes on the
field, a cap on simultaneous bodies (performance).

**Mathematical model:** RTP is measured **empirically** — a 1M launch run in a headless physics
simulation, not analytically. Required:
- RTP 95–97% from the run;
- **determinism**: a fixed timestep + a fixed seed → a reproducible result (otherwise the RTP
  cannot be verified and the round is not stateless);
- the payout distribution (not just the mean): the share of launches into each bucket;
- a cap on active bodies so the physics does not drift when the fps drops.

**Compliance profile:** the same as C1.

### Archetypes

| ID | Name | Mechanic | Unique feature |
|----|------|----------|----------------|
| **AD** | Coin Pusher / Dozer | Coins drop onto a moving shelf and push prizes over the edge | A build-up of coin "overhang" at the edge — a visual promise |
| **AE** | Plinko | A ball falls through a field of pegs into multiplier buckets | A choice of risk profile (number of rows / bucket layout) |
| **AF** | Pachinko | A vertical field, balls fall into traps, triggering a jackpot gate | The jackpot gate: a hit launches a separate slot round |

---

## The full archetype index A–AF

| Category | Archetypes |
|----------|------------|
| C1 Social Casino 🎰 | **A** 3×3 slot · **B** 5×3 video slot · **C** scatter-pays · **D** Hold&Spin · **E** video poker · **F** blackjack · **G** roulette · **H** bingo |
| C2 Originals ⚡ | **I** crash · **J** mines · **K** dice · **L** hi-lo · **M** tower · **N** keno · **O** scratch · **P** bonus pick |
| C3 Spin-to-Progress 🏰 | **Q** build-and-raid · **R** board-dice · **S** prize-wheel · **T** album · **U** raid&shield |
| C4 Gacha 🎁 | **V** banner pull · **W** card packs · **X** case opener · **Y** gashapon |
| C5 Roguelike 🃏 | **Z** poker deckbuilder · **AA** reel roguelike · **AB** dice-builder · **AC** push-your-luck |
| C6 Physics ⚙️ | **AD** coin pusher · **AE** plinko · **AF** pachinko |

---

## How the archetype is chosen (in `/auto-idea` and `/autocreate`)

The archetype sets the **mechanic**. So that games of the same archetype do not repeat, two
independent axes are cycled on top of it:

```
Game = Archetype (WHAT the mechanic is)
     × Layout Archetype L1–L6 (HOW it is composed — layout-archetypes.md)
     × Design DNA (HOW it looks — anti-slop-design.md)
```

A pseudo-random choice that avoids repeating the previous one:

```python
import time
ARCHETYPES = [
    # C1
    "A", "B", "C", "D", "E", "F", "G", "H",
    # C2
    "I", "J", "K", "L", "M", "N", "O", "P",
    # C3
    "Q", "R", "S", "T", "U",
    # C4
    "V", "W", "X", "Y",
    # C5
    "Z", "AA", "AB", "AC",
    # C6
    "AD", "AE", "AF",
]
archetype = ARCHETYPES[int(time.time()) % len(ARCHETYPES)]
```

> **Unique Mode.** If the user asks for a unique mechanic, invent a new one — but it MUST remain
> a gambling mechanic and fall into one of the six categories (usually at the seam between two:
> "plinko where the buckets are poker hands", "crash with a pity counter").
> The category and its mathematical model are fixed in the concept before production begins.

## The mandatory concept block

Every `design/gdd/game-concept.md` MUST open with a classification block — downstream phases
read it literally:

```markdown
## Classification
- **Category**: C1 | C2 | C3 | C4 | C5 | C6 — [category name]
- **Archetype**: [A–AF | UNIQUE] — [name]
- **Mathematical model**: [RTP | Instant-Win RTP | Economy | Gacha | Run Win-Rate | Physics RTP]
- **Target metric**: [e.g. "RTP 96.0% ±1%", "hard pity 70, SSR 1.2%", "run win-rate 32%"]
- **Compliance profile**: [full (age gate + disclaimer + 18+) | relaxed C5 (justify it)]
- **Game language**: English (default) | [another language, only if the user explicitly asked]
```

Without this block, `/gate-check concept` returns FAIL.
