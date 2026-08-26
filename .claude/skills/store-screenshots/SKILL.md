---
name: store-screenshots
description: "Build a casino-grade App Store and Google Play storefront kit for a gambling game: a text-free concept panorama sliced into panels with a seam allowance, real gameplay screenshots in device frames with compliant English marketing typography, a feature graphic, an applied launcher icon, and an in-game emblem. Panel 1 leads with the protagonist at full size and the game's real objects are built into the artwork at foreground scale, not pasted on it. The key art and the app share one world in both directions — the panorama carries the game's real objects and the game wears the panorama as its background. Every set uses high-stakes casino storefront composition while its palette, materials, characters, and typography follow the game's C1-C6 category, archetype, and Design DNA. Output is a downloadable ZIP under project_zip/."
argument-hint: "[--count 8] [--panels 3] [--size 1320x2868|1290x2796|play] [--no-play-set] [--gutter 100] [--pop vivid|soft|max|off] [--hero hero.png] [--props a.png,b.png] [--sprite-light 0.35] [--no-backdrop] [--lang en] [--frame ios|android|none] [--type-mood bold|epic|tech|playful|elegant|retro|clean] [--no-captions] [--no-apply] [--no-wire-logo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Store Screenshots — Complete Storefront Kit

Create everything needed to present the game in App Store Connect and Google Play:

| Deliverable | Source |
|---|---|
| Panels 1…P: one wide, text-free concept illustration led by the hero on panel 1 and carrying the game's real objects at foreground scale, sliced into adjacent panels | GPT Images 2.0 → `store_compose.py triptych --sprite --gutter` |
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
| Key art → app | The concept panels' world, hero, palette, materials, and light must be visible on the game's own screens | `store_compose.py backdrop` exports the panorama as the game's menu and gameplay background, and Phase 3 wires it in **before** a single frame is captured |
| App → key art | The concept panels must contain the game's **real** objects — the exact symbols, tokens, characters, and props the player touches | `store_compose.py triptych --sprite` composites the shipped PNGs from `assets/images/` into the panorama |

Describing a symbol to an image model produces something *similar*. Compositing the shipped sprite
produces the *same object*. Use the second for the objects that must match.

**Phase order is part of the contract.** Art → apply to the game → capture frames. Capturing
gameplay first and applying branding afterwards is exactly the bug that ships a listing whose two
halves show different products.

**The shared object list.** In Phase 0, choose 3–5 named objects that must appear on both sides of
the listing — the hero plus the two or three symbols the round is actually played with. Record them
in `STORE_BRIEF.md`. Entry 1 is always the hero. Phase 9 verifies every one of them by eye in at
least one concept panel *and* at least one gameplay frame. A missing entry is a blocker.

## Lead with the hero, build the objects in — the composition contract

Continuity gets the right objects into the picture. This gets them in at the right size and in the
right place, which is the other note the publisher's designer sends listings back for: *put the
protagonist on the first screen, always, so it hits the eye immediately — and the game's objects
are not worked into the design at all and are far too small; build them into the artwork itself.*
Three rules, all defaults rather than options:

**1. The protagonist owns panel 1.** Screenshot 1 is the only one the store shows at full size;
everything after it is a thumbnail in a strip. Whatever stops the scroll has to be there and has to
be big, and it is the hero — not a logo, not an establishing shot, not whichever slice of the
panorama happens to be prettiest. `triptych` enforces it: the first `--sprite` is treated as the
hero, lands on panel 1 at ≈0.58× the panel width, and stands with its feet past the bottom edge.

**2. Objects are built into the design, not laid on top of it.** A game symbol shrunk to a fifth of
a panel and dropped onto the background reads as a sticker — which is worse than no inlay at all,
because it also makes the whole picture look assembled. Real objects belong in the foreground at a
third of a panel or more, standing on the scene's ground plane, casting a contact shadow, tinted by
the light they are standing in, with the nearest ones cropped by the frame edge. The compositor does
the seating — foot anchoring, contact shadow, edge light-wrap and colour cast (`--sprite-light`) —
but it can only seat an object into a scene that has somewhere to stand, so Phase 1 has to draw one.

