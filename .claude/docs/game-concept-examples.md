# Game concept examples and preview references

Inspect the matching local preview when a user requests one of these game families. For the six
named requests below, the listed preview is mandatory input to `/autocreate`, including the
`--from-concept` path and common spacing, punctuation, hyphenation, and capitalization variants of
the name. A reference entry is either one file or a folder; when it is a folder, every file in it
is mandatory input and the table states each file's job. These are visual identity references;
suitable pixels may be reused as runtime assets when cleanly isolated and sharp at target size.
They are not complete game specifications or validated balance designs. Use
`.claude/docs/visual-context.md` and record the preview path, borrowed traits, original adaptations,
lead kind, and topology decision in the generated concept before producing assets.

| Request family | Preview | Classification | Lead and assets | Store starting composition |
|---|---|---|---|---|
| Book of Ra / Book of Ra game | `examples-games/book-of-ra.png` | C1 / B / M1 | Character; reference-matched desert archaeologist, enchanted book, ankhs, scarabs, falcons, Egyptian relics | Large reference-matched explorer on the first panel; readable 5×3 field occupies the right; sunset temple depth and relic spill support the gameplay |
| Joker / Joker game | `examples-games/joker2.png`, with `examples-games/joker.jpeg` as secondary reference | C1 / A / M1 | Character; reference-matched impish, slightly vicious Joker, bells, cherries, gems, supported multiplier chips | Large reference-matched Joker on first panel; readable 3×3 field spans the right two by default; gestures lead toward play |
| Joker Jewels / Joker's Jewels / joker-jewels | `examples-games/joker-jewels/` — all four files: `jj_reference.jpeg` (key-art staging), `jj_gameplay.jpeg` (board topology and symbol family), `jj_character-reference.jpeg` and `jj_character-reference2.jpeg` (jester lead) | C1 / B / M1 | Character; reference-matched belled-cap jester in a striped costume, plus faceted red and cyan gems, blue orb, lute, juggling clubs, jester shoes, crown bonus symbol | Large reference-matched jester on the first panel; readable 5×3 field occupies the right; gems, bunting and confetti spill through the foreground |
| Shining Crown / Shining Crown game | `examples-games/shining-crown.jpeg` | C1 / A / M1 | Object; crown, jewel star, clover gem, ruby, supported multiplier medallions | No invented player or mascot; slides 1–2 show authentic reels at a three-quarter/3D angle, with reward objects across the foreground |
| Zeus Game / Zeus slot | `examples-games/zeus.jpeg` | C1 / C / M1 | Character; reference-matched thunder god, lightning, eagle, laurel, temple and storm symbols | Large reference-matched Zeus on first panel; readable 7×6 field occupies the right; lightning and game objects can spill through the foreground |
| Plinko / Plinko game | `examples-games/plinko.jpeg` | C6 / AE / M6 | Mechanic; glossy colored balls, pegs, buckets, charged coins | Active tilted peg field can fill all three panels; trajectories and coins carry motion; no invented person or mascot |
| Chicken risk game | No exact local preview required | C2 / M / M2 step model, if using safe-step wagering | Character; expressive chicken, safe/risk tiles, supported reward tokens | Chicken on first panel; actual staged risk path may span the remaining panels or whole scene |

**Joker and Joker Jewels are separate families.** A request that names only a Joker resolves to the
3×3 row and `joker2.png`. A request that names Joker Jewels, Joker's Jewels, Jokers Jewels or
`joker-jewels` resolves to the `examples-games/joker-jewels/` folder and its 5×3 topology, and is
never satisfied by the plain Joker row or by the unspecified-slot 3×3 default.

**Joker Jewels file roles.** Use `jj_reference.jpeg` for the festive purple staging, bunting,
confetti and the mask-with-gems subject pairing; `jj_gameplay.jpeg` for the 5×3 board, the purple
reel strips and the symbol family (jester face, crown bonus, lute, juggling clubs, jester shoes,
red and cyan faceted gems, blue orb); and both character references for the lead's striped
costume, three-point belled cap, painted face and juggling gesture. Do not reproduce the
`Joker's Jewels` wordmark, the operator logo or branding, the reference UI chrome and copy, or the
reference paytable — those figures are another product's currency and payouts, not this game's M1
model.

## How close to the reference — match it

When a request maps to a reference, **recreate what the reference shows.** Not a reinterpretation,
not an homage, not "inspired by": put the generated game beside the reference and they should read
as the same game. Match all of it, as closely as the generator can get —

- the theme and setting;
- the character: costume colours and pattern, cap or headwear shape and bell count, face paint,
  build, pose and expression;
- the full cast of symbols, object for object, with their materials and colours;
- the palette, the light and the background treatment;
- the board topology and the frame around it;
- the composition — what sits where on the menu and on the game screen;
- the UI mood: button shapes, panel materials, reel-strip colour, frame ornament;
- the rhythm of a round: how the reveal paces and where the anticipation sits.

**Do not introduce variation for its own sake.** No "make it your own", no fresh take, no
re-theming, no substituted symbols, no palette shift, no inverted brightness. Wherever a choice is
open, take the one that looks more like the reference. A result that reads as a different game is
wrong, and it is regenerated toward the reference rather than away from it.

