---
name: store-screenshots
description: "Build a casino-grade App Store and Google Play storefront kit for a gambling game: a text-free concept panorama, dense enough to stand beside a real listing, sliced into panels that reassemble into that exact picture — nothing discarded between them, no panel ending mid-object, the cuts placed on the quietest columns the picture has, real gameplay screenshots in device frames with compliant English marketing typography, a feature graphic, an applied launcher icon, and an in-game emblem. Panel 1 is composed *for* the protagonist: the art draws it an ornamental berth, the figure fills about three quarters of the panel's height with the ornament crowning the headroom above it, and the scene's own foreground closes back over its feet. The middle panel is a generated 3D gameplay scene, not a pasted screenshot: an actual resolving gameplay frame is supplied as authoritative visual context, then the field is created together with the scene so its real mechanic, grid, symbols and state remain recognizable while perspective, material, lighting, shadow, ornament and foreground interaction make it belong to the same world. Every shipped sprite asset is inventoried, assigned across the split slides, supplied as visual context, and visibly recreated inside a natural physical role — held, mounted, emerging, nested, embedded in machinery or architecture, or partly occluded — as part of the same rendered scene. No sprite is omitted, pasted as an icon, arranged as a contact sheet, or repeated merely to fill space. The key art and the app share one world in both directions — the panorama carries the game's real objects and the game wears the panorama as its background. Every set uses high-stakes casino storefront composition while its palette, materials, characters, and typography follow the game's C1-C6 category, archetype, and Design DNA. Output is a downloadable ZIP under project_zip/."
argument-hint: "[--count 8] [--panels 3] [--size 1320x2868|1290x2796|play] [--no-play-set] [--gutter 0|100] [--seam-snap auto|off] [--pop vivid|soft|max|off] [--hero hero.png] [--hero-height 0.72] [--sprite-dir assets/images/sprites] [--props a.png,b.png] [--board auto|rest|off] [--sprite-light 0.35] [--occlude 0.14] [--no-backdrop] [--lang en] [--frame ios|android|none] [--type-mood bold|epic|tech|playful|elegant|retro|clean] [--no-captions] [--no-apply] [--no-wire-logo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Store Screenshots — Complete Storefront Kit

Create everything needed to present the game in App Store Connect and Google Play:

| Deliverable | Source |
|---|---|
| Panels 1…P: one wide, text-free concept illustration composed around the hero on panel 1 and visibly integrating every shipped sprite asset across the split panels, sliced into adjacent panels that lay back down into the whole picture | GPT Images 2.0 → `store_compose.py triptych --sprite-dir … --seam-snap` |
| The layout draft the finished picture is rendered from — real hero at full panel height under the berth's ornament, the real field caught mid-payout, and a real reward/prop in a decorated physical home on the final panel | actual gameplay win frame → `store_compose.py boardplate --from-shot` + `triptych --pano-only` |
| One integrated illustration: the draft, actual gameplay frame, and exhaustive sprite manifest used as references to generate a single three-dimensional scene | `gpt_image.py edit --image draft --image gameplay --image <every sprite> --fidelity high` |
| The same key art wired into the app as its own background | `store_compose.py backdrop` → `assets/images/backgrounds/` |
| Panels P+1…N: real gameplay frames in a device mockup with marketing captions | `web_verify.mjs` → `store_compose.py showcase` |
| Google Play feature graphic, 1024×500 | `store_compose.py banner` |
| Launcher icon for all Android/iOS/web densities | image generation → `store_compose.py icon` → `flutter_launcher_icons` |
| In-game emblem/logo with transparent background | image generation → `tools/cutout.py` |

Build two screenshot sets from the same art and gameplay frames:

- App Store: iPhone 6.9-inch format, 1320×2868 by default, under `store/`.
- Google Play: 1080×1920 (9:16), under `store-play/`.

Do not downscale one set into the other. Recompose typography and device framing for each aspect ratio. Google Play rejects images whose long side is more than twice the short side, so the 2.17:1 App Store files cannot serve as the Play set.

All generated copy is English unless the user explicitly requests another player-facing language. The concept panels contain no letters at all; captions and titles are rendered by the compositor, never by the image model.

This skill creates local artifacts only. It does not publish, commit, change game balance, or build release binaries. It does apply branding — icon, emblem, and the key-art backdrop — to the project.

## Storefront ↔ game continuity — the blocking contract

The most expensive rejection a generated storefront collects is not a compliance word or a wrong
pixel size. It is this: the first panels advertise a world — a god, a machine, a vault — and then
screenshot 4 opens the app and none of it is there. Reviewers read that as artwork bought for a
different product, and it has cost real submissions.

Continuity runs in **both** directions, and both are mandatory:

| Direction | Requirement | How it is enforced |
|---|---|---|
| Key art → app | The concept panels' world, hero, palette, materials, and light must be visible on the game's own screens | `store_compose.py backdrop` exports the panorama as the game's menu and gameplay background, and Phase 3 wires it in **before** the final storefront frames are captured |
| App → key art (objects) | **Every shipped sprite asset** must appear visibly somewhere across the concept panels, with every panel carrying part of the set | `--sprite-dir` inventories and distributes all raster sprites in the draft; the exhaustive manifest is passed to the integration render at high fidelity and audited one row per file |
| App → key art (the field) | Where the art shows the game being *played* — a grid, reels, a board, a track, a peg field — it must clearly derive from the actual game while being created as part of the same 3D scene | a real resolving gameplay frame is the authoritative context image; `boardplate --from-shot` supplies layout/perspective guidance, and both go into the integration render as references rather than being pasted into the final art |

Describing a symbol to an image model produces something *similar*. **Handing it the file** produces
the same object — that is what the reference-image render in Phase 2b is for, and why it always runs
at `--fidelity high`. Compositing the sprite also produces the same object, but flat; it is the
draft and the fallback, not the deliverable.

**This applies hardest to the play field, and it is the newest returned listing.** A concept panel
arrived showing a full-bleed 3×3 grid: neon-framed cells, a crown, a helmet, a lyre — all of it
invented by the image model. The app's actual board was a gold-edged panel of round medallions on
flat tiles. Two different games in one listing. The note back was exactly that: *the gameplay
example in the slider and the real gameplay have to be the same*.

So the image model does not **invent** the field from a written description. The first panorama
generation draws the world and an empty stage. The integration generation then receives the real
gameplay frame, the board plate and the real object files as visual context and creates the field
**with** that world: one perspective, one material space, one lighting rig, real contact and real
depth. The final field is generated scene art, not a screenshot layer, but it must remain
unmistakably the same game — same mechanic, grid, symbol identities, ordering and resolving state.
If it becomes a decorative fantasy board or a flat rectangular screen, regenerate it.

**Phase order is part of the contract.** A reference-only gameplay frame is read or captured first
so the integration model knows what the game truly looks like; it is an input, never an upload.
Then art → apply to the game → capture the final storefront frames. Reusing the pre-branding
reference as a showcase screenshot is exactly the bug that ships a listing whose two halves show
different products.

**The exhaustive sprite manifest.** In Phase 0, inventory every shipped sprite below the game's
sprite directories. None are optional merely because they are secondary symbols, collectibles,
tokens, modifiers, effects or alternate states. Record every file in `STORE_BRIEF.md`, with the
hero marked first and primary anchors reserved for panel 1 (hero), panel 2 (field/mechanic) and the
final panel (reward/progression object). Distribute the remaining sprites across the panels with a
specific physical role for each. Phase 9 verifies every manifest row in the generated concept art
and separately verifies that every panel carries part of the complete set. One missing sprite or
one panel with no assigned sprites is a blocker.

## Compose the slide around the hero, build the objects in — the composition contract

Continuity gets the right objects into the picture. This gets them in at the right size and in the
right place, which is what the publisher's designer sends listings back for: *put the protagonist
on the first screen, always, so it hits the eye immediately — and the game's objects are not worked
into the design at all and are far too small; build them into the artwork itself.* Seven rules, all
defaults rather than options:

**0. The result is one picture, not an assembly.** This is the note that outranks the rest: *don't
just insert them into the slide — use them as strong context and make one complete image, so it
looks natural and three-dimensional, not inserted.* A composite can only ever put the right objects
in the right places; it cannot give them volume, a shared perspective, shadows falling across each
other, or air between the near and the far. So the composite is a **draft**, and the deliverable is
rendered from it with the real asset files and actual gameplay frame as reference images (Phase 2).
The gameplay reference has no special permission to remain as pixels: it informs the generated
field, then disappears into the same 3D render as everything else. Every rule below describes what
that draft has to establish and what the render has to preserve.

**1. The protagonist owns panel 1, at the panel's own scale.** Screenshot 1 is the only one the
store shows at full size; everything after it is a thumbnail in a strip. Whatever stops the scroll
has to be there and has to be big, and it is the hero — not a logo, not an establishing shot, not
whichever slice of the panorama happens to be prettiest. The latest note is about how big:
*the player on the first slide should be bigger — full height, but not too much.* Sizing a figure
by the panel's **width** is what made it small: 0.58× the width of a 1320×2868 panel is a hero
barely 40% of the panel's height, standing in a landscape. So the hero is sized by **height**:
`triptych` treats the first `--sprite` as the hero, fills ≈0.72 of the panel's height with it
(width capped at 0.86× the panel), and stands it with its feet past the bottom edge. The
compositor prints both numbers — `hero.png → panel 1 … (1135px, 86% of the panel, 68% of its
height)` — and warns when a squat cutout hits the width cap before it reaches full height. The fix
for that is a taller export or a tighter crop of the sprite's empty margins, never a shrug.

**2. Panel 1 is drawn *for* the character, and the picture is decorated *around* it.** The
follow-up note was precise: *don't merely insert a player — make it fit the slide; the slide itself
has to contain the player, as its context.* A correctly sized, correctly lit cutout still fails
that test if the picture behind it would be complete without it. So the slice that becomes panel 1
is composed as a **hero berth**: a stage, ledge, throne, doorway or pool of light with the
perspective converging on it, the brightest key light falling there, and foreground furniture — a
rail, rocks, chips, foliage — drawn along its bottom edge for the character to stand behind.
Phase 1 draws that berth **empty**; Phase 2 seats the real hero in it and the compositor closes the
scene's own foreground back over its feet (`occlude`, default 0.14 of the hero's height). Light
says *lit by the picture*; occlusion says *inside the picture*, and it is the cue a designer reads
first.

