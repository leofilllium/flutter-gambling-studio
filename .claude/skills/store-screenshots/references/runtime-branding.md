# Runtime branding and background preservation

Read when applying the icon/emblem or an explicitly requested background redesign.
Variables are initialized by the main runbook. This operation follows art verification
and precedes final runtime capture.

## Phase 3 — apply branding without replacing the game's backgrounds

The reference-only context frame from preflight remains an input to the artwork and is never part
of the upload set. The icon and emblem may be applied before final capture, but ordinary
`/store-screenshots` runs do **not** replace, rewire, recolour, blur, or regenerate a menu,
gameplay, splash, or shared runtime background.

Before any project edit, record a background guard under `$ART_DIR`:

```bash
{
  rg --files assets 2>/dev/null \
    | rg -i '(^|/)(backgrounds?|backdrops?)(/|$)|(^|/)(background|bg)_[^/]+\.(png|webp|jpe?g|svg)$' \
    || true
} | sort -u > "$ART_DIR/runtime-background-assets.txt"

while IFS= read -r background_path; do
  [[ -z "$background_path" ]] || shasum -a 256 "$background_path"
done < "$ART_DIR/runtime-background-assets.txt" \
  > "$ART_DIR/runtime-background-assets-before.sha256"

rg -n -i 'background|backdrop|bg_' lib pubspec.yaml 2>/dev/null \
  | sed -E 's/^([^:]+):[0-9]+:/\1:/' \
  > "$ART_DIR/runtime-background-references-before.txt" || true
```

These files establish both halves of the invariant: the existing image bytes and the code/config
references that select them.

**Launcher icon.** If no suitable square icon art exists yet (`assets/branding/app_icon.png` or a
game-world emblem crop from `art/panorama.png`), generate one with the same Codex GPT
Images 2.0 path as the rest of the asset set (`generate-png-asset/SKILL.md`, budgeted as one
`generate` source): a full-bleed square composition of the game's hero character/object/emblem
on its own themed background, matching the Design DNA.

**No drawn frame, bezel, ring, or rounded-square backdrop in the icon art.** Google Play and
iOS apply their own mask (circle, squircle, adaptive shape) on top of the square source; a
border baked into the artwork doubles up with the platform mask, gets cropped unevenly, or reads
as a second competing edge. The subject fills the frame edge-to-edge with its own silhouette and
background — no illustrated ring/frame/plate around it, unlike in-game symbol icons which may use
themed edging per `anti-slop-design.md`.

This launcher-icon art is an **opaque full-bleed square scene** (hero subject + themed
background), not a chroma-key cutout sprite: do not generate it with the flat magenta/green key
background used for `symbol`/`sprite`-class assets in `generate-png-asset/SKILL.md`, and do not
run `tools/cutout.py` on the 1024 master. Only the separate `app_icon_fg.png` adaptive-foreground
crop needs a transparent background (generate or derive it with alpha, or cut it with
`tools/cutout.py --type icon`, before passing it as `--fg-src`).

Use `store_compose.py icon` to create the 1024 master, 512 listing icon, and adaptive foreground
from that source. Add/configure `flutter_launcher_icons` in `pubspec.yaml`, then run:

```bash
dart run flutter_launcher_icons
```

Verify generated Android mipmaps, adaptive icon resources, iOS AppIcon entries, and web icons. The
App Store master must be opaque. Inspect `store_icon_512.png` at thumbnail size against a circular
and a rounded-square mask; reject and regenerate if any drawn border/frame is visible.

**Emblem.** Copy the emblem to `assets/images/ui/ui_game_logo.png`, register it in `pubspec.yaml` or the shared asset registry, and—unless `--no-wire-logo`—add one responsive `Image.asset` to the main menu. Do not rewrite the screen.

**Runtime backgrounds.** Leave the files and their wiring alone. A mismatch between storefront art
and the existing game is fixed by regenerating storefront art from the existing backgrounds,
runtime frames, field, hero, and sprites. It is never fixed by silently replacing the game.

Only when the user explicitly requested a runtime-background redesign and supplied
`--apply-backdrop` may this separate operation run:

```bash
"$STORE_PYTHON" tools/store_compose.py backdrop --src "$ART_DIR/panorama.png" \
  --out-dir assets/images/backgrounds --prefix bg_keyart \
  --variants menu,game --size 1080x1920 --offset -0.55 --pop soft --calm 0.45 \
  --confirm-game-background-replacement
```

`store_compose.py backdrop` refuses to write without the long confirmation flag. The presence of
`--apply-backdrop` alone is not permission: the user's request must explicitly mention changing
the actual game's background. Record that request and every affected file in `STORE_INFO.md`.

Run formatting and analysis after these targeted edits. Revert any wiring that introduces an error,
an overflow, or a contrast regression, and say so in the final report — a broken screen is worse
than a missing emblem.

Unless the explicit backdrop opt-in was valid, recompute the background hashes/references and
compare them before continuing:

```bash
{
  rg --files assets 2>/dev/null \
    | rg -i '(^|/)(backgrounds?|backdrops?)(/|$)|(^|/)(background|bg)_[^/]+\.(png|webp|jpe?g|svg)$' \
    || true
} | sort -u > "$ART_DIR/runtime-background-assets-after.txt"

while IFS= read -r background_path; do
  [[ -z "$background_path" ]] || shasum -a 256 "$background_path"
done < "$ART_DIR/runtime-background-assets-after.txt" \
  > "$ART_DIR/runtime-background-assets-after.sha256"

rg -n -i 'background|backdrop|bg_' lib pubspec.yaml 2>/dev/null \
  | sed -E 's/^([^:]+):[0-9]+:/\1:/' \
  > "$ART_DIR/runtime-background-references-after.txt" || true

cmp "$ART_DIR/runtime-background-assets.txt" \
    "$ART_DIR/runtime-background-assets-after.txt" \
  || { echo "BLOCKER: store screenshots added or removed a runtime background asset"; exit 1; }
cmp "$ART_DIR/runtime-background-assets-before.sha256" \
    "$ART_DIR/runtime-background-assets-after.sha256" \
  || { echo "BLOCKER: store screenshots changed a runtime background asset"; exit 1; }
cmp "$ART_DIR/runtime-background-references-before.txt" \
    "$ART_DIR/runtime-background-references-after.txt" \
  || { echo "BLOCKER: store screenshots changed runtime background wiring"; exit 1; }
```
