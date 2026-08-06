# How to build a mini-game MVP from scratch

This guide walks you through building a gambling mini-game (slot, roulette, crash, mines,
gacha, plinko and so on) in `flutter-gambling-studio`, from an empty folder to a working APK.

> The studio builds **only** gambling games — six categories C1–C6,
> see `.claude/docs/gambling-categories.md`.

> **Important**: development can run through Claude Code or through OpenAI Codex.
> In Codex the entry point is `AGENTS.md`, and the commands, roles and hooks come from
> `.codex/` and `.claude/`. You direct the process; the agents write the mathematics, the
> design, the code and the effects.

---

## Option 1: the one-click path (magic)

If you want a finished game instantly, with no questions asked:

```bash
/autocreate
```

The studio picks one of the 32 archetypes (A–AF), declares a mathematical model, generates
`pubspec.yaml`, draws the assets, writes the logic, the UI and the compliance layer, runs the
balance simulation and configures the project. A few minutes later you can run `flutter run`.

---

## Option 2: the designer's path (step by step)

If you want control over every aspect (mechanics, balance, theme):

### Step 1. The concept (brainstorm)
First you pick the category and the archetype.

```bash
/brainstorm
```
The agent asks about the category (C1 casino · C2 originals · C3 spin-to-progress · C4 gacha ·
C5 roguelike · C6 physics), the archetype and the theme. The result is a
`design/gdd/game-concept.md` file with the mandatory **Classification** block (category,
archetype, mathematical model, target metric, compliance profile).

### Step 2. Break it into components
```bash
/map-systems
```
The studio decomposes the idea into a class architecture for Flame. The map helps the
programmers understand the scale of the work.

### Step 3. Set up the mathematical model
Each category is computed with its own model (the thresholds are in
`.claude/docs/math-models.md`):
```bash
/design-system rtp-weights       # C1: symbols, weights, the payout table  → M1
/design-system multiplier-curve  # C2: house edge and the multiplier curve → M2
/design-system energy-economy    # C3: regeneration, cap, source/sink      → M3
/design-system pity-system       # C4: base rates and soft/hard pity       → M4
```
`game-mathematician` steps in, computes the parameters and saves them to the JSON config
(`design/balance/*.json`) — the single source of truth for those numbers.

### Step 4. Draw the graphics
Ask for the base assets.
```bash
/generate-asset ui spin-button
/generate-asset symbol cherry
/generate-asset sprite chip-gold
```

### Step 5. Orchestrate development (code + VFX)
Once the plan, the balance and the assets are ready, call the team:
```bash
/team-dev "Build the game core from our design document"
```
This skill runs `mechanics-programmer` (writing the Flutter+Flame logic) and `juice-artist`
(setting up the effects, particles and animation) together.

### Step 6. Game audio
Without sound the game is dead.
```bash
@sound-designer Set up the sounds and BGM through flame_audio.
```

### Step 7. Check the balance and the quality
```bash
/balance-check
```
This runs the category's model through `tools/simulate_math.py` (1,000,000 trials) and returns
a PASS / CONCERNS / FAIL verdict with a report in `design/balance/simulation-report.md`.
A FAIL stops production: the numbers are fixed by `game-mathematician`, and only in JSON.

Directly, when you need it quickly:
```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
python3 tools/simulate_math.py --selftest   # the reference configs for all six models
```

### Step 8. Release
Once the game runs under `flutter run`, it is time for the final quality check.
```bash
/release-checklist
```
The checklist includes the **compliance blockers**: age gate, disclaimer, responsible play,
odds disclosure, and the absence of real-currency symbols next to the game balance
(`.claude/rules/responsible-gaming.md`). Without them the store will reject the game.

---

🎉 **Done — your MVP is built.**
Keep improving the game by adding features: `/add-feature "add a Wild symbol"` or
`/add-feature "add auto-bet with limits"` — the balance is recalculated automatically.
