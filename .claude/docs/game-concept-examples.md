# Game concept examples and preview references

Inspect the matching local preview when a user requests one of these game families. For the five
named requests below, the listed preview is mandatory input to `/autocreate`, including common
spacing, punctuation, and capitalization variants of the name. These are starting directions for
original concepts, not runtime assets, fixed templates, or validated balance designs. Use
`.claude/docs/visual-context.md` and record the preview path, borrowed traits, original adaptations,
lead kind, and topology decision in the generated concept before producing assets.

| Request family | Preview | Classification | Lead and assets | Store starting composition |
|---|---|---|---|---|
| Book of Ra / Book of Ra game | `examples-games/book-of-ra.png` | C1 / B / M1 | Character; original desert archaeologist, enchanted book, ankhs, scarabs, falcons, Egyptian relics | Large adapted explorer on the first panel; readable 5×3 field occupies the right; sunset temple depth and relic spill support the gameplay |
| Joker / Joker game | `examples-games/joker2.png`, with `examples-games/joker.jpeg` as secondary reference | C1 / A / M1 | Character; original impish, slightly vicious Joker, bells, cherries, gems, supported multiplier chips | Large adapted Joker on first panel; readable 3×3 field spans the right two by default; gestures lead toward play |
| Shining Crown / Shining Crown game | `examples-games/shining-crown.jpeg` | C1 / A / M1 | Object; crown, jewel star, clover gem, ruby, supported multiplier medallions | No invented player or mascot; slides 1–2 show authentic reels at a three-quarter/3D angle, with reward objects across the foreground |
| Zeus Game / Zeus slot | `examples-games/zeus.jpeg` | C1 / C / M1 | Character; original thunder god, lightning, eagle, laurel, temple and storm symbols | Large adapted Zeus on first panel; readable 7×6 field occupies the right; lightning and game objects can spill through the foreground |
| Plinko / Plinko game | `examples-games/plinko.jpeg` | C6 / AE / M6 | Mechanic; glossy colored balls, pegs, buckets, charged coins | Active tilted peg field can fill all three panels; trajectories and coins carry motion; no invented person or mascot |
| Chicken risk game | No exact local preview required | C2 / M / M2 step model, if using safe-step wagering | Character; expressive chicken, safe/risk tiles, supported reward tokens | Chicken on first panel; actual staged risk path may span the remaining panels or whole scene |

For Book of Ra, Joker, and Zeus Game, retain the requested character archetype and role while
making the generated character visibly original. Change several identity-defining choices such
as facial structure, age, hair or headwear, costume silhouette, palette, accessories, pose, and
gesture; do not trace the preview, reproduce its exact face/costume, import its pixels, or copy a
logo. Preserve the useful composition and subject language so the requested family still reads.
For Shining Crown and Plinko, the absence of a main character is part of the reference contract:
do not add a host, mascot, hand, player silhouette, deity, or other living lead.

## Concept seeds

**Prism Drop:** Stake virtual chips, release a luminous ball into a cosmic peg field, and reveal
the bucket's configured multiplier. The core feeling is the last deflection before landing.
Use the Plinko preview's diagonal action, oversized glossy balls, luminous trails and saturated
separation. Rebuild the actual board from the M6 config; the preview does not establish bucket
count, probabilities, or multipliers. M6 RTP target: 95–97%, verified by simulation.

**Sun Archive:** A 5×3 Egyptian-adventure slot centered on a glowing book reveal and an explorer
who discovers the configured winning state. Borrow the preview's explorer-left/field-right staging,
sunset temple depth, turquoise-and-gold relic family, and dense archaeological foreground. Create
an original explorer design and original symbols rather than duplicating the reference character.
The visible 5×3 topology is intentional for this named family and must match the M1 config, runtime,
and store captures. M1 RTP target: 95–97%.

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

**Thunder Reels:** A 7×6 Zeus scatter-pays slot built around a lightning reveal of a configured
winning cluster. Zeus is an in-game character and visual lead, with an original
eagle/bolt/laurel asset family.
Borrow the local preview's character-left/field-right energy, cloud-bright Olympus depth, electric
blue/gold separation, and tumbling thematic objects while changing Zeus's face, costume details,
pose, and supporting ornament. The preview's 7×6 topology is intentional for this named family and
must match the M1 config, runtime, and store captures; the reference does not establish symbol
weights, cluster thresholds, or payouts. Lightning effects never manufacture near misses or change
resolved results.

**Chicken Dare:** A virtual-stake safe-step game: choose to advance to another risk tier or take
the current virtual reward. It is C2/M2, not an endless runner. The chicken's comic defiance makes
it the visual lead. Configure the step probabilities and cash-out multipliers in the M2 model;
use x5/x10 tokens only when those exact steps are supported. House edge and maximum multiplier
are disclosed; target RTP is 96–99%.

For every seed, finish the normal concept: complete loop, production plan, mobile/expanded layout,
asset manifest, meta systems, required screens, responsible-play copy and a verifiable JSON model.
The preview alone never proves playable UI, balance, or a completed game.
