---
name: store-screenshots
description: "Create a store kit with theme-matched x5/x10/x25/x50/x100 multiplier balls, a one-scene panorama, real capture slides, feature graphic, icon/emblem and ZIP. Match game assets and topology; preserve runtime backgrounds."
argument-hint: "[--count 8] [--panels 3] [--lead-kind character|object|mechanic] [--character-framing bust|mascot] [--banner-layout free|left-heavy] [--size 1320x2868|play] [--no-play-set] [--frame ios|android|none] [--no-apply] [--no-wire-logo] [--no-captions] [--apply-backdrop]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Context-based store kit

Read `.claude/docs/visual-context.md`, `.claude/docs/game-concept-examples.md`, and the game's
concept, art direction, asset manifest, math config and runtime evidence. Inspect matching
`examples-games/` previews by default. References guide composition; the shipped assets and
mechanics govern identity. Never change a real game to match a preview's topology or palette.

Create local artifacts; do not publish or build release binaries. Apply icon/emblem unless
`--no-apply`. Runtime backgrounds and wiring remain unchanged unless their separate redesign
was explicitly requested. All copy is English unless another game language was requested.

## Outputs

Default N=8 screenshots: P=3 adjacent concept panels sliced from one fully generated panorama followed by
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
- For an object/mechanic-led game with no living character in its concept and shipped inventory,
  mark slides 1 and 2 as gameplay-led. Each opening crop, reviewed separately, must show
  recognizable authentic play at a three-quarter/3D angle, either through two readable samples
  or one continuous angled gameplay surface with meaningful play visible in both. Do not
  introduce a person, hand, animal,
  mascot or player silhouette; slide 1 cannot be a decorative object-only scene.
- Actual topology and resolving state. New unspecified classic slots default to 3×3; store
  work preserves the shipped game's dimensions, symbols, ordering and outcome. Record the
  gameplay capture as a visual reference for generation, never as a layer for the panorama.
- Complete sprite inventory, source-to-PNG mapping, scene role and in-app evidence per file.
- List the five store-only balls separately from shipped sprites; they need theme references,
  not in-app asset evidence.
- Required store-art multiplier-ball set for every game: `x5`, `x10`, `x25`, `x50`, and `x100`,
  whether or not those values exist in the game's paytable. These are themed marketing-scene
  objects, not a gameplay state, a payout claim or a reason to change game math. Record which
  values, if any, are actual in-game rewards and keep unsupported values out of real gameplay
  captures, captions, paytable claims and feature-phone UI. Never present the five balls as a
  guaranteed result. Render showcase captions with compositor typography; only the short ball
  inscriptions may be generated into the marketing art.
- Multiplier-ball art direction: which shipped object or visual motif inspires the ball, plus
  its material, palette, ornament, lighting, target size and placement in the panorama and
  feature scene. Size is judged in the final panel crop, not the wide source image.
  Record the exact labels separately from the visual treatment so a styled ball never changes
  a game's payout meaning.
  Map each value to a final panorama panel and an airborne zone, or to a showcase background
  when `--panels 0`. For a character-led three-panel scene, plan the balls chiefly around
  gameplay in panels 2 and 3; use panel 1 only where the character stays clear. For an
  object/mechanic lead, distribute them around the actual play surface wherever it spans.
  Reserve room for all five at the intended size before generating the scene.
- Independent feature layout: `free` by default or justified `left-heavy`; no reserved device zone.
  The feature graphic is text-free: record the chosen capture for its right-side phone, not a
  title or tagline.
- Generation budget and recovery limit inherited from the asset manifest; no unlimited retries.

Inventory all shipped gameplay sprite roots from the registry/pubspec, including secondary and
alternate states. Exclude UI chrome, fonts, backgrounds and store outputs. Preserve originals;
convert non-PNG sources to standalone lossless PNG references and verify real alpha using
`tools/cutout.py --check`. Review complete silhouettes, identity and source-color separation at
full size and 64px. Actual sprite files are identity references, not just written descriptions.
Use staged integration when reference count exceeds the transport's limit; audit every file.

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
board can anchor several. Multiple boards are valid only when their real states remain readable.
When the shipped game has no living character, its first two carousel slides must instead be
gameplay-led: present the real board or mechanic at a readable three-quarter/3D angle in each crop,
or span one continuous angled surface across both with meaningful gameplay visible in both. Never
add a human, hand, animal, mascot or player silhouette to supply drama. The object lead may frame
the action, but it cannot replace gameplay in slide 1.

