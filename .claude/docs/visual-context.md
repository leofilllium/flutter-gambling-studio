# Visual context — concepts, assets, and store art

Use this contract when proposing a game, generating its assets, or composing its storefront.
The user's brief and an existing game's actual mechanics and Design DNA are authoritative.
For matching new-game requests, inspect the relevant previews in `examples-games/` by default
and read `.claude/docs/game-concept-examples.md`. They are visual references, not runtime assets
or complete game specifications. A missing reference does not block an unrelated concept.

## Decide the visual lead before generating

Record `lead_kind: character | object | mechanic`, the lead's identity and runtime role,
reference paths, traits borrowed, original adaptations, board topology, and supported multiplier
markers in `design/gdd/game-concept.md`. Carry those decisions into `design/art-direction.md`,
the asset manifest, generation prompts, and `STORE_BRIEF.md`.

| Lead | When it fits | Default storefront direction |
|---|---|---|
| Character | Zeus, Joker, chicken, another actual character or animal mascot | Recognizable large character on the first panel; action may occupy any remaining space or span panels |
| Object | Crown, multiplier coin, capsule, treasure, machine is the visual star | Let that asset and the real mechanic drive the composition; no person, bust slot, or character-only opening panel |
| Mechanic | Plinko drop, reels, wheel, cash-out trajectory is the attraction | Lead with active play; a board or trajectory may extend through all panels |

A chicken is a character even though it is not a person. A crown or coin is an object even if
someone calls it the game's “hero.” Do not invent a mascot just to fill a template. Conversely,
do include a requested character in the concept, asset plan, and relevant in-game states rather
than inventing it only for the store. Existing games retain their established lead.

## Reference-led original assets

Preserve relevant visual qualities from the chosen examples: bold silhouettes, glossy modeled
volume, tactile materials, saturated color separation, confident expressions and decisive action.
Create a coherent new asset family from the game's concept; do not crop example pixels into
runtime sprites or import example logos. Similar subject families are welcome when the request
calls for them: bells/cherries/gems for a Joker slot, crowns and jewel coins for a royal slot,
balls/pegs/buckets for Plinko. Do not randomize away the user's requested game family.

All art uses polished cartoon 2.5D casual-game illustration with a consistent top-left key,
rounded/exaggerated forms, smooth gradients, glossy highlights, and restrained star glints.
Build the actual runtime set first; store generation then uses those shipped assets as identity
references. A marketing reference cannot override the real game's colors, symbols, or topology.

### Joker expression

The default Joker is a mischievous, slightly vicious trickster: sharp confident grin, angled
eyebrows, lively eyes, pointed jester cap with bells, bold contrasting costume, and a theatrical
gesture. Favor impish swagger over a polite elegant courtier. Keep it playful and readable;
avoid horror, gore, creepy realistic skin, monstrous teeth, or frightening expressions.
Rich fabrics and gold trim can support the character without making elegance its personality.

### Slot topology

An unspecified “slot game” request defaults to a classic **3 reels × 3 visible rows (3×3)**,
not 4×4. Save the topology
in the concept and the M1 JSON config; implementation, board assets, runtime screenshots, and
marketing must agree. A requested 5×3 video slot, cluster slot, or an existing different grid
keeps its documented dimensions. Do not change a shipped game to satisfy a marketing default.

### Multiplier coins

Prefer prominent `x5` and `x10` coins/badges in runtime rewards and storefront object spills
when the theme and actual mechanics support those values. Coin material and edging follow the
game: royal jewel medallion, playful jester chip, charged Plinko token, and so on.
At new-concept design time, prefer real x5/x10 reward tiers when they suit the mechanic and have
the game-mathematician verify the resulting model before generating their assets. This is a
concept choice, not permission for store generation to alter an existing game's payouts.
Record each marker's exact config/paytable source and meaning in the manifest. A total payout,
per-line multiplier, bonus modifier, and ten-pull count are different meanings; do not substitute
one for another or imply a guaranteed reward. If x5/x10 do not exist, use a supported value or
unlettered objects. Never change balance just to justify a promotional coin.

These short, verified game-object inscriptions are exceptions to the no-baked-copy rule.
Keep ordinary UI and marketing text in code/compositor typography. Check exact lettering at
runtime size; generate/edit the inscription or render it from the same config value on an
unlettered source, without recoloring a symbol to invent a new payout identity.

## Flexible store composition

Plan every panel as a readable crop of one continuous scene. Choose positions and spans from
the mechanic, aspect ratio, and visual lead. Examples include character-left/gameplay-right-two,
full-width active Plinko, object-led reels across all three, or a contained field on any panel.
The middle panel has no privileged role. Multiple play fields are allowed when they depict
real, coherent states and each remains readable; one continuous field is often stronger.

For character-led concepts, default to a large first-panel character. Use a waist-up crop for
humanoids; use a readable species-appropriate crop for animal mascots. Protect the whole head,
hair/headwear and attached silhouette from the first seam, with at least 2% top headroom;
left and lower edge crops are allowed. Object/mechanic leads have prominence and readability
checks, not anatomy or first-panel silhouette requirements.

Boards may cross any seams. Put cuts through noncritical housing, gaps, or background; keep
faces, decisive symbols, multiplier inscriptions, bucket outcomes, and critical interaction
clear of the actual gaps. Review both the assembled panorama and the gapped carousel. If a
critical region cannot survive a proposed span, move/scale the composition or change the cuts.

When checking background detail, exclude measured foreground subjects and gameplay fields;
the upper half of a picture is not necessarily its background. The compositor accepts separate
gameplay bounds in addition to lead/hero and critical-region bounds. Preserve measurable real
background and the palette, light and foreground-object checks; do not mask busy scenery away.

Use a varied foreground spill of real game objects across the lower edge and selected flying
objects at different depths. Preserve sharp primary forms, source colors, contact shadows,
clear action, and a broad smooth luminous far plane. Casino-grade energy comes from composition
and materials; it does not prescribe a universal gold/neon palette. Maintain the store art's
saturation floor (0.68, target 0.78–0.88) and controlled glare without tinting runtime art.

The feature graphic needs its own horizontal render and the same context decision. A left-heavy
3/5–2/5 arrangement is an option, not a universal rule. Object-led and mechanic-led banners may
use the full width. No reserved device-shaped zone; the clean source must look finished alone.
Real gameplay showcase frames remain actual captures. Store work preserves menu/gameplay/splash
background assets and wiring; redesigning them requires an explicit user request.