The same note asked for one thing more: *more decorative*. A berth is a place to stand; what makes
the slide read as a poster instead of a photograph of a character is the **ornament around and
above** the figure. The hero now fills three quarters of the panel's height, which leaves one band
— roughly the top quarter to third — directly above its head, and that band is the decoration
budget: an arch, portal, crest, canopy, banner or drapery closing over the head, columns or
lanterns flanking the shoulders, a light burst or halo behind where the head will be, embers,
petals or coins drifting through it. `triptych` measures that band and calls it out — `panel 1
crown: detail 1.0, 100% … above the hero's head is empty` — because empty sky there is the single
easiest way to spend the extra height on nothing. The answer to a flat crown is regenerating the
berth with the ornament in it, never scaling the hero up until its head fills the gap: a figure
cropped at the crown is not decoration.

**3. Objects are built into the design, not laid on top of it.** A game symbol shrunk to a fifth of
a panel and dropped onto the background reads as a sticker — which is worse than no inlay at all,
because it also makes the whole picture look assembled. Real objects belong in the foreground at a
third of a panel or more, standing on the scene's ground plane, casting a contact shadow, tinted by
the light they are standing in, with the nearest ones cropped by the frame edge. The compositor does
the seating — foot anchoring, contact shadow, edge light-wrap and colour cast (`--sprite-light`) —
but it can only seat an object into a scene that has somewhere to stand, so Phase 1 has to draw one.

**4. The middle panel is gameplay created with the scene, not a screenshot mounted in it.** Panel
1 sells the world; the middle panel answers *what do I actually do*. Use an actual resolving/win
frame as authoritative visual context, then ask the integration model to rebuild that play field
as a physical part of the same illustration. It gains the scene's perspective, thickness,
material, highlights, cast/reflected light, contact shadows, atmosphere and selective foreground
overlap. The stage, trim and payout decoration grow from its construction instead of forming a
picture frame around a flat rectangle.

The freedom is three-dimensional, not mechanical. Keep the real field readable and recognizable:
same topology, symbol identities, meaningful ordering, active cells, outcome and essential state.
Do not stretch it beyond recognition, replace symbols, turn the grid into ornamental texture, or
cover the decisive interaction. The result should look like the game's board exists physically in
the key-art world — not like a phone screenshot was pasted into a decorative bezel, and not like
unrelated concept art merely inspired by the game.

**5. Every shipped sprite carries the game, not only a selected few.** One real hero on panel 1
and one real board on panel 2 do not excuse the rest of the sprite library disappearing. Inventory
every file in the game's sprite roots and assign each one to exactly one primary appearance across
the panels. The hero leads the first panel, the real field/mechanic leads the middle, and a reward
or progression object leads the last; all remaining symbols, tokens, collectibles, modifiers,
effects, alternate states and props are distributed around those focal beats. `triptych
--sprite-dir` recursively builds that layout/reference manifest, reserves hero and board roles,
fills uncovered panels first, then balances the remaining files. It prints `panel N game anchors:`
and warns on `NONE`.

Coverage alone is not the finish. Give every anchor a **physical job in that panel's scene**. It is
held or worn by the hero, rising out of the paying field, mounted into a machine, nested in a
carved shrine, resting in a fitted pedestal, crossing in front of architecture, or partly hidden
behind foreground furniture. Build decoration *around its function* — trim following its
silhouette, a socket made for its base, particles emitted by it, reflected light on nearby material,
supporting ribbons/foliage/mechanism — without redesigning the asset itself. A repeated icon
floating over three backgrounds technically covers three panels and still fails. A row of icons,
contact sheet, trophy shelf, tiled pattern, or cloud of badges also fails: those are arrangements
of assets, not a scene built from them.

**6. Include all assets without flattening the hierarchy.** Exhaustive coverage removes the object
count cap; it does not remove art direction. Keep the hero, gameplay field and final reward as the
three primary beats. Turn supporting sprites into purposeful secondary constructions at several
depths: carvings in the architecture, working parts of machinery, objects carried by a trail,
rewards emerging from a mechanism, fitted ornaments, physical hazards, or scene-scale effects.
Each remains individually recognizable at final panel size, but not every asset competes at hero
scale. When the reference-image limit cannot carry the full manifest in one render, use the staged
high-fidelity integration process in Phase 2b and prove that earlier assets survived every pass.

The target is one finished picture — the hero standing at full height in a place the art built and
decorated for it at one end, gameplay recreated from the real win frame as a readable physical
mechanism across the middle, and the final panel built around a real reward/prop as its own scene
beat, with the complete sprite manifest carried through the three environments with weight,
purpose, contact and shadow. Ask the model for the world that way in Phase 1, place every reference
into the draft, then render the whole picture — including the gameplay field — together in Phase 2.
Nothing is pasted back afterward.

## Category-specific art direction

The storefront must sell the round mechanic, not generic casino atmosphere. Read `design/gdd/game-concept.md`, `design/art-direction.md`, and `design/structure.md`.

| Category | Required visual story |
|---|---|
| C1 Social Casino | Reels, cards, or wheel at the decisive stop/reveal moment |
| C2 Casino Originals | The risk decision: rising multiplier, mine field, tower, or cash-out tension without money claims |
| C3 Spin-to-Progress | The spin/die/wheel and the progression world together |
| C4 Gacha | Capsule/pack/case opening, rarity reveal, and collection context |
| C5 Casino Roguelike | The assembled strategic engine: cards, modifiers, synergies, and score |
| C6 Coin Pusher/Plinko | Physical trajectory, field depth, targets, and accumulated potential |

Never apply the same neon-purple-and-gold casino look to every game. Theme, palette, materials, lighting, typography, and mood come from the current game's Design DNA. If the panorama could be moved to another studio game unchanged, it fails.

### Casino-style storefront grammar — mandatory

Every set must read immediately as a premium gambling-game storefront, even when the Design DNA
is cozy, playful, retro, papery, or minimal. “Casino-style” describes the marketing composition,
not a mandatory black/neon/gold skin:

- Lead with the decisive wager/reveal/drop/collect moment and make the real mechanic unmistakable —
  unmistakable because the game's own field and symbols are in the picture, not because a model
  drew something that looks like a casino.
- Use one dominant outcome object or mechanic, strong foreground/midground/background depth,
  directional light, controlled particles, motion/anticipation, and a clear reward focal point.
- Make virtual chips, multipliers, cards, reels, capsules, balls, modifiers, or collection rewards
  feel tactile and premium in the current Design DNA. Never imply real-money value.
- Use short, bold, mechanic-specific captions on gameplay showcase frames. The text-free panorama
  remains cinematic and contains no generated lettering.
- Prefer exciting active, tension, reveal, and celebration states over flat menu documentation.
  At least half of the real-gameplay frames must show the core round in motion or resolving.
- Keep the device frame secondary to the gameplay. The real screen inside it must remain large and
  readable; decorative background may support it but cannot overpower it.

A generic casino lobby, random luxury props, or a neon-and-gold reskin without the game's mechanic
fails just as surely as a flat utility-app screenshot.

### Saturation and light are a requirement, not a taste

A listing is reviewed as a strip of thumbnails standing beside nine competitors, and raw
image-model output lands flat and desaturated in that context — the note that comes back is always
the same: *make it richer and brighter*. So:

- Ask the image model for the vivid end of the game's own palette: saturated colour, luminous rim
  and key light, glowing highlights, deep contrast, rich material response. Not a pastel and not a
  haze; never a grey, washed midtone field.
- Every compositor art path then applies a colour grade on top (`--pop`, default `vivid`: vibrance
  + midtone lift + contrast + highlight bloom, none of which can clip). Raise it to `--pop max`
  when the art is still soft; drop to `soft` only when the art already screams.
- **Do not grade the real gameplay frames.** Both stores require a screenshot to represent what the
  app renders. If the captured frames look dull, the *game* is dull — fix it with the key-art
  backdrop, in-game lighting, and juice, then re-capture. Never brighten a frame in post.

### Density is the other half of the brief

The complaint that arrives beside "make it brighter" is "it is too simple, too boring". Raw
image-model output tends to a poster: one object, one glow, a gradient, and acres of nothing.
Standing in a strip beside nine finished listings, that reads as a placeholder — and no colour
grade rescues an empty picture. A storefront panorama is a **finished illustration**, so ask for
one and check that one came back:

- **Three planes, all of them occupied.** A foreground that crops on the frame edge (rail, rocks,
  spilled chips, foliage, a shoulder), a midground carrying the hero berth and the field stage, and
  a background that is a *place* — architecture, landscape, crowd, machinery, weather — not a
  gradient behind the subject.
- **Ornament at three scales.** The silhouette that survives a thumbnail; the mid detail that
  appears when the reviewer taps to full size — panelling, trim, plating, embroidery, carved edges;
  and micro texture — grain, wear, scratches, engraving, condensation. A shape with one flat fill
  and a bevel is the look being complained about.
- **More than one light.** The scene's key from the top left, plus practical lights that belong to
  the world (lanterns, signage, screens, embers, the glow off the reward itself) and a rim or
  bounce separating the subject from the background. One flat key light is what makes a render look
  like clip art.
- **Three distinguishable materials**, each responding differently: metal with a tight specular,
  cloth or paper with none, stone or wood with grain, glass or liquid with transmission.
- **Atmosphere that carries the empty areas.** Volumetric shafts, haze with depth, drifting
  particulate — dust, sparks, spray, petals, coins in flight. Empty sky or a plain wall is where
  a panel dies.
- **Something is happening.** A moment mid-event: a reaction, a spill, a trail, a crowd turning to
  look. A static product arrangement of correct objects is still boring.
- **Every panel is its own slide.** Each of the P panels must have a subject and an event of its
  own. One good panel plus two panels of background is a three-screenshot listing with one
  screenshot in it.

The opposite failure is real too, so hold the hierarchy while adding the density: depth of field,
value grouping and a calmer halo around the hero and the play field keep them the first things the
eye lands on. Detail everywhere with no focal point is noise, which reads as cheap for a different
reason.