**3. Stop at five.** The reference the designer sent as a *good* example came with its own
correction: slightly too many objects. A hero plus two or three symbols reads at thumbnail size; a
pile does not. `triptych` warns past five.

The target is one finished picture — hero large at one end, the mechanic across the middle, the
game's real objects carried through the foreground — not a background with props arranged on it.
Ask the model for it that way in Phase 1, then composite the real files into the composition it has
already drawn (Phase 2).

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

- Lead with the decisive wager/reveal/drop/collect moment and make the real mechanic unmistakable.
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

## Arguments and defaults

| Argument | Default | Meaning |
|---|---|---|
| `--count N` | `8` | Total screenshots |
| `--panels P` | `3` | Number of adjacent concept panels; `0` disables them |
| `--size` | `1320x2868` | Main set; also supports `iphone-6.9`, `iphone-6.9-alt`, `iphone-6.5`, and `play` |
| `--gutter` | `auto` (≈100 px at 1320-wide panels) | Seam allowance discarded between panels; `0` butt-joins them |
| `--pop` | `vivid` | Colour grade applied to generated art (`off`, `soft`, `vivid`, `max`) |
| `--hero` | first shared object | The protagonist PNG that leads panel 1; if omitted, entry 1 of the shared object list |
| `--props` | auto | Comma-separated game PNGs inlaid into the panorama, capped at four alongside the hero; the default comes from the shared object list |
| `--sprite-light` | `0.35` | How hard inlaid objects are pulled into the scene's light (colour cast + edge light-wrap). `0` pastes them flat |
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

## Phase 0 — preflight, store brief, and the shared object list

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

Then inventory the game's real art and choose the **shared object list**:

```bash
ls assets/images/sprites/ assets/images/ui/ assets/images/backgrounds/ 2>/dev/null
```

Pick 3–5 objects that carry this game's identity — the hero/character plus the two or three symbols
the round is actually played with (the eagle, the bolt, the shield; the capsule, the rarity gem;
the ball, the peg field). **List the hero first and mark it as the hero**: it is the object that
leads panel 1, and every downstream phase reads that ordering. Record in `STORE_BRIEF.md`, for each
one: its name, its PNG path, its role (hero or symbol), where it will appear in the concept art, and
which gameplay screen shows it. That table is what Phase 9 audits.

If the game has no character, the hero slot goes to the single object the round is *about* — the
machine, the wheel, the case, the tower. Panel 1 still has to lead with something and it still has
to be the thing the player is there for.

Choose copy that describes play and collection, not payment or financial gain. Use the exact English disclaimer from `ComplianceCopy.disclaimer` in listing metadata.

Run the compositor's font probe and select a display/body pair that covers every caption glyph. Prefer the game's bundled fonts; otherwise choose by Design DNA, not a studio-wide default.

## Phase 1 — generate brand art

Use image generation for three sources:

1. **Concept panorama:** one continuous text-free scene wide enough for P panels **plus the seam
   allowance** — ask for the widest the model will produce. Ask for a *finished illustration*, not a
   backdrop: this is the picture the whole kit is cut from, and Phase 2 only reinforces a
   composition it already has.
   - **The hero goes in the leftmost 1/P of the width** — the slice that becomes panel 1 — drawn
     large enough to fill roughly two thirds of the frame height, facing into the scene, lit as the
     brightest subject in the picture. Everything else is composed around it.
   - The category mechanic and the peak moment run across the middle; the virtual reward resolves
     toward the far end.
   - Describe the shared-object list explicitly, in the game's own materials and palette, and ask
     for those objects **large in the foreground, standing on a readable ground plane**, some of
     them cropped by the bottom edge — a scene with somewhere for Phase 2 to seat the real files.
     Say how many; more than five and the picture turns into a heap.
   - Keep important objects away from the panel seams — at 3 panels they sit at 1/3 and 2/3 of the
     width. Ask for the vivid end of the palette: saturated colour, luminous key and rim light, deep
     contrast, glowing highlights. Explicitly request no text, logo, letters, numbers, UI, device
     frame, or panel dividers.
