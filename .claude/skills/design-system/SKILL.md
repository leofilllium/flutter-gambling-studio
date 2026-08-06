---
name: design-system
description: "Designs one individual system of a gambling game: symbol weights and payouts (C1), the multiplier curve and cash-out (C2), the energy economy and the spin event table (C3), rates and pity (C4), modifiers and run targets (C5), board geometry and bucket multipliers (C6). Generates a GDD document with game-mathematician and game-designer involved."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write
argument-hint: "<system-name> (e.g. rtp-weights, free-spins, multiplier-curve, pity-system, energy-economy)"
---

# `design-system` — detailing a game system

Interactively designs one **game** system of a gambling game (mechanics/balance).

> The **visual design system** (Design DNA → theme tokens: palette, type scale, shapes, motion)
> and the **composition** (Layout Archetype) live in the concept: `design/gdd/game-concept.md`
> (Design DNA) and `design/art-direction.md` (Layout). See `.claude/rules/anti-slop-design.md`
> (plus its craft fundamentals) and `.claude/docs/layout-archetypes.md`. This skill is about
> game systems, not about the theme.

## Workflow

1. **Context**: read `design/gdd/game-concept.md`, the **Classification** block —
   it sets the category (C1–C6) and the mathematical model (M1–M6).

2. **The system's type**: decide who leads the work.

   | Category | Mathematics (`game-mathematician`) | Mechanics (`game-designer`) |
   |----------|------------------------------------|-----------------------------|
   | **C1** 🎰 | symbol weights, the payout table, RTP, hit rate | Wild/Scatter, free spins, bonus round, bet tiers |
   | **C2** ⚡ | house edge, the multiplier formula, the cap | cash-out, auto-bet and its limits, round history |
   | **C3** 🏰 | spin event weights, unlock prices, energy regeneration | raids, shields, the collection, board seasons |
   | **C4** 🎁 | base rates, soft/hard pity, E[pulls] | banners, the x10 guarantee, duplicate conversion |
   | **C5** 🃏 | round thresholds, modifier strength, income | the between-rounds shop, unlocks, the daily run |
   | **C6** ⚙️ | bucket multipliers, the hit distribution | the risk profile, special prizes, the jackpot gate |

   **Audio/VFX** in every category: `juice-artist` / `sound-designer`
   (anticipation, near-miss, cash-out, reveal, cascade).

3. **The interactive part (questions)** — examples by system:

   `rtp-weights` (C1):
   - The list of base symbols and their roles (low/medium/premium/Wild/Scatter).
   - The multiplier on the rarest symbol (x100? x1000?).
   - The share of losing rounds (usually 65–80%, i.e. a hit rate of 20–35%).

   `multiplier-curve` (C2):
   - The target house edge (1% / 2–3% / 4%).
   - The shape of the curve and the maximum multiplier (a cap is mandatory).
   - Which step the player usually cashes out on — the feel is calibrated around that.

   `pity-system` (C4):
   - The SSR base rate and hard pity (50–90).
   - Whether there is soft pity, from which pull, and with what step.
   - Whether the player sees the pity counter (recommended: yes).

   `energy-economy` (C3):
   - The energy cap, regeneration per hour, the cost of a spin.
   - How many sessions a day should be available for free.
   - The unlock price step (≤ 1.6×) and whether income grows along with progress.

4. **Generating the draft**:
   Write it to `design/gdd/[system-name].md`, in English.
   Required fields:
   - *Balance impact* — how the system affects the model's target metric (RTP / pity / the economy)
   - *Visual feedback* — what feedback the player gets when it fires
   - *Edge cases* — boundary situations (zero balance, tap spam, the session breaking mid-round)
   - *Config keys* — which fields will appear in the model's JSON config

5. **Next steps**:
   - `/balance-check` — mandatory if the system touches the model's numbers
   - Call `/team-dev` to program the system
