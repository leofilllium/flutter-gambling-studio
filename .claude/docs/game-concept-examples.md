# Game concept examples and preview references

Inspect the matching local preview when a user requests one of these game families. These are
starting directions for original concepts, not fixed templates or validated balance designs.
Use `.claude/docs/visual-context.md` and record reference choices in the generated concept.

| Request family | Preview | Classification | Lead and assets | Store starting composition |
|---|---|---|---|---|
| Cosmic Plinko | `examples-games/plinko.jpeg` | C6 / AE / M6 | Mechanic; glossy colored balls, pegs, buckets, charged coins | Active tilted peg field can fill all three panels; trajectories and coins carry motion; no invented person |
| Royal crown slot | `examples-games/shining-crown.jpeg` | C1 / A / M1 | Object; crown, jewel star, clover gem, ruby, supported multiplier medallions | Crown/reels own the composition, with reward objects across the foreground; no character-only first panel |
| Joker classic slot | `examples-games/joker2.png`, optionally `examples-games/joker.jpeg` | C1 / A / M1 | Character; impish slightly vicious Joker, bells, cherries, gems, supported multiplier chips | Large Joker on first panel; readable 3×3 field spans the right two by default; gestures lead toward play |
| Zeus lightning slot | No exact local preview required | C1 / A / M1 | Character; bold Zeus, lightning, eagle, thematic reward coins | Large Zeus on first panel; reels and lightning resolve wherever they read best; avoid generic crown substitution |
| Chicken risk game | No exact local preview required | C2 / M / M2 step model, if using safe-step wagering | Character; expressive chicken, safe/risk tiles, supported reward tokens | Chicken on first panel; actual staged risk path may span the remaining panels or whole scene |

## Concept seeds

**Prism Drop:** Stake virtual chips, release a luminous ball into a cosmic peg field, and reveal
the bucket's configured multiplier. The core feeling is the last deflection before landing.
Use the Plinko preview's diagonal action, oversized glossy balls, luminous trails and saturated
separation. Rebuild the actual board from the M6 config; the preview does not establish bucket
count, probabilities, or multipliers. M6 RTP target: 95–97%, verified by simulation.

**Crown Cascade:** A classic 3×3 virtual-chip slot whose three crowned symbols illuminate a real
winning line. Borrow royal tactility, jewel silhouettes, dramatic lighting and the coin spill
from the crown preview. The preview's single visible strip is not the new game's row count.
Create 3 visible rows, model-supported payout coins, and original frame ornament. M1 RTP target:
95–97%; declare paylines, weights and payouts before generation.

**Joker's Dare:** A 3×3 slot with five configured paylines and a grinning theatrical trickster.
Bells, cherries and gems read at phone size; supported x5/x10 medallions can punctuate rewards.
Borrow `joker2.png`'s character-left/field-right composition and bold gesture, but sharpen the
Joker's mischievous expression rather than producing an elegant host. Derive every depicted
winning line from the actual resolver; five lines are a concept choice that must enter M1.

**Thunder Reels:** A 3×3 Zeus slot built around a lightning reveal of a configured winning line.
Zeus is an in-game character and visual lead, with an original eagle/bolt/laurel asset family.
Keep the first-panel face clear and let the field extend across the right two panels when useful.
The game is C1/M1; lightning effects never manufacture near misses or change resolved results.

**Chicken Dare:** A virtual-stake safe-step game: choose to advance to another risk tier or take
the current virtual reward. It is C2/M2, not an endless runner. The chicken's comic defiance makes
it the visual lead. Configure the step probabilities and cash-out multipliers in the M2 model;
use x5/x10 tokens only when those exact steps are supported. House edge and maximum multiplier
are disclosed; target RTP is 96–99%.

For every seed, finish the normal concept: complete loop, production plan, mobile/expanded layout,
asset manifest, meta systems, required screens, responsible-play copy and a verifiable JSON model.
The preview alone never proves playable UI, balance, or a completed game.
