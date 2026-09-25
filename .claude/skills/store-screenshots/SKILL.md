---
name: store-screenshots
description: "Create a store kit: generate the feature banner first (character on the left), then a complete panorama with character, gameplay and x5/x10/x25/x50/x100 multiplier balls rendered in one image-generation call from the banner and a shipped ball asset as references. Add real capture slides, feature graphic, icon/emblem and ZIP. Match game assets and topology; preserve runtime backgrounds."
argument-hint: "[--count 8] [--panels 3] [--lead-kind character|object|mechanic] [--character-framing bust|mascot] [--banner-layout free|left-heavy] [--size 1320x2868|play] [--no-play-set] [--frame ios|android|none] [--no-apply] [--no-wire-logo] [--no-captions] [--apply-backdrop]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Context-based store kit

Read `.claude/docs/visual-context.md`, `.claude/docs/game-concept-examples.md`, and the game's
concept, art direction, asset manifest, math config and runtime evidence. Inspect matching
`examples-games/` previews by default. References guide composition; the shipped assets and
mechanics govern identity. Never change a real game to match a preview's topology or palette.

**Generation order: banner first, then panorama.** The horizontal feature banner, with the
character on the left, is the first image generated. It establishes the campaign's world:
environment, palette, lighting, board housing, lower-edge band and multiplier-ball look. The
accepted banner is then attached as **world context** to the panorama call (and to the
`--panels 0` showcase background), so the carousel and the feature graphic read as one campaign.

For a character-led kit, the shipped character asset is the canonical player reference in
**every** image-generation call and is always attached first. Supply the original asset file
again for a retry or a separate icon render. The accepted banner is the only generated image a
later call may receive, and only as world context: it is never the character reference, and the
panorama is a new composition, not an edit, outpaint or crop of the banner. The generated scene
may establish pose and composition, but it cannot redefine the character's face, silhouette,
costume or colors. If the character has multiple shipped layers, use the original layers or a
lossless assembly of them.

Multiplier balls must look airborne. Several must fly **in front of gameplay** and visibly cover
parts of the board, symbols or outcome area in the marketing scene. None may overlap the visible
player/hero character silhouette, including headwear, face, hands and costume. Gameplay occlusion
is intentional; player occlusion is a placement error. Keep the five ball labels legible. Review art
once at final crop size; use format/dimension checks for exports. Do not run numeric composition
gates or repeat visual audits to optimize scores.

**The image model generates the multiplier balls and their labels in the same call as the rest
of the scene.** Choose one suitable shipped round asset, such as a ball, coin, token or orb,
confirm its path in the game's asset registry or `pubspec.yaml`, and attach that file to every
scene-generation call as the **multiplier reference**. The model paints the balls from that
reference: same silhouette, material, color and ornament, rendered at scene scale with the scene's
own light, reflections, glow and motion. Write the exact labels `x5`, `x10`, `x25`, `x50` and
`x100` into the prompt so the model letters them onto the balls. Never cut out, copy, paste or
alpha-composite the asset (or any sprite, label, board plate or screenshot crop) into generated
art, and never draw a label with Pillow, the compositor or any other script. The compositor only
grades, slices and frames finished images.

Create local artifacts; do not publish or build release binaries. Apply icon/emblem unless
`--no-apply`. Runtime backgrounds and wiring remain unchanged unless their separate redesign
was explicitly requested. All copy is English unless another game language was requested.

## Outputs

Default N=8 screenshots: P=3 adjacent concept panels sliced from one complete panorama followed by
N−P actual gameplay/meta captures with optional device frames and captions. Produce `store/`
at 1320×2868 and `store-play/` at 1080×1920 independently, not by resizing one set into the other.
Include a dedicated text-free 1024×500 feature graphic: the banner scene plus one phone on the
right holding a real screenshot, with no title or copy on the left or anywhere else (see Phase 5),
icon masters/platform densities (1024 launcher master, 512×512 Play listing icon, frame-free —
see Phase 3), transparent emblem, `STORE_BRIEF.md`, `STORE_INFO.md`, and ZIP under `project_zip/`.
`--no-play-set` omits Play screenshots. `--panels 0` skips panorama work and uses real captures
for all N screenshots, with the required multiplier balls in a themed showcase background; it
still generates the banner first and produces the feature graphic. Marketing portrait formats
never constrain the runtime app's full mobile/expanded viewport behavior.

