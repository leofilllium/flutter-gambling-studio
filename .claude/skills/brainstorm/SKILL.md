---
name: brainstorm
description: "Interactive generation of a gambling game concept. Settles the category (C1-C6: social casino, casino originals, spin-to-progress, gacha, casino roguelike, coin pusher/plinko), the archetype, the mathematical model, the theme, the mechanic and the one unique piece of juice."
argument-hint: "[a theme, or 'open' for an open brainstorm]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

> **GAMBLING ONLY.** The studio does not make puzzles, runners, shooters or clickers. If the
> user proposes a non-gambling idea, say so directly in one sentence and offer the nearest
> gambling mechanic with the same feel (for example "match-3" → a scatter-pays/cluster slot
> with a tumble cascade, category C1, archetype C).
>
> The canonical reference for categories and archetypes: `.claude/docs/gambling-categories.md`.
> Every concept is for Android phones and iPhone in portrait only. Read
> `.claude/docs/mobile-phone-contract.md`; do not offer tablet/iPad, desktop, wide-screen, or
> landscape variants.

When this skill is invoked:

1. **Check the existing documents**: `design/gdd/game-concept.md`. If it exists, ask whether we
   are continuing that work.

2. **The interactive phases (ask the questions step by step)**:

   **Phase 0: choosing the category and archetype**
   The mandatory first step is to settle the category:

   | ID | Category | What it is | Archetypes |
   |----|----------|------------|------------|
   | **C1** 🎰 | Social Casino | A casino floor simulated with virtual chips: slot, poker, blackjack, roulette, bingo | A–H |
   | **C2** ⚡ | Casino Originals | An instant round with a live multiplier and cash-out: crash, mines, dice, hi-lo, tower, keno, scratch | I–P |
   | **C3** 🏰 | Spin-to-Progress | The spin is the energy source for a casual meta: a village, a board, an album, raids | Q–U |
   | **C4** 🎁 | Gacha & Loot-Box | Pulls with rarities and pity: banners, packs, cases, gashapon | V–Y |
   | **C5** 🃏 | Casino Roguelike | Casino mechanics as the combat system of a single-player roguelike | Z–AC |
   | **C6** ⚙️ | Coin Pusher & Plinko | Physics as the outcome generator: dozer, plinko, pachinko | AD–AF |

   Then the specific archetype inside the category (or a hybrid at the seam of two categories).

   **Phase 1: theme and emotion**
   - What atmosphere are we creating? (Neon cyberpunk, Egypt, space, fantasy, a cosy bingo
     room, a fairground, a Japanese arcade hall?)
   - Who is our target audience? (Casual or hardcore?)
   - ⚠️ Do not default to "dark neon + gold" — that is casino slop, not a choice. Ask about the
     world before you ask about the palette.

   **Phase 2: the mathematical model** (determined by the category)

   The thresholds and formulas are in `.claude/docs/math-models.md`.

   *C1 → model M1 (Paytable RTP):*
   - *Low volatility (RTP ~96.5%)*: frequent small wins, for a long session
   - *Medium volatility (RTP ~96%)*: balanced, wins up to x200
   - *High volatility (RTP ~95%)*: rare but large jackpots (up to x1000)
   - Hit rate 20–35%, the number of reels/lines, whether there is a bonus mode

   *C2 → model M2 (Instant-Win RTP):*
   - House edge: 1% (generous) / 2–3% (standard) / 4% (harsh) → RTP 96–99%
   - The maximum multiplier and the win cap
   - Whether there is auto-bet, and its limits
   - Round history on screen — mandatory

   *C3 → model M3 (Economy):*
   - The energy cap and regeneration (how many sessions a day it covers)
   - The spin event table: coins / shield / attack / raid / jackpot and their weights
   - Pace: how many sessions until a meaningful unlock (target 2–5)
   - Whether there is a PvP layer (raids/revenge) or PvE only

   *C4 → model M4 (Gacha):*
   - The base rate of the rarest tier (0.5–2%)
   - Hard pity (50–90 pulls), and whether soft pity is needed
   - What a duplicate does (shards / level / trade)
   - The odds disclosure screen — mandatory

   *C5 → model M5 (Run Win-Rate):*
   - The target run win-rate (25–40%), the run length (8–20 minutes)
   - How many rounds per run and how the targets escalate
   - How many modifiers there are and how different they are
   - A daily run on a shared seed?

   *C6 → model M6 (Physics RTP):*
   - The field geometry and bucket multipliers, target RTP 95–97%
   - Does the player choose a risk profile?
   - The limit on simultaneous bodies (performance)

   **Phase 3: the mechanic**
   - What is the core round loop? (bet → outcome → reveal → payout)
   - Which special elements will there be? (Wild/Scatter, cash-out, pity, jokers, special buckets)
   - How complex are the controls? How many taps to the first round (target ≤ 3)?

   **Phase 4: juiciness**
   - Which visual feature will set the game apart? (Cascading explosions? A decelerating
     spinner? A slowdown before the crash? A coin avalanche? A shaking camera?)
   - ⚠️ Anticipation and near-miss must be HONEST: they display the real outcome, they do not
     tune the feeling.

   **Phase 5: visual identity and composition**
   - **Design DNA**: which world/mood? The palette, fonts, shapes and motion all derive from it
     (see `.claude/rules/anti-slop-design.md`). Brightness is light/dark per the theme, not
     "always dark".
   - **Layout Archetype** (L1–L6, see `.claude/docs/layout-archetypes.md`): how are the screens
     composed (top HUD / bottom console / floating corners / thumb rail / split / cards)?
     Vary both the style and the composition, so the game does not resemble the previous ones.
   - **Phone proof**: how the composition adapts across 360×640, 360×800, 390×844 and 430×932
     while keeping the primary action in thumb reach and the core loop above the fold.

   **Phase 6: the compliance profile**
   - The full profile (age gate + disclaimer + responsible play + 18+) — the default.
   - Relaxed — only for C5 without purchases and without currency wagering; requires a justification.
   - Whether a separate odds disclosure screen is needed (mandatory for C4 and paid spins in C3).
   - See `.claude/rules/responsible-gaming.md`.

   **Phase 7: the game's language**
   - English by default — every player-facing string, plus store metadata.
   - Only ask about another language if the user brings it up; if they do, record the choice in
     the Classification block. See `CLAUDE.md` → Language.

3. **Synthesis**: produce 3 concepts to choose from. Each must include an elevator pitch, the
   category and archetype, the mathematical model with its target metric, the theme, the "juicy"
   feature, the **Design DNA** and the **Layout Archetype** — and ideally 3 different visual
   directions (light/dark/minimal, say) rather than three neon ones.

4. **Writing the document**: create `design/gdd/game-concept.md` from the
   `.claude/docs/templates/gambling-concept.md` template — starting with the **Classification**
   block (category, archetype, model, target metric, config, compliance profile).
   Record the phone-only portrait target in the Classification and Layout sections.

5. **Next steps**:
   - "Use `/design-system [system]` to design the mechanic in detail"
   - "Use `/balance-check` to verify the mathematics before any code"
   - "Use `/prototype [mechanic]` to check the juiciness"
   - "Bring in `/team-dev` to start development"