2. **Icon art:** one bold central mechanic/hero silhouette, readable at 48 px, no text, no thin border, and no transparent holes.
3. **Game emblem:** a distinctive symbol/crest derived from the mechanic and world, with no letters or words, generated on a flat removable background.

Use the same Design DNA and top-left light for all three. Run `tools/cutout.py` on the emblem and inspect alpha edges. Regenerate an asset only when the source is genuinely defective.

If the image tool accepts reference images, pass the actual sprite files from the shared object
list. If it does not, do not treat the description as sufficient — Phase 2 composites the real
files instead.

## Phase 2 — seat the game's real objects into the key art

Composite the shipped PNGs from the shared object list into the panorama, so the panels advertise
objects the app demonstrably contains — hero first:

```bash
python3 tools/store_compose.py triptych --src "$ART_DIR/keyart.png" --out "$OUT_DIR" \
  --panels 3 --size 1320x2868 --gutter auto --pop vivid \
  --save-pano "$ART_DIR/keyart-integrated.png" \
  --sprite assets/images/sprites/sprite_eagle.png@hero \
  --sprite assets/images/sprites/sprite_bolt.png@panel=2,rot=-8 \
  --sprite assets/images/sprites/sprite_shield.png \
  --sprite-glow-color "#F0B34A"
```

- **The first `--sprite` is the hero** unless another carries `@hero`. It takes panel 1 at ≈0.58×
  the panel width with its feet past the bottom edge, so the store's one full-size screenshot opens
  on the protagonist. Pass the hero first and the default is already right.
- Sprites must be transparent PNGs. The compositor warns when one is opaque — run
  `python3 tools/cutout.py <file> --type sprite` first, or the panel shows a background box.
- Omit `x` and objects are auto-placed at graded depths — roughly a third of a panel wide, fanning
  out from panel 2, anchored by the foot to the picture's ground plane, the nearest ones running off
  the bottom edge, always clear of the seam allowance. Use `x`/`y`/`w`/`rot`/`panel`/`bleed` when
  the panorama's composition wants a specific spot; `w` below `0.25` is sticker territory.
- Every object is seated, not pasted: a contact shadow at its foot, a colour cast pulled from the
  art it covers, and an edge light-wrap that spills the surrounding scene over its rim. Tune with
  `--sprite-light` (default `0.35`) and per-object `contact=`/`light=`; `--sprite-light 0` restores
  the flat paste, which is exactly what reads as a sticker.
- Pass the game's accent colour as `--sprite-glow-color` so the objects sit *in* the light of the
  scene rather than on top of it.
- A hero plus two or three symbols beats five. The panorama is still a picture, not a sprite sheet,
  and the compositor warns past five.
- Foreground scale needs source pixels. The compositor warns when a sprite has to be upscaled more
  than 2×; when it does, export the asset larger or have Phase 1 draw that object into the panorama
  rather than shipping a soft hero on the one screenshot the store shows at full size.
- `--save-pano` writes the graded panorama with the objects already in it. Phases 3 and 7 read that
  file, so the app's background and the feature graphic show the same integrated picture the panels
  do instead of the bare model output.

If an object cannot be made to sit in the scene convincingly, regenerate the panorama with that
object described into the composition instead — but the object still has to be there, and still at
foreground size.

## Phase 3 — apply the storefront to the game

This is the direction that gets listings rejected, and it must happen **before** any gameplay frame
is captured.

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
shared-object list must be findable in them. If the backdrop did not survive a screen, if the hero
never appears in the app, or if the symbols on screen look nothing like the ones in the panels, fix
the game and re-capture. Do not proceed and compensate in composition.

