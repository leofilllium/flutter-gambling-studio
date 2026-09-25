---
name: store-screenshots
description: "Create a store kit with asset-backed x5/x10/x25/x50/x100 multiplier balls, a panorama, real capture slides, feature graphic, icon/emblem and ZIP. Match game assets and topology; preserve runtime backgrounds."
argument-hint: "[--count 8] [--panels 3] [--lead-kind character|object|mechanic] [--character-framing bust|mascot] [--banner-layout free|left-heavy] [--size 1320x2868|play] [--no-play-set] [--frame ios|android|none] [--no-apply] [--no-wire-logo] [--no-captions] [--apply-backdrop]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Context-based store kit

Read `.claude/docs/visual-context.md`, `.claude/docs/game-concept-examples.md`, and the game's
concept, art direction, asset manifest, math config and runtime evidence. Inspect matching
`examples-games/` previews by default. References guide composition; the shipped assets and
mechanics govern identity. Never change a real game to match a preview's topology or palette.

For a character-led kit, the shipped character asset is the canonical player reference in
**every** image-generation call. Supply the original asset file again for a retry or a separate
banner/icon render; never use an earlier generated image as the character reference or edit a
generated image into the next source. The generated scene may establish composition, but it
cannot redefine the character's face, silhouette, costume or colors. If the character has
multiple shipped layers, use the original layers or a lossless assembly of them.

Multiplier balls must look airborne. Several must fly **in front of gameplay** and visibly cover
parts of the board, symbols or outcome area in the marketing scene. None may overlap the visible
player/hero character silhouette, including headwear, face, hands and costume. Gameplay occlusion
is intentional; player occlusion is a placement error. Keep the five ball labels legible. Review art
once at final crop size; use format/dimension checks for exports. Do not run numeric composition
gates or repeat visual audits to optimize scores.

The visible body/background of every multiplier ball must come from an **actual shipped game
asset file**. Choose one suitable ball, coin, token or other round gameplay asset and reuse its
pixels for all five values. Confirm its path in the game's asset registry or `pubspec.yaml`.
Add the inscription to copies of that asset; do not generate a new
ball, ask the image model to redraw the backing, or accept a merely similar-looking orb. Place
the asset-based balls into the marketing scene before slicing it. Their position, rotation,
shadow and motion cues may vary, while the source artwork remains recognizable.

Create local artifacts; do not publish or build release binaries. Apply icon/emblem unless
`--no-apply`. Runtime backgrounds and wiring remain unchanged unless their separate redesign
was explicitly requested. All copy is English unless another game language was requested.

## Outputs

Default N=8 screenshots: P=3 adjacent concept panels sliced from one complete panorama followed by
N−P actual gameplay/meta captures with optional device frames and captions. Produce `store/`
at 1320×2868 and `store-play/` at 1080×1920 independently, not by resizing one set into the other.
Include a dedicated text-free 1024×500 feature graphic: the scene plus one phone on the right
holding a real screenshot, with no title or copy on the left or anywhere else (see Phase 5),
icon masters/platform densities (1024 launcher master, 512×512 Play listing icon, frame-free —
see Phase 3), transparent emblem, `STORE_BRIEF.md`, `STORE_INFO.md`, and ZIP under `project_zip/`.
`--no-play-set` omits Play screenshots. `--panels 0` skips panorama work and uses real captures
for all N screenshots, with the required multiplier balls in a themed showcase background; it
still produces the separate feature graphic. Marketing portrait formats never constrain the
runtime app's full mobile/expanded viewport behavior.

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
- Panel map with anchors and gameplay positions/spans. Any panel, the right two, or all three
  may carry gameplay. There is no required middle field or final reward-only panel.
- Lower-edge object plan: roughly 5–7 large game objects across a three-panel character scene
  when that treatment fits, with sparse coin accents, small edge overlaps, clear silhouettes
  and no supporting surface. Record the game's warm/cool light sources and polished materials.
- For an object/mechanic-led game with no living character in its concept and shipped inventory,
  mark slides 1 and 2 as gameplay-led. Each opening crop, reviewed separately, must show
  recognizable authentic play at a three-quarter/3D angle, either through two readable samples
  or one continuous angled gameplay surface with meaningful play visible in both. Do not
  introduce a person, hand, animal,
  mascot or player silhouette; slide 1 cannot be a decorative object-only scene.
- Actual topology and resolving state. New unspecified classic slots default to 3×3; store
  work preserves the shipped game's dimensions, symbols, ordering and outcome. Record the
  gameplay capture as a visual reference for generation, never as a layer for the panorama.
