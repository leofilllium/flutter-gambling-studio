---
name: store-screenshots
description: "Build a complete App Store and Google Play storefront kit for a gambling game: a text-free concept panorama sliced into panels, real gameplay screenshots in device frames with compliant English marketing typography, a feature graphic, an applied launcher icon, and an in-game emblem. Art direction follows the game's C1-C6 category, archetype, and Design DNA. Output is a downloadable ZIP under project_zip/."
argument-hint: "[--count 8] [--panels 3] [--size 1320x2868|1290x2796|play] [--no-play-set] [--lang en] [--frame ios|android|none] [--type-mood bold|epic|tech|playful|elegant|retro|clean] [--no-captions] [--no-apply] [--no-wire-logo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Store Screenshots — Complete Storefront Kit

Create everything needed to present the game in App Store Connect and Google Play:

| Deliverable | Source |
|---|---|
| Panels 1…P: one wide, text-free concept illustration sliced into adjacent panels | GPT Images 2.0 → `store_compose.py triptych` |
| Panels P+1…N: real gameplay frames in a device mockup with marketing captions | `web_verify.mjs` → `store_compose.py showcase` |
| Google Play feature graphic, 1024×500 | `store_compose.py banner` |
| Launcher icon for all Android/iOS/web densities | image generation → `store_compose.py icon` → `flutter_launcher_icons` |
| In-game emblem/logo with transparent background | image generation → `tools/cutout.py` |

Build two screenshot sets from the same art and gameplay frames:

- App Store: iPhone 6.9-inch format, 1320×2868 by default, under `store/`.
- Google Play: 1080×1920 (9:16), under `store-play/`.

Do not downscale one set into the other. Recompose typography and device framing for each aspect ratio. Google Play rejects images whose long side is more than twice the short side, so the 2.17:1 App Store files cannot serve as the Play set.

All generated copy is English unless the user explicitly requests another player-facing language. The concept panels contain no letters at all; captions and titles are rendered by the compositor, never by the image model.

This skill creates local artifacts only. It does not publish, commit, change game balance, or build release binaries.

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

## Arguments and defaults

| Argument | Default | Meaning |
|---|---|---|
| `--count N` | `8` | Total screenshots |
| `--panels P` | `3` | Number of adjacent concept panels; `0` disables them |
| `--size` | `1320x2868` | Main set; also supports `iphone-6.9`, `iphone-6.9-alt`, `iphone-6.5`, and `play` |
| `--no-play-set` | off | Skip the separate 9:16 Play set |
| `--lang` | `en` | Caption/title language; change only on explicit request |
| `--frame` | `ios` | `ios`, `android`, or `none` |
| `--type-mood` | from DNA | `bold`, `epic`, `tech`, `playful`, `elegant`, `retro`, or `clean` |
| `--font-dir` | `assets/fonts` if present | Prefer bundled game fonts |
| `--no-captions` | off | Produce clean gameplay frames |
| `--no-apply` | off | Generate kit files without modifying project branding |
| `--no-wire-logo` | off | Do not add the emblem to the main menu |
| `--name` | pubspec name | Archive base name |

For landscape games, swap width and height and use `--panels 0`.

## Phase 0 — preflight and store brief

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

Choose copy that describes play and collection, not payment or financial gain. Use the exact English disclaimer from `ComplianceCopy.disclaimer` in listing metadata.

Run the compositor's font probe and select a display/body pair that covers every caption glyph. Prefer the game's bundled fonts; otherwise choose by Design DNA, not a studio-wide default.

## Phase 1 — capture real gameplay frames

Reuse existing runtime frames only when they are valid portrait phone images with `h/w` between 1.9 and 2.35. Otherwise capture a new Chrome/CDP tour:

```bash
flutter run -d web-server --web-port=0 > .claude/runtime-logs/flutter-run.log 2>&1 &
node tools/web_verify.mjs --url "$WEB_URL" --out "$RAW_DIR" \
  --size 390x844 --dpr 3 --budget 180 --quick
```

Capture at least a menu, active round, peak-tension state, win/reward state, and one meaningful progression/meta state. Frames must show actual UI and actual game state—never mock numbers or fake gameplay.

Reject empty, duplicated, error, overflow, loading-only, wrong-aspect, or non-gameplay frames. Parse the Flutter log for exceptions before continuing.

## Phase 2 — generate brand art

Use image generation for three sources:

1. **Concept panorama:** one continuous text-free scene wide enough for P panels. Compose the category mechanic, peak moment, hero, and virtual reward across the full width. Keep important objects away from panel seams. Explicitly request no text, logo, letters, numbers, UI, device frame, or panel dividers.
2. **Icon art:** one bold central mechanic/hero silhouette, readable at 48 px, no text, no thin border, and no transparent holes.
3. **Game emblem:** a distinctive symbol/crest derived from the mechanic and world, with no letters or words, generated on a flat removable background.

Use the same Design DNA and top-left light for all three. Run `tools/cutout.py` on the emblem and inspect alpha edges. Regenerate an asset only when the source is genuinely defective.

## Phase 3 — compose and apply branding