## Phase 0 — context and preflight

Select and verify an existing interpreter before installing dependencies. A missing import in
system Python does not mean the project's virtual environment is missing that package. Honor
an explicit `STORE_PYTHON` executable path; otherwise probe the active environment, project
`.venv`, and `python3` in that order. Keep the selected absolute path for subsequent tool calls
(including separate shells); do not assume a previous shell's activation persists.

```bash
if [[ -z "${STORE_PYTHON:-}" ]]; then
  for store_candidate in "${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}" "$PWD/.venv/bin/python" python3; do
    [[ -n "$store_candidate" ]] || continue
    if "$store_candidate" -c 'import PIL, numpy' >/dev/null 2>&1; then
      STORE_PYTHON=$("$store_candidate" -c 'import sys; print(sys.executable)')
      break
    fi
  done
fi
[[ -n "${STORE_PYTHON:-}" ]] || {
  echo "No probed interpreter imports Pillow and numpy. Set up a project environment and rerun preflight."
  exit 1
}
"$STORE_PYTHON" -c 'import sys, PIL, numpy; print(sys.executable); print("Pillow", PIL.__version__, "numpy", numpy.__version__)' || exit 1
```

If no existing environment passes, use the project's dependency setup and install into the
chosen environment with its own `-m pip`; avoid a bare `pip` that may target another Python.
A failed explicit `STORE_PYTHON` stops preflight so the chosen interpreter can be corrected.
Use `"$STORE_PYTHON"` for the compositor and other Python tools in this runbook.

Require a real Flutter game, Pillow/numpy, the image-generation path, compositor and capture
tools. Read `"$STORE_PYTHON" tools/store_compose.py --help` and the relevant subcommand help.
Runbook options such as count, board, hero, no-apply and apply-backdrop govern orchestration;
do not blindly pass them to compositor subcommands. Initialize:

```bash
PROJECT_NAME=$(awk '/^name:/{print $2; exit}' pubspec.yaml)
TS=$(date +%Y%m%d-%H%M%S)
STORE_ROOT=project_zip
STORE_DIR="$STORE_ROOT/$PROJECT_NAME-store-$TS"
ART_DIR="$STORE_DIR/art"
RAW_DIR="$STORE_DIR/raw"
OUT_DIR="$STORE_DIR/store"
PLAY_DIR="$STORE_DIR/store-play"
mkdir -p "$ART_DIR" "$RAW_DIR" "$OUT_DIR" "$PLAY_DIR"
```

Write `STORE_BRIEF.md` before any generation call:

- Category/model, title, virtual currency, theme, source palette/materials/light and fonts.
- `lead_kind: character | object | mechanic`, exact subject and in-game role. A chicken is a
  character; a crown/coin/board is not. No invented mascot or character-only opening for objects.
- Inspected references, borrowed traits and original adaptations.
- Banner plan: lead on the left, gameplay placement, lower-edge band, which multiplier labels
  appear in it and where, and what continues under the phone on the right.
- Panel map with anchors and gameplay positions/spans. Any panel, the right two, or all three
  may carry gameplay. There is no required middle field or final reward-only panel. Note where
  the character's pose, crop or panel differs from the banner.
- Lower-edge plan (see Phase 1): the game's own objects chosen for the close-up foreground band,
  their left-to-right order, which ones cross seams, and the currency used for the coin layer.
  Record the game's warm/cool light sources and polished materials.
- For an object/mechanic-led game with no living character in its concept and shipped inventory,
  mark slides 1 and 2 as gameplay-led. Each opening crop, reviewed separately, must show
  recognizable authentic play at a three-quarter/3D angle, either through two readable samples
  or one continuous angled gameplay surface with meaningful play visible in both. Do not
  introduce a person, hand, animal,
  mascot or player silhouette; slide 1 cannot be a decorative object-only scene.
- Actual topology and resolving state. New unspecified classic slots default to 3×3; store
  work preserves the shipped game's dimensions, symbols, ordering and outcome. Record the
  gameplay capture as a visual reference for generation, never as a layer for the panorama.