- The canonical character asset path (if present), the shipped asset used as the backing for
  every multiplier ball, plus source assets used for other visible gameplay objects. Record
  their scene roles. The ball backing must be an actual asset file, not a style reference.
- Required store-art multiplier-ball set for every game: `x5`, `x10`, `x25`, `x50`, and `x100`,
  whether or not those values exist in the game's paytable. These are themed marketing-scene
  objects, not a gameplay state, a payout claim or a reason to change game math. Record which
  values, if any, are actual in-game rewards and keep unsupported values out of real gameplay
  captures, captions, paytable claims and feature-phone UI. Never present the five balls as a
  guaranteed result. Render showcase captions with compositor typography; only the short ball
  inscriptions may be added to the marketing art.
- Multiplier-ball art direction: the exact shipped backing asset path, its original material,
  palette and ornament, plus lighting, target size and placement in the panorama and feature
  scene. Size is judged in the final panel crop, not the wide source image. Aim for
  prominent balls around 35-40% of a portrait panel's width, adjusting for the artwork.
  Record the exact labels separately from the visual treatment so a styled ball never changes
  a game's payout meaning.
  Map each value to a position and flight direction across the full panorama, judging space in
  the final portrait crops. Scatter the five balls across at least two panels with no fixed
  count or label assignment per panel; slide 1 may have none. Place at least two ball bodies
  across the board/mechanic or its symbols so they visibly hide a portion of gameplay in the
  exported marketing panels. Keep every ball outside the player/hero silhouette. Map the same
  behavior in the feature scene and, for `--panels 0`, the themed showcase background wherever
  the marketing scene depicts gameplay. Do not alter authentic captured gameplay in a phone.
- Independent feature layout: `free` by default or justified `left-heavy`; no reserved device zone.
  The feature graphic is text-free: record the chosen capture for its right-side phone, not a
  title or tagline.
- One initial attempt per required scene (panorama, feature scene and any icon), with at most
  one fresh retry for an objective failure in that scene. Both start from the original assets.
  Do not iterate from generated output.

Collect the original character asset and the gameplay sprites that will be visible in the art.
Exclude UI chrome, fonts, backgrounds and store outputs. Preserve originals; convert non-PNG
sources to lossless PNG references only when the image tool needs PNG. If reference slots are
limited, prioritize the original character asset, then the gameplay capture and visible sprites.
Written descriptions and generated previews never replace the character asset.
For the ball backing, choose a shipped round asset such as a ball, coin or token. If it has no
transparent background, cut it out locally without redrawing its body. If no shipped asset can
serve as a recognizable ball backing, report the missing source instead of inventing an orb.

Capture or locate a real active/resolving gameplay frame as reference-only context. Record its
field rectangle and actual state. A symbol-built board is provisional until a real frame exists.
Games without a grid use the actual curve, machine, card or other mechanic surface. Record all
runtime-background files, hashes and selecting code/config references before any edits, including
registered splash/shared backgrounds outside conventional directories. See
[references/runtime-branding.md](references/runtime-branding.md).

## Phase 1 — composition and integrated art

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

Build an art-directed foreground sequence across the lower edge. For a three-panel character-led
scene, start with roughly 5–7 large, recognizable game objects across the **whole panorama**;
small coins may be sparse accents. Adjust the count to the actual game and composition rather
than forcing this number onto a scene that already works, such as an open Zeus composition.
Arrange the main objects deliberately from left to right, cropping some at the camera edge.
Avoid rigid equal spacing and identical scale while preserving clear individual silhouettes;
one object may cover only a small edge of its neighbor. Do not stack objects into a heap, fill
the bottom with many miniature duplicates, or add any supporting surface beneath the foreground
objects: no floor, fabric, tabletop, platform or velvet drape. Use modest size and angle changes
for rhythm. Light the objects with reflected color and edge light, without ground-contact
shadows. A few other game objects may fly higher. Keep the asset-backed multiplier balls visibly
in flight, including when they cross the foreground; none rests on a lower object.

Show all five themed multiplier balls at least once across the prepared panorama's store
panels; when `--panels 0`, include them in the themed background of at least one showcase slide
as well as the clean feature scene. Give each marking a rounded ball or orb as its physical
backing; place the inscription on the ball itself, not as floating typography. Use five copies
of the selected shipped game asset as the physical backings. Preserve its silhouette, material,
color and ornament; resize or rotate copies and add labels, shadows and motion cues locally.
Do not redraw, recolor into a generic bubble, or replace the asset with an AI approximation.
These store-only labeled copies supplement the planned lower-edge objects. Compose them into the
scene before slicing, scattered at irregular heights, depths and flight directions. At least two
must cross in front of the board or mechanic and visibly obscure part of it; do not move them all
above the action to preserve gameplay visibility. They may overlap lower props but must remain
clear of the player/hero silhouette. A ball seated on a surface, clipped inscription or player
overlap needs a local placement correction. Avoid a row, regular grid or tight cluster. Match any
user-supplied size reference.