Use `store_compose.py icon` to create the 1024 master, 512 listing icon, and adaptive foreground. Add/configure `flutter_launcher_icons` in `pubspec.yaml`, then run:

```bash
dart run flutter_launcher_icons
```

Verify generated Android mipmaps, adaptive icon resources, iOS AppIcon entries, and web icons. The App Store master must be opaque.

Copy the emblem to `assets/images/ui/ui_game_logo.png`, register it in `pubspec.yaml` or the shared asset registry, and—unless `--no-wire-logo`—add one responsive `Image.asset` to the main menu. Do not rewrite the screen. Run formatting and analysis after this targeted edit; revert the wiring if it introduces an error.

## Phase 4 — compose the concept panels

Slice the same panorama separately for the App Store and Play dimensions with `store_compose.py triptych`. Produce numbered `store-01.png` through `store-0P.png` plus `_panorama-preview.png` for inspection.

Vision-check the stitched preview:

- Adjacent panels form one continuous image in upload order.
- No seam cuts the hero's face, central mechanic, reward, or decisive action.
- No letters, fake glyphs, captions, UI, or panel borders appear.
- The mechanic and category are recognizable without generic casino cues.

The preview is a verification artifact and must not be listed for store upload.

## Phase 5 — compose gameplay showcase frames

Select `COUNT-P` real frames that tell one coherent story: enter the game, play a live round, reach tension, win/reveal, and progress. Write short English captions that are specific to the actual mechanic and avoid payout language.

Run `store_compose.py showcase` once for the main set and once for the Play set using the same ordered frame/caption list. Use the chosen font pair and Design DNA palette. Captions must remain within safe areas, retain at least 4.5:1 contrast, and render every glyph correctly.

Vision-check every composed file for clipping, misspellings, empty glyph boxes, distorted phone frames, fake gameplay, or inconsistent typography.

## Phase 6 — feature graphic

Create `feature-graphic-1024x500.png` with `store_compose.py banner`. Use the panorama or a real gameplay frame as the image layer. Render the English game title and tagline with the compositor; never ask the image model to draw them.

The feature graphic is for Google Play and may also be included in the press kit.

## Phase 6.5 — blocking compliance gate

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

## Phase 7 — verification

```bash
python3 tools/store_compose.py check --dir "$OUT_DIR" --store appstore
python3 tools/store_compose.py check --dir "$PLAY_DIR" --store play
```

Both checks must pass. Confirm readable RGB PNG files, consistent dimensions, no alpha in Play screenshots, file sizes within store limits, and correct aspect ratios. Then perform a final vision pass across both ordered sets.

## Phase 8 — store information

Write `$STORE_DIR/STORE_INFO.md` in English with:

- Build timestamp, category, archetype, title, tagline, and dimensions.
- An inventory of both screenshot sets, feature graphic, icons, emblem, and verification-only preview.
- Ordered caption mapping.
- Exactly what branding was applied to the project.
- Compliance profile, ratings, simulated-gambling answer, disclaimer, odds disclosure, and grep/vision results.
- Exact Google Play and App Store upload order. Emphasize that `_panorama-preview.png` is not uploaded.

## Phase 9 — package

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x '*.DS_Store')
[[ -s "$ARCHIVE_PATH" ]] || { echo "Store ZIP was not created."; exit 1; }
unzip -t "$ARCHIVE_PATH" >/dev/null || { echo "Store ZIP is corrupt."; exit 1; }
shasum -a 256 "$ARCHIVE_PATH" > "$ARCHIVE_PATH.sha256"
```

Verify the archive contains numbered PNGs in both `store/` and `store-play/` unless the Play set was explicitly disabled.

## Phase 10 — final report

Report the title/tagline, category/archetype, App Store and Play counts/dimensions, panorama panel range, gameplay-frame range, feature graphic, icon application status, emblem wiring status, compliance verdict, ratings/disclaimer, archive path/size, and SHA-256. State the exact upload order for each store.

## Quality gates

- Preflight tools and fonts are available.
- At least one valid phone-aspect raw frame exists; the final selection includes active play and a win/reward state.
- Panorama, icon, and emblem share one visual world and pass vision review.
- Launcher icons are applied unless `--no-apply` was requested.
- Concept panels are text-free and stitch correctly in both sets.
- Showcase captions are readable, correctly spelled, and rendered with full glyph coverage.
- Compliance grep and vision checks pass with no exceptions.
- `check --store appstore` and `check --store play` both pass.
- The ZIP is valid, contains the required files, and has a recorded SHA-256.

## Forbidden

- Changing gameplay logic, state, configuration, balance, or economy.
- Committing, publishing, uploading, or deleting existing project artifacts.
- Drawing fake gameplay, fake values, generated lettering, device frames, or panel separators into model-generated art.
- Generic casino art direction unrelated to the current category and Design DNA.
- Any real-money promise, currency symbol, banknote, cash/payout language, or financial implication.
- Reusing the 6.9-inch files as the Play set or scaling them instead of recomposing.
- Hiding generation, compliance, verification, or packaging failures.
- Listing `_panorama-preview.png` as an upload asset.