- The canonical character asset path (if present), the shipped asset attached as the
  multiplier reference, plus source assets used for other visible gameplay objects. Record
  their scene roles. The multiplier reference must be an actual asset file.
- Required store-art multiplier-ball set for every game: `x5`, `x10`, `x25`, `x50`, and `x100`,
  whether or not those values exist in the game's paytable. These are themed marketing-scene
  objects, not a gameplay state, a payout claim or a reason to change game math. Record which
  values, if any, are actual in-game rewards and keep unsupported values out of real gameplay
  captures, captions, paytable claims and feature-phone UI. Never present the five balls as a
  guaranteed result. Showcase captions on real-capture slides use compositor typography; the
  ball inscriptions are generated by the image model from the prompt, and nothing letters the
  generated art afterward.
- Multiplier-ball art direction: the multiplier reference path, its original material, palette
  and ornament, the label style (display face, color, outline), glow/sparkle treatment, lighting,
  target size and placement in the banner, panorama and any showcase background. Size is judged
  in the final panel crop, not the wide source image. Aim for prominent balls around 35-40% of a
  portrait panel's width, adjusting for the artwork.
  Record the exact labels separately from the visual treatment so a styled ball never changes
  a game's payout meaning.
  Map each value to a position and flight direction across the full panorama, judging space in
  the final portrait crops. Scatter the five balls across at least two panels with no fixed
  count or label assignment per panel; slide 1 may have none. Place at least two ball bodies
  across the board/mechanic or its symbols so they visibly hide a portion of gameplay in the
  exported marketing panels. Keep every ball outside the player/hero silhouette. Map the same
  behavior in the banner and, for `--panels 0`, the themed showcase background wherever the
  marketing scene depicts gameplay. Do not alter authentic captured gameplay in a phone.
- Independent feature layout: `free` by default or justified `left-heavy`; no reserved device zone.
  The feature graphic is text-free: record the chosen capture for its right-side phone, not a
  title or tagline.
- One initial attempt per required scene (banner, panorama, any `--panels 0` showcase background
  and any icon), with at most one fresh retry for an objective failure in that scene. Retries
  restart from the original assets, plus the accepted banner for scenes generated after it. Do not
  iterate from a rejected output. If the banner is retried, later scenes use the accepted one.

Collect the original character asset and the gameplay sprites that will be visible in the art.
Exclude UI chrome, fonts, backgrounds and store outputs. Preserve originals; convert non-PNG
sources to lossless PNG references only when the image tool needs PNG. If reference slots are
limited, prioritize the original character asset, then the accepted banner (for later scenes),
the multiplier reference, the gameplay capture and visible sprites.
Written descriptions and generated previews never replace the character asset.
For the multiplier reference, choose a shipped round asset such as a ball, coin, orb or token.
If it sits on an opaque background, a local cutout may give the model a cleaner reference; that
cutout is only an input to generation and never enters the art. If no shipped asset can serve
as a recognizable ball reference, report the missing source instead of inventing an orb.

Capture or locate a real active/resolving gameplay frame as reference-only context. Record its
field rectangle and actual state. A symbol-built board is provisional until a real frame exists.
Games without a grid use the actual curve, machine, card or other mechanic surface. Record all
runtime-background files, hashes and selecting code/config references before any edits, including
registered splash/shared backgrounds outside conventional directories. See
[references/runtime-branding.md](references/runtime-branding.md).

## Phase 1 — banner first, then the complete panorama

### Composition rules shared by every scene

Choose the panorama aspect from panel count and target geometry. Character-led Zeus/Joker/chicken
games default to a large real character on panel 1; humanoids use a waist-up crop and animals a
species-appropriate crop. Protect the complete head/headwear with 2% top headroom and attached
forms from the first seam. Use `--character-framing bust` for humanoids and `mascot` for a
compact chicken/animal. Mascot mode uses prominence by area rather than humanoid height; it
still protects the head, first-panel placement and attached silhouette. Left/bottom crops are
allowed for a bust; preserve the mascot's recognizable form. Joker is a mischievous, slightly vicious
playful trickster, not an elegant courtier or horror figure. Object/mechanic scenes have no empty
character berth and no anatomy constraints. Keep a strong game anchor in every panel; a continuous
board can anchor several. Flying multiplier balls must cover part of the board or mechanic in
marketing art.
When the shipped game has no living character, its first two carousel slides must instead be
gameplay-led: present the real board or mechanic at a readable three-quarter/3D angle in each crop,
or span one continuous angled surface across both with meaningful gameplay visible in both. Never
add a human, hand, animal, mascot or player silhouette to supply drama. The object lead may frame
the action, but it cannot replace gameplay in slide 1.