Plan the full panorama before generation, or the portrait showcase background for `--panels 0`.
A rough layout sketch may indicate panel cuts and subject positions, but it must not contain a
screenshot-shaped opening intended for later fill.
Give the image generator the canonical character asset, actual gameplay capture, relevant shipped
sprites and matching previews as references. Label the original character asset as **identity
authority** and the capture as **context only**: it establishes the real mechanic, field
dimensions, symbol identities, ordering and resolving state. Request a complete, coherent image
in one generation: the game surface itself appears as a scene-native three-quarter/3D view, with
its housing, depth, lighting, foreground interactions and surrounding environment generated
together. Ask the model to leave plausible flight paths for the multiplier balls, but **not** to
draw any multiplier balls or inscriptions. Noncritical board structure may cross seams.

Put this composition requirement in the **first** scene-generation prompt, adapting the details
to the game's actual characters, board and environment:

> One continuous, fully illustrated game panorama. Leave flight paths at varied heights, depths
> and horizontal positions for five balls copied from the shipped ball asset. Several paths must
> cross the board or mechanic in the foreground, so the later balls visibly cover some gameplay.
> Keep all ball paths clear of the player/hero character silhouette. Do not draw balls, orb
> substitutes, multiplier labels or empty circular placeholders. Reproduce the supplied original
> character asset faithfully; do not derive the character from a generated scene.

Include this lighting direction in the first prompt for every game. Use the lower-edge direction
when the scene needs it, preserving an already effective open composition. Adapt both to the
game's real palette and objects:

> Along the lower edge, place about 5–7 large game objects across the full three-panel scene
> in a deliberate left-to-right sequence, with only small edge overlaps and readable silhouettes.
> A few coins may accent the gaps. Crop selected objects at the bottom camera edge. Avoid a pile,
> miniature clutter, rigid equal spacing and identical scale. Do not add any supporting surface
> beneath them: no fabric, floor, tabletop, podium or drape. Give the scene vivid, high-impact
> mobile-game key-art lighting from the game's authentic palette. Separate warm and cool hues,
> add clean specular highlights to polished materials, theme-appropriate rim light on primary
> subjects, and reflected color between nearby objects. Use small star glints selectively and
> localized bloom around real light sources or verified magical effects. Keep shadows rich in
> color, midtones saturated, and a few highlights near white. Keep the background luminous but
> subordinate through softer focus and lower local contrast. Preserve the source asset colors;
> avoid a global color wash, muddy shadows, flat lighting, matte gems and all-over haze. The
> scene should look exciting and premium before compositor grading.

Save the generated scene as `art/keyart-scene.png`. Use Pillow to copy the actual ball asset five
times, add `x5`, `x10`, `x25`, `x50` and `x100` to those copies, then alpha-composite them onto the
scene at the planned positions. Let at least two cover gameplay while none covers the player.
Add local shadow/light and directional motion cues so they look airborne. Save the complete result
as `art/keyart-integrated.png`; this is the source passed to
`triptych`. Apply the same asset-backed procedure to the feature scene and `--panels 0` showcase
background. Do not use `triptych --sprite` or compose a gameplay board from screenshot pieces.
If a label or ball placement is wrong, correct the local overlay once; do not regenerate the
scene for a ball error. If the character drifts from its asset, make at most one fresh scene
attempt with the **original** character asset and gameplay references. Never use the previous
generated scene as the character reference.

Use the available built-in image tool; headless generation follows `generate-png-asset/SKILL.md`
and `tools/gpt_image.py` with prompt files/repeated `--image` inputs. Supply the original character
asset as the first identity reference on every call; use the gameplay capture and previews for
composition. Do not paste, warp or texture-map any screenshot crop, board plate, symbol grid or
other gameplay block into the panorama, either before or after image
generation. Do not generate a background or empty board recess to fill later. The compositor may
grade and slice the finished panorama; it must not assemble its gameplay field. `boardplate` is
retired for this workflow, and `triptych` refuses `--sprite` and `--sprite-dir`. Pass the capture
and shipped sprites directly to image generation as references. Ball overlays are the only
asset-based addition to the finished scene before final slicing; the compositor only grades and
slices that prepared image.

Use the runtime capture to keep the game surface recognizable. The generated marketing scene
may be partly covered by flying balls; authentic gameplay remains visible in the separate real
captures. Check for a pasted screenshot boundary in the single final visual pass.

