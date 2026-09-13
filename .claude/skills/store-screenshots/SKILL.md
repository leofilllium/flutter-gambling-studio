---
name: store-screenshots
description: "Create a context-based store kit: character-, object-, or mechanic-led panorama with flexible gameplay spans, real screenshots, a dedicated feature graphic, icon/emblem and ZIP. Use matching examples-games previews and actual game assets and topology. Preserve runtime backgrounds."
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

Default N=8 screenshots: P=3 adjacent concept panels from one integrated panorama followed by
N−P actual gameplay/meta captures with optional device frames and captions. Produce `store/`
at 1320×2868 and `store-play/` at 1080×1920 independently, not by resizing one set into the other.
Include a dedicated 1024×500 feature graphic, icon masters/platform densities, transparent
emblem, `STORE_BRIEF.md`, `STORE_INFO.md`, and ZIP under `project_zip/`.
`--no-play-set` omits Play screenshots. `--panels 0` skips panorama work and uses real captures
for all N screenshots; it still produces the separate feature graphic. Marketing portrait
formats never constrain the runtime app's full mobile/expanded viewport behavior.

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
- Actual topology and resolving state. New unspecified classic slots default to 3×3; store
  work preserves the shipped game's dimensions, symbols, ordering and outcome.
- Complete sprite inventory, source-to-PNG mapping, scene role and in-app evidence per file.
- Verified coin inscriptions, preferably x5/x10 when supported and thematic, with exact config/
  paytable source and meaning. No invented multipliers or guaranteed rewards. Only these short
  game-object markings may be generated; render captions/titles with compositor typography.
- Independent feature layout: `free` by default or justified `left-heavy`; no reserved device zone.
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

Build the lower edge from a varied spill of actual game objects: scale, rotation, height, overlap,
contact shadows and shared light. Add recognizable flying/falling objects at varied depths. Keep
primary subjects sharp, source-colored and dominant over a broad smooth luminous far plane.
Generic stage furniture, particles or a tidy row cannot replace the actual object spill.

Prepare an optional physical board reference from the measured actual frame:

```bash
"$STORE_PYTHON" tools/store_compose.py boardplate --out "$ART_DIR/board-plate.png" \
  --from-shot "$RAW_DIR/gameplay-reference-win.png" --rect "$FIELD_RECT" \
  --radius 0.04 --yaw -16 --pitch 7 --depth 0.06 --sheen 0.2
```

`FIELD_RECT` is the measured x,y,w,h, not a universal crop. Draft with `triptych --pano-only
--save-pano` and explicit placement when useful. Example sprite specifications:

| Layout | Arguments |
|---|---|
| Joker first, board right two | `--lead-kind character --sprite "hero.png@hero" --sprite "board.png@board,x=0.67,w=1.9"` |
| Chicken first | `--lead-kind character --character-framing mascot --sprite "chicken.png@hero"` |
| Full-width Plinko | `--lead-kind mechanic --sprite "board.png@board,x=0.5,w=2.9"` |
| Crown/object-led slot | `--lead-kind object --sprite "crown.png@prop,panel=1,w=0.9,h=0.7" --sprite "board.png@board,x=0.58,w=2.2"` |
| Contained board on chosen panel | `--sprite "board.png@board,panel=3,w=0.85"` |

Here x is normalized across the panorama and w uses panel widths. Width/height are fit limits:
the default board height 0.56 can constrain a square or portrait board before the requested width
is reached. Supply measured h as well when appropriate; inspect the actual span and readability,
and accept a narrower field or redesign the scene instead of stretching the mechanic. Use real
paths, `--sprite-dir` for complete supporting coverage, `--object-frame
auto`, and selected falls. `@hero` is only for actual characters; props use panel/x/y/w placement.
The draft is an aid, not a finished illustration. Noncritical board structure can cross seams.

Use the available built-in image tool; headless generation follows `generate-png-asset/SKILL.md`
and `tools/gpt_image.py` with prompt files/repeated `--image` inputs. Final integration receives
the draft if used, actual resolving frame, field plate, shipped sprites and matching previews.
Label which references govern identity and which govern composition. Request one coherent scene
whose field gains physical depth/light/perspective while retaining real topology, symbols and
outcome. A pasted screenshot rectangle and an attractive invented board both fail. Do not paste
a screenshot over the final render. Save the integrated result as `art/keyart-integrated.png`.

Render `art/long-banner-integrated.png` separately for the horizontal feature graphic with the
same identity and lead kind. Full-width action is valid. A left-heavy 3/5–2/5 composition is
optional. The clean source must look finished alone: no device, UI, reserved zone or marketing
words. Keep actual game objects across the lower edge and sharp primary subjects.