`triptych` measures this and prints it per panel — `panel 2: detail 6.4, 31% of it empty ground`.
Above 55% empty, or a detail figure under 4, it says so: that panel is a backdrop, and the fix is
to regenerate the art from a fuller brief, never to grade or crop it.

## Arguments and defaults

| Argument | Default | Meaning |
|---|---|---|
| `--count N` | `8` | Total screenshots |
| `--panels P` | `3` | Number of adjacent concept panels; `0` disables them |
| `--size` | `1320x2868` | Main set; also supports `iphone-6.9`, `iphone-6.9-alt`, `iphone-6.5`, and `play` |
| `--gutter` | `0` | Nothing is discarded between panels: they reassemble into the picture. An explicit width (`100`, `auto`) throws that strip away instead, for a publisher who asks the panels to line up across the store's carousel gap — it costs the picture |
| `--seam-snap` | `auto` (12% of a panel) | How far the tiling may slide so the cuts land on the picture's quietest columns. With a lossless cut this is the only lever there is. `off` restores the content-blind even split |
| `--pop` | `vivid` | Colour grade applied to generated art (`off`, `soft`, `vivid`, `max`) |
| `--hero` | first manifest entry marked hero | The protagonist PNG that leads panel 1; pass it explicitly before `--sprite-dir` so its role overrides directory discovery |
| `--hero-height` | `0.72` | The hero's share of panel 1's **height** — the panel is sized by it, the width is only a cap. Below ≈0.6 the figure is scenery again; above ≈0.8 there is no crown left for the berth's ornament. Passed through as `h=` on the hero sprite |
| `--props` | auto | Legacy explicit comma-separated sprite list; use only for precise assignments that are then completed by `--sprite-dir`, never to select a subset of shipped sprites |
| `--sprite-dir` | required sprite roots | Repeatable directory whose PNG, WebP and JPEG files are recursively added to the exhaustive draft manifest; explicit `--sprite` entries win duplicate roles/placement |
| `--board` | `auto` | Prefer a real resolving gameplay crop (`boardplate --from-shot`) as the field reference, stand the draft plate in the scene's perspective, and place it in the middle. A symbol-built plate is provisional context only until a frame exists. `rest` is only for a mechanic with no resolving state; `off` for a game with no readable field |
| `--integrate` | `on` | Generate the finished panorama from the draft, actual gameplay frame and real assets as reference images (`gpt_image.py edit`). The field is recreated with the 3D scene, never pasted afterward. `off` may retain a layout draft for debugging but cannot produce a shippable concept panorama |
| `--sprite-light` | `0.35` | How hard inlaid objects are pulled into the scene's light (colour cast + edge light-wrap). `0` pastes them flat |
| `--occlude` | hero `0.14`, props `0.08`, board `0` | How much of an object's height the scene's foreground closes back over, so heroes and supporting props sit *in* the picture. The board stays unobscured for legibility; `0` leaves an object in front of everything |
| `--no-backdrop` | off | Do not wire the key art into the game as its background |
| `--no-play-set` | off | Skip the separate 9:16 Play set |
| `--lang` | `en` | Caption/title language; change only on explicit request |
| `--frame` | `ios` | `ios`, `android`, or `none` |
| `--type-mood` | from DNA | `bold`, `epic`, `tech`, `playful`, `elegant`, `retro`, or `clean` |
| `--font-dir` | `assets/fonts` if present | Prefer bundled game fonts |
| `--no-captions` | off | Produce clean gameplay frames |
| `--no-apply` | off | Generate kit files without modifying project branding |
| `--no-wire-logo` | off | Do not add the emblem to the main menu |
| `--name` | pubspec name | Archive base name |

This storefront kit remains portrait-phone-first, so keep its App Store and Google Play outputs
in the documented portrait sizes. That marketing format does not constrain the runtime app:
tablet, landscape, desktop, and Web must still use their full viewport responsively.

## Phase 0 — preflight, store brief, and the exhaustive sprite manifest

Verify the project and tools:

```bash
[[ -f pubspec.yaml ]] || { echo "A Flutter project with pubspec.yaml is required."; exit 1; }
python3 -c "import PIL, numpy" || { echo "Pillow and numpy are required."; exit 1; }
[[ -f tools/store_compose.py ]] || { echo "tools/store_compose.py is missing."; exit 1; }

PROJECT_NAME=$(grep -m1 -E '^name:' pubspec.yaml | awk '{print $2}')
[[ -z "$PROJECT_NAME" ]] && PROJECT_NAME="game"
TS=$(date +%Y%m%d-%H%M%S)
STORE_ROOT="project_zip"
STORE_DIR="$STORE_ROOT/$PROJECT_NAME-store-$TS"
RAW_DIR="$STORE_DIR/raw"
ART_DIR="$STORE_DIR/art"
OUT_DIR="$STORE_DIR/store"
PLAY_DIR="$STORE_DIR/store-play"
mkdir -p "$RAW_DIR" "$ART_DIR" "$OUT_DIR" "$PLAY_DIR" assets/branding
```

Write `$STORE_DIR/STORE_BRIEF.md` with the English title, compliant tagline (42 characters or fewer), category, archetype, virtual stake object, outcome mechanic, peak-tension moment, virtual reward, hero, palette, mood, render style, background color, typography mood, and game currency name.

Then inventory **all** of the game's sprite art. The manifest is exhaustive, not a shortlist:

```bash
rg --files assets/images/sprites assets/sprites 2>/dev/null \
  | rg -i '\.(png|webp|jpe?g|svg)$' | sort > "$ART_DIR/sprite-manifest-all.txt"
[[ -s "$ART_DIR/sprite-manifest-all.txt" ]] \
  || { echo "BLOCKER: no sprite assets found"; exit 1; }
rg -i '\.(png|webp|jpe?g)$' "$ART_DIR/sprite-manifest-all.txt" \
  > "$ART_DIR/sprite-manifest-raster.txt" || true
```

If the app registers additional sprite roots in `pubspec.yaml` or its asset registry, include those
roots in the same command. Do not include generated store outputs, backgrounds, UI chrome, fonts,
or launcher icons merely because they are raster files. Do include every shipped gameplay sprite,
including secondary symbols, rewards, particles/effects, alternate states and nested files. Convert
SVG sprite sources to lossless transparent PNG before `triptych`, write source → converted path in
the manifest, append each converted path to `sprite-manifest-raster.txt`, and retain the original
source as the identity reference. A vector file is not an excuse for omission. Before Phase 1,
verify that the number of unique raster-reference paths equals the number of unique source paths.

**List the hero first and mark it as the hero**: it leads panel 1, and every downstream phase reads
that role. Record one row per discovered sprite in `STORE_BRIEF.md`: source path, raster reference
path, gameplay role/state, assigned concept panel, the physical feature it becomes part of there,
the decoration/contact that connects it, and a gameplay screen or code/asset-registry location
that proves it belongs to the app. The number of table rows must equal the manifest's unique source
count. That table is what Phase 9 audits.

For the default three panels, assign the coverage before generating anything:

| Panel | Required real anchor | Natural construction — decide this now |
|---|---|---|
| 1 | Hero, plus a hero-held/worn object when useful | Empty decorated berth shaped around the hero; foreground crosses its feet |
| 2 | The real field or mechanic object | Fitted stage/machine caught mid-resolution; nearby surfaces take its light |
| 3 | Named reward, collectible, token, prop, modifier, capsule, ball, or progression object | Fitted shrine, pedestal, machinery, architecture, trail, or environment built around its exact silhouette |

The field counts as panel 2's primary anchor even though it is recorded separately below. When
`--board off`, reserve different mechanic and reward sprites for panels 2 and 3. Distribute every
remaining manifest row across the three scenes with purposeful roles and a clear scale/depth
hierarchy. Do not duplicate one floating symbol to fake coverage, and do not omit a secondary file
because its panel already has an anchor.

Then record **the field** — the surface the round is played on, and the second thing Phase 9
audits:

- Its shape, read off the game's own config, not guessed: `3x3`, `5x3`, a 5×5 mine grid, a
  peg field, a wheel, a track. For a slot this is `reels.count` × `reels.visible_rows` in
  `design/balance/rtp-config.json`.
- Every symbol PNG that appears on it, in the game's own reading order.
- Its real colours and materials, sampled from the game — the board/panel background, the cell
  tile, the edge, the corner radius — or the path of the real board asset in
  `assets/images/ui/` if one is shipped.
- One actual resolving gameplay frame used as visual context for the integration render. Prefer an
  existing verified frame; otherwise capture a reference-only win state during preflight. Record
  its path and field rectangle. This frame may predate the new branding because it is never shipped;
  Phase 4 still captures all final showcase frames after branding.

A game whose round has no readable field — a crash curve, a capsule machine, a single scratch card —
records the object the round *happens on* instead (the rocket and its curve, the machine, the card)
and runs with `--board off`. Panel 1 and the mechanic still have to be real; there is simply no
grid to assemble.

If the game has no character, the hero slot goes to the single object the round is *about* — the
machine, the wheel, the case, the tower. Panel 1 still has to lead with something and it still has
to be the thing the player is there for.

Choose copy that describes play and collection, not payment or financial gain. Use the exact English disclaimer from `ComplianceCopy.disclaimer` in listing metadata.

Run the compositor's font probe and select a display/body pair that covers every caption glyph. Prefer the game's bundled fonts; otherwise choose by Design DNA, not a studio-wide default.

## Phase 1 — generate brand art

Use image generation for three sources:

1. **Concept panorama:** one continuous text-free scene wide enough for P panels **plus the seam
   allowance** — ask for the widest the model will produce. Ask for a *finished illustration*, not
   a backdrop: this is the world the whole kit is cut from. Phase 2 places the game's real objects
   into it and renders the result as one picture, so what matters most here is that the scene has
   depth, a light direction, a ground plane and somewhere for those objects to stand — a flat
   backdrop gives the render nothing to integrate them into.
   - **The leftmost 1/P of the width is the hero berth** — the slice that becomes panel 1. Ask for
     a place built for a character to stand: a stage, ledge, throne, balcony, doorway or pool of
     light, with the scene's perspective converging on it, the brightest key light falling there,
     and foreground furniture along its bottom edge — a rail, steps, rocks, chips, foliage — for
     the figure to stand behind. Size it for a figure that will fill about **three quarters of the
     panel's height**, standing with its feet past the bottom edge. **Ask for it empty:** no
     character, no silhouette, no mannequin. The real hero is composited into it in Phase 2, and a
     drawn one there means two protagonists on the one screenshot the store shows at full size.
     Everything else in the picture is composed around that berth.
   - **Ask for the berth as ornament, not just as furniture.** The hero's head will land at about
     a third down the panel, and everything above that line is the decoration the note asked for:
     an arch, portal, crest, canopy, banner or drapery closing over the head, columns, statues,
     braziers or lanterns flanking the shoulders, a light burst, halo or window blazing behind
     where the head will be, and embers, petals, coins or motes drifting through the band. Name it
     in the prompt as its own subject — "the top third of the left panel is an ornamented crown
     over an empty berth" — or the model hands back sky, and the compositor will say so
     (`panel 1 crown: … above the hero's head is empty`).
   - **Leave a clear stage in the middle for the field** and ask for it empty too: a table, plinth,
     cabinet face, altar or floor plane, lit and unobstructed, about two thirds of one panel wide.
     `boardplate` fills it in Phase 2 with the game's own grid, caught at the moment it pays.
   - **Ask for the payout happening around that stage**, because the plate supplies the field and
     nothing else: light blasting up out of the stage's surface, coins, sparks, tokens or shards
     thrown into the air and crossing the stage's near edge, a crowd, a machine or the sky
     reacting, the reward resolving above it. This is what stops the middle panel — the listing's
     gameplay example — from being a board on a table. The *drama* of the mechanic is the model's
     job; the mechanic's own hardware is not.
   - **Build the rightmost panel for a real game object too.** Name the exact object assigned to
     panel 3 in the brief, but ask the model to draw its *empty physical home*, not a substitute:
     a fitted shrine whose opening follows its silhouette, a machine socket with the right contact
     plane, an opened vault/pedestal, a progression arch, a curved trail, or environment that will
     close in front of it. Carry the decoration out of that function — carved trim, ribbons,
     foliage, braces, cables, sparks, reflected light — so adding the reference asset completes the
     scene rather than laying an icon on it. The final third may not be generic scenery and may not
     contain a model-drawn version of the object.
   - Describe the exhaustive sprite manifest explicitly, grouped by panel and physical function.
     Ask for the hero and primary mechanic/reward anchors **large in the foreground, standing on a
     readable ground plane**, with some cropped by the bottom edge. Give every secondary sprite an
     identifiable home at another depth — mounted in architecture, nested in machinery, emerging
     from the resolution, carried through a trail, or functioning as a world-scale effect. The base
     scene must contain enough coherent constructions to receive every assigned file without
     becoming a contact sheet. Every third gets part of the full manifest.
   - **Ask for a dense picture, panel by panel.** Name what fills each third: its subject, its
     event, its real-game anchor, the physical construction waiting for that anchor, and its
     background place. Spell out the three planes, the ornament scales, the second and third light
     sources, the materials and the atmosphere from "Density is the other half of the brief" — an
     image model that is not told to populate the frame will hand back one object on a gradient
     every time. Say explicitly that the empty regions carry haze, particulate and structure
     rather than flat colour.
   - Keep important objects away from the panel seams — at 3 panels they sit at 1/3 and 2/3 of the
     width — and ask for a **calm vertical corridor** at each of them: sky, wall, haze, floor,
     roughly an eighth of a panel wide. This is the only protection a seam has. The panels must
     reassemble into the whole picture, so nothing can be discarded at a cut and the slicer can
     only slide the tiling as a whole to find quiet ground; if the art is busy edge to edge, some
     cut lands on a subject and the only fix left is regenerating the art. Ask for the vivid end of
     the palette: saturated colour, luminous key and rim light, deep contrast, glowing highlights.
   - **The negative list is part of the prompt, not a nicety.** No text, logo, letters, numbers,
     device frame or panel dividers — and no invented game board, reel grid, cells, symbol tiles,
     icon frames, HUD, balance, meter or multiplier in this first base-art pass. The gameplay field
     is generated only in Phase 2, where the actual gameplay frame is present as visual context.
   - Inspect the returned image against that list before going on. A grid, a symbol frame or a
     stray HUD in the source is a defect: regenerate. Do not crop it out, do not cover it with the
     board plate, and do not accept it because the rest of the picture is good.
   - Inspect it for **emptiness** in the same pass, thirds first: a third that is a gradient with
     one shape on it is a defect too, and it is the one most easily mistaken for "clean". Regenerate
     with the missing plane named — usually the background place and the atmosphere. The berth and
     the stage are empty of a *subject*, not empty of a *picture*: both are built, lit, ornamented
     surfaces.
2. **Icon art:** one bold central mechanic/hero silhouette, readable at 48 px, no text, no thin border, and no transparent holes.
3. **Game emblem:** a distinctive symbol/crest derived from the mechanic and world, with no letters or words, generated on a flat removable background.

Use the same Design DNA and top-left light for all three. Run `tools/cutout.py` on the emblem and inspect alpha edges. Regenerate an asset only when the source is genuinely defective.

If the image tool accepts reference images, pass the actual gameplay frame and every sprite file
from the exhaustive manifest. If it does not support reference images, it cannot satisfy the
identity/integration contract; use a reference-capable integration path rather than substituting a
flat composite or a description-only generation. Input-count limits are handled by the staged
high-fidelity process in Phase 2b, never by dropping manifest rows.

## Phase 2 — use gameplay as context, then render one finished picture

The output of this phase is **one illustration**, not an assembly. Compositing the real files or a
gameplay screenshot onto the art gets identity right and the picture wrong: the rectangle is flat,
its camera does not belong to the world, its edges are too clean, and a designer reads it as pasted
in the first second. The actual gameplay still has to author the mechanic — that part is not
negotiable — so its captured frame is used as **visual context the finished 3D field is generated
from**, never as a layer preserved in the final panorama.

Three steps: assemble a placement draft from the real gameplay, render the entire picture together,
then prove that gameplay survived as gameplay while becoming part of the scene.

### Phase 2a — the layout draft

Lift the resolving field from the actual game, give that draft object the scene's broad perspective,
then compose the placement draft:

```bash
python3 tools/store_compose.py boardplate --out "$ART_DIR/board-plate.png" \
  --from-shot "$RAW_DIR/gameplay-reference-win.png" \
  --rect 0.06,0.22,0.88,0.44 --radius 0.04 \
  --yaw -16 --pitch 7 --depth 0.06 --sheen 0.2

python3 tools/store_compose.py triptych --src "$ART_DIR/keyart.png" \
  --out "$ART_DIR/draft" --pano-only --save-pano "$ART_DIR/keyart-draft.png" \
  --panels 3 --size 1320x2868 --pop vivid \
  --sprite assets/images/sprites/sprite_eagle.png@hero \
  --sprite "$ART_DIR/board-plate.png@board,light=0.15" \
  --sprite assets/images/sprites/sprite_bolt.png@panel=3,rot=-8,occlude=0.10 \
  --sprite assets/images/sprites/sprite_shield.png@panel=1,rot=6 \
  --sprite-dir assets/images/sprites \
  --sprite-glow-color "#F0B34A"
```

- `gameplay-reference-win.png` is the authoritative context: a real captured resolving state, not
  a mockup and not an idle board. The plate is a placement aid derived from it. Neither the full
  frame nor the plate is pasted into the deliverable; both are references for Phase 2b.
- If no runtime frame can be captured during preflight, a plate built from the real grid, symbol
  files and sampled colours may establish the first draft. It is provisional. After Phase 4
  captures a real win frame, rebuild the plate and rerun Phase 2b with that complete gameplay frame
  as context before packaging.
- `--win`, `--dim` and `--lift` are fallback draft tools only. With `--from-shot`, the captured game
  already supplies the resolving state and those flags are refused. Never add a storefront-only win
  cue that the game itself does not show.
- **`--yaw`/`--pitch`/`--depth` are not decoration.** They give the board a near edge, a far edge
  and a visible slab thickness, so even the draft shows an object standing on the stage rather than
  a rectangle facing the camera. Match them to the perspective Phase 1 drew. The compositor warns
  when all three are zero.
- `--pano-only` writes the draft and nothing else. It is a reference image, never an upload asset,
  and it does not go in the kit's `store/` directory.
- Everything the earlier phases established still holds here: hero on panel 1 at ≈0.72 of the panel
  *height* under an ornamented crown, the field on the middle panel and paying, all manifest assets
  distributed at purposeful scales/depths, and nothing important on a seam. `--hero-height` rides
  through as the hero sprite's `h=` key (`--sprite hero.png@hero,h=0.68`); `w=` is the width cap,
  and it is the one to raise for a broad-shouldered cutout that hits it before reaching full
  height. The draft is composed against the same cuts the final slice will use, so an object placed
  clear of a seam here stays clear of it there.
- Read the `panel N game anchors:` lines before moving on. Every panel must name at least one real
  file and none may print `NONE`. Fixed hero/board placements are reserved first, so an unassigned
  supporting prop automatically fills the uncovered panel; explicit `panel=` remains available
  when the art has a precise fitted home. The default `occlude=0.08` on props closes a small amount
  of the scene back over them in the draft, while the integration pass below supplies final volume,
  mutual shadow, and decoration. A coverage warning is a blocker, not a suggestion to duplicate a
  floating icon.
- Read the `sprite inventory:` line too. Its total must equal the unique reference count in
  `sprite-manifest-raster.txt`, plus the board plate when that derived reference is passed separately.
  Inspect the placement draft and confirm that every manifest file appears in its assigned panel;
  directory discovery is a completeness mechanism, not permission to accept illegible overlap.
  Repeat `--sprite-dir` for every raster sprite root and pass converted SVG references explicitly
  with `--sprite converted.png@panel=N`; their source rows still remain in the exhaustive audit.

### Phase 2b — the integration pass

Hand the draft, the **actual gameplay frame**, and the objects' own files to the image model and ask
for one finished picture. The draft carries composition, the full gameplay frame carries mechanic
and state, the object files carry identity, and the model supplies the thing none can provide when
pasted together — a single rendered space with real perspective, volume, contact and atmosphere:

```bash
SPRITE_IMAGE_ARGS=()
while IFS= read -r sprite_path; do
  SPRITE_IMAGE_ARGS+=(--image "$sprite_path")
done < "$ART_DIR/sprite-manifest-raster.txt"

python3 tools/gpt_image.py edit \
  --prompt-file "$ART_DIR/integration-prompt.txt" \
  --image "$ART_DIR/keyart-draft.png" \
  --image "$RAW_DIR/gameplay-reference-win.png" \
  --image "$ART_DIR/board-plate.png" \
  "${SPRITE_IMAGE_ARGS[@]}" \
  --out "$ART_DIR/keyart-integrated.png" \
  --size 1536x1024 --quality high --fidelity high
```

- **Order matters.** The draft goes first: it is the layout. The actual gameplay frame goes second:
  it is contextual truth, not a layer to copy. The board plate follows as perspective guidance,
  then one reference per manifest row in the same order the prompt names them. Compare the number
  of `--image` sprite arguments against `sprite-manifest-raster.txt`; they must match.
- **`--fidelity high` is the setting that makes this work at all.** It is what keeps the eagle the
  game's eagle instead of an eagle. Never drop it to save time or budget.
- If one call cannot accept the full manifest, integrate in **panel-scoped high-fidelity batches**.
  The first batch carries the draft, actual gameplay frame, board plate and the three primary
  anchors. Each later pass uses the previous full panorama as its first image, the gameplay frame
  second whenever panel 2 is touched, and the next small group of sprite files after it. The prompt
  names those files, their assigned panel and their exact physical jobs, while explicitly preserving
  every already-integrated sprite. After each pass, audit all earlier rows plus the new rows. If an
  earlier sprite changes identity, disappears or becomes a pasted badge, rerun with a smaller batch;
  never solve an input limit by dropping it. Keep `--fidelity high` on every pass and retain the pass
  manifest in `STORE_INFO.md`.
- The prompt asks for a *render*, not a retouch. Say, in the game's own art language:
  - Reproduce the layout of the first reference image exactly — same subject in the same place at
    the same size, same panorama proportions, nothing added and nothing moved.
  - Use the second reference image as **gameplay context only**. Do not paste, frame, mask or retain
    its rectangular screenshot pixels. Create the play field anew inside the panorama as a solid
    3D mechanism belonging to the stage: scene-matched perspective and thickness, materials that
    take the same key/rim light, real contact and cast shadows, reflections on nearby surfaces,
    atmospheric depth, and foreground elements naturally passing in front of non-critical edges.
  - Preserve what makes it actual gameplay while integrating it: field topology and proportions,
    recognizable symbols, meaningful cell order, active/resolving state and decisive interaction.
    Perspective may change; mechanic identity may not. Keep the core field readable and do not let
    ornament, particles, props or dramatic foreshortening obscure how the game is played.
  - Reproduce **every** sprite reference exactly once in its assigned scene role: the same silhouette, colours,
    materials, ornament and detail. Do not redesign, restyle, simplify or substitute them. The grid
    keeps the same symbols in the same cells in the same order, and the same cells keep paying: the
    payline, the lit cells, the fallen-back cells and the symbol standing proud of the board are
    the state of the round, not clutter to tidy away.
  - Preserve the draft's exhaustive panel assignments and make every sprite complete a physical
    construction rather than hover over it: hero seated in the decorated berth on panel 1, field
    fitted into and illuminating the resolving stage on panel 2, the named reward/prop built into
    panel 3, and supporting sprites held, mounted, nested, emerging, travelling through, working as
    machine parts, or partly occluded by their decorated contexts. Let nearby trim follow each form
    and nearby material catch its light, but do not paint over an identifying silhouette. Do not
    arrange sprites as an icon row, contact sheet, inventory grid, trophy shelf, repeated pattern,
    tiled collage, or cloud of floating badges.
  - Render them as physical objects in one three-dimensional space: their own perspective agreeing
    with the scene's, real volume and thickness, cast shadows landing on the ground and on each
    other, contact where they touch, edges caught by the scene's key and rim light, atmospheric
    depth between the near objects and the far ones.
  - The character stands **in** the world: something in the foreground crosses in front of it, the
    ground takes its shadow, the scene's light wraps its silhouette. It keeps the size the draft
    gives it — about three quarters of the panel's height — and the ornament crowning the band
    above its head stays, gaining the render's depth: the arch or canopy in front of and behind the
    figure, the light burst reading as air, the drifting particles catching the key light.
  - Finish it as one painting — no cutout edges, no drop shadows, no sticker outlines, nothing that
    looks composited.
  - Keep every plane of the draft populated and **add** the finish a render can give that a
    composite cannot: micro texture and wear on the materials, the secondary lights and their
    spill, volumetric haze between the planes, particulate in the air. The render must not
    simplify the picture into a cleaner, emptier version of itself — that is the most common way
    an integration pass makes the art worse, and `triptych`'s per-panel detail figures catch it.
  - No text, letters, numbers, logo, app chrome, HUD, device frame, screenshot border or panel
    dividers, and no invented game symbols beyond the ones supplied. The gameplay reference informs
    the field; it does not import the phone screen surrounding it.
- Iterate on the prompt, not on the objects. If the board still reads as a decal, explicitly ask
  for shared perspective, visible thickness, attached architecture, mutual occlusion, cast light
  and shadows. If it becomes too decorative to read as gameplay, restate the protected mechanic
  topology and decisive interaction while keeping the 3D scene treatment.
- **The integration pass is mandatory for concept panels.** If the image model is unavailable,
  retain the Phase 2a composite only as a layout draft and report the concept-art portion blocked.
  Do not slice or package that draft as a storefront deliverable: a correctly referenced screenshot
  pasted into the scene still fails the requested treatment.

### Phase 2c — the identity gate

The integration pass is the one step in this skill that can silently change what the listing
advertises, so it is verified before anything downstream reads the file. Open
`keyart-integrated.png` beside every source/reference pair and answer one row per manifest entry:

| Sprite path | Assigned panel | Same identity? | Physical construction | Contact / overlap / shared light? | Recognizable at final panel size? |
|---|---|---|---|---|---|

- The row count must equal the exhaustive source-manifest count, every source must appear once,
  and every verdict column must be yes. A "close enough" symbol is the exact defect that
  returned the last listing, and it is harder to spot in a beautifully rendered picture than in an
  obvious paste-up.
- For the field, compare against the actual gameplay frame: same mechanic topology, recognizable
  symbol art, meaningful ordering and resolving outcome. Then check the other direction: the final
  field has scene-matched perspective, volume, material, light, contact and selective overlap, with
  no surviving rectangular screenshot boundary. It must pass identity **and** integration.
- “Built into the scene” means a visible physical relationship: contact with a fitted surface,
  mutual overlap or occlusion, shared perspective, cast/reflected light, and decoration belonging
  to that relationship. A clean cutout edge plus a generic glow is a no even when identity passed.
- Check coverage as a second axis: every manifest row has an unmistakable primary appearance and
  panel 1, panel 2, and panel 3 each contain assigned rows. An empty panel, a missing secondary
  sprite, or the same floating icon repeated to fill one is a failed integration pass.
- One object drifting is fixed by re-running with a tighter prompt naming that object, or with
  fewer references on the call. Repeated drift means the concept-art portion is blocked: neither a
  redesigned symbol nor the composited placement draft is an acceptable deliverable.
- The picture that passes this gate becomes `$ART_DIR/keyart-integrated.png`, which Phases 3, 5 and
  7 all read. There is only ever one integrated panorama in a kit.

## Phase 3 — apply the storefront to the game

This is the direction that gets listings rejected, and it must happen **before** any final
storefront gameplay frame is captured. The reference-only context frame from preflight remains an
input to the artwork and is never part of the upload set.

**Launcher icon.** Use `store_compose.py icon` to create the 1024 master, 512 listing icon, and adaptive foreground. Add/configure `flutter_launcher_icons` in `pubspec.yaml`, then run:

```bash
dart run flutter_launcher_icons
```

Verify generated Android mipmaps, adaptive icon resources, iOS AppIcon entries, and web icons. The App Store master must be opaque.

**Emblem.** Copy the emblem to `assets/images/ui/ui_game_logo.png`, register it in `pubspec.yaml` or the shared asset registry, and—unless `--no-wire-logo`—add one responsive `Image.asset` to the main menu. Do not rewrite the screen.

**Key-art backdrop.** Unless `--no-backdrop`, export the same panorama as the game's own background and wire it in:

```bash
python3 tools/store_compose.py backdrop --src "$ART_DIR/keyart-integrated.png" \
  --out-dir assets/images/backgrounds --prefix bg_keyart \
  --variants menu,game --size 1080x1920 --offset -0.55 --pop vivid --calm 0.45
```

- Use the panorama Phase 2 saved with `--save-pano`, not the raw generation: the app's own
  background should carry the same hero and the same seated objects the panels do.
- Choose `--offset` (with `--zoom` for slack) so the crop contains the **hero and the mechanic**,
  not empty sky. That slice is the world the player will live inside; make it the same slice the
  first panel sells.
- `bg_keyart_menu.png` goes behind the main menu / lobby at full strength.
- `bg_keyart_game.png` is the same picture, blurred, dimmed, and slightly desaturated by `--calm`
  so the live field, HUD, and buttons keep the eye. Raise `--calm` if any control loses contrast.
- Register both in `pubspec.yaml`, then point the existing menu and gameplay scaffolds at them with
  a `BoxDecoration`/`DecorationImage` (`fit: BoxFit.cover`) or a Flame background component, behind
  the existing layers. Do not restructure the screens.

Run formatting and analysis after these targeted edits. Revert any wiring that introduces an error,
an overflow, or a contrast regression, and say so in the final report — a broken screen is worse
than a missing background.

## Phase 4 — capture real gameplay frames

Capture only after Phase 3, so the frames show the applied emblem and the key-art background. Reuse
existing runtime frames **only** if they were captured after this run's branding was applied and are
valid portrait phone images with `h/w` between 1.9 and 2.35. Otherwise capture a new Chrome/CDP tour:

```bash
flutter run -d web-server --web-port=0 > .claude/runtime-logs/flutter-run.log 2>&1 &
node tools/web_verify.mjs --url "$WEB_URL" --out "$RAW_DIR" \
  --size 390x844 --dpr 3 --budget 180 --quick
```