Build the lower edge from an irregular, cropped spill of actual game objects across its full
width: vary scale, rotation, height, overlap, contact shadows and depth so it reads as a
tumbled heap rather than a tidy row or one isolated pile. Add recognizable flying/falling
objects above it. Keep primary subjects sharp, source-colored and dominant over a broad
smooth subordinate far plane. Generic stage furniture or particles cannot replace the spill.

Show all five themed multiplier balls at least once across the generated panorama's store
panels; when `--panels 0`, include them in the themed background of at least one showcase slide
as well as the clean feature scene. Give each marking a rounded ball or orb as its physical
backing; place the inscription on the ball itself, not as floating typography. Derive the ball's
material, colour, ornament, edge treatment and light from the game's Design DNA and actual
objects. A Plinko ball, jester bead, jeweled sphere or mechanical capsule should feel native to
its game. Avoid reusing a generic bubble across store kits. These store-only balls supplement
the required spill of actual game objects: keep them visibly airborne above it, at different
heights and horizontal positions with clear space between neighboring balls. Do not collect
them in the lower heap, along one baseline, or in a tight cluster. In a character-led triptych,
favor panels 2 and 3 around the action; panel 1 is optional only if the character's face,
headwear, hands and silhouette remain clear. For other layouts, follow the actual mechanic.
Make each ball a prominent secondary subject, not a small coin or badge. For a character-led
slot panorama, aim for a diameter around 1.3–1.5 visible reel-cell widths in the final panel;
adapt that proportion to the primary repeated object in other mechanics. If the user supplies
an approved visual example, match its scale and apply any requested size adjustment relative
to that example. Leave obvious breathing room between balls, aiming for at least half a ball
diameter of clear space between their outlines. Vary depth and scale modestly while keeping
each number readable at store thumbnail size. Compose enough room for these balls from the
start; enlarging a crowded finished panorama can hide symbols, cross seams or clip outer edges.
Do not let the balls obscure the real board, decisive outcome or protected seams.

Plan the full panorama before generation, or the portrait showcase background for `--panels 0`.
A rough layout sketch may indicate panel cuts and subject positions, but it must not contain a
screenshot-shaped opening intended for later fill.
Give the image generator the actual gameplay capture, shipped sprite assets and matching previews
as references. Label the capture as **context only**: it establishes the real mechanic, field
dimensions, symbol identities, ordering and resolving state. Request a complete, coherent image
in one generation: the game surface itself appears as a scene-native three-quarter/3D view, with
its housing, depth, lighting, foreground interactions and surrounding environment generated
together. The panorama must already look finished before the compositor slices it. Noncritical
board structure may cross seams.

In the generation prompt, identify five separate game-native balls with the exact inscriptions
`x5`, `x10`, `x25`, `x50` and `x100`; give their distinct airborne positions, spacing
from each other and separation from the lower real-object heap, plus their store-only visual role.
Treat the balls as physical parts of the scene, never floating labels or UI overlays. Check the
model's rendered digits before any export and correct illegible or changed values within the
bounded art recovery budget.

Use the available built-in image tool; headless generation follows `generate-png-asset/SKILL.md`
and `tools/gpt_image.py` with prompt files/repeated `--image` inputs. Supply the actual resolving
frame, shipped sprites and matching previews directly as references where the tool supports them.
Label which references govern identity and which govern composition. Save the single generated
scene as `art/keyart-integrated.png`. Do not paste, warp or texture-map any screenshot crop,
board plate, symbol grid or other gameplay block into the panorama, either before or after image
generation. Do not generate a background or empty board recess to fill later. The compositor may
grade and slice the finished panorama; it must not assemble its gameplay field.