## Phase 5 — compose the concept panels

Slice the same panorama separately for the App Store and Play dimensions with `store_compose.py triptych`, passing the **same `--sprite` list in the same order** so both sets lead with the same hero on panel 1 and carry the same objects. Produce numbered `store-01.png` through `store-0P.png` plus `_panorama-preview.png` for inspection.

**Slice with a seam allowance.** The store does not show the first panels edge to edge — the
carousel puts a gap between every pair. Butt-joined panels therefore do *not* reconstruct the
picture on the listing page: everything crossing a boundary is displaced by the width of that gap,
which is why a coin or a face sitting on a seam comes back from review looking broken. `--gutter`
composes the panorama wider than the panels and throws away a strip at each cut, so the store's own
gutter stands in for it. `auto` is ≈100 px at 1320-wide panels and scales with `--size`, so the App
Store and Play sets slice identically. Only pass `--gutter 0` if a specific store surface is known
to show the panels flush.

The compositor also reports, per seam, how busy the picture is exactly where it cuts. Ratios near
1.0 mean the cuts land on calm background. A warning above 1.35× means a subject is being sliced:
slide the crop (`--zoom 1.15 --offset ±0.3`), widen `--gutter`, or regenerate the art with calm
space at that fraction of the width.

Vision-check the stitched preview — it paints the store's gutters in, so it shows what the listing
page shows, gaps and all:

- Adjacent panels form one continuous image in upload order **across the painted gaps**.
- **Panel 1 opens on the protagonist**, large enough to be the first thing the eye lands on and
  recognizable as a character rather than a decorative shape. If the hero is absent, small, or
  upstaged on panel 1, that panel is wrong no matter how good the rest of the strip is.
- Every inlaid object reads as part of the picture: standing on something, shadowed at the contact
  point, lit by the scene, at foreground scale. Anything that looks stuck on gets re-seated
  (`--sprite-light`, `contact=`, a larger `w`) or removed.
- No seam cuts the hero's face, central mechanic, reward, decisive action, or an inlaid game object.
- No letters, fake glyphs, captions, UI, or panel borders appear.
- The mechanic and category are recognizable without generic casino cues.
- At least one object from the shared list is unmistakably present, and it is the same object the
  gameplay frames show.
- The panels are not crowded: a hero and two or three symbols, not a heap.
- The panorama uses casino-grade tension, depth, tactility, and reward focus while remaining
  unmistakably specific to this game's Design DNA.
- Colour is rich and the image is bright enough to hold up at thumbnail size.

The preview is a verification artifact and must not be listed for store upload.

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

Then run the **continuity audit** across both ordered sets and write the result into `STORE_INFO.md`
as a table:

| Shared object | Seen in concept panel | Seen in gameplay frame |
|---|---|---|

Every row must have both columns filled with a specific file name. An empty cell is a blocker:
either inlay the object into the panorama (Phase 2) or surface it in the game and re-capture
(Phases 3–4). Confirm in the same pass that the panels and the gameplay frames share one palette,
one light direction, and one material language, and that neither set looks flat next to the other.

Record the hero row separately, with the fraction of panel 1 it occupies and the compositor's own
`inlay hero …` line. Below half the panel width, or absent from panel 1, is a blocker.

## Phase 10 — store information

Write `$STORE_DIR/STORE_INFO.md` in English with:

- Build timestamp, category, archetype, title, tagline, and dimensions.
- An inventory of both screenshot sets, feature graphic, icons, emblem, and verification-only preview.
- Ordered caption mapping.
- The hero object, its size on panel 1 as a fraction of the panel, and the supporting objects with
  the panels they were seated into.
- The seam allowance used, in pixels, for each set.
- Exactly what branding was applied to the project — icon, emblem, and every background file the
  key art was wired into, with the screens that now use them.
- The continuity audit table.
- Compliance profile, ratings, simulated-gambling answer, disclaimer, odds disclosure, and grep/vision results.
- Exact Google Play and App Store upload order. Emphasize that `_panorama-preview.png` is not uploaded.

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