Capture at least a menu, active round, peak-tension state, win/reward state, and one meaningful progression/meta state. Frames must show actual UI and actual game state—never mock numbers or fake gameplay.

Reject empty, duplicated, error, overflow, loading-only, wrong-aspect, or non-gameplay frames. Parse the Flutter log for exceptions before continuing.

Before selecting any gameplay frame, apply `.claude/docs/gameplay-screen-contract.md`. Reject and
stop for UI correction when the live field is a thumbnail/nested window, the core loop requires
scrolling, a large information card competes with the mechanic, or buttons are cramped, uneven,
clipped, off-screen, or disconnected. Store composition must never crop, enlarge, or cover a weak
gameplay layout to make it look acceptable.

Then run the continuity read: the captured frames must visibly share the panorama's world, and the
primary hero/mechanic/reward anchors must be findable in them. Every remaining manifest sprite must
have its recorded in-app evidence: a selected gameplay frame where practical, otherwise its actual
asset-registry/code reference and state. If the backdrop did not survive a screen, if the hero never
appears in the app, or if the symbols on screen look nothing like the ones in the panels, fix the
game and re-capture. Do not proceed and compensate in composition.

**The captured win frame now becomes the authoritative integration context.** Put it next to panel
2 and check that they show the same game: the same mechanic topology, recognizable symbols,
meaningful ordering and resolving outcome. Then check that panel 2 is a created 3D scene rather
than that frame pasted into one. This is the exact pair of failures the designer will see first,
so make both comparisons before they do. Rebuild the plate from the frame and rerun Phase 2b with
this complete win frame as the second context image:

```bash
python3 tools/store_compose.py boardplate --out "$ART_DIR/board-plate.png" \
  --from-shot "$RAW_DIR/04-win.png" --rect 0.06,0.22,0.88,0.44 --radius 0.04
```

Lift the **win** frame, not a resting one: the panel it lands on is the listing's gameplay example,
and the state the app was in when the frame was captured is the state the panel advertises. On the
rerun, substitute `$RAW_DIR/04-win.png` for the provisional
`$RAW_DIR/gameplay-reference-win.png` input in the Phase 2b command. Do not composite either image
after generation; they remain references only.

Re-running Phase 2 also re-exports the backdrop (Phase 3) and the feature graphic (Phase 7) from
the corrected panorama, so do those again rather than leaving three versions of the art in one kit.

## Phase 5 — compose the concept panels

Slice `$ART_DIR/keyart-integrated.png` separately for the App Store and Play dimensions with
`store_compose.py triptych`. Pass **no `--sprite`**: the objects are painted into that picture
already, and inlaying them a second time would put a flat copy on top of the rendered one. Produce
numbered `store-01.png` through `store-0P.png` plus `_panorama-preview.png` and
`_carousel-preview.png` for inspection.

The draft was graded before the render, so the integrated art arrives with the grade already in it:
slice at `--pop soft`, and only raise it if the returned picture is genuinely flat. Never slice the
Phase 2a composite as a fallback; it contains placement references rather than finished scene art.

**The panels must reassemble into the whole picture.** Lay them side by side in upload order and
the panorama has to come back exactly as it was rendered — not a millimetre of it missing anywhere.
That is the contract the slice is built around: `--gutter` defaults to `0`, panel *i* ends on the
very column panel *i+1* begins on, and slicing discards nothing between them. The compositor says
so on every run — `they reassemble the panorama exactly, 0px discarded` — and if that line ever
reports missing pixels, the kit is wrong.

**What protects a seam is where it falls, not what is removed there.** An even split cuts at
exactly 1/3 and 2/3 whatever is standing there, and when that is a face, a coin or the board's near
edge the panel stops mid-object. `--seam-snap` composes a little slack into the panorama and slides
the whole tiling inside it, choosing the position where the cuts land on the quietest columns the
picture has. Panel width is fixed by the store and nothing may be discarded, so the cuts move
*together*: this is the only lever, which is why Phase 1 has to ask the art for a calm vertical
corridor at each boundary. `auto` searches ±12% of a panel. `--seam-snap off` restores the
content-blind split; there is no good reason to use it.

**The seam allowance is opt-in and it costs the picture.** `--gutter 100` composes the panorama
wider and throws that strip away at each cut, so the store's own carousel gap stands in for it and
the panels line up across the gaps on the listing page. The price is a hole: each panel then ends
mid-object wherever the cut fell, and the set no longer reassembles. Pass it only when a publisher
has explicitly asked for that alignment, and record it in `STORE_INFO.md` when you do.

The compositor reports what it chose and what it cost:

- `panorama slid -70px inside its slack so the cuts miss the subjects` — where the tiling landed.
  Record it in `STORE_INFO.md`.
- `_panorama-preview.png` — the panels laid edge to edge, cut positions marked with short ticks at
  the top and bottom edges only. This is the proof: it must read as one uninterrupted picture.
- `_carousel-preview.png` — the same panels with the store's own gap (~4.5% of a panel) drawn
  between them, which is what the listing page shows. Nothing important may straddle a cut here.
- `seam 1→2: detail 0.94× the picture's average` — how busy the picture is exactly where it cuts.
  Ratios near 1.0 mean the cuts landed on calm background.
- A warning above 1.35× means a subject is being sliced and no position inside the search radius
  avoided it. Widen `--seam-snap` (up to 15%), slide the crop (`--zoom 1.15 --offset ±0.3`), or
  regenerate the art with a calm vertical corridor at that fraction of the width. Never answer it
  with `--gutter`: cutting a hole in the subject is not a way to stop cutting the subject.
- `panel 2: detail 6.4, 31% of it empty ground` — the density check from the art direction above.
  A panel called out as empty ground is regenerated, never graded or cropped into shape.

Both previews are verification artifacts and neither is uploaded.

Vision-check both previews — `_panorama-preview.png` for whether the panels are still one picture,
`_carousel-preview.png` for whether that survives the store's own gaps:

- **The panels are one picture again.** `_panorama-preview.png` shows no join at all: no step in a
  gradient, no jump in a line, no object with a slice missing out of it. The compositor's
  `0px discarded` line says the arithmetic is right; this says the eye agrees.
- Adjacent panels still read together in `_carousel-preview.png`, where the store's gaps are drawn
  in — nothing important straddles a cut.
- **Panel 1 opens on the protagonist**, at full height — roughly three quarters of the panel, feet
  past the bottom edge, head about a third of the way down — and recognizable as a character rather
  than a decorative shape. The compositor's `hero … % of its height` figure says the arithmetic is
  right; this says the eye agrees. If the hero is absent, small, or upstaged on panel 1, that panel
  is wrong no matter how good the rest of the strip is.
- **The band above the hero's head is decorated, not sky.** An arch, canopy, crest, banner, halo,
  flanking columns or lanterns, particles in the light — something that frames the figure and makes
  the slide read as a poster. The compositor's `panel 1 crown` line measures it; a flat crown is
  regenerated art, not a bigger sprite.
- **Panel 1 would look unfinished without the hero.** Cover the figure with a thumb: what is left
  should read as a stage waiting for someone, not as a complete illustration that happens to have a
  character on it. Something in the scene overlaps the hero's feet, its shadow lands on the berth,
  and the light on it comes from the light in the picture. If it still reads as inserted, the fix
  is the berth (Phase 1) or the seating (`occlude=`, `contact=`, `light=`) — never a bigger sprite.
- **The board is gameplay-derived and scene-created.** It retains the actual frame's mechanic
  topology, recognizable symbols, meaningful ordering and resolving outcome, while standing in the
  scene as a solid object with perspective, a visible near edge, attached material, mutual light
  and natural overlap. A flat screenshot rectangle is a blocker. So is a beautiful fantasy board
  whose mechanic or symbols no longer read as the real game.
- **The middle panel shows the actual round resolving, not a board at rest.** Preserve whichever
  cells, symbols and outcome cues the gameplay frame truly shows; do not manufacture a lifted
  symbol or payline solely for the storefront. The created scene reacts through attached structure,
  reflected light, controlled particles and surrounding action. Cover the field with a thumb: what
  remains should still be a moment. Cover the surround: what remains should still read as gameplay.
- **Nothing in the strip looks composited.** No screenshot rectangle, cutout edge, drop-shadow
  halo, object facing the camera while the scene recedes, or silhouette too clean for the painting
  around it. Every
  object has volume, sits in the scene's perspective, casts a shadow onto something, and is caught
  by the same light. It also has a physical relationship to the panel — held, fitted, mounted,
  emerging, travelling through, or partly behind something — with decoration growing from that
  relationship rather than floating around it. If one still reads as laid on, that is a Phase 2b
  re-run, not a crop.
- Primary anchors are at foreground scale and standing on something. Secondary sprites may occupy
  smaller midground roles, but each remains individually recognizable and has physical contact,
  shared light, or mutual overlap with its construction. Anything reduced to an unreadable speck
  or generic decoration goes back through Phase 2b with its role and minimum readable scale restated.
- No seam cuts the hero's face, central mechanic, reward, decisive action, or an inlaid game object.
  Check it on `_carousel-preview.png`: every one of them sits whole inside a single panel, so the
  store's gap falls on background.
- **Every panel is a finished illustration, not a backdrop.** Three occupied depth planes, ornament
  at more than one scale, more than one light, materials that respond differently, and atmosphere
  carrying the areas with no subject in them. A panel that is a gradient with one shape on it fails
  even if the shape is the right one — and the compositor's `% empty ground` line already said so.
- Density did not cost the hierarchy: the hero on panel 1 and the play field are still the first
  things the eye lands on, held apart from the detail by focus, value or a calmer surround.
- No letters, fake glyphs, captions, UI, HUD, meters, balances, or panel borders appear.
- The mechanic and category are recognizable without generic casino cues.
- **Every split panel has a real game anchor.** Panel 1 has the hero, panel 2 has the real
  field/mechanic, and panel 3 has the named reward/collectible/token/prop assigned in the brief.
  Each is unmistakably the same object the gameplay frames show. Decorative world-building alone
  cannot stand in for the final panel's object, and duplicating one floating icon across panels
  does not pass.