Count rows, columns, paylines, buckets and symbols against the runtime capture and verify the
decisive outcome. If the model changes topology or state, reject the image and use the bounded
generation/edit budget to correct the whole coherent scene with the capture as reference. If a
faithful scene still cannot be generated, report a blocker; do not substitute a composited field.

When the brief calls for angled or environment-integrated gameplay, a perspective transform alone
is not evidence of integration. The generated field must visibly satisfy all three contextual-embedding
groups: **structural reception** (a recessed housing, altar or console with readable thickness,
edging and plane-matched perspective); **photometric contact** (contact shadow plus local colour
spill, light wrap or reflection consistent with the scene's key light); and **spatial interaction**
(a foreground or atmospheric element crossing the housing edge without hiding decisive cells). A
rectangular drop shadow, glow or decorative platform around a screenshot-like rectangle does
not satisfy this contract. Review these cues at final panel size as well as in the continuous
panorama. Recount the final exported topology and recheck the decisive outcome after all crops and
seam adjustments.

Render `art/long-banner-integrated.png` separately for the horizontal feature graphic with the
same identity and lead kind. Full-width action is valid. A left-heavy 3/5–2/5 composition is
optional. The clean source must look finished alone: no device, UI, reserved zone or marketing
words. Do not ask the image model for a title, logo, wordmark, tagline or empty copy space; a
left side left blank for text is a failed banner. Keep actual game objects across the lower edge
and sharp primary subjects.

## Phase 2 — identity and critical-region review

Compare every sprite and the integrated field with the actual runtime frame. Record source,
reference, visible panels, scene role, identity and runtime evidence. Missing sprites, wrong
topology/state, floating stickers, unplanned lettering, wrong multiplier labels or unreadable
primary forms require a bounded correction. Reject any visible capture boundary, preserved
screenshot pixels, flat UI crop, empty placeholder or pasted board plate. Review the generation
inputs and edits to confirm the complete scene was generated together. If budget runs out,
report the blocker instead of shipping a draft.

Review both the assembled panorama and gapped carousel. Boards may span seams; tight regions
around faces, decisive symbols, multiplier inscriptions and bucket/reveal outcomes must survive
the gaps. Protect those details, not the entire board housing. Every crop still needs readable
game content. Geometry metrics cannot identify a Joker, read lettering or verify a payline:
visual comparison is mandatory.
Inspect each multiplier ball at full and thumbnail size for exact lettering, a distinct readable
backing, theme-consistent materials and lighting, the planned prominent size relative to the
game's symbols or approved reference, and no overlap with decisive gameplay. Check
that the balls read as separate flying objects above the irregular lower spill, with varied
height and lateral position instead of a bottom row or cluster. Inspect the final App Store
and Play carousel crops separately: every label and enough of its ball to read as a physical
object must remain visible after slicing, gutters and the different outer/top crops. A source
panorama alone cannot establish this; correct placement or export geometry if a value is cut
or crowded. For `--panels 0`, inspect the showcase slide separately from the feature graphic.

Make a final-size contact sheet of every delivered panorama panel (and the gapped carousel) before
packaging. Inspect each protected inscription and decisive face at thumbnail size, then inspect
the seam-adjacent hero at full size. A strict numeric art gate does not replace this crop review:
if a label is clipped or a hero crosses a publisher gap, correct the generated scene or bounds and
rerun the strict composition gate before continuing.

For an object/mechanic-led game with no living character, explicitly reject any invented living
player or mascot in slide 1. Verify that slides 1 and 2 each contain recognizable authentic
gameplay at a three-quarter/3D angle; when one field spans both, inspect the separate crops rather
than accepting the assembled panorama alone.

Use restrained, theme-led store grading by default: preserve the concept's exposure, add only a
modest colour lift when it helps thumbnail readability, and keep source-color separation,
foreground depth, and a broad smooth subordinate background. Do not require a bright far plane,
glare, bloom, or a universal saturation score. Those treatments are valid only when the Design DNA
or user explicitly calls for them. Crushed unreadable darkness, clipped highlights, excessive
saturation, or excessive far-plane detail still fail. Correct store art without recoloring runtime
assets.

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
weak gameplay. If the actual state changed, correct integration/feature art and remeasure/re-export;
an unchanged matching capture does not justify another generation call.

## Phase 4 — context-aware final exports

Always explicitly select lead-kind. CLI default character exists only for old callers.
For characters, pass the same selected `--character-framing` on drafts, diagnostics, final
panorama exports and banners; otherwise the compatibility default is humanoid `bust`.

| Kind | Final bounds | Check |
|---|---|---|
| character | `--hero-bounds x,y,w,h` | Prominent first-panel character; head/attached silhouette protected |
| object/mechanic | `--lead-bounds x,y,w,h` | Prominent recognizable lead anywhere, including across panels |
| all | Repeat `--protected-bounds x,y,w,h` | Critical details avoid actual crop edges and gaps |
| all | Repeat `--gameplay-bounds x,y,w,h` | Actual fields, wherever placed, are excluded from background-only detail measurements |

Measured hero/lead bounds are already excluded from background detail. Add gameplay-bounds for
separate fields, especially a character-led scene with a large board on the right. Field boxes
may cross seams; they do not replace tight protected bounds around decisive symbols. Mask only
real subjects, not busy scenery. At least 5% of the upper background must remain measurable;
empty masks cannot bypass the gate. Palette/light and foreground-object detail still apply.

Measure normalized bounds on the **final prepared panorama**, including seam-snap slack, not the
unprocessed source. Banner bounds use its final delivery crop. First export diagnostics under
art/ with identical size/zoom/offset/seam settings, inspect and measure. `--seam-snap off` makes
a planned split easy to reproduce; auto is valid when measurements and actual cuts are checked
together. Remeasure after any geometry change and separately for each store's aspect ratio.

```bash
"$STORE_PYTHON" tools/store_compose.py triptych --src "$ART_DIR/keyart-integrated.png" \
  --out "$OUT_DIR" --panels 3 --size 1320x2868 --pop soft --seam-snap off \
  --lead-kind mechanic --lead-bounds "$LEAD_BOUNDS" \
  --protected-bounds "$OUTCOME_BOUNDS" --art-gate strict
```

Resolve measured variables first. Character exports use hero-bounds instead of lead-bounds;
object exports use lead-kind object. Repeat protected regions as necessary. Export Play with
`--size play` and separately measured bounds. Do not pass sprites on final slicing calls: they
already belong to the integrated render. Strict mode writes no deliverable on failure; warn
is diagnostic-only and off is for tests. Carousel exports default to `--gutter auto`: the continuous
source extends beneath a hidden strip scaled from 100px at a 1320px card, matching the publisher's
inter-card separator. Keep faces, inscriptions and decisive outcomes outside those hidden strips;
atmosphere and noncritical field structure may cross them. Use `--gutter 0` only for a publisher
known to render true butt joints or for a lossless diagnostic panorama. Inspect the carousel preview
with gaps as the authoritative seam check. Panorama/carousel previews are verification files, not
upload slides.

## Phase 5 — showcases and feature graphic

Use `showcase` on real captures with the game's fonts/type mood and secondary device framing.
Typical Joker typography is bold/playful, not automatic elegance. Captions describe actual play.
Resolve filenames and words from this game's inventory; honor frame/no-captions/language/count.

```bash
"$STORE_PYTHON" tools/store_compose.py showcase --shot "$RAW_DIR/03-spin.png" \
  --bg "$ART_DIR/keyart-integrated.png" --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop soft
```

With panels 0, generate `art/multiplier-showcase-bg.png` as a portrait marketing background
inspired by the existing game background, with all five themed balls. Use it behind at least one
real-capture showcase; keep the capture and runtime background files unchanged. Compose Play
separately.

Feature example, after measuring the final horizontal crop:

```bash
"$STORE_PYTHON" tools/store_compose.py banner --keyart "$ART_DIR/long-banner-integrated.png" \
  --out "$STORE_DIR/feature-graphic-1024x500.png" \
  --base-out "$ART_DIR/long-banner-source-1024x500.png" --size 1024x500 --pop soft \
  --lead-kind object --lead-bounds "$BANNER_LEAD_BOUNDS" \
  --banner-layout free --banner-gate strict \
  --shot "$RAW_DIR/03-spin.png" --frame "${DEVICE_FRAME:-ios}"
```

Character banners use hero-bounds; mechanic banners use lead-bounds. Supply critical protected
regions and gameplay-bounds for separate field surfaces too. Free layout retains palette/readability/foreground checks; left-heavy additionally checks
the 3/5–2/5 density pattern. Add the phone only after the clean source passes, and retain base-out.

**The feature graphic is a banner with one phone on the right and no text.** It carries no
title, tagline, logo, wordmark, caption, badge or call to action — not on the left, not over the
scene, not beside the device. The scene fills the frame and the phone sits on the right; the left
is pure illustration with no scrim or copy space. The compositor enforces this: `banner` refuses
`--title`, `--tagline` and `--logo`. The only lettering that may appear is a themed multiplier-ball
inscription already inside the generated scene or the game's own UI inside the captured screenshot.
When `--panels 0`, the clean feature scene carries all five multiplier balls without displacing
the game's decisive play or creating a text block; verify that the phone does not cover them.

**The feature graphic always carries one device.** `--shot` is required: pick the single
strongest current capture (active play or a win moment, not the menu) and pass it so the compositor
inlays a real phone mockup with that authentic screenshot on the right side of the 1024×500 canvas
inside Play's safe area — a full scene occupies most of the frame and one device sits to the right,
never a bare screenshot rectangle (`--frame none` is refused) or a pasted capture with no scene
around it. `--base-out` keeps the clean device-free scene for the art/readability gates; `--out` is
the one shipped with the phone composited in. Do not ship a feature graphic with no device.

## Phase 6 — verify, report and package

Run `store_compose.py check --dir "$OUT_DIR" --store appstore` and, when enabled, the equivalent
Play check. Verify RGB PNGs, dimensions, no store-screenshot transparency, file sizes, aspect,
numbering/counts and feature dimensions. Open the feature graphic and confirm it shows no title,
tagline, logo or other copy, no blank left-hand text space, and exactly one framed phone on the
right. Review final rendered App Store and Google Play crops
separately, at thumbnail and full size. For object/mechanic-led panoramas, explicitly confirm in
each crop that an identifiable spill of actual lower game objects remains in frame.
Read responsible-gaming.md; check captions, metadata and art for currency symbols, misleading
multipliers and payout promises. Metadata retains the virtual-currency disclaimer, simulated
gambling declaration, rating and applicable odds disclosure. Interpret text matches in context.
Check all five final ball inscriptions against the required store-art set. A missing or altered
label fails the store kit; an unsupported gameplay value does not. Keep the balls visually
separate from real gameplay captures so the captured outcome remains authentic. Record the
final crop locations and the airborne spacing and lower-spill verdict in STORE_INFO.md.

Recheck runtime-background inventory/hashes/wiring: normal result UNCHANGED. If branding changed
Dart, run format/analysis and relevant existing tests, and verify the menu still fits. Compositor
success is not runtime or visual verification.

Write STORE_INFO.md with context/reference decisions; panel map; upload order/dimensions/counts;
complete per-sprite identity and per-panel anchor audit; real state/topology/integration evidence;
the five store-only multiplier balls, their theme treatment, actual gameplay support if any,
and final-panel visibility; prompts/budget/corrections; evidence that the gameplay capture was reference-only
and the panorama was generated as one complete scene; measured bounds and seam review for each
geometry; strict gate results
and visual verdicts; feature source/layout/review, its right-side capture and a no-text verdict;
branding/capture/log evidence; background guard and compliance. For no-living-character object/mechanic games, record the no-invented-player
check and separate slide-1/slide-2 angled-gameplay verdicts. Never call a draft or diagnostic a
finished panorama.

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x '*.DS_Store')
unzip -t "$ARCHIVE_PATH"
shasum -a 256 "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
```

Verify ZIP contents: ordered screenshots, feature graphic, branding and audits. Final answer
links ZIP/report, gives composition/counts and actual limitations. On a reusable failure or a
verified faster method, invoke `/auto-learn` with evidence; proposals remain on review branches
and never merge automatically.