**Inspect and supply the reference.** View every mapped file at full size before writing the
concept and before generation. Record the exact costume pattern, cap, symbol list, reel colour,
frame ornament, background, linework, depth and light. Pass the relevant image files into a
reference-capable generator at high fidelity; use those observations in the prompt as specific
constraints. Text-only generation when image inputs are available causes identity drift.

### Production limits

1. **The title, wordmark, logo and operator branding.** Those are the trademarks of a published
   commercial product, and the generated game ships under its own name and its own logo.
   Everything the logo sits on top of is matched.
2. **Source image quality.** Direct reuse is appropriate only for a clean element or background
   that remains sharp at its actual displayed size. A flattened screenshot is usually unsuitable
   as a whole game background because it bakes in symbols, controls, title or payout text. Isolate
   suitable pixels with provenance, or generate a production-sized asset from the actual source
   image as a high-fidelity visual input. Do not substitute a merely similar character or symbol.
3. **The paytable numbers.** A release is blocked without a green `tools/simulate_math.py` run,
   and figures read off a screenshot cannot be verified. Build the model with the same *shape* —
   the same symbol ranks, the same kind of bonus, the same volatility feel — and let
   `game-mathematician` land it inside the category's RTP window.

Everything outside these limits is matched, not adapted.

For Book of Ra, Joker, Joker Jewels, and Zeus Game the character is the lead: rebuild that
character as the reference draws it. For Shining Crown and Plinko the absence of a main
character is itself part of the reference contract: do not add a host, mascot, hand, player
silhouette, deity or other living lead.

## Concept seeds

**Prism Drop:** Stake virtual chips, release a luminous ball into a cosmic peg field, and reveal
the bucket's configured multiplier. The core feeling is the last deflection before landing.
Match the Plinko preview's diagonal action, oversized glossy balls, luminous trails and saturated
separation. Build the visible board to look like the preview's, and take its bucket count,
probabilities and multipliers from the M6 config — those are the numbers, not the look. M6 RTP target: 95–97%, verified by simulation.

**Sun Archive:** A 5×3 Egyptian-adventure slot centered on a glowing book reveal and an explorer
who discovers the configured winning state. Borrow the preview's explorer-left/field-right staging,
sunset temple depth, turquoise-and-gold relic family, and dense archaeological foreground. Rebuild
the explorer and the symbol cast as the preview draws them, object for object. The visible 5×3
topology is intentional for this named family and must match the M1 config, runtime,
and store captures. M1 RTP target: 95–97%.

**Crown Cascade:** A classic 3×3 virtual-chip slot whose three crowned symbols illuminate a real
winning line. Match the crown preview's royal tactility, jewel silhouettes, dramatic lighting,
frame ornament and coin spill. The preview's single visible strip is not the new game's row
count: build 3 visible rows with model-supported payout coins. M1 RTP target:
95–97%; declare paylines, weights and payouts before generation.

**Joker's Dare:** A 3×3 slot with five configured paylines and a grinning theatrical trickster.
Bells, cherries and gems read at phone size; supported x5/x10 medallions can punctuate rewards.
Match `joker2.png`'s character-left/field-right composition, its Joker and its bold gesture; keep
the mischievous expression rather than drifting toward an elegant host. Derive every depicted
winning line from the actual resolver; five lines are a concept choice that must enter M1.

**Harlequin Revel:** A 5×3 jewel slot with fixed paylines paying left to right and a crown bonus
symbol that pays from any position. A striped-costume jester is the visual lead and appears in the
menu, the idle board and the win celebration. Match the references' carnival purple staging,
bunting and confetti, glossy faceted gem silhouettes, and the jester's striped costume, belled cap
and painted face as the character files draw them. The 5×3
topology is intentional for this named family and must match the M1 config, runtime and store
captures. A low fixed line count (the reference family uses five) is a deliberate classic-feel
choice below archetype B's usual 10–25; record the chosen count in the concept and the JSON config.
The reference establishes no weights, payouts or bonus rules. M1 RTP target: 95–97%, hit rate
20–35%.

**Thunder Reels:** A 7×6 Zeus scatter-pays slot built around a lightning reveal of a configured
winning cluster. Zeus is an in-game character and visual lead, with the preview's
eagle/bolt/laurel asset family.
Match the local preview's character-left/field-right energy, cloud-bright Olympus depth, electric
blue/gold separation, tumbling thematic objects, and Zeus himself. The preview's 7×6 topology is intentional for this named family and
must match the M1 config, runtime, and store captures; the reference does not establish symbol
weights, cluster thresholds, or payouts. Lightning effects never manufacture near misses or change
resolved results.

**Chicken Dare:** A virtual-stake safe-step game: choose to advance to another risk tier or take
the current virtual reward. It is C2/M2, not an endless runner. The chicken's comic defiance makes
it the visual lead. Configure the step probabilities and cash-out multipliers in the M2 model;
use x5/x10 tokens only when those exact steps are supported. House edge and maximum multiplier
are disclosed; target RTP is 96–99%.

Every seed's *look* comes from its preview and every seed's *numbers* come from its model — those
are the only two sources. Finish the normal concept around them: complete loop, production plan,
mobile/expanded layout, asset manifest, meta systems, required screens, responsible-play copy and
a verifiable JSON model. The preview alone never proves playable UI, balance, or a completed
game.