Give the image generator the canonical character asset, actual gameplay capture, relevant shipped
sprites, the multiplier reference and matching previews. Label the original character asset as
**identity authority**, the multiplier reference as the **ball model**, and the capture as
**context only**: it establishes the real mechanic, field dimensions, symbol identities, ordering
and resolving state. Request a complete, coherent image in one generation: the game surface
itself appears as a scene-native three-quarter/3D view, with its housing, depth, lighting,
foreground band, labelled multiplier balls and surrounding environment generated together.
Noncritical board structure may cross seams. A rough layout sketch may indicate panel cuts and
subject positions, but it must not contain a screenshot-shaped opening intended for later fill.
Do not generate a background, empty board recess or blank ball placeholder to fill later.

**Lower edge.** Frame the bottom of the scene like close-up casino key art: the game's own
symbols and objects rendered very large, near the camera, across the full width. For a
three-panel scene use roughly 5–7 hero objects, each around a third to half of a panel wide,
overlapping one another in depth, cropped by the bottom edge and at some seams, and occupying
about the lower quarter to third of the image. Beneath and between them, a continuous glittering
layer of the game's gold coins (or its own currency) runs the whole width, so the band reads as
a treasure spill rather than a row of cutouts. The coins are game objects, not a surface: no
floor, fabric, tabletop, podium, platform or velvet drape. Vary scale and angle for rhythm; keep
each hero object's silhouette readable; do not shrink it into miniature clutter. Light the band
with the scene's warm and cool sources: specular highlights, rim light and reflected color. A few
other game objects may fly higher. The multiplier balls stay visibly in flight, including when
they cross the foreground; none rests on a lower object.

**Multiplier balls.** Show all five labelled balls at least once across the panorama's store
panels; when `--panels 0`, include them in the themed showcase background as well as the banner.
Each ball is the multiplier reference re-rendered by the model: keep its silhouette, material,
color and ornament recognizable while the scene's lighting shapes it, with a specular highlight,
rim light in the scene's accent color, reflected color from neighbors, a halo, sparkle ring or
energy glow drawn from the game's own FX vocabulary, and a short motion trail. The label is the
dominant feature on the ball face: short chunky display numerals filling roughly 60–70% of the
ball's width, in the game's warm display color (gold/yellow in most casino themes) with a dark
outline, an inner highlight and a slight 3D bevel, following the ball's curvature. A flat
sticker look, a thin or small label, an unlit disc and a ball that looks pasted over the scene
are the failures this rule prevents. Scatter the balls at irregular heights, depths and flight
directions. At least two must cross in front of the board or mechanic and visibly obscure part of
it; do not move them all above the action to preserve gameplay visibility. They may overlap lower
props but must remain clear of the player/hero silhouette. Avoid a row, regular grid or tight
cluster. Match any user-supplied size reference.

### 1a — Banner (the first generation call)

Generate `art/long-banner.png` before anything else. For a character-led game the character
stands large on the left; object/mechanic leads put the lead object or the angled gameplay
surface there instead, with no invented character. The mechanic sits at a three-quarter/3D angle
beside the lead, the environment runs edge to edge, and the lower-edge band crosses the full
width. The right third continues the scene without a face, decisive symbol or ball label, because
`banner` seats the phone there (centered at 82% of the width, about a third of it wide). That area
is not an empty reserved zone: background, housing and foreground run through it. Include at least
two labelled multiplier balls (all five when `--panels 0`), clear of the character and the phone
area. No title, logo, wordmark, tagline, device, UI or copy space; a left side left blank for text
is a failed banner. The banner must look finished alone.

