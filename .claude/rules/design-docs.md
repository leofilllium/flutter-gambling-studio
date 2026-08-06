---
description: Required sections and structure for gambling game GDD documents (categories C1-C6)
globs: ["design/**/*.md", "docs/**/*.md"]
---

# Design Document Standards — Mini-Game GDD

Every GDD is written in English, like the rest of the studio's output.

## The 8 required sections for every GDD

Every document in `design/gdd/` MUST contain these sections:

### 1. Overview
One paragraph: what this mechanic is, who it is for, why it exists.

### 2. Player fantasy
How should the player feel? What are they "living through"?
Example: "The player feels the tension build as the reels come to rest — every thud on the
floor creates the sense that a win is close."

### 3. Detailed rules
An unambiguous description of the mechanic. No room for interpretation.

### 4. Formulas
ALL the mathematics, with variables:
```
Win = Bet × Symbol_multiplier × Number_of_winning_lines
RTP = Σ(combination_probability × payout) / bet
```

### 5. Edge cases
- What if the balance is 0?
- What if the win exceeds the current jackpot?
- What if free spins are interrupted by a pause?
- What happens with a Scatter and a Wild on the same line?

### 6. Dependencies
Other systems this mechanic depends on:
- `WeightedRNG` — the source of randomness
- `PaylineEvaluator` — win calculation
- `AudioService` — audio feedback

### 7. Tuning knobs
Every value the game-mathematician is allowed to change:
| Parameter | Current | Range | Effect |
|-----------|---------|-------|--------|
| Wild weight | 1 | 0–3 | ↑ weight = ↑ RTP |
| Free spins multiplier | 3 | 1–5 | ↑ multiplier = ↑ volatility |

### 8. Acceptance criteria
Testable success conditions:
- [ ] AC-1: RTP within 95–97% over 1M simulations
- [ ] AC-2: Hit rate 25–35%
- [ ] AC-3: A Wild substitutes for any symbol except a Scatter
- [ ] AC-4: 3 Scatters in any position triggers free spins

## Document lifecycle

```
Draft → [OPEN questions] → Review → Approved (Status: ✅ Approved YYYY-MM-DD)
→ Implemented (link to the PR) → Deprecated (if the mechanic is removed)
```

## File naming template

Common to every category:

```
design/gdd/
├── game-concept.md            # The concept: category C1–C6, archetype, math model, compliance
├── math-model.md              # Model M1–M6: formulas, thresholds, link to the JSON config
├── round-flow.md              # The full round cycle: bet → outcome → reveal → payout
└── compliance-screens.md      # Age gate, disclaimer, responsible play, odds disclosure
```

Plus documents for the mechanics of the specific category:

| Category | Typical GDDs |
|----------|--------------|
| C1 🎰 | `reel-mechanics.md`, `payline-system.md`, `wild-scatter.md`, `free-spins.md` |
| C2 ⚡ | `multiplier-curve.md`, `cashout-rules.md`, `seed-fairness.md` |
| C3 🏰 | `spin-event-table.md`, `energy-economy.md`, `raid-shield.md`, `collection.md` |
| C4 🎁 | `banner-rates.md`, `pity-system.md`, `duplicate-conversion.md` |
| C5 🃏 | `run-structure.md`, `modifier-registry.md`, `shop-economy.md` |
| C6 ⚙️ | `physics-setup.md`, `bucket-payouts.md`, `determinism.md` |

## References from code

The code MUST reference the GDD:
```dart
/// Implements [design/gdd/payline-system.md].
/// AC-3: a Wild substitutes for any symbol except a Scatter.
class PaylineEvaluator { ... }
```

## Payout tables — the required format

```markdown
| Symbol  | 2 in a row | 3 in a row | Weight | Probability (3 reels) |
|---------|------------|------------|--------|-----------------------|
| Cherry  | 1×         | 5×         | 10     | 18.6%                 |
| Bar     | 2×         | 10×        | 7      | 9.1%                  |
| Seven   | —          | 25×        | 4      | 3.0%                  |
| Diamond | —          | 75×        | 2      | 0.7%                  |
| Wild    | —          | 100×       | 1      | 0.2%                  |
```