Render `art/long-banner-scene.png` separately for the horizontal feature graphic with the same
identity and lead kind, then place copies of the same shipped ball asset and save
`art/long-banner-integrated.png`. Full-width action is valid. A left-heavy 3/5–2/5 composition is
optional. The clean source must look finished alone: no device, UI, reserved zone or marketing
words. Do not ask the image model for a title, logo, wordmark, tagline or empty copy space; a
left side left blank for text is a failed banner. Keep actual game objects across the lower edge
in the same shallow, art-directed sequence, with sharp primary subjects.

## Phase 2 — visual review criteria (apply after exports)

After the first full export, inspect one contact sheet showing the final App Store and Play crops,
plus the feature graphic. Compare the character to its original asset, verify that `x5`, `x10`,
`x25`, `x50` and `x100` appear on distinct airborne balls, and check for clipped labels, missing
panels or an obvious pasted screenshot boundary. Compare the ball backings to the selected
shipped asset; a newly invented or AI-redrawn ball body is an error. Confirm at least two ball
bodies visibly cover gameplay and none overlaps the player/hero silhouette. Do not move balls
off the board to clear the action. Check that the lower edge has a deliberate sequence of large,
individually readable objects, without a supporting surface or a heap of tiny props. For a game
without a character, check that no player/mascot was invented. Fix a ball error in its local
overlay; reserve the one fresh generation attempt for a clear scene identity or lighting failure,
using the original assets again. Do not do repeated full-size/thumbnail passes, per-sprite
audits, numeric scoring or subjective regeneration cycles.

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

Select the game's lead kind and export directly from the complete prepared scene. Turn the
numeric art gates off; do not measure hero, lead, gameplay or protected-region boxes. Inspect
actual final crops once in Phase 2. If a label or character is cut by a seam, make one crop
adjustment and re-export. A flying ball covering gameplay is never a reason to adjust the crop.

```bash
"$STORE_PYTHON" tools/store_compose.py triptych --src "$ART_DIR/keyart-integrated.png" \
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
  --bg "$ART_DIR/keyart-integrated.png" --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop soft
```

With panels 0, generate a portrait marketing scene inspired by the existing game background,
then place all five copies of the shipped ball asset into it and save
`art/multiplier-showcase-bg.png`. Use it behind at least one real-capture showcase; keep the
capture and runtime background files unchanged. Compose Play separately.

Feature example:

```bash
"$STORE_PYTHON" tools/store_compose.py banner --keyart "$ART_DIR/long-banner-integrated.png" \
  --out "$STORE_DIR/feature-graphic-1024x500.png" \
  --base-out "$ART_DIR/long-banner-source-1024x500.png" --size 1024x500 --pop soft \
  --lead-kind object --banner-layout free --banner-gate off \
  --shot "$RAW_DIR/03-spin.png" --frame "${DEVICE_FRAME:-ios}"
```

Use the appropriate `--lead-kind` for the game. Keep the original character asset as a direct
identity reference if the banner requires a separate generation call. Review the final banner
with the phone once; do not run focal bounds, gameplay bounds or numeric banner gates.

**The feature graphic is a banner with one phone on the right and no text.** It carries no
title, tagline, logo, wordmark, caption, badge or call to action — not on the left, not over the
scene, not beside the device. The scene fills the frame and the phone sits on the right; the left
is pure illustration with no scrim or copy space. The compositor enforces this: `banner` refuses
`--title`, `--tagline` and `--logo`. The only lettering that may appear is a themed multiplier-ball
inscription added to an asset-backed ball or the game's own UI inside the captured screenshot.
When `--panels 0`, the clean feature scene carries all five multiplier balls. The balls cover
some of the scene's gameplay, stay clear of the player and keep their labels legible. The phone
may cover other parts of the illustration.

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
The Phase 2 review checks the five ball inscriptions once. A missing or altered label needs the
one allowed correction; an unsupported gameplay value does not. Balls in the prepared marketing
scene must cover some gameplay while leaving the player clear. Keep separate real gameplay
captures authentic.

Recheck runtime-background inventory/hashes/wiring: normal result UNCHANGED. If branding changed
Dart, run format/analysis and relevant existing tests, and verify the menu still fits. Compositor
success is not runtime or visual verification.

Write STORE_INFO.md with the original character asset path, the exact shipped ball-backing asset
path, references used for each image call, panel and lower-edge plan, upload order/dimensions/
counts, five store-only ball labels and whether each exists in gameplay, the single visual
verdict for balls covering gameplay while clearing the player, any correction, feature phone
capture and no-text result, background guard and compliance notes. Do not require per-sprite
audit tables, measured bounds, numeric gate results
or repeated visual verdicts.

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