- **Every exhaustive-manifest row appears across the strip.** Compare the art to the manifest one
  sprite at a time; missing alternate states, secondary rewards or effects still fail. The set must
  read as one world with clear focal hierarchy, never an icon row, inventory grid or contact sheet.
- The panorama uses casino-grade tension, depth, tactility, and reward focus while remaining
  unmistakably specific to this game's Design DNA.
- Colour is rich and the image is bright enough to hold up at thumbnail size.

Both previews are verification artifacts and must not be listed for store upload.

## Phase 6 — compose gameplay showcase frames

Select `COUNT-P` real frames that tell one coherent casino-round story: enter the game, commit the
virtual stake/risk, reach tension, resolve/reveal, celebrate, and progress. At least half must show
active core gameplay or its immediate result. Write short English captions that are specific to
the actual mechanic and avoid payout language.

Use the key art — the integrated panorama from `--save-pano`, or the slice adjacent to the last
concept panel — as the `--bg` behind the device, so the visual language does not change at the
boundary between the two halves of the listing, and the game's objects keep appearing behind the
phone:

```bash
python3 tools/store_compose.py showcase --shot "$RAW_DIR/03-spin.png" \
  --bg "$ART_DIR/keyart-integrated.png" --out "$OUT_DIR/store-04.png" --size 1320x2868 \
  --caption "Every Spin Counts" --type-mood epic --pop vivid \
  --caption-color "#FFF6DC" --caption-color2 "#F0B34A"
```

Run it once for the main set and once for the Play set using the same ordered frame/caption list. Use the chosen font pair and Design DNA palette. Captions must remain within safe areas, retain at least 4.5:1 contrast, and render every glyph correctly.

`--pop` grades the *background* only; the real frame inside the device is never touched.

Vision-check every composed file for clipping, misspellings, empty glyph boxes, distorted phone frames, fake gameplay, or inconsistent typography.

## Phase 7 — feature graphic

Create `feature-graphic-1024x500.png` with `store_compose.py banner`. Use the **integrated**
panorama (`$ART_DIR/keyart-integrated.png`) as the image layer, so the graphic carries the hero and
the seated objects rather than the bare generation. A centre crop of a 3-panel panorama misses panel
1 entirely, so slide it with `--offset` (`--zoom` for slack) until the hero is in frame *and* clear
of the furniture: the title lockup and its scrim own the left half, and `--shot` puts the device in
the right third. Drop `--shot` if the hero needs that room. Render the English game title and
tagline with the compositor; never ask the image model to draw them.

The feature graphic is for Google Play and may also be included in the press kit.

## Phase 8 — blocking compliance gate

Write every visible title, tagline, and caption to `$STORE_DIR/STORE_COPY.txt`. The copy must contain no promise of cash, payout, earnings, withdrawals, prizes with monetary value, or real-currency symbols/codes.

```bash
grep -niE 'real money|payout|win cash|earn (real )?money|withdraw|cash ?out|prize fund' \
  "$STORE_DIR/STORE_COPY.txt" && { echo "BLOCKER: prohibited payout claim"; exit 1; }

grep -nE '[$€₽£¥]|\bUSD\b|\bEUR\b|\bRUB\b' "$STORE_DIR/STORE_COPY.txt" \
  && { echo "BLOCKER: real-currency symbol or code"; exit 1; }
```

For C2, describe the mechanic as “collect before the crash” or similar; do not use “cash out” in storefront copy.

Vision-check every final panel, showcase frame, banner, and icon for currency symbols, banknotes, money bags, payout/cash text hallucinations, balances marked with real currency, or realistic payment hardware. Any hit is a release blocker and must be fixed in the image, not merely reported.

Record the required rating, simulated-gambling questionnaire answer, category, disclaimer, and odds-disclosure requirement in `STORE_INFO.md`. Full-profile games normally require 18+ on Google Play and 17+ on App Store; use the concept's recorded compliance profile for C5 exceptions.

## Phase 9 — verification

```bash
python3 tools/store_compose.py check --dir "$OUT_DIR" --store appstore
python3 tools/store_compose.py check --dir "$PLAY_DIR" --store play
```

Both checks must pass. Confirm readable RGB PNG files, consistent dimensions, no alpha in Play screenshots, file sizes within store limits, and correct aspect ratios.

Then run the **exhaustive sprite continuity audit** across both ordered sets and write the result
into `STORE_INFO.md` as a table with one row per source manifest entry:

| Source sprite | Raster reference | Assigned concept panel | Physical scene role | Identity preserved? | In-app evidence |
|---|---|---|---|---|---|

Every source sprite must have exactly one row, a visible concept-panel location, a specific physical
role, an identity yes, and in-app evidence (a frame or exact code/asset-registry location). An empty
cell or a manifest asset absent from the art is a blocker: rerun the appropriate Phase 2b integration
batch and then all downstream exports. Confirm in the same pass that the panels and gameplay frames
share one palette, one light direction, and one material language, and that neither set looks flat
next to the other. Record the arithmetic explicitly: `sources discovered = raster references =
integration references = visibly present rows = audited rows`.

Then audit the split slides themselves — object continuity can pass while panel 3 is still only
background:

| Concept panel | Manifest sprites visible here | Primary anchor | Built into what? | Contact / overlap / shared light? | Decoration grows from the objects? |
|---|---|---|---|---|---|
| 1 | Paths/names | Hero | Berth / throne / ledge / doorway | yes/no | yes/no |
| 2 | Paths/names | Field/mechanic | Stage / machine / altar / track | yes/no | yes/no |
| 3 | Paths/names | Reward/prop | Shrine / socket / pedestal / trail / architecture | yes/no | yes/no |

The union of the `Manifest sprites visible here` column must equal the exhaustive manifest with no
duplicates used to fake coverage. Every panel row needs a named primary asset and three specific
visual answers; all yes.
“Placed over the background”, “surrounded by glow”, “arranged in a contact sheet”, or the same
free-floating icon copied between panels is a no. For `P` other than three, add one row per panel
and apply the same gate.

Record the hero row separately, with the fractions of panel 1 it occupies — **width and height
both** — the compositor's own `inlay hero …` line, its `panel 1 crown` line, and whether the inlay
line ends in `+ occluded by the foreground`. Under 0.6 of the panel's height, absent from panel 1,
standing in front of the whole scene, or crowned by empty sky is a blocker.

Record the field row separately too, and answer it by looking at the two images rather than at the
command line:

| The field | Concept panel | Actual gameplay context | Same mechanic/layout? | Same symbols/state? | Created as 3D scene art? | No pasted screenshot edge? |
|---|---|---|---|---|---|---|

Four yeses or the plate is rebuilt from the frame (`boardplate --from-shot` on the win frame) and
the integration render plus Phases 3 and 7 are re-run. The two tests are independent: gameplay
identity can pass while the frame still looks pasted, and 3D integration can pass while the model
has invented a different game. `--board rest` answers the state column with the reason there is no
win state to show. `--board off` fills the whole row with the object the round happens on instead,
and it is audited the same way.

## Phase 10 — store information

Write `$STORE_DIR/STORE_INFO.md` in English with:

- Build timestamp, category, archetype, title, tagline, and dimensions.
- An inventory of both screenshot sets, feature graphic, icons, emblem, and the two
  verification-only previews.
- Ordered caption mapping.
- The hero object, its size on panel 1 as fractions of the panel's width **and height**, what the
  `panel 1 crown` line measured above its head and what ornament fills that band, whether the
  scene's foreground was closed back over it, and the supporting objects with the panels they were
  seated into.
- Which actual gameplay frame and field rectangle supplied the integration context; how the board
  plate was derived; its yaw/pitch/depth; the resolving state it carried; and which panel it landed
  on. Record explicitly that the gameplay frame was used as a reference and was not pasted into the
  final panorama. `--board rest` and `--board off` record why instead.
- The integration pass's draft, actual gameplay frame, object references and fidelity; the identity
  gate's per-object verdict; and the field's separate gameplay-identity / 3D-integration /
  no-screenshot-edge verdict. An unavailable or failed integration is reported as a blocker, never
  as an un-integrated shipped fallback.
- The exhaustive sprite-manifest totals, source → raster mappings, per-panel distribution, every
  sprite's physical role and final identity/integration verdict, plus the ordered high-fidelity
  batch passes when the manifest required more than one call. The five completeness counts from
  Phase 9 must match.
- The per-panel anchor audit: the exact real asset anchoring every split slide, the physical
  construction it completes, its contact/overlap/shared-light evidence, and how decoration grows
  naturally from it. Explicitly record panel 3 rather than summarizing the triptych as a whole.
- That the panels reassemble the panorama with nothing discarded (quote the compositor's
  `0px discarded` line), how far the tiling slid inside its slack, and each seam's final detail
  ratio. If an explicit `--gutter` was used instead, say so, give the width, and say who asked
  for it.
- The per-panel detail figures and empty-ground percentages, with a note on any panel that
  was regenerated for being too sparse.
- Exactly what branding was applied to the project — icon, emblem, and every background file the
  key art was wired into, with the screens that now use them.
- The continuity audit table.
- Compliance profile, ratings, simulated-gambling answer, disclaimer, odds disclosure, and grep/vision results.
- Exact Google Play and App Store upload order. Emphasize that neither `_panorama-preview.png` nor
  `_carousel-preview.png` is uploaded.