Attach, in order: the original character asset (identity authority), the multiplier reference
(ball model), the gameplay capture (context only), visible shipped sprites, matching previews.
When the tool takes custom sizes, `3840x1872` matches the 1024×500 delivery aspect.

### 1b — Panorama (banner as world context)

Generate `art/panorama.png` as a new composition for the panel geometry. The accepted banner is
attached as **world context**, not as a source to extend: the panorama inherits its environment,
palette, lighting, board housing, lower-edge treatment and ball look. The character may take a
different pose, expression, crop or panel than in the banner; identity still comes only from the
original asset. One call renders everything: character, scene-native gameplay, the lower-edge
band, all five labelled balls in flight, and the environment.

Attach, in order: the original character asset (identity authority), the accepted banner (world
context — not a character reference), the multiplier reference (ball model), the gameplay
capture (context only), visible shipped sprites, matching previews. When the tool takes custom
sizes, `3456x2384` (about 1.45:1) covers three 1320×2868 panels plus the default hidden seam
allowance.

For `--panels 0`, generate the portrait `art/multiplier-showcase-bg.png` the same way, with the
banner as world context, all five labelled balls in the scene and the existing game background
as inspiration. Keep runtime background files unchanged.

### First-prompt requirements

Put this composition requirement in the **first** prompt of the panorama call, adapting the
details to the game's actual characters, board, colors and environment. Adapt the same text to
the banner (character left, at least two balls, the right third continuing the scene) and to any
showcase background:

> One continuous, fully illustrated game panorama set in the world of the attached banner:
> same environment, palette, lighting and board housing, in a new composition. Reproduce the
> supplied original character asset faithfully; the banner is world context, not the character
> reference. Paint five multiplier balls modeled on the attached ball asset, flying at varied
> heights, depths and horizontal positions. Letter each ball on its face with exactly one of
> these inscriptions, each used once: "x5", "x10", "x25", "x50", "x100". Make every label big,
> chunky 3D display numerals in [warm display color] with a dark outline and inner highlight,
> filling most of the ball face and following its curve. Light the balls with the scene: glossy
> specular highlights, [accent] rim light, a glowing [halo/sparkle ring/energy flare from the
> game's FX], and a short motion trail. At least two balls fly in front of the board and cover
> part of it; keep every ball clear of the character's silhouette. No other text, title, logo or
> UI anywhere in the image.

Include this lower-edge and lighting direction in the first prompt of every scene, adapting it to
the game's real palette and objects:

> Across the whole lower edge, place about 5–7 of the game's own objects very large and close to
> the camera: [ordered list], overlapping each other in depth and cropped by the bottom edge, filling
> about the lower quarter to third of the image. Under and between them, a continuous glittering
> layer of gold coins runs the full width. No floor, fabric, tabletop, podium or drape, and no
> miniature clutter. Give the scene vivid, high-impact mobile-game key-art lighting from the game's
> authentic palette. Separate warm and cool hues, add clean specular highlights to polished
> materials, theme-appropriate rim light on primary subjects, and reflected color between nearby
> objects. Use small star glints selectively and localized bloom around real light sources or
> verified magical effects. Keep shadows rich in color, midtones saturated, and a few highlights
> near white. Keep the background luminous but subordinate through softer focus and lower local
> contrast. Preserve the source asset colors; avoid a global color wash, muddy shadows, flat
> lighting, matte gems and all-over haze. The scene should look exciting and premium before
> compositor grading.

Use the available built-in image tool; headless generation follows `generate-png-asset/SKILL.md`
and `tools/gpt_image.py edit` with a prompt file and repeated `--image` inputs in the order above.
The compositor may grade and slice the finished panorama; it must not assemble its gameplay
field or add anything to it. `boardplate` is retired for this workflow, and `triptych` refuses
`--sprite` and `--sprite-dir`.

Use the runtime capture to keep the game surface recognizable. The generated marketing scene
may be partly covered by flying balls; authentic gameplay remains visible in the separate real
captures. Check for a pasted screenshot boundary in the single final visual pass.

### Correcting a generated scene

Read every inscription at final crop size. A misspelled, missing, duplicated or extra label, a ball
on the character, a ball resting on a lower object or character drift from its asset is an
objective failure: use the scene's one fresh retry with the same references. If exactly one
inscription is still wrong after the retry, make at most one image-tool edit of the selected
scene that changes only that inscription, naming the exact label in the prompt and attaching the
original character asset first. Never letter it with a script. If that edit alters anything else,
keep the unedited scene and record the defect in `STORE_INFO.md`. A label cut by a seam is fixed
by the crop (Phase 4), not by regeneration.

## Phase 2 — visual review criteria (apply after exports)

After the first full export, inspect one contact sheet showing the final App Store and Play crops,
plus the feature graphic. Compare the character to its original asset, verify that `x5`, `x10`,
`x25`, `x50` and `x100` each appear once, spelled exactly, on distinct airborne balls, and check
for clipped labels, missing panels or an obvious pasted screenshot boundary. Check that the balls
read as the multiplier reference (silhouette, material, color, ornament) painted into the scene:
lit by it, with glow and motion, labels bold and dominant. A flat, pasted-looking or small-label
ball is an error. Confirm at least two ball bodies visibly cover gameplay and none overlaps the
player/hero silhouette. Do not move balls off the board to clear the action. Check that the
panorama visibly shares the banner's world, and that the lower edge is a close-up band of large,
readable game objects over a continuous coin layer, without a floor, drape or heap of tiny props.
For a game without a character, check that no player/mascot was invented. Apply the correction
policy from Phase 1; do not do repeated full-size/thumbnail passes, per-sprite audits, numeric
scoring or subjective regeneration cycles.

Judge lighting in the generated source, before compositor grading. It should feel vivid and
celebratory while retaining the game's authentic colors. Look for clean highlights, selected
glints, local bloom and color-rich shadows; reject a flat global cast or uniformly dull scene.
Avoid clipped highlights, crushed shadows, blanket saturation and bloom that washes out faces,
symbols or text. The compositor should preserve the source look; make at most one visible
exposure adjustment and do not tune numeric palette or foreground metrics. Keep runtime assets
untouched.

## Phase 3 — branding and current captures

Follow [references/runtime-branding.md](references/runtime-branding.md) for icon/emblem application,
platform-density checks and background guards. Honor no-apply/no-wire-logo. An explicit separate
runtime redesign is required for apply-backdrop and `--confirm-game-background-replacement`;
the flag alone does not provide authorization. Preserve all backgrounds and wiring by default.

Capture menu, active play, peak tension, win/reward and a useful meta state after branding using
`/emulator-test` or `tools/web_verify.mjs` against the actual running URL. A typical capture uses
`--size 390x844 --dpr 3 --budget 180 --quick`. Reuse frames only if current and authentic. Reject
blank, duplicate, loading, error, overflow and fabricated states; parse runtime exception logs.
Apply `.claude/docs/gameplay-screen-contract.md`: never use cropping or device chrome to conceal
weak gameplay. If the actual state changed, correct integration/feature art and re-export;
an unchanged matching capture does not justify another generation call.

## Phase 4 — final exports

Select the game's lead kind and export directly from the complete generated panorama. Turn the
numeric art gates off; do not measure hero, lead, gameplay or protected-region boxes. Inspect
actual final crops once in Phase 2. If a label or character is cut by a seam, make one crop
adjustment and re-export. A flying ball covering gameplay is never a reason to adjust the crop.

```bash
"$STORE_PYTHON" tools/store_compose.py triptych --src "$ART_DIR/panorama.png" \
  --out "$OUT_DIR" --panels 3 --size 1320x2868 --pop soft --seam-snap off \
  --lead-kind mechanic --art-gate off
```

Use `--lead-kind character` or `object` as applicable. Export Play separately with `--size play`
from the same complete source; do not resize the App Store panels. The compositor's default
gutter remains suitable for a carousel. A label cut by the gutter needs one crop correction;
at least two balls must still cover gameplay, and no ball may cover the player.

## Phase 5 — showcases and feature graphic

Use `showcase` on real captures with the game's fonts/type mood and secondary device framing.
Typical Joker typography is bold/playful, not automatic elegance. Captions describe actual play.
Resolve filenames and words from this game's inventory; honor frame/no-captions/language/count.

```bash
"$STORE_PYTHON" tools/store_compose.py showcase --shot "$RAW_DIR/03-spin.png" \
  --bg "$ART_DIR/panorama.png" --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop soft
```

With panels 0, use `art/multiplier-showcase-bg.png` (Phase 1b) behind at least one real-capture
showcase; keep the capture and runtime background files unchanged. Compose Play separately.

Feature example:

```bash
"$STORE_PYTHON" tools/store_compose.py banner --keyart "$ART_DIR/long-banner.png" \
  --out "$STORE_DIR/feature-graphic-1024x500.png" \
  --base-out "$ART_DIR/long-banner-source-1024x500.png" --size 1024x500 --pop soft \
  --lead-kind character --banner-layout free --banner-gate off \
  --shot "$RAW_DIR/03-spin.png" --frame "${DEVICE_FRAME:-ios}"
```

Use the appropriate `--lead-kind` for the game. Review the final banner with the phone once; do
not run focal bounds, gameplay bounds or numeric banner gates.

**The feature graphic is a banner with one phone on the right and no text.** It carries no
title, tagline, logo, wordmark, caption, badge or call to action — not on the left, not over the
scene, not beside the device. The scene fills the frame and the phone sits on the right; the left
is pure illustration with no scrim or copy space. The compositor enforces this: `banner` refuses
`--title`, `--tagline` and `--logo`. The only lettering that may appear is a multiplier-ball
inscription generated by the image model or the game's own UI inside the captured screenshot.
When `--panels 0`, the banner carries all five multiplier balls. The balls cover some of the
scene's gameplay, stay clear of the player and the phone, and keep their labels legible. The
phone may cover other parts of the illustration.

**The feature graphic always carries one device.** `--shot` is required: pick the single
strongest current capture (active play or a win moment, not the menu) and pass it so the compositor
inlays a real phone mockup with that authentic screenshot on the right side of the 1024×500 canvas
inside Play's safe area — a full scene occupies most of the frame and one device sits to the right,
never a bare screenshot rectangle (`--frame none` is refused) or a pasted capture with no scene
around it. `--base-out` keeps the clean device-free scene; `--out` is
the one shipped with the phone composited in. Do not ship a feature graphic with no device.

## Phase 6 — verify, report and package

Run `store_compose.py check --dir "$OUT_DIR" --store appstore` and, when enabled, the equivalent
Play check. Verify RGB PNGs, dimensions, no store-screenshot transparency, file sizes, aspect,
numbering/counts and feature dimensions. In the single visual review from Phase 2, confirm the
feature graphic has no title, tagline, logo or other copy and exactly one framed phone on the
right; do not repeat the image review here.
Read responsible-gaming.md; check captions, metadata and art for currency symbols, misleading
multipliers and payout promises. Metadata retains the virtual-currency disclaimer, simulated
gambling declaration, rating and applicable odds disclosure. Interpret text matches in context.
The Phase 2 review checks the five ball inscriptions once. A missing or altered label follows the
Phase 1 correction policy; an unsupported gameplay value does not need one. Balls in the
generated marketing scene must cover some gameplay while leaving the player clear. Keep separate
real gameplay captures authentic.

Recheck runtime-background inventory/hashes/wiring: normal result UNCHANGED. If branding changed
Dart, run format/analysis and relevant existing tests, and verify the menu still fits. Compositor
success is not runtime or visual verification.

Write STORE_INFO.md with the original character asset path, the multiplier reference asset path,
the generation order and the references attached to each image call (the banner as world context
for the panorama), panel and lower-edge plan, upload order/dimensions/counts, five store-only ball
labels and whether each exists in gameplay, the single visual verdict for balls covering gameplay
while clearing the player, any retry or inscription correction, feature phone capture and no-text
result, background guard and compliance notes. Do not require per-sprite audit tables, measured
bounds, numeric gate results or repeated visual verdicts.

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x '*.DS_Store')
unzip -t "$ARCHIVE_PATH"
shasum -a 256 "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
```

Verify ZIP contents: ordered screenshots, feature graphic and branding. Final answer links
ZIP/report, gives composition/counts and actual limitations. Record reusable failures or faster
methods for a separate `/auto-learn` run; do not add that workflow to store-kit delivery.
