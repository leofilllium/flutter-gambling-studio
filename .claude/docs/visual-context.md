# Visual context — concepts, assets, and store art

Use this contract when proposing a game, generating its assets, or composing its storefront.
The user's brief and an existing game's actual mechanics and Design DNA are authoritative.
For matching new-game requests, inspect the relevant previews in `examples-games/` by default
and read `.claude/docs/game-concept-examples.md`. They are visual references, not runtime assets
or complete game specifications. A missing reference does not block an unrelated concept.

`/autocreate` requests named **Book of Ra**, **Joker**, **Joker Jewels**, **Shining Crown**,
**Zeus Game**, or **Plinko** must use the exact local reference mapping in
`game-concept-examples.md`, on the `--from-concept` path as well; do not replace it with a generic
category reference. Book of Ra, Joker, Joker Jewels, and Zeus are character-led: keep the
archetype, role and world, and redraw the person as an original design — close adaptation, not a
copy and not a departure. The full rule is the closeness contract in `game-concept-examples.md`,
and it governs the whole concept, not only the art. Shining Crown and Plinko are
object/mechanic-led and must not gain an invented main character or mascot.
**Joker** and **Joker Jewels** are two different entries: Joker Jewels resolves to every file in
the `examples-games/joker-jewels/` folder and to a 5×3 board, never to the plain Joker row's 3×3.

## Decide the visual lead before generating

Record `lead_kind: character | object | mechanic`, the lead's identity and runtime role,
reference paths, traits borrowed, original adaptations, board topology, and supported multiplier
markers in `design/gdd/game-concept.md`. Carry those decisions into `design/art-direction.md`,
the asset manifest, generation prompts, and `STORE_BRIEF.md`.

Once the assets exist, record the lead's own file as `Lead asset: <path>` in the concept (or the
art direction) — the runtime menu gate reads it. The lead is the main menu's centrepiece, not
just the storefront's: see `quality-bar.md` §1 and V19 in `.claude/skills/emulator-test/SKILL.md`.

| Lead | When it fits | Default storefront direction |
|---|---|---|
| Character | Zeus, Joker, chicken, another actual character or animal mascot | Recognizable large character on the first panel; action may occupy any remaining space or span panels |
| Object | Crown, multiplier coin, capsule, treasure, machine is the visual star | Let that asset and the real mechanic drive the composition; when the game has no living character, slides 1–2 show angled authentic gameplay and introduce no person or mascot |
| Mechanic | Plinko drop, reels, wheel, cash-out trajectory is the attraction | Lead with active play; a board or trajectory may extend through all panels |

A chicken is a character even though it is not a person. A crown or coin is an object even if
someone calls it the game's “hero.” Do not invent a mascot just to fill a template. Conversely,
do include a requested character in the concept, asset plan, and relevant in-game states rather
than inventing it only for the store. Existing games retain their established lead.

## Reference-led original assets

Preserve relevant visual qualities from the chosen examples: bold silhouettes, glossy modeled
volume, tactile materials, saturated color separation, confident expressions and decisive action.
Create a coherent new asset family from the game's concept; do not crop example pixels into
runtime sprites or import example logos. The subject family is required, not optional:
bells/cherries/gems for a Joker slot, crowns and jewel coins for a royal slot, balls/pegs/buckets
for Plinko. The reference's world, cast of objects and palette family carry over; the drawing of
each object is new. Do not randomize away the user's requested game family — see the closeness
contract in `game-concept-examples.md`.

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
not 4×4. A named preview-mapped family overrides that default with its own mapped topology:
Joker 3×3, Joker Jewels and Book of Ra 5×3, Zeus Game 7×6. Save the topology
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

For an object/mechanic-led game with no living character in its concept and shipped inventory,
the first two carousel slides are gameplay-led. Show the authentic board or mechanic at a readable
three-quarter/3D angle in each crop, or use one continuous angled gameplay surface with meaningful
play visible in both. Do not invent a human, hand, animal, mascot or player silhouette, and do not
use a decorative object-only first slide. Preserve the real topology, symbols and resolving state.
Character-led games keep their existing character-first defaults.

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
clear action, and a broad smooth subordinate far plane. Casino-grade energy comes from composition
and materials; it does not prescribe a universal gold/neon palette, high-key exposure, or an
aggressive saturation target. Keep the Design DNA's value structure, use a restrained theme-led
colour grade by default, and reserve brightness lifts, bloom, glare, and intense saturation for an
explicit concept or user direction. Never tint runtime art.

The feature graphic needs its own horizontal render and the same context decision. A left-heavy
3/5–2/5 arrangement is an option, not a universal rule. Object-led and mechanic-led banners may
use the full width. No reserved device-shaped zone; the clean source must look finished alone.
The shipped feature graphic is that scene plus one framed phone on the right holding a real
capture, and it carries no text: no title, tagline, logo, wordmark or copy on the left or
anywhere else, and no blank space kept for them.
Real gameplay showcase frames remain actual captures. Store work preserves menu/gameplay/splash
background assets and wiring; redesigning them requires an explicit user request.


## Image reference transport preflight

Check the active image transport's reference limit before submitting a large asset set.
A built-in transport observed in September 2026 accepted at most five paths even though its
visible schema showed only an array. Treat that as observed transport behavior, not a permanent
limit for every provider. A request rejected during argument validation is not a generated
source or a spent quality correction; record the rejection separately.

When the inventory exceeds the supported limit, preserve complete reference coverage through
staged integration or a labeled lossless contact sheet made from the original files. Inspect
every original at full size and game size and retain its alpha audit and source-to-sheet
mapping. Keep important identity references as separate inputs where possible; label runtime
frames as topology/state evidence and previews as composition references. Do not omit secondary
symbols to fit the limit, mistake a contact sheet for finished art, or claim packed references
guarantee faithful output. Compare every resulting identity and the full field with the original
sources after generation; all existing visual, math, seam and runtime gates still apply.

## Deterministic runtime-background guards

Before and after store branding, compare the same complete background/splash file inventory,
SHA-256 hashes and code/config selecting references. Sort file paths before hashing. Search
tools may return identical matches in a different filesystem traversal order: normalize away
line numbers where the guard already calls for that, then sort the full reference records
before comparing them. Keep paths and complete matched content; sorting must never discard
a removed/added reference or suppress a changed selector. Preserve raw inventories as evidence.
If an exact comparison fails but sorted records and asset hashes match, report unchanged
background wiring with an ordering-only diagnostic. Never recolor or replace a runtime
background to resolve an inventory-order difference.