## Phase 11 — package

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x '*.DS_Store')
[[ -s "$ARCHIVE_PATH" ]] || { echo "Store ZIP was not created."; exit 1; }
unzip -t "$ARCHIVE_PATH" >/dev/null || { echo "Store ZIP is corrupt."; exit 1; }
shasum -a 256 "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
```

Verify the archive contains numbered PNGs in both `store/` and `store-play/` unless the Play set was explicitly disabled.

## Phase 12 — final report

Report the title/tagline, category/archetype, App Store and Play counts/dimensions, panorama panel range, that the panels reassemble into the whole picture with nothing discarded, the per-seam detail ratios, the per-panel detail figures, whether the panorama was rendered from the draft or shipped as the composite, the exhaustive sprite-manifest counts and per-panel distribution, any staged high-fidelity integration passes, the one-row-per-sprite identity/integration verdict, the real anchor on **each** split panel and the physical/decorative construction it completes, the hero on panel 1 (its share of the panel's width and height, what crowns the band above its head, and that the scene closes in front of it), the actual gameplay frame used as context for the middle field, how that field preserved the mechanic/state while being recreated as scene-matched 3D art, confirmation that no screenshot layer or rectangular edge survived, gameplay-frame range, feature graphic, icon application status, emblem wiring status, backdrop wiring status (which files, which screens), the continuity audit verdict including the field row and the per-panel anchor audit, compliance verdict, ratings/disclaimer, archive path/size, and SHA-256. State the exact upload order for each store.

## Quality gates

- Preflight tools and fonts are available.
- The exhaustive sprite manifest exists in `STORE_BRIEF.md` with one row per unique shipped sprite
  source, source → raster mappings, the hero first, all rows assigned across the concept panels,
  and a named physical/decorative construction for each. The discovered, raster-reference,
  integration-reference, visibly-present and audited counts are equal.
- At least one valid phone-aspect raw frame exists; the final selection includes active play and a win/reward state.
- Gameplay frames were captured **after** branding and the backdrop were applied.
- Every selected gameplay frame passes the full-viewport gameplay-screen contract; no thumbnail
  field, nested window, core-loop scrolling, disconnected controls, or poor button proportions.
- The ordered set passes the casino-style storefront grammar: mechanic-first tension, depth,
  tactility, outcome focus, and active/reveal/celebration coverage.
- Panel 1 leads with the hero at no less than 0.6 of the panel's height, and the compositor
  reported it as `inlay hero … → panel 1 … + occluded by the foreground`.
- Panel 1 was composed as a berth for the hero: covering the figure leaves a stage waiting for
  someone, not a finished picture with a character laid on it.
- The band above the hero's head is ornament — arch, canopy, crest, banner, halo, flanking
  columns, particles — and the compositor left no `crown … is empty sky` warning standing.
- The middle panel shows the game's real resolving outcome. Any lit/dimmed cells, raised symbol or
  outcome cue comes from the actual gameplay context rather than storefront invention; the created
  scene adds 3D construction and controlled reaction without covering the decisive interaction.
  `--board rest` was used only for a mechanic with no win state, and `STORE_INFO.md` says why.
- The play field was generated with the scene from an actual gameplay context frame. The audit's
  four columns — same mechanic/layout, same symbols/state, created as 3D scene art, no pasted
  screenshot edge — are all yes. It remains readable while carrying the scene's perspective,
  thickness, materials, light, shadows, contact and controlled foreground overlap.
- The panorama is one rendered picture, not a paste-up: no screenshot rectangle, cutout edge,
  drop-shadow halo, or object facing the camera while the scene around it recedes survives.
- The identity gate passed for every sprite — same silhouette, colours and defining detail as its
  reference, recognizable at final panel size, and visibly built into the scene. A flat composite
  is never accepted as the concept-panel fallback.
- Every split panel contains at least one unmistakable real game anchor and the compositor printed
  no `panel N game anchors: NONE`: panel 1 hero, middle panel field/mechanic, final panel named
  reward/collectible/token/prop. Each completes a different scene beat; none is a duplicated
  floating icon used to satisfy coverage mechanically.
- Primary anchors are at foreground scale; every secondary sprite remains individually
  recognizable at final panel size. All read as seated in the scene — grounded, lit by the same
  light, held/fitted/mounted/emerging/working as a mechanism/partly occluded, with decoration
  growing from that relationship — never pasted or grouped as a contact sheet.
- Panorama, icon, and emblem share one visual world and pass vision review.
- Launcher icons are applied unless `--no-apply` was requested.
- The key art is wired into the game as its background unless `--no-backdrop` was requested, and
  `flutter analyze` is clean afterwards.
- The continuity audit is complete with one row per sprite: every row appears in a concept panel
  and has specific in-app evidence; the primary anchors also appear in captured gameplay frames.
- **The panels reassemble into the whole picture in both sets**: the compositor reported `0px
  discarded`, and `_panorama-preview.png` shows no join — no step, no jump, no object with a slice
  missing. Anything else is a blocker, not a note.
- They still read together in `_carousel-preview.png`, with the store's own gaps drawn in, and are
  text-free.
- The cuts were placed by the picture, not by arithmetic: `--seam-snap` was left on, and every seam
  either measures calm or was resolved by regenerating the art. No panel ends mid-object.
- No seam warning above 1.35× is left unresolved, and none was answered with `--gutter`.
- Every panel passes the density check: three occupied depth planes, ornament at more than one
  scale, more than one light source, differentiated materials, atmosphere through the quiet areas —
  and no panel left flagged as empty ground by the compositor.
- The added density did not bury the focal points: the hero and the play field still lead.
- Colour and brightness hold up at thumbnail size in both sets.
- Showcase captions are readable, correctly spelled, and rendered with full glyph coverage.
- Compliance grep and vision checks pass with no exceptions.
- `check --store appstore` and `check --store play` both pass.
- The ZIP is valid, contains the required files, and has a recorded SHA-256.

## Forbidden

- Changing gameplay logic, state, configuration, balance, or economy. Applying the icon, emblem,
  and key-art backdrop is the only project modification this skill makes.
- Shipping gameplay frames captured before the branding and backdrop were applied, or reusing them
  in the upload set. One pre-branding resolving frame is allowed only as reference context for the
  integration generation and must never be exported as a storefront screenshot.
- Shipping concept panels that show objects, characters, or a world the app does not contain.
- Omitting any shipped gameplay sprite from the concept panorama, passing only a curated selection
  of primary anchors to the integration render, or accepting manifest/reference/audit counts that
  do not match.
- Shipping any split concept panel with no real game anchor because the panorama as a whole has
  enough assets, or filling that gap by repeating the same floating icon over generic scenery.
- Letting the image model invent the game's board, reels, grid, cells, symbol tiles, icon frames,
  HUD, balance, or multiplier from a description — or keeping such art because the rest of the
  picture is good. Actual gameplay must be present as authoritative visual context when the field
  is generated with the scene.
- Pasting, masking or framing the gameplay screenshot into the final panorama, including a flat
  front-on rectangle surrounded by an ornate bezel. The screenshot is a generation reference,
  never a final layer; the created field must share the scene's perspective, volume, material,
  light, shadow, contact, atmosphere and controlled overlap.
- Using “make it 3D” as permission to lose the game: no replacement symbols, changed topology,
  ornamentalized cells, unreadable foreshortening or decoration covering the decisive interaction.
- Shipping the flat composite as the finished panorama under any circumstance, or running the
  integration pass below `--fidelity high`.
- Accepting an integrated picture whose objects were redesigned, restyled, simplified or
  substituted, because the render looks good. A beautiful wrong symbol is the same rejection as an
  ugly one, and harder to catch.
- Building the board plate in invented colours when the game's own board colours, or its shipped
  board asset, were available to sample.
- Shipping gameplay frames that share nothing visual with the concept panels.
- Shipping a set whose panels do not lay back down into the whole picture. Any strip discarded
  between panels — an unrequested `--gutter`, a re-crop, a "tidied" edge — means every panel ends
  mid-object, which is the defect this contract exists to prevent. `--gutter` is used only when a
  publisher has explicitly asked for the panels to line up across the store's carousel gap, and
  the choice is recorded.
- Cutting the panorama blind — `--seam-snap off`, or `--gutter` used to answer a hot seam. Cutting
  a hole in the subject is not a way to stop cutting the subject; the cuts have to move off it, or
  the art has to be regenerated with a calm corridor there.
- Leaving a subject sitting on a cut because `_panorama-preview.png` "looks fine" as a continuous
  image — of course it does, that is the panorama. The store's gaps are in
  `_carousel-preview.png`, and that is where a straddled subject shows.
- Shipping a panel that is a gradient with one object on it — an empty backdrop dressed up with a
  colour grade — or accepting one because the compositor's empty-ground warning was "only a
  warning". Sparse art is regenerated from a fuller brief, not graded, cropped or captioned into
  looking finished.
- Letting the integration pass hand back a cleaner, emptier version of the draft and shipping it
  because it renders nicely.
- Colour-grading, relighting, or retouching a real gameplay frame instead of fixing the game.
- Drawing fake gameplay, fake values, generated lettering, device frames, or panel separators into model-generated art.
- Compositing a game object into the key art unlit, unscaled, and unshadowed so it reads as a
  sticker, or at a size that makes it decoration rather than part of the composition.
- Treating contact shadow plus glow as sufficient integration. Each game object must complete a
  physical, decorated construction in its panel — held, fitted, mounted, nested, emerging,
  travelling through, or partly occluded — and the final render must show mutual contact and light.
- Solving exhaustive coverage with pasted icons, an inventory grid, contact sheet, trophy shelf,
  tiled sprite pattern, or cloud of floating badges. All sprites are context for one rendered
  world and must have natural physical jobs inside it.
- Opening the listing on anything other than the protagonist: a logo panel, an empty establishing
  shot, or a first panel where the hero is small, cropped out, or upstaged.
- Sizing the hero by the panel's width and shipping the 40%-of-the-height figure that produces, or
  answering an empty crown band by scaling the hero up until its head fills it — the band is
  ornament the art owes the slide, not spare room for a bigger sprite.
- Shipping the play field at rest on the panel that is the listing's gameplay example, or making it
  interesting by inventing a win the game cannot pay: the cells that light up come from the game's
  own paytable, drawn onto the game's own field.
- Dropping the real hero onto a panel 1 that was drawn as a complete picture without it, or
  pasting it in front of the whole scene with nothing overlapping its feet — "inserted" is the
  word the designer used, and it is visible immediately.
- Drawing a character into the hero berth in Phase 1 and then compositing the real hero on top of
  it, so the one full-size screenshot shows two protagonists.
- Generic casino art direction unrelated to the current category and Design DNA.
- Flat utility-app screenshots with no casino-round tension, outcome focus, or premium depth.
- Hiding a weak gameplay layout with aggressive cropping, oversized device chrome, captions,
  concept art, or decorative effects.
- Any real-money promise, currency symbol, banknote, cash/payout language, or financial implication.
- Reusing the 6.9-inch files as the Play set or scaling them instead of recomposing.
- Hiding generation, compliance, verification, or packaging failures.
- Listing `_panorama-preview.png` or `_carousel-preview.png` as an upload asset.