Report the title/tagline, category/archetype, App Store and Play counts/dimensions, panorama panel range and seam allowance, the hero on panel 1 and the objects seated into the art, gameplay-frame range, feature graphic, icon application status, emblem wiring status, backdrop wiring status (which files, which screens), the continuity audit verdict, compliance verdict, ratings/disclaimer, archive path/size, and SHA-256. State the exact upload order for each store.

## Quality gates

- Preflight tools and fonts are available.
- The shared object list exists in `STORE_BRIEF.md` with 3–5 entries, real asset paths, and the
  hero first.
- At least one valid phone-aspect raw frame exists; the final selection includes active play and a win/reward state.
- Gameplay frames were captured **after** branding and the backdrop were applied.
- Every selected gameplay frame passes the full-viewport gameplay-screen contract; no thumbnail
  field, nested window, core-loop scrolling, disconnected controls, or poor button proportions.
- The ordered set passes the casino-style storefront grammar: mechanic-first tension, depth,
  tactility, outcome focus, and active/reveal/celebration coverage.
- Panel 1 leads with the hero at no less than half the panel width, and the compositor reported it
  as `inlay hero … → panel 1`.
- Every inlaid object is at least a quarter of a panel wide and reads as seated in the scene —
  grounded, shadowed at the contact point, lit by the same light — not pasted onto it.
- No more than five objects are inlaid, and the compositor's crowding warning is unresolved nowhere.
- Panorama, icon, and emblem share one visual world and pass vision review.
- Launcher icons are applied unless `--no-apply` was requested.
- The key art is wired into the game as its background unless `--no-backdrop` was requested, and
  `flutter analyze` is clean afterwards.
- The continuity audit table is complete: every shared object appears in both a concept panel and a
  gameplay frame.
- Panels are sliced with a seam allowance, stitch correctly across the preview's painted gutters in
  both sets, and are text-free.
- No seam warning above 1.35× is left unresolved.
- Colour and brightness hold up at thumbnail size in both sets.
- Showcase captions are readable, correctly spelled, and rendered with full glyph coverage.
- Compliance grep and vision checks pass with no exceptions.
- `check --store appstore` and `check --store play` both pass.
- The ZIP is valid, contains the required files, and has a recorded SHA-256.

## Forbidden

- Changing gameplay logic, state, configuration, balance, or economy. Applying the icon, emblem,
  and key-art backdrop is the only project modification this skill makes.
- Capturing gameplay frames before the branding and backdrop are applied, or reusing frames from
  before this run's branding.
- Shipping concept panels that show objects, characters, or a world the app does not contain.
- Shipping gameplay frames that share nothing visual with the concept panels.
- Butt-joining the panels when the store will put a gutter between them, or leaving a subject
  sitting on a seam because the preview "looks fine" as a continuous image.
- Colour-grading, relighting, or retouching a real gameplay frame instead of fixing the game.
- Drawing fake gameplay, fake values, generated lettering, device frames, or panel separators into model-generated art.
- Compositing a game object into the key art unlit, unscaled, and unshadowed so it reads as a
  sticker, or at a size that makes it decoration rather than part of the composition.
- Opening the listing on anything other than the protagonist: a logo panel, an empty establishing
  shot, or a first panel where the hero is small, cropped out, or upstaged.
- Piling more than five objects into the panorama because they are all "real".
- Generic casino art direction unrelated to the current category and Design DNA.
- Flat utility-app screenshots with no casino-round tension, outcome focus, or premium depth.
- Hiding a weak gameplay layout with aggressive cropping, oversized device chrome, captions,
  concept art, or decorative effects.
- Any real-money promise, currency symbol, banknote, cash/payout language, or financial implication.
- Reusing the 6.9-inch files as the Play set or scaling them instead of recomposing.
- Hiding generation, compliance, verification, or packaging failures.
- Listing `_panorama-preview.png` as an upload asset.