## Phase 2 — identity and critical-region review

Compare every sprite and the integrated field with the actual runtime frame. Record source,
reference, visible panels, scene role, identity and runtime evidence. Missing sprites, wrong
topology/state, floating stickers, invented lettering or unreadable primary forms require a
bounded correction. If budget runs out, report the blocker instead of shipping a draft.

Review both the assembled panorama and gapped carousel. Boards may span seams; tight regions
around faces, decisive symbols, multiplier inscriptions and bucket/reveal outcomes must survive
the gaps. Protect those details, not the entire board housing. Every crop still needs readable
game content. Geometry metrics cannot identify a Joker, read lettering or verify a payline:
visual comparison is mandatory.

Maintain store-art saturation ≥0.68, target 0.78–0.88, controlled glare, source-color separation,
foreground depth and broad bright smooth background. Saturated darkness or excessive far-plane
detail does not pass. Correct store art without recoloring runtime assets.

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
  --out "$OUT_DIR" --panels 3 --size 1320x2868 --pop max --seam-snap off \
  --lead-kind mechanic --lead-bounds "$LEAD_BOUNDS" \
  --protected-bounds "$OUTCOME_BOUNDS" --art-gate strict
```

Resolve measured variables first. Character exports use hero-bounds instead of lead-bounds;
object exports use lead-kind object. Repeat protected regions as necessary. Export Play with
`--size play` and separately measured bounds. Do not pass sprites on final slicing calls: they
already belong to the integrated render. Strict mode writes no deliverable on failure; warn
is diagnostic-only and off is for tests. Default gutter 0 discards no pixels; report any explicitly
requested nonzero gutter. Panorama/carousel previews are verification files, not upload slides.

## Phase 5 — showcases and feature graphic

Use `showcase` on real captures with the game's fonts/type mood and secondary device framing.
Typical Joker typography is bold/playful, not automatic elegance. Captions describe actual play.
Resolve filenames and words from this game's inventory; honor frame/no-captions/language/count.

```bash
"$STORE_PYTHON" tools/store_compose.py showcase --shot "$RAW_DIR/03-spin.png" \
  --bg "$ART_DIR/keyart-integrated.png" --out "$OUT_DIR/store-04.png" \
  --size 1320x2868 --caption "Every Spin Counts" --type-mood playful --pop vivid
```

With panels 0, use the existing game background for showcase composition. Compose Play separately.
Feature example, after measuring the final horizontal crop:

```bash
"$STORE_PYTHON" tools/store_compose.py banner --keyart "$ART_DIR/long-banner-integrated.png" \
  --out "$STORE_DIR/feature-graphic-1024x500.png" \
  --base-out "$ART_DIR/long-banner-source-1024x500.png" --size 1024x500 --pop max \
  --lead-kind object --lead-bounds "$BANNER_LEAD_BOUNDS" \
  --banner-layout free --banner-gate strict
```

Character banners use hero-bounds; mechanic banners use lead-bounds. Supply critical protected
regions and gameplay-bounds for separate field surfaces too. Free layout retains light/palette/foreground checks; left-heavy additionally checks
the 3/5–2/5 density pattern. Add optional typography/real capture only after the clean source
passes, retain base-out, and recheck readability after overlays.

## Phase 6 — verify, report and package

Run `store_compose.py check --dir "$OUT_DIR" --store appstore` and, when enabled, the equivalent
Play check. Verify RGB PNGs, dimensions, no store-screenshot transparency, file sizes, aspect,
numbering/counts and feature dimensions. Review all images at thumbnail and full size.
Read responsible-gaming.md; check captions, metadata and art for currency symbols, misleading
multipliers and payout promises. Metadata retains the virtual-currency disclaimer, simulated
gambling declaration, rating and applicable odds disclosure. Interpret text matches in context.

Recheck runtime-background inventory/hashes/wiring: normal result UNCHANGED. If branding changed
Dart, run format/analysis and relevant existing tests, and verify the menu still fits. Compositor
success is not runtime or visual verification.

Write STORE_INFO.md with context/reference decisions; panel map; upload order/dimensions/counts;
complete per-sprite identity and per-panel anchor audit; real state/topology/integration evidence;
prompts/budget/corrections; measured bounds and seam review for each geometry; strict gate results
and visual verdicts; feature source/layout/review; branding/capture/log evidence; background guard
and compliance. Never call a draft or diagnostic a finished panorama.

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
