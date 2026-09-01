#!/usr/bin/env python3
"""
store_compose.py — store-listing image compositor for the game studio.

Produces the full set of publishable listing images for ANY game the studio
makes (genre/theme agnostic — everything visual comes from the arguments):

  triptych  N vertical panels sliced out of ONE wide key-art panorama, so the
            first N store screenshots REASSEMBLE into that exact picture: the
            cuts are butt-joined, nothing at all is discarded between the panels
            and no panel ends mid-object. WHERE the cuts fall is chosen by the
            picture, not by arithmetic (`--seam-snap`): the tiling slides until
            they land on the quietest columns, and the art is asked for a calm
            corridor there. `--gutter` can still throw a seam allowance away at
            each cut, for a publisher who asks the panels to line up across the
            store's own carousel gap — but that is opt-in, because it puts a
            hole in the picture.
            `--sprite` inlays the game's real objects into the art — hero on
            panel 1, the real field on panel 2, and a real reward/prop anchoring
            panel 3 — so every split slide belongs unmistakably to the game.
            Auto-placement fills an uncovered panel before adding a second
            object to another one, and supporting props are tucked behind the
            scene's foreground instead of left on its surface. This is a
            *conceptual* poster of the game world, not a screen of the app —
            and it carries NO TEXT: lettering across a panel boundary is cut by
            the store's gutters, and a lockup inside one panel breaks the
            single-picture illusion.
  boardplate
            the game's REAL play field as a transparent cutout for `triptych
            --sprite plate.png@board`: the shipped symbol files laid into the
            game's own grid (or the field lifted straight out of a captured
            frame), stood up in perspective with a slab edge. `--win` builds it
            at the moment the round pays — payline, ring, spill light, the rest
            of the field falling back and the paying symbol lifting out of its
            cell — because the middle panel of a listing is its gameplay
            example, and a correct grid at rest reads as a diagram.
  showcase  a real in-game frame placed inside a drawn phone (bezel, notch,
            home indicator, glass glare, drop shadow) over a themed background,
            with the caption typography that sells the frame.
  banner    Google Play feature graphic (1024x500) — key art + optional device
            mockup + title lockup, laid out inside Play's safe area.
  backdrop  the same key art exported as the GAME's background (menu / gameplay
            / splash treatments), which is what stops the listing and the app
            from looking like two different products.
  icon      launcher/store icon set derived from generated art: 1024 master,
            1024 adaptive foreground (subject inside Android's 66% safe zone),
            512 store icon.
  fonts     report which display faces this machine can actually use.
  check     validates a finished directory against store constraints, with a
            per-store verdict (Play / App Store) on every file.

Screenshot size defaults to 1320x2868 — the App Store's 6.9" slot, the single
upload that covers every current iPhone. Google Play will NOT take that shape
(it caps the long side at 2× the short one), so a listing aimed at both stores
exports a second set at `--size play` (1080x1920, exactly 9:16).

Why a tool instead of inline ImageMagick: rounded corners, notches, glare,
fractional-alpha shadows and display typography are exactly the steps that
silently degrade when written as one-off `convert` incantations. Here they are
deterministic, testable and identical across every game.

Every generated-art path is colour graded on the way out (`--pop`): a listing is
reviewed as a strip of thumbnails beside nine competitors, and ungraded model
output reads washed out there. Real gameplay frames are never graded — a store
screenshot must show what the app renders, so a dull frame is fixed by giving
the game the key art as its background, not in post.

Typography is treated as display type, not UI labels: the face is chosen by
mood (or taken from the game's own assets/fonts via --font-dir), letter spacing
is tuned per mood, and text is rendered through an alpha mask so the fill can
be a gradient in the game's palette and the shadow can be a real blur.

Requires: Pillow + numpy (both already required by tools/cutout.py).

Examples:
  python3 tools/store_compose.py fonts --font-dir assets/fonts
  python3 tools/store_compose.py triptych --src keyart.png --out store/ \\
      --panels 3 --size 1320x2868 --save-pano art/keyart-integrated.png \\
      --sprite assets/images/sprites/eagle.png@hero \\
      --sprite assets/images/sprites/lightning.png@panel=2 \\
      --sprite assets/images/sprites/shield.png --sprite-glow-color "#F0B34A"
  python3 tools/store_compose.py backdrop --src art/keyart-integrated.png \\
      --out-dir assets/images/backgrounds --variants menu,game --offset -0.6
  python3 tools/store_compose.py showcase --shot raw/02-menu.png \\
      --bg art/keyart-integrated.png \\
      --out store/store-04.png --size 1320x2868 --caption "Every Spin Counts" \\
      --type-mood epic --caption-color "#FFF6DC" --caption-color2 "#F0B34A"
  python3 tools/store_compose.py showcase ... --size play   # 9:16 set for Play
  python3 tools/store_compose.py banner --keyart art/keyart-integrated.png \\
      --shot raw/02-menu.png --offset -0.6 \\
      --out store/feature-graphic-1024x500.png --title "Zeus Slots" \\
      --tagline "Match. Chain. Ascend." --type-mood epic --title-color2 "#F0B34A"
  python3 tools/store_compose.py icon --src icon_art.png --fg-src emblem.png \\
      --out-dir assets/branding --bg "#2A0E4F"
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    sys.stderr.write(
        f"❌ store_compose.py requires Pillow + numpy ({exc}).\n"
        "   Debian/Ubuntu: apt-get install -y python3-pil python3-numpy\n"
        "   pip:           pip install pillow numpy\n"
    )
    sys.exit(2)

RES = getattr(Image, "Resampling", Image).LANCZOS

# Store constraints we validate against (Google Play phone screenshots).
PLAY_MIN_SIDE = 320
PLAY_MAX_SIDE = 3840
PLAY_MAX_BYTES = 8 * 1024 * 1024
# Play rejects a screenshot whose long side is more than twice the short side.
PLAY_MAX_RATIO = 2.0

# Canonical portrait sizes. The App Store's 6.9" slot is the default because a
# single 6.9" upload covers every current iPhone in App Store Connect.
#
# Its 2.17:1 shape is ILLEGAL on Google Play (PLAY_MAX_RATIO above), so a
# listing that targets BOTH stores needs a second export at 9:16 — `check`
# prints a per-store verdict so that never gets discovered at upload time.
SIZE_PRESETS = {
    "iphone-6.9": (1320, 2868),   # App Store 6.9" (primary)
    "iphone-6.9-alt": (1290, 2796),  # App Store 6.9" (accepted alternative)
    "iphone-6.5": (1242, 2688),   # App Store 6.5" (legacy slot)
    "play": (1080, 1920),         # Google Play phone, exactly 9:16
}
DEFAULT_SCREEN_SIZE = "1320x2868"

# ── font discovery ──────────────────────────────────────────────────────────
#
# Store titles are DISPLAY typography, not UI labels, and the single biggest
# reason generated listings look amateur is that they were set in whatever
# metric-compatible Arial clone the container happened to ship. So instead of a
# fixed path list we index the machine's fonts and choose by *character*:
# a mood picks an ordered list of families, and the game's own typeface (via
# --font-dir assets/fonts) outranks all of them, because that face IS the
# game's identity.

FONT_DIRS = (
    "/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts",
    "/System/Library/Fonts", "/Library/Fonts", "~/Library/Fonts",
    "C:/Windows/Fonts",
)

# Faces that are fine for body copy but read as "no design decision was made"
# in a 200px store title. Their selection is reported, not silently accepted.
GENERIC_FACES = ("liberation", "dejavu", "arial", "helvetica", "freesans", "nimbus", "sfns")

# Never set text in these, whatever the directory: a Flutter project's
# assets/fonts commonly holds an icon font, and titles would render as glyph
# soup.
NON_TEXT_FONTS = ("icon", "symbol", "emoji", "awesome", "material", "dingbat", "braille")

# Appended to every mood so resolution always terminates on something readable.
FALLBACK_FAMILIES = (
    "Inter", "Roboto", "NotoSans", "OpenSans", "Montserrat",
    "LiberationSans", "DejaVuSans", "Arial",
)

# mood -> ordered family preferences + the spacing/case that face wants.
# Families are listed most-characterful first and span Linux packages, macOS
# system fonts and Windows, so the same mood degrades gracefully anywhere.
TYPE_MOODS: dict[str, dict] = {
    "bold": {  # poster-loud, genre-neutral — the default
        "display": ("Anton", "ArchivoBlack", "Oswald", "LeagueGothic", "BebasNeue",
                    "Impact", "Montserrat", "Inter", "Roboto"),
        "body": ("Montserrat", "Inter", "Roboto", "OpenSans", "NotoSans"),
        "upper": True, "tracking": 0.02,
    },
    "epic": {  # myth, fantasy, high stakes
        "display": ("Cinzel", "PlayfairDisplay", "EBGaramond", "Bodoni72", "Didot",
                    "Georgia", "NotoSerif", "LiberationSerif", "DejaVuSerif"),
        "body": ("EBGaramond", "NotoSerif", "Georgia", "Lato", "NotoSans"),
        "upper": True, "tracking": 0.06,
    },
    "tech": {  # sci-fi, cyber, neon
        "display": ("Orbitron", "Rajdhani", "Saira", "Exo2", "TitilliumWeb",
                    "Chakra", "Play", "RobotoCondensed", "Inter", "NotoSans"),
        "body": ("Inter", "Roboto", "TitilliumWeb", "Play", "NotoSans"),
        "upper": True, "tracking": 0.12,
    },
    "playful": {  # casual, candy, kids, cozy
        "display": ("Baloo", "Fredoka", "Comfortaa", "Quicksand", "Nunito",
                    "Rubik", "MarkerFelt", "Montserrat", "NotoSans"),
        "body": ("Nunito", "Quicksand", "Rubik", "OpenSans", "NotoSans"),
        "upper": False, "tracking": 0.0,
    },
    "elegant": {  # premium, minimal, refined
        "display": ("Cormorant", "PlayfairDisplay", "EBGaramond", "Didot",
                    "Optima", "Palatino", "NotoSerif", "Georgia"),
        "body": ("EBGaramond", "Lato", "NotoSerif", "Georgia", "NotoSans"),
        "upper": True, "tracking": 0.14,
    },
    "retro": {  # arcade, pixel, 8-bit
        "display": ("PressStart2P", "Silkscreen", "VT323", "Monoton", "Bungee",
                    "Impact", "Oswald", "JetBrainsMono", "FiraCode", "DejaVuSansMono"),
        "body": ("VT323", "JetBrainsMono", "FiraCode", "DejaVuSansMono",
                 "LiberationMono", "Menlo"),
        "upper": True, "tracking": 0.06,
    },
    "clean": {  # modern, neutral, restraint
        "display": ("Inter", "Montserrat", "HelveticaNeue", "Roboto", "Cantarell",
                    "Ubuntu", "Lato", "OpenSans", "NotoSans"),
        "body": ("Inter", "Roboto", "OpenSans", "Lato", "Cantarell", "NotoSans"),
        "upper": False, "tracking": 0.01,
    },
}

# Weight tokens ordered best-first for each intent.
_HEAVY_ORDER = ("black", "heavy", "ultrabold", "extrabold", "extrabld", "bold",
                "semibold", "demibold", "medium", "regular", "book")
_LIGHT_ORDER = ("regular", "normal", "book", "text", "medium", "light", "thin",
                "semibold", "demibold", "bold", "black", "heavy")

# What may legally follow a family name in a filename. This gate is what stops
# "NotoSans" from matching NotoSansAdlam-Regular.ttf — a font for the Adlam
# script, which would set a Latin title entirely in tofu boxes.
_STYLE_TOKENS = (
    "black", "heavy", "ultra", "extra", "bold", "bd", "semi", "demi", "medium",
    "regular", "normal", "book", "light", "thin", "italic", "oblique", "roman",
    "condensed", "narrow", "display", "text", "mono", "std", "pro", "variable",
)


# ───────────────────────────── console ──────────────────────────────────────

def die(msg: str) -> "None":
    sys.stderr.write(f"❌ {msg}\n")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def warn(msg: str) -> None:
    print(f"⚠️  {msg}")


def info(msg: str) -> None:
    print(f"   {msg}")


# ───────────────────────────── basics ───────────────────────────────────────

def parse_size(text: str) -> tuple[int, int]:
    key = str(text).strip().lower()
    if key in SIZE_PRESETS:
        return SIZE_PRESETS[key]
    try:
        w, h = key.replace("×", "x").split("x")
        size = (int(w), int(h))
    except Exception:
        die(f"bad --size {text!r}; expected WIDTHxHEIGHT (e.g. 1320x2868) "
            f"or a preset: {', '.join(SIZE_PRESETS)}")
    if size[0] < 16 or size[1] < 16:
        die(f"--size {text!r} is too small")
    return size


def store_verdict(w: int, h: int) -> tuple[bool, bool, str]:
    """Return (play_ok, appstore_ok, note) for a finished screenshot size.

    The two stores disagree about shape: Play caps the long side at 2× the
    short one, while the App Store's 6.9" slot is 2.17:1. One PNG cannot
    satisfy both, so we say so per file instead of failing the whole run.
    """
    long_side, short_side = max(w, h), min(w, h)
    ratio = long_side / short_side
    play_ok = (PLAY_MIN_SIDE <= short_side and long_side <= PLAY_MAX_SIDE
               and ratio <= PLAY_MAX_RATIO + 1e-6)
    appstore_ok = (w, h) in {
        SIZE_PRESETS["iphone-6.9"], SIZE_PRESETS["iphone-6.9-alt"],
        SIZE_PRESETS["iphone-6.5"],
    }
    if not play_ok and ratio > PLAY_MAX_RATIO:
        note = (f"{ratio:.2f}:1 — Play needs ≤{PLAY_MAX_RATIO:.2f}:1 "
                f"(export a second set at {SIZE_PRESETS['play'][0]}×{SIZE_PRESETS['play'][1]})")
    elif not appstore_ok:
        note = "not an App Store Connect display slot — fine for Play only"
    else:
        note = ""
    return play_ok, appstore_ok, note


def hex_rgba(text: str, alpha: int = 255) -> tuple[int, int, int, int]:
    s = str(text).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 8:
        r, g, b, a = (int(s[i:i + 2], 16) for i in (0, 2, 4, 6))
        return (r, g, b, a)
    if len(s) != 6:
        die(f"bad colour {text!r}; expected #RGB, #RRGGBB or #RRGGBBAA")
    r, g, b = (int(s[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, alpha)


def opt_rgba(text: str | None, alpha: int = 255):
    """hex_rgba for optional colours — empty/unset means 'no second stop'."""
    return hex_rgba(text, alpha) if str(text or "").strip() else None


def load_image(path: str | Path, label: str = "image") -> Image.Image:
    p = Path(path)
    if not p.is_file():
        die(f"{label} not found: {p}")
    if p.stat().st_size == 0:
        die(f"{label} is empty (0 bytes): {p}")
    try:
        img = Image.open(p)
        img.load()
    except Exception as exc:
        die(f"{label} is not a readable image ({p}): {exc}")
    return img.convert("RGBA")


def cover(img: Image.Image, w: int, h: int, sharpen: bool = True,
          bias_x: float = 0.0, zoom: float = 1.0) -> Image.Image:
    """Scale to fully cover w×h (preserving aspect), then crop.

    `zoom` >1 oversamples to create horizontal slack; `bias_x` in -1..1 then
    slides the crop window inside that slack (-1 = hard left, +1 = hard right).
    That pair is how a face sitting on a panel seam gets moved off it without
    paying for a whole new generation.
    """
    tw, th = max(w, round(w * zoom)), max(h, round(h * zoom))
    scale = max(tw / img.width, th / img.height)
    nw, nh = max(tw, math.ceil(img.width * scale)), max(th, math.ceil(img.height * scale))
    out = img.resize((nw, nh), RES)
    # Generated art is usually smaller than a store canvas; a light unsharp pass
    # is the difference between "upscaled" and "soft".
    if sharpen and scale > 1.25:
        amount = int(min(120, 45 * scale))
        out = out.filter(ImageFilter.UnsharpMask(radius=2, percent=amount, threshold=3))
    slack_x, slack_y = nw - w, nh - h
    left = int(round(slack_x * (0.5 + 0.5 * max(-1.0, min(1.0, bias_x)))))
    top = slack_y // 2
    return out.crop((left, top, left + w, top + h))


def contain(img: Image.Image, w: int, h: int) -> Image.Image:
    """Scale to fit inside w×h preserving aspect (no crop, no padding)."""
    scale = min(w / img.width, h / img.height)
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), RES)


def rr_mask(size: tuple[int, int], radius: int, ss: int = 3) -> Image.Image:
    """Antialiased rounded-rectangle alpha mask (supersampled)."""
    w, h = size
    radius = int(max(0, min(radius, min(w, h) // 2)))
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=255
    )
    return m.resize((w, h), RES)


def rr_ring(size: tuple[int, int], radius: int, stroke: int) -> Image.Image:
    """Alpha mask of a rounded-rectangle outline `stroke` px thick."""
    w, h = size
    stroke = max(1, min(stroke, min(w, h) // 2))
    outer = rr_mask(size, radius)
    inner = Image.new("L", size, 0)
    inner.paste(rr_mask((w - 2 * stroke, h - 2 * stroke), max(0, radius - stroke)),
                (stroke, stroke))
    return Image.fromarray(
        np.clip(np.asarray(outer, dtype=np.int16)
                - np.asarray(inner, dtype=np.int16), 0, 255).astype(np.uint8), "L")


def gradient(size: tuple[int, int], stops, horizontal: bool = False) -> Image.Image:
    """Linear gradient. `stops` = [(pos 0..1, (r,g,b,a)), ...] sorted by pos."""
    w, h = size
    n = max(2, w if horizontal else h)
    pos = np.asarray([s[0] for s in stops], dtype=np.float64)
    cols = np.asarray([s[1] for s in stops], dtype=np.float64)
    t = np.linspace(0.0, 1.0, n)
    line = np.stack([np.interp(t, pos, cols[:, i]) for i in range(4)], axis=1)
    if horizontal:
        arr = np.repeat(line[None, :, :], h, axis=0)
    else:
        arr = np.repeat(line[:, None, :], w, axis=1)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    # `n` is floored at 2, so a 1px-thin ramp comes back one row/column too big.
    return out if out.size == (w, h) else out.resize((max(1, w), max(1, h)), RES)


def drop_shadow(img: Image.Image, blur: int, dy: int, opacity: float) -> tuple[Image.Image, int]:
    """Return (image on a padded transparent canvas with a soft shadow, pad)."""
    pad = int(blur * 3 + abs(dy) + 4)
    canvas = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    mask = Image.new("L", canvas.size, 0)
    mask.paste(img.getchannel("A"), (pad, pad + dy))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    mask = mask.point(lambda v: int(v * opacity))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow.putalpha(mask)
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(img, (pad, pad))
    return canvas, pad


def paste_clipped(base: Image.Image, img: Image.Image, x: int, y: int) -> None:
    """alpha_composite that tolerates `img` hanging off any edge of `base`.

    Needed for the bleed layout, where the phone deliberately runs past the
    bottom of the canvas; the plain in-place alpha_composite would raise.
    """
    bw, bh = base.size
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(img.width, bw - x), min(img.height, bh - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    base.alpha_composite(img.crop((sx0, sy0, sx1, sy1)), (x + sx0, y + sy0))


def save_png(img: Image.Image, path: Path, keep_alpha: bool = False) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = img if keep_alpha else img.convert("RGB")
    out.save(path, "PNG", optimize=True)
    size = path.stat().st_size
    if not path.is_file() or size == 0:
        die(f"failed to write {path}")
    return size


# ───────────────────────────── typography ───────────────────────────────────

def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


@lru_cache(maxsize=32)
def _scan_fonts(root: str) -> tuple[tuple[str, str], ...]:
    """Index one directory tree as ((normalised stem, path), ...)."""
    base = Path(root).expanduser()
    if not base.is_dir():
        return ()
    found: set[tuple[str, str]] = set()
    for path in base.rglob("*"):
        if path.suffix.lower() not in (".ttf", ".otf", ".ttc") or not path.is_file():
            continue
        stem = _norm(path.stem)
        if any(bad in stem for bad in NON_TEXT_FONTS):
            continue
        found.add((stem, str(path)))
    return tuple(sorted(found))


def _face_score(stem: str, path: str, prefer: str) -> int:
    heavy = prefer == "heavy"
    order = _HEAVY_ORDER if heavy else _LIGHT_ORDER
    # A filename with no weight token IS the regular cut (Arial.ttf) — which is
    # exactly what body text wants, and only a maybe for display, where the
    # face may instead be single-weight by design (Impact, PressStart2P).
    score = 40 if heavy else 95
    for i, token in enumerate(order):
        if token in stem:
            score = 100 - i * (4 if heavy else 7)
            break
    if "italic" in stem or "oblique" in stem:
        score -= 50
    if path.lower().endswith(".ttc"):
        score -= 8  # collection: Pillow can only address face 0 reliably
    return score


def _is_family(stem: str, key: str) -> bool:
    """True when `stem` is a cut OF family `key`, not merely prefixed by it."""
    if not stem.startswith(key):
        return False
    rest = stem[len(key):]
    return rest == "" or rest.startswith(_STYLE_TOKENS)


# Two unassigned private-use codepoints. A font renders both with the same
# .notdef glyph (the tofu box), which gives us a reference bitmap to compare
# real characters against.
_NOTDEF_PROBES = ("\uE83A", "\uE9B1")


def _render_key(font, char: str) -> bytes:
    box = Image.new("L", (96, 96), 0)
    ImageDraw.Draw(box).text((8, 8), char, font=font, fill=255)
    return box.tobytes()


@lru_cache(maxsize=1024)
def _covers(path: str, charset: str) -> bool:
    """Can this face actually SET this text, or will it come out as tofu boxes?

    This gate matters more than any other font choice here. Store copy is
    English by default, which every face covers — but a game the user asked for
    in another language may need glyphs that display faces (Bodoni, Didot,
    Impact, Anton, Orbitron, Press Start 2P ship Latin only) simply do not have.
    Without the check such a caption composites as a row of empty rectangles —
    which is exactly what it did before this existed.
    """
    if not charset:
        return True
    try:
        font = ImageFont.truetype(path, 40)
        notdef = _render_key(font, _NOTDEF_PROBES[0])
        if notdef != _render_key(font, _NOTDEF_PROBES[1]):
            return True  # can't identify this face's .notdef — don't guess
        return all(ch.isspace() or _render_key(font, ch) != notdef for ch in charset)
    except Exception:
        return False


def _charset(sample: str) -> str:
    """Deduplicated, order-stable probe set for a piece of copy."""
    seen: list[str] = []
    for ch in str(sample or ""):
        if not ch.isspace() and ch not in seen:
            seen.append(ch)
    return "".join(seen[:64])


def _best_face(pool, families, prefer: str, charset: str = "",
               skipped: list | None = None) -> str | None:
    """First family that matches AND can set the copy; weight breaks ties."""
    for family in families:
        key = _norm(family)
        hits = [(stem, path) for stem, path in pool if _is_family(stem, key)]
        if not hits:
            continue
        for stem, path in sorted(hits, key=lambda h: _face_score(h[0], h[1], prefer),
                                 reverse=True):
            if _covers(path, charset):
                return path
        if skipped is not None:
            skipped.append(family)
    return None


def pick_face(families, prefer: str = "heavy", extra_dirs=(), charset: str = "",
              skipped: list | None = None) -> str | None:
    project = [entry for d in extra_dirs for entry in _scan_fonts(d)]
    if project:
        # The game ships its own typeface — use it even if it matches no mood,
        # because listing type that differs from in-game type looks like a
        # different product. Coverage still vetoes: an unreadable title is worse
        # than an off-brand one.
        hit = _best_face(project, families, prefer, charset, skipped)
        if hit:
            return hit
        usable = [e for e in project if _covers(e[1], charset)]
        if usable:
            return max(usable, key=lambda h: _face_score(h[0], h[1], prefer))[1]
    system = [entry for d in FONT_DIRS for entry in _scan_fonts(d)]
    return (_best_face(system, families, prefer, charset, skipped)
            or _best_face(system, FALLBACK_FAMILIES, prefer, charset))


class TypePlan:
    """Resolved faces + the spacing/case the chosen mood asks for.

    `display_text` / `body_text` are the actual copy about to be set. They are
    required, not optional: face selection is only correct once it knows which
    glyphs it has to produce.
    """

    def __init__(self, args, display_text: str = "", body_text: str = "") -> None:
        mood = getattr(args, "type_mood", None) or "bold"
        spec = TYPE_MOODS[mood]
        dirs = tuple(getattr(args, "font_dir", None) or ())
        for d in dirs:
            if not Path(d).expanduser().is_dir():
                warn(f"--font-dir {d} is not a directory — ignoring")
        explicit = getattr(args, "font", None)
        explicit_body = getattr(args, "font_regular", None)
        for flag, value, copy in (("--font", explicit, display_text),
                                  ("--font-regular", explicit_body, body_text)):
            if not value:
                continue
            if not Path(value).is_file():
                die(f"{flag} not found: {value}")
            missing = [c for c in _charset(copy) if not _covers(value, c)]
            if missing:
                die(f"{flag} {Path(value).name} has no glyphs for {''.join(missing)!r} — "
                    "that text would composite as empty boxes. Choose a face that "
                    "covers the copy's alphabet, or drop the flag and let --type-mood pick.")

        self.mood = mood
        display_set, body_set = _charset(display_text), _charset(body_text or display_text)
        self.skipped: list[str] = []
        self.display = explicit or pick_face(
            tuple(spec["display"]) + FALLBACK_FAMILIES, "heavy", dirs,
            charset=display_set, skipped=self.skipped)
        self.body = explicit_body or explicit or pick_face(
            tuple(spec["body"]) + FALLBACK_FAMILIES, "regular", dirs, charset=body_set)
        tracking = getattr(args, "tracking", None)
        self.tracking = spec["tracking"] if tracking is None else tracking
        self.upper = spec["upper"] and not getattr(args, "no_uppercase", False)
        self.outline = getattr(args, "text_outline", 0.0) or 0.0

    def report(self) -> None:
        info(f"type: {self.mood} — display {Path(self.display).name if self.display else 'built-in'}"
             f", body {Path(self.body).name if self.body else 'built-in'}"
             f", tracking {self.tracking:+.2f}em, {'UPPER' if self.upper else 'sentence'} case")
        if self.skipped:
            info(f"skipped {', '.join(self.skipped)} — no glyphs for this copy's alphabet")
        if self.display and any(g in _norm(Path(self.display).stem) for g in GENERIC_FACES):
            warn(f"display face {Path(self.display).name} is a generic UI font — a store title "
                 "set in it reads as 'default Arial'. Point --font-dir at the game's own "
                 "assets/fonts, or install display faces in the image "
                 "(fonts-montserrat / fonts-ebgaramond / fonts-inter).")


def load_font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


_SCRATCH = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def text_width(text: str, font, tracking_px: float) -> float:
    if not tracking_px:
        return _SCRATCH.textlength(text, font=font)
    # Per-glyph advance loses kerning, which is the correct trade at display
    # sizes where the tracking is an explicit design choice.
    return (sum(_SCRATCH.textlength(c, font=font) for c in text)
            + tracking_px * max(0, len(text) - 1))


def _greedy_wrap(words, font, max_w: int, tracking_px: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if not current or text_width(probe, font, tracking_px) <= max_w:
            current = probe
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _balance(words, font, max_w: int, tracking_px: float, count: int) -> list[str] | None:
    """Split `words` into exactly `count` lines with the narrowest widest line.

    Greedy wrapping fills each line to the margin, which for a two-line display
    setting typically leaves one long line and one orphan — and forces a smaller
    size than necessary, since the fit is driven by the longest line. Ties go to
    the longer-line-first shape, which is what centred display type wants.
    """
    n = len(words)
    if count < 2 or n < count:
        return None

    def width(i: int, j: int) -> float:
        return text_width(" ".join(words[i:j]), font, tracking_px)

    from functools import lru_cache as _cache

    @_cache(maxsize=None)
    def solve(start: int, left: int):
        if left == 1:
            w = width(start, n)
            return (w, (n,)) if w <= max_w else (float("inf"), ())
        best = (float("inf"), ())
        for cut in range(start + 1, n - left + 2):
            w = width(start, cut)
            if w > max_w:
                break
            tail, cuts = solve(cut, left - 1)
            worst = max(w, tail)
            if worst < best[0]:
                best = (worst, (cut,) + cuts)
        return best

    worst, cuts = solve(0, count)
    solve.cache_clear()
    if worst == float("inf"):
        return None
    out, prev = [], 0
    for cut in cuts:
        out.append(" ".join(words[prev:cut]))
        prev = cut
    return out


def wrap_lines(text: str, font, max_w: int, tracking_px: float = 0.0) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        greedy = _greedy_wrap(words, font, max_w, tracking_px)
        balanced = _balance(words, font, max_w, tracking_px, len(greedy))
        lines.extend(balanced or greedy)
    return [ln for ln in lines if ln != ""] or [""]


def fit_text(text: str, font_path: str | None, max_w: int, max_h: int,
             max_size: int, min_size: int = 14, spacing: float = 1.16,
             max_lines: int = 3, tracking: float = 0.0):
    """Largest size at which `text` wraps inside max_w×max_h and max_lines.

    Returns (font, lines, total_height, line_step, tracking_px).
    """
    def measure(size: int):
        font = load_font(font_path, size)
        tracking_px = tracking * size
        lines = wrap_lines(text, font, max_w, tracking_px)
        line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
        step = int(line_h * spacing)
        widest = max(text_width(ln, font, tracking_px) for ln in lines)
        return font, lines, len(lines) * step, step, widest, tracking_px

    lo, hi, best = min_size, max(min_size, max_size), None
    while lo <= hi:
        mid = (lo + hi) // 2
        font, lines, total, step, widest, tpx = measure(mid)
        if total <= max_h and widest <= max_w and len(lines) <= max_lines:
            best = (font, lines, total, step, tpx)
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        font, lines, total, step, _, tpx = measure(min_size)
        best = (font, lines, total, step, tpx)
    return best


def _draw_tracked(draw: ImageDraw.ImageDraw, xy, text: str, font,
                  tracking_px: float, **kw) -> None:
    if not tracking_px:
        draw.text(xy, text, font=font, **kw)
        return
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, **kw)
        x += _SCRATCH.textlength(char, font=font) + tracking_px


def _lines_mask(size, lines, font, tracking_px, x, y, w, step,
                stroke: int = 0) -> Image.Image:
    """Alpha coverage of the text block — the substrate every effect paints on."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    cy = y
    for line in lines:
        lx = x + (w - text_width(line, font, tracking_px)) / 2
        _draw_tracked(draw, (lx, cy), line, font, tracking_px, fill=255,
                      stroke_width=stroke, stroke_fill=255 if stroke else None)
        cy += step
    return mask


def _shift(mask: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("L", mask.size, 0)
    out.paste(mask, (dx, dy))
    return out


def _scaled(mask: Image.Image, alpha: int) -> Image.Image:
    return mask if alpha >= 255 else mask.point(lambda v: v * alpha // 255)


def _fill_layer(mask: Image.Image, c1, c2=None) -> Image.Image:
    """Paint `mask` with a flat colour, or a vertical c1→c2 ramp across it.

    The ramp spans the text's own bounding box rather than the canvas, so a
    caption near the top and a title near the bottom get the same gradient.
    """
    if not c2 or tuple(c2[:3]) == tuple(c1[:3]):
        layer = Image.new("RGBA", mask.size, tuple(c1[:3]) + (0,))
        layer.putalpha(_scaled(mask, c1[3]))
        return layer
    box = mask.getbbox()
    rgb = Image.new("RGB", mask.size, tuple(c1[:3]))
    if box:
        bw, bh = max(1, box[2] - box[0]), max(1, box[3] - box[1])
        rgb.paste(gradient((bw, bh), [(0.0, c1), (1.0, c2)]).convert("RGB"), (box[0], box[1]))
    layer = rgb.convert("RGBA")
    layer.putalpha(_scaled(mask, c1[3]))
    return layer


def draw_text_block(base: Image.Image, text: str, box: tuple[int, int, int, int],
                    font_path: str | None, colour, max_size: int,
                    valign: str = "center", max_lines: int = 3,
                    colour2=None, tracking: float = 0.0, uppercase: bool = False,
                    outline: float = 0.0, outline_colour=(0, 0, 0, 235),
                    shadow: float = 0.55, min_size: int = 14) -> tuple[int, int]:
    """Draw auto-fitted, centred display text inside box=(x,y,w,h).

    Rendering goes through an alpha mask so the fill can be a gradient and the
    shadow can be a real blur. The old approach — a hard offset copy plus a
    thick stroke — is what makes generated titles read as clip art.

    Returns (top, height) of the drawn block so callers can stack elements.
    """
    x, y, w, h = box
    if not text.strip():
        return (y, 0)
    if uppercase:
        text = text.upper()
    font, lines, total, step, tracking_px = fit_text(
        text, font_path, w, h, max_size, min_size=min_size,
        max_lines=max_lines, tracking=tracking)
    top = y if valign == "top" else (y + h - total if valign == "bottom" else y + (h - total) // 2)

    mask = _lines_mask(base.size, lines, font, tracking_px, x, top, w, step)

    if shadow > 0:
        blur = max(1.0, font.size * 0.055)
        drop = max(1, round(font.size * 0.05))
        smoke = _shift(mask, 0, drop).filter(ImageFilter.GaussianBlur(blur))
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        layer.putalpha(_scaled(smoke, int(max(0.0, min(1.0, shadow)) * 255)))
        base.alpha_composite(layer)

    if outline > 0:
        width = max(1, round(font.size * outline))
        edge = _lines_mask(base.size, lines, font, tracking_px, x, top, w, step, stroke=width)
        base.alpha_composite(_fill_layer(edge, outline_colour))

    base.alpha_composite(_fill_layer(mask, colour, colour2))
    return (top, total)


def accent_rule(base: Image.Image, cx: int, top: int, width: int, height: int,
                c1, c2=None) -> None:
    """Short rounded bar — the cheapest mark that says a human set this type."""
    width, height = max(4, width), max(2, height)
    bar = gradient((width, height), [(0.0, c1), (1.0, c2 or c1)], horizontal=True)
    bar.putalpha(rr_mask((width, height), height // 2))
    base.alpha_composite(bar, (cx - width // 2, top))


def scrim(base: Image.Image, box: tuple[int, int, int, int], strength: float = 0.72,
          from_top: bool = False, ramp: float = 0.34) -> None:
    """Gradient darkening behind text so contrast holds over busy art.

    The ramp is the *fade* zone only; past it the scrim holds full strength, so
    text placed inside the box always sits on a predictable floor. A scrim that
    is still fading where the words are is the classic unreadable-caption bug.
    """
    x, y, w, h = box
    if w <= 0 or h <= 0:
        return
    a = int(max(0.0, min(1.0, strength)) * 255)
    r = max(0.02, min(0.9, ramp))
    stops = ([(0.0, (0, 0, 0, a)), (1.0 - r, (0, 0, 0, a)), (1.0, (0, 0, 0, 0))]
             if from_top else
             [(0.0, (0, 0, 0, 0)), (r, (0, 0, 0, a)), (1.0, (0, 0, 0, a))])
    base.alpha_composite(gradient((w, h), stops), (x, y))


# ───────────────────────────── device frame ─────────────────────────────────

def device_frame(shot: Image.Image, style: str = "ios") -> Image.Image:
    """Draw a phone around `shot`. Frame geometry follows the shot's aspect."""
    sw, sh = shot.size
    bezel = max(4, round(sw * 0.030))          # black glass border
    rail = max(3, round(sw * 0.018))           # metal side rail
    s_radius = round(sw * 0.082)
    inset = bezel + rail
    bw, bh = sw + 2 * inset, sh + 2 * inset
    b_radius = s_radius + inset

    body = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))

    # Metal rail: horizontal sheen so the edge reads as brushed aluminium.
    rail_art = gradient((bw, bh), [
        (0.00, (72, 74, 82, 255)),
        (0.06, (214, 217, 224, 255)),
        (0.16, (140, 144, 154, 255)),
        (0.50, (238, 240, 246, 255)),
        (0.84, (140, 144, 154, 255)),
        (0.94, (214, 217, 224, 255)),
        (1.00, (72, 74, 82, 255)),
    ], horizontal=True)
    body.paste(rail_art, (0, 0), rr_mask((bw, bh), b_radius))

    # Black glass slab inside the rail.
    glass_w, glass_h = bw - 2 * rail, bh - 2 * rail
    glass = Image.new("RGBA", (glass_w, glass_h), (11, 11, 15, 255))
    body.paste(glass, (rail, rail), rr_mask((glass_w, glass_h), s_radius + bezel))

    # The screenshot itself.
    body.paste(shot, (inset, inset), rr_mask((sw, sh), s_radius))

    overlay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    if style == "ios":
        nw, nh = round(sw * 0.42), round(sw * 0.078)
        nx, ny = inset + (sw - nw) // 2, inset - 1
        notch = Image.new("RGBA", (nw, nh), (8, 8, 11, 255))
        notch_mask = rr_mask((nw, nh), nh // 2)
        # Square off the top edge so the notch merges into the bezel.
        ImageDraw.Draw(notch_mask).rectangle([0, 0, nw - 1, nh // 2], fill=255)
        overlay.paste(notch, (nx, ny), notch_mask)
        slit_w, slit_h = round(nw * 0.30), max(2, round(nh * 0.13))
        slit_x, slit_y = nx + (nw - slit_w) // 2 - round(nw * 0.05), ny + (nh - slit_h) // 2
        od.rounded_rectangle([slit_x, slit_y, slit_x + slit_w, slit_y + slit_h],
                             radius=slit_h // 2, fill=(48, 50, 58, 255))
        cam_r = max(2, round(nh * 0.17))
        cam_x = slit_x + slit_w + round(nw * 0.10)
        cam_cy = ny + nh // 2
        od.ellipse([cam_x - cam_r, cam_cy - cam_r, cam_x + cam_r, cam_cy + cam_r],
                   fill=(26, 30, 44, 255))
        od.ellipse([cam_x - cam_r // 2, cam_cy - cam_r // 2, cam_x, cam_cy],
                   fill=(60, 88, 130, 255))
        bar_w, bar_h = round(sw * 0.36), max(3, round(sw * 0.011))
        bar_x, bar_y = inset + (sw - bar_w) // 2, inset + sh - round(sw * 0.032)
        od.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                             radius=bar_h // 2, fill=(255, 255, 255, 205))
    else:  # android — punch-hole camera, gesture pill
        cam_r = max(3, round(sw * 0.017))
        cam_x, cam_y = inset + sw // 2, inset + round(sw * 0.042)
        od.ellipse([cam_x - cam_r, cam_y - cam_r, cam_x + cam_r, cam_y + cam_r],
                   fill=(10, 10, 14, 255))
        od.ellipse([cam_x - cam_r + 2, cam_y - cam_r + 2, cam_x + cam_r - 2, cam_y + cam_r - 2],
                   fill=(30, 40, 62, 255))
        bar_w, bar_h = round(sw * 0.30), max(3, round(sw * 0.009))
        bar_x, bar_y = inset + (sw - bar_w) // 2, inset + sh - round(sw * 0.028)
        od.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                             radius=bar_h // 2, fill=(255, 255, 255, 190))

    # Side buttons riding the rail.
    btn_w = max(2, rail)
    for y0, y1 in ((0.19, 0.25), (0.28, 0.37), (0.39, 0.48)):
        od.rounded_rectangle([0, int(bh * y0), btn_w + 1, int(bh * y1)],
                             radius=btn_w, fill=(96, 99, 108, 255))
    od.rounded_rectangle([bw - btn_w - 2, int(bh * 0.30), bw - 1, int(bh * 0.44)],
                         radius=btn_w, fill=(96, 99, 108, 255))

    # Glass reflection: one hard diagonal band, the classic mockup tell.
    glare = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(glare).polygon(
        [(0, 0), (int(bw * 0.92), 0), (0, int(bh * 0.62))], fill=(255, 255, 255, 26)
    )
    ImageDraw.Draw(glare).polygon(
        [(0, 0), (int(bw * 0.44), 0), (0, int(bh * 0.30))], fill=(255, 255, 255, 16)
    )
    overlay.alpha_composite(glare)

    body.alpha_composite(Image.composite(
        overlay, Image.new("RGBA", (bw, bh), (0, 0, 0, 0)), rr_mask((bw, bh), b_radius)
    ))
    return body


def build_device(shot_path: str, screen_w: int, style: str) -> Image.Image:
    shot = load_image(shot_path, "screenshot")
    scale = screen_w / shot.width
    shot = shot.resize((screen_w, max(1, round(shot.height * scale))), RES)
    if style == "none":
        rounded = Image.new("RGBA", shot.size, (0, 0, 0, 0))
        rounded.paste(shot, (0, 0), rr_mask(shot.size, round(screen_w * 0.055)))
        return rounded
    return device_frame(shot, style)


def treat_background(bg: Image.Image, treatment: str) -> Image.Image:
    """Push the background back so the device stays the focal point."""
    if treatment == "none":
        return bg
    presets = {"soft": (0.0035, 0.14), "blur": (0.010, 0.22), "dim": (0.0, 0.28)}
    blur_frac, dim = presets.get(treatment, presets["soft"])
    out = bg
    if blur_frac:
        out = out.filter(ImageFilter.GaussianBlur(max(1.0, out.width * blur_frac)))
    if dim:
        veil = Image.new("RGBA", out.size, (0, 0, 0, int(dim * 255)))
        out = Image.alpha_composite(out, veil)
    return out


# ───────────────────────────── grade ────────────────────────────────────────
#
# A listing is judged as a strip of ~150px thumbnails standing next to nine
# competitors, and raw image-model output almost always arrives a stop flat and
# a shade desaturated for that context. Reviewers read it as "washed out" and
# ask for the same two things every time: more saturation, more light. So the
# grade is part of composition here, not an optional post-step — every art path
# applies one by default and `--pop off` opts out.
#
# The saturation lift is *vibrance*, not a flat multiply: the boost is weighted
# by how unsaturated a pixel already is, so a sky or a gold rim gains while an
# already-screaming neon does not clip into a flat patch. Brightness is a gamma
# lift, which moves midtones and mathematically cannot blow a highlight out.
# Contrast is a smoothstep blend, which cannot crush a shadow to black. The
# bloom — a screen-blended blur of the highlights — is what actually reads as
# "brighter" once the image is thumbnail-sized.

LUMA = np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32)

POP_PRESETS: dict[str, tuple[float, float, float, float]] = {
    # name:  vibrance, lift, contrast, bloom
    "off":   (0.00, 0.00, 0.00, 0.00),
    "soft":  (0.14, 0.03, 0.06, 0.10),
    "vivid": (0.30, 0.07, 0.12, 0.22),
    "max":   (0.48, 0.12, 0.18, 0.36),
}
DEFAULT_POP = "vivid"


def pop_grade(img: Image.Image, preset: str = DEFAULT_POP, *,
              vibrance: float | None = None, lift: float | None = None,
              contrast: float | None = None, bloom: float | None = None) -> Image.Image:
    """Saturate and brighten generated art so it survives thumbnail review."""
    if preset not in POP_PRESETS:
        die(f"--pop {preset}: choose one of {', '.join(POP_PRESETS)}")
    p_vib, p_lift, p_con, p_bloom = POP_PRESETS[preset]
    vib = p_vib if vibrance is None else vibrance
    lft = p_lift if lift is None else lift
    con = p_con if contrast is None else contrast
    blm = p_bloom if bloom is None else bloom
    if max(abs(vib), abs(lft), abs(con), abs(blm)) < 1e-4:
        return img

    src = img.convert("RGBA")
    arr = np.asarray(src, dtype=np.float32) / 255.0
    rgb, alpha = arr[..., :3].copy(), arr[..., 3:]

    if con:
        rgb = rgb * (1.0 - con) + (rgb * rgb * (3.0 - 2.0 * rgb)) * con
    if lft:
        rgb = np.power(np.clip(rgb, 0.0, 1.0), 1.0 / (1.0 + 2.0 * lft))
    if vib:
        luma = (rgb * LUMA).sum(axis=-1, keepdims=True)
        sat = rgb.max(axis=-1, keepdims=True) - rgb.min(axis=-1, keepdims=True)
        rgb = np.clip(luma + (rgb - luma) * (1.0 + vib * (1.0 - sat)), 0.0, 1.0)
    if blm:
        knee = 0.72
        luma = (rgb * LUMA).sum(axis=-1, keepdims=True)
        highlights = np.clip((luma - knee) / (1.0 - knee), 0.0, 1.0)
        halo = Image.fromarray(
            (np.clip(rgb * highlights, 0.0, 1.0) * 255 + 0.5).astype(np.uint8), "RGB")
        halo = halo.filter(ImageFilter.GaussianBlur(
            max(2.0, min(img.width, img.height) * 0.012)))
        h = np.asarray(halo, dtype=np.float32) / 255.0
        rgb = 1.0 - (1.0 - rgb) * (1.0 - np.clip(h * blm, 0.0, 1.0))

    out = np.concatenate([np.clip(rgb, 0.0, 1.0), alpha], axis=-1)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def desaturate(img: Image.Image, amount: float) -> Image.Image:
    """Pull colour toward luma — used to push a backdrop behind live UI."""
    a = max(0.0, min(1.0, amount))
    if a <= 0:
        return img
    arr = np.asarray(img.convert("RGBA"), dtype=np.float32)
    rgb, alpha = arr[..., :3], arr[..., 3:]
    luma = (rgb * LUMA).sum(axis=-1, keepdims=True)
    mixed = np.concatenate([rgb + (luma - rgb) * a, alpha], axis=-1)
    return Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8), "RGBA")


def vignette(img: Image.Image, strength: float) -> Image.Image:
    """Darken the corners so the centre of a backdrop keeps the eye."""
    s = max(0.0, min(1.0, strength))
    if s <= 0:
        return img
    w, h = img.size
    nx = (np.linspace(0.0, 1.0, w, dtype=np.float32) * 2.0 - 1.0)[None, :]
    ny = (np.linspace(0.0, 1.0, h, dtype=np.float32) * 2.0 - 1.0)[:, None]
    r = np.sqrt(nx * nx + ny * ny) / math.sqrt(2.0)
    falloff = np.clip((r - 0.45) / 0.55, 0.0, 1.0) ** 1.6
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.putalpha(Image.fromarray((falloff * s * 255).astype(np.uint8), "L"))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def calm(img: Image.Image, strength: float) -> Image.Image:
    """Push a backdrop back so the live field, HUD and buttons stay readable.

    The same picture, still recognisably the store's key art — just no longer
    competing with the reels drawn on top of it.
    """
    s = max(0.0, min(1.0, strength))
    if s <= 0:
        return img
    out = img.filter(ImageFilter.GaussianBlur(max(1.0, img.width * 0.016 * s)))
    out = desaturate(out, 0.35 * s)
    veil = Image.new("RGBA", out.size, (0, 0, 0, int(0.55 * s * 255)))
    return Image.alpha_composite(out.convert("RGBA"), veil)


# ──────────────────────── seams, gutters and props ──────────────────────────
#
# THE PANELS MUST REASSEMBLE INTO THE WHOLE PICTURE. Lay them side by side and
# the panorama has to come back exactly as it was drawn — not a millimetre of it
# missing anywhere. That is the contract, and it is why `--gutter` defaults to 0:
# panel i ends on the very column panel i+1 begins on, so nothing is discarded
# between them and the set is one picture cut into parts.
#
# The alternative — composing wider than N panels and throwing a strip away at
# each cut, so the store's own carousel gap stands in for the discarded strip —
# is still reachable as `--gutter 100`, because some publishers ask for it. It
# buys alignment on the listing page at the price of a hole in the picture: every
# panel then ends mid-object wherever the cut fell, which is exactly the "it cuts
# too much" the default exists to avoid. Opt-in, never automatic.
#
# What protects a seam now is WHERE it falls, not what is removed there: the
# whole tiling slides (`--seam-snap`) until the cuts land on quiet columns, and
# Phase 1 asks the art for a calm vertical corridor at each panel boundary.

GUTTER_REF_W = 1320   # the App Store 6.9" panel the allowance was measured on
GUTTER_REF_PX = 100   # the allowance publishers ask for at that panel width
DEFAULT_GUTTER = "0"  # lossless by default: the panels reassemble the picture


def parse_gutter(spec: str, panel_w: int) -> int:
    """`auto` | pixels (`100`) | a fraction of the panel (`7.5%`) → pixels."""
    text = str(spec).strip().lower()
    if text in ("", "auto"):
        return round(panel_w * GUTTER_REF_PX / GUTTER_REF_W)
    try:
        px = (round(panel_w * float(text[:-1]) / 100.0) if text.endswith("%")
              else int(round(float(text))))
    except ValueError:
        die(f"--gutter {spec}: expected auto, pixels (100) or a percentage (7.5%)")
    if px < 0:
        die(f"--gutter {spec}: a seam allowance cannot be negative")
    if px > panel_w * 0.25:
        die(f"--gutter {px}px is more than a quarter of a {panel_w}px panel — "
            "that is not a seam allowance, that is a missing slice")
    return px


# Where the allowance is TAKEN OUT is as important as how wide it is.
#
# A fixed allowance at a fixed fraction of the width is content-blind: it throws
# the strip away wherever the arithmetic lands it, and when that is across a
# face, a coin or the board's edge, the panel simply stops mid-object. The note
# that comes back is "it cuts too much, the picture breaks" — not because 100px
# is the wrong number, but because it was removed from the worst possible place.
#
# So the panorama is composed with a little slack and the cuts are allowed to
# slide inside it: the picture's own column energy chooses where the strips come
# out, and they settle on quiet background — sky, wall, floor, haze — instead of
# through the subject. The allowance itself stays the publisher's ~100px.

SNAP_REF = 0.12            # search radius, as a fraction of one panel width
DEFAULT_SNAP = "auto"
SNAP_GAP_DRIFT = 0.40      # how far ONE allowance may drift from the nominal width
SEAM_HOT = 1.35            # detail ratio at which a seam is cutting a subject
CAROUSEL_GAP = 0.045       # the store's own gap between thumbnails, ~ per panel width


def parse_snap(spec: str, panel_w: int) -> int:
    """`auto` | `off`/`0` | pixels | a percentage of the panel → radius in px."""
    text = str(spec).strip().lower()
    if text in ("", "auto"):
        return round(panel_w * SNAP_REF)
    if text in ("off", "none"):
        return 0
    try:
        px = (round(panel_w * float(text[:-1]) / 100.0) if text.endswith("%")
              else int(round(float(text))))
    except ValueError:
        die(f"--seam-snap {spec}: expected auto, off, pixels (60) or a percentage (5%)")
    if px < 0:
        die(f"--seam-snap {spec}: a search radius cannot be negative")
    if px > panel_w * 0.15:
        die(f"--seam-snap {px}px is more than 15% of a {panel_w}px panel — the cuts "
            "would wander far enough to change what each panel is about")
    return px


def panel_span(index: int, panel_w: int, gutter: int) -> tuple[int, int]:
    """Left/right x of panel `index` inside the gutter-aware panorama."""
    left = index * (panel_w + gutter)
    return left, left + panel_w


def uniform_spans(panels: int, panel_w: int, gutter: int,
                  margin: int = 0) -> list[tuple[int, int]]:
    """The evenly spaced cuts: every panel a gutter apart, no snapping."""
    return [(margin + left, margin + right)
            for left, right in (panel_span(i, panel_w, gutter) for i in range(panels))]


def _edge_map(pano: Image.Image, small_h: int) -> tuple[np.ndarray, float]:
    """Edge magnitude of the picture at `small_h`, plus the downscale factor."""
    scale = small_h / pano.height
    small_w = max(16, round(pano.width * scale))
    grey = np.asarray(pano.convert("L").resize((small_w, small_h), RES), dtype=np.float32)
    dx = np.zeros_like(grey)
    dx[:, 1:] = np.abs(np.diff(grey, axis=1))
    dy = np.zeros_like(grey)
    dy[1:, :] = np.abs(np.diff(grey, axis=0))
    return dx + dy, scale


def _column_energy(pano: Image.Image, small_h: int = 320) -> tuple[np.ndarray, float]:
    """Per-column edge energy of the picture, plus the downscale factor.

    A vision pass can miss a seam running through a hand or a coin; column edge
    energy cannot, and it is cheap enough to evaluate thousands of candidate
    cuts against.
    """
    energy, scale = _edge_map(pano, small_h)
    return energy.mean(axis=0), scale


def _strip_energy(column: np.ndarray, scale: float, x0: int, width: int,
                  probe: int) -> float:
    """Mean column energy over the strip the cut discards at `x0`."""
    a = int(round(x0 * scale))
    b = int(round((x0 + width) * scale))
    if b - a < 2:  # butt-joint: measure a thin band across the cut instead
        mid = (a + b) // 2
        a, b = mid - probe, mid + probe
    a = max(0, min(column.size - 1, a))
    b = max(a + 1, min(column.size, b))
    return float(column[a:b].mean())


def plan_panel_spans(pano: Image.Image, panels: int, panel_w: int, gutter: int,
                     radius: int) -> list[tuple[int, int]]:
    """Choose where to cut so the discarded strips land on calm background.

    The panels keep their exact store size and each allowance keeps very nearly
    its nominal width; what moves is where the strips are taken from. The whole
    tiling may slide within `radius`, and each individual allowance may drift a
    little around the nominal one — which together is what stops a panel ending
    halfway through the hero's face, the failure a fixed 1/3, 2/3 split produces
    the moment the art is not conveniently empty there.

    The allowance itself is the publisher's number and stays close to it: a cut
    that "solved" a seam by shrinking the gap to nothing would just bring back
    the displacement the gutter exists to prevent.
    """
    slack = pano.width - (panels * panel_w + (panels - 1) * gutter)
    if radius <= 0 or slack <= 0 or panels < 2:
        return uniform_spans(panels, panel_w, gutter, margin=max(0, slack // 2))

    column, scale = _column_energy(pano)
    reference = float(column.mean()) or 1.0
    probe = max(1, round(panel_w * 0.02 * scale))
    step = max(2, round(panel_w * 0.005))
    # `--gutter 0` is an explicit butt-joint: the tiling may still slide as a
    # whole, but no cut is allowed to open a gap the caller said not to leave.
    tol = min(radius, round(gutter * SNAP_GAP_DRIFT))

    # State = how far the tiling has slid right of the panorama's left edge, so
    # the search stays a few dozen states wide however many panels there are.
    offsets = list(range(0, slack + 1, step))
    if offsets[-1] != slack:
        offsets.append(slack)
    home = min(offsets, key=lambda o: abs(o - slack / 2))  # the even split
    # A drifting allowance is only worth taking for a real gain, so pay a small,
    # bounded price for leaving the publisher's nominal width behind.
    drift_cost = 0.08 * reference

    best = {o: 0.0 for o in offsets}
    back: list[dict[int, int]] = []
    for seam in range(panels - 1):
        nxt: dict[int, float] = {}
        prev: dict[int, int] = {}
        for o_from in offsets:
            base = best[o_from]
            cut = o_from + (seam + 1) * panel_w + seam * gutter
            for o_to in offsets:
                drift = o_to - o_from
                if abs(drift) > tol:
                    continue
                width = gutter + drift
                if width < 0 or cut + width + panel_w > pano.width:
                    continue
                cost = (base + _strip_energy(column, scale, cut, width, probe)
                        + (drift_cost * abs(drift) / tol if tol else 0.0))
                if o_to not in nxt or cost < nxt[o_to]:
                    nxt[o_to] = cost
                    prev[o_to] = o_from
        if not nxt:  # nothing reachable: keep the even split rather than guess
            return uniform_spans(panels, panel_w, gutter, margin=slack // 2)
        best = nxt
        back.append(prev)

    end = min(best, key=best.get)
    chain = [end]
    for prev in reversed(back):
        chain.append(prev[chain[-1]])
    chain.reverse()

    spans: list[tuple[int, int]] = []
    for i, offset in enumerate(chain):
        left = offset + i * (panel_w + gutter)
        spans.append((left, left + panel_w))
    if spans[-1][1] > pano.width:  # numeric safety net; never expected
        return uniform_spans(panels, panel_w, gutter, margin=slack // 2)

    if chain[0] != home:
        info(f"panorama slid {chain[0] - home:+d}px inside its slack so the cuts miss "
             f"the subjects")
    for i in range(1, panels):
        gap = spans[i][0] - spans[i - 1][1]
        if gap != gutter:
            info(f"seam {i}→{i + 1}: allowance {gap}px ({gap - gutter:+d}px) — "
                 f"taken out of calmer ground")
    return spans


def seam_report(pano: Image.Image, spans: list[tuple[int, int]]) -> None:
    """Measure how busy the picture is exactly where the store will cut it.

    Ratios near 1.0 mean the cuts land on calm background. Anything well above
    the picture's average means a subject is being sliced, and the panel will
    look like it stops mid-object on the listing page.
    """
    if len(spans) < 2:
        return
    panel_w = spans[0][1] - spans[0][0]
    column, scale = _column_energy(pano)
    reference = float(column.mean()) or 1.0
    probe = max(1, round(panel_w * 0.02 * scale))

    hot: list[tuple[int, float]] = []
    for i in range(1, len(spans)):
        x0 = spans[i - 1][1]
        width = spans[i][0] - x0
        ratio = _strip_energy(column, scale, x0, width, probe) / reference
        info(f"seam {i}→{i + 1}: detail {ratio:.2f}× the picture's average")
        if ratio > SEAM_HOT:
            hot.append((i, ratio))
    for i, ratio in hot:
        warn(f"seam {i}→{i + 1} runs through the busiest part of the picture "
             f"({ratio:.2f}× average) — a subject is being cut there, and no cut "
             f"inside the search radius avoided it. Widen --seam-snap, slide the crop "
             f"(--zoom 1.15 --offset ±0.3), or regenerate the art with calm space "
             f"{i}/{len(spans)} of the way across.")


# Is the picture actually a picture?
#
# The other half of the same complaint is that the art comes back "too simple,
# too boring": a gradient, a glow, one object, and acres of empty. That reads as
# a placeholder backdrop in a strip of thumbnails standing next to nine finished
# listings, and no amount of grading rescues it. Flatness is measurable — a
# finished illustration keeps detail across most of its area, a backdrop does
# not — so it is measured here rather than left to a vision pass that has
# already accepted it once.

FLAT_LEVEL = 3.0     # local activity below this reads as empty ground
FLAT_SHARE = 0.55    # more of the panel than this being empty = a backdrop
THIN_DETAIL = 4.0    # mean activity below this = nothing is going on at all


def detail_report(pano: Image.Image, spans: list[tuple[int, int]]) -> list[float]:
    """Per-panel richness: how much of each panel carries any detail at all."""
    energy, scale = _edge_map(pano, 360)
    small_w = energy.shape[1]
    # Local activity, not per-pixel edges: a smooth gradient scores zero either
    # way, but ornament, texture, particles and material breakup survive the
    # blur, which is exactly the difference between an illustration and a wash.
    activity = np.asarray(
        Image.fromarray(energy.clip(0, 255).astype(np.uint8))
        .filter(ImageFilter.BoxBlur(4)), dtype=np.float32)

    shares: list[float] = []
    for i, (left, right) in enumerate(spans):
        a = max(0, int(round(left * scale)))
        b = min(small_w, max(a + 1, int(round(right * scale))))
        panel = activity[:, a:b]
        flat = float((panel < FLAT_LEVEL).mean())
        mean = float(panel.mean())
        shares.append(flat)
        info(f"panel {i + 1}: detail {mean:.1f}, {flat * 100:.0f}% of it empty ground")
        if flat > FLAT_SHARE:
            reason = (f"{flat * 100:.0f}% of it is empty ground — a subject on a wash, "
                      "with no background place and nothing carrying the quiet areas")
        elif mean < THIN_DETAIL:
            reason = (f"its detail measures {mean:.1f} — the shapes are there but they "
                      "are flat fills: no material texture, ornament or secondary light "
                      "anywhere in the frame")
        else:
            continue
        warn(f"panel {i + 1} reads as a backdrop, not a finished illustration: {reason}. "
             "Beside a competitor's listing that reads as a placeholder. Regenerate the "
             "art with three occupied depth planes, ornament at more than one scale, a "
             "second light source, differentiated materials, and atmosphere through the "
             "empty region — do not grade or crop it into looking finished.")
    return shares


def crown_report(pano: Image.Image, span: tuple[int, int], hero_top: int,
                 panel: int = 1) -> float | None:
    """How decorated the band above the hero's head is, on panel 1.

    The hero now fills most of the panel's height, which leaves one band above
    its head — and that band is what the note "more decorative" is about. A
    berth drawn as a place to *stand* leaves sky there; a berth drawn as an
    ornament around the character fills it with the arch, the crest, the banner,
    the hanging lamps and the light burst the figure's head sits inside. The
    difference is the whole distance between a screenshot and a poster, and it
    is measurable the same way panel emptiness is.

    Returns the band's empty share, or None when the hero is so tall there is no
    band left to judge.
    """
    left, right = span
    if hero_top <= pano.height * 0.06:
        return None
    energy, scale = _edge_map(pano, 360)
    activity = np.asarray(
        Image.fromarray(energy.clip(0, 255).astype(np.uint8))
        .filter(ImageFilter.BoxBlur(4)), dtype=np.float32)
    a = max(0, int(round(left * scale)))
    b = min(activity.shape[1], max(a + 1, int(round(right * scale))))
    bottom = min(activity.shape[0], max(1, int(round(hero_top * scale))))
    band = activity[:bottom, a:b]
    flat = float((band < FLAT_LEVEL).mean())
    mean = float(band.mean())
    info(f"panel {panel} crown: detail {mean:.1f}, {flat * 100:.0f}% of the "
         f"{hero_top / pano.height:.0%} of the panel above the hero's head is empty")
    if flat > FLAT_SHARE or mean < THIN_DETAIL:
        warn(f"the band above the hero's head on panel {panel} is empty sky: the "
             "berth was drawn as a place to stand, not as an ornament around the "
             "character. "
             "That band is the one the store shows at full size and it is what makes "
             "the slide read as decorated — ask Phase 1 for the berth as a framing "
             "device (arch, portal, crest, banner, drapery, flanking lanterns or "
             "columns, a light burst behind where the head will be, embers or petals "
             "drifting through it) and regenerate. Do not answer it by scaling the "
             "hero up into the gap — a cropped head is not ornament.")
    return flat


# How auto-placed game objects are sized, where they land, and how they are
# seated INTO the picture rather than onto it.
#
# The publisher's designer sent the first kit back with two notes: the acting
# character was not on the first screen, and the game's own objects were "not
# worked into the design at all, and far too small" — pasted on rather than built
# in. Their own reference leads with the character filling most of the leftmost
# panel and carries the symbols large in the foreground, lit by the same scene.
#
# So: the first object is the HERO and it takes panel 1, props are about a third
# of a panel wide instead of a fifth, everything is anchored by its FOOT so it
# stands on the picture's ground plane (the nearest ones deliberately running
# off the bottom edge, the way a real foreground element does), and every object
# is seated with a contact shadow, an edge light-wrap and a colour cast sampled
# from the art underneath it.
#
# The next round of notes went one step further: "not just insert a player —
# the slide itself has to contain the player, as its context". A cutout that is
# lit correctly but sits in front of *everything* still reads as a layer. So the
# hero is also OCCLUDED: after it is pasted, the scene's own foreground band is
# composited back over its feet, which is the one cue that says the picture was
# drawn around it. Phase 1 draws the berth, this closes the scene over it.

# The round after that asked for one more thing on the same screenshot: "the
# player on the first slide should be bigger and more decorative — full height,
# but not too much". Sizing the hero by WIDTH is what made it small: a 0.58×
# panel-width figure on a 1320×2868 panel is barely 40% of the panel's height,
# which reads as a person standing in a landscape. So the hero is sized by its
# HEIGHT — it fills HERO_H of the panel — and the width is only a cap. The
# headroom left above the head is deliberate and is the "not too much" half of
# the note: it is where the berth's ornament lives (arch, crest, banner, the
# light burst behind the head), and it is what keeps "bigger" from becoming
# "cropped at the neck".
HERO_H = 0.72                     # of the panel's HEIGHT — the driver
HERO_W = 0.86                     # of the panel's WIDTH — a cap, not a target
HERO_MIN_H = 0.60                 # below this the figure is scenery again
HERO_X, HERO_FOOT = 0.47, 1.04    # foot past the frame: the hero stands in front
HERO_OCCLUDE = 0.14               # of its height, taken back by the foreground
PROP_H = 0.42                     # height cap for a supporting object
PROP_OCCLUDE = 0.08               # props also sit behind scene furniture, not on it
# Cycled, so props read as a composed scene at three depths instead of a row of
# stickers at one height and one size.
_PROP_W = (0.36, 0.29, 0.33, 0.26, 0.30)
_PROP_X = (0.34, 0.66, 0.50, 0.30, 0.70)
_PROP_FOOT = (1.02, 0.88, 0.97, 0.84, 1.00)
# The play field built out of the game's REAL symbols (`boardplate`). It is the
# picture's mechanic, so it takes the middle panel at nearly full width and
# stands inside the frame instead of bleeding off the bottom like a foreground
# prop — a board cropped by the edge stops reading as a board. The middle panel
# is the slide that was called boring, and half of the answer is size: the field
# is the subject of that screenshot, not an illustration of one. The other half
# is that it must be caught mid-round rather than at rest (`boardplate --win`).
BOARD_W, BOARD_H = 0.78, 0.56
BOARD_X, BOARD_FOOT = 0.50, 0.88
CROWDED = 5                       # past this the same designer says it is a heap
DEFAULT_SPRITE_LIGHT = 0.35       # how hard an object is pulled into the scene
_SPRITE_KEYS = ("x", "y", "w", "h", "rot", "glow", "shadow", "opacity", "panel",
                "bleed", "contact", "light", "occlude")
_SPRITE_FLAGS = ("hero", "prop", "board")


def parse_sprite_spec(spec: str) -> dict:
    """`path[@hero|prop,x=0.3,y=0.6,w=0.34,rot=-8,bleed=0.05,contact=0.6,...]`."""
    path, _, tail = str(spec).partition("@")
    path = path.strip()
    if not path:
        die("--sprite needs a PNG path")
    out: dict = {"path": path}
    for chunk in (c.strip() for c in tail.split(",") if c.strip()):
        key, sep, value = chunk.partition("=")
        key = key.strip().lower()
        if not sep and key in _SPRITE_FLAGS:
            out["role"] = key
            continue
        if not sep or key not in _SPRITE_KEYS:
            die(f"--sprite {spec}: unusable placement key {chunk!r} — use the "
                f"{'/'.join(_SPRITE_FLAGS)} role flag or "
                f"{'/'.join(_SPRITE_KEYS)}=N (e.g. eagle.png@hero or "
                f"gem.png@x=0.3,y=0.6,w=0.34)")
        try:
            out[key] = float(value)
        except ValueError:
            die(f"--sprite {spec}: {key}={value!r} is not a number")
    return out


def plate_patch(base: Image.Image, x0: int, y0: int, w: int, h: int) -> Image.Image:
    """The art under a sprite's box, edge-extended where the box leaves the canvas.

    An object that bleeds past the bottom of the frame still needs something to
    sample its light from, and PIL's out-of-bounds crop fill is black — which
    would smear a dark band into exactly the foreground object the panel leads
    with.
    """
    bx0, by0 = max(0, x0), max(0, y0)
    bx1, by1 = min(base.width, x0 + w), min(base.height, y0 + h)
    if bx1 <= bx0 or by1 <= by0:
        return Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 255))
    crop = np.asarray(base.crop((bx0, by0, bx1, by1)).convert("RGBA"))
    pad = ((by0 - y0, (y0 + h) - by1), (bx0 - x0, (x0 + w) - bx1), (0, 0))
    return Image.fromarray(np.pad(crop, pad, mode="edge"), "RGBA")


def seat_in_scene(art: Image.Image, plate: Image.Image, light: float) -> Image.Image:
    """Make a cutout share the plate's light instead of sitting on top of it.

    Two compositing passes, both cheap and both the difference between "inlaid"
    and "sticker": a colour cast that pulls the object toward the light it is
    standing in, and a light-wrap that spills the surrounding art over the
    object's own rim, the way a lit edge actually behaves.
    """
    amount = max(0.0, min(1.0, light))
    if amount <= 0:
        return art
    arr = np.asarray(art, dtype=np.float32) / 255.0
    rgb, alpha = arr[..., :3], arr[..., 3:4]
    covered = float(alpha.sum())
    if covered < 1.0:
        return art

    plate_rgb = np.asarray(plate.convert("RGBA"), dtype=np.float32)[..., :3] / 255.0
    # Mean of the art the object actually covers — its local light, not the
    # panorama's global average, so an object in a gold pool warms and one in a
    # blue shadow cools.
    mean = (plate_rgb * alpha).sum(axis=(0, 1)) / covered
    tint = 0.34 * amount
    rgb = rgb + (mean[None, None, :] - rgb) * tint
    art = Image.fromarray(
        (np.clip(np.concatenate([rgb, alpha], axis=-1), 0.0, 1.0) * 255 + 0.5)
        .astype(np.uint8), "RGBA")

    radius = max(2.0, art.width * 0.07)
    blurred = np.asarray(art.getchannel("A").filter(
        ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0
    # Inside-edge band: opaque here, but close enough to an edge that the blur
    # has already fallen off. Zero deep inside the object and zero outside it.
    band = np.clip(alpha[..., 0] * (1.0 - blurred), 0.0, 1.0) ** 0.85
    wrap = plate.convert("RGBA").filter(ImageFilter.GaussianBlur(radius * 1.6))
    wrap.putalpha(Image.fromarray(
        (band * 0.85 * amount * 255 + 0.5).astype(np.uint8), "L"))
    return Image.alpha_composite(art, wrap)


def scene_front(pano: Image.Image, x0: int, y0: int, w: int, h: int,
                amount: float):
    """Lift the scene's foreground so it can be closed back over an object's feet.

    Call this *before* the object is pasted and composite the result after:
    light and a contact shadow make a cutout *lit by* the picture; only
    occlusion makes it *inside* the picture.

    It takes the strip of art the object's lowest band covers — the floor, the
    rail, the chips, whatever the panorama drew there — and returns it with a
    soft vertical ramp, so the object ends up standing behind the foreground
    instead of in front of the whole illustration.

    Only art that is actually on the canvas is reused: a foot that runs past the
    bottom edge has no floor to hide behind, and edge-extended rows would smear
    a band of the last visible pixel row across the hero's shins.
    """
    strength = max(0.0, min(1.0, amount))
    band = int(round(h * strength))
    if band < 2:
        return None
    bottom = min(pano.height, y0 + h)
    top = max(0, bottom - band, y0)
    bx0, bx1 = max(0, x0), min(pano.width, x0 + w)
    if bottom - top < 2 or bx1 - bx0 < 2:
        return None
    front = pano.crop((bx0, top, bx1, bottom)).convert("RGBA")
    # 0 at the top of the band, opaque at the bottom: the foreground rises over
    # the object the way a floor edge does, with no visible cut line.
    ramp = np.linspace(0.0, 1.0, front.height, dtype=np.float32) ** 1.6
    alpha = np.asarray(front.getchannel("A"), dtype=np.float32) / 255.0
    front.putalpha(Image.fromarray(
        (np.clip(alpha * ramp[:, None], 0.0, 1.0) * 255 + 0.5).astype(np.uint8), "L"))
    return front, bx0, top


def contact_shadow(pano: Image.Image, cx: int, foot_y: int, width: int,
                   strength: float) -> None:
    """Ground the object where it meets the floor of the scene.

    An offset drop shadow says "this is a layer above the picture"; a squashed,
    darkest-at-the-contact-point ellipse says "this is standing there".
    """
    s = max(0.0, min(1.0, strength))
    if s <= 0 or width <= 0:
        return
    sw, sh = max(8, round(width * 1.02)), max(4, round(width * 0.19))
    blur = max(2.0, sw * 0.075)
    pad = int(blur * 3)
    mask = Image.new("L", (sw + 2 * pad, sh + 2 * pad), 0)
    ImageDraw.Draw(mask).ellipse([pad, pad, pad + sw - 1, pad + sh - 1], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    mask = mask.point(lambda v: int(v * s * 0.82))
    layer = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    layer.putalpha(mask)
    paste_clipped(pano, layer, cx - layer.width // 2, foot_y - layer.height // 2)


def inlay_sprites(pano: Image.Image, specs, panels: int, panel_w: int,
                  panel_h: int, gutter: int, glow_color: str = "#FFFFFF",
                  light: float = DEFAULT_SPRITE_LIGHT,
                  spans: list[tuple[int, int]] | None = None) -> list[str]:
    """Composite the game's OWN objects into the concept art.

    Stores reject listings whose first panels advertise a world the app does not
    contain. Describing the game's symbols to an image model produces something
    similar; pasting the shipped sprite produces the same object. This does the
    second — leading with the hero on panel 1, at a size that survives the
    thumbnail strip, seated in the scene's own light, and always clear of the
    seam allowance so a store gutter can never bisect one.

    `spans` are the cuts the panorama will actually be sliced on. They are
    passed in rather than recomputed because the seams are snapped to the
    picture's calm ground first: an object placed against the nominal 1/3, 2/3
    arithmetic can sit on a seam that has since moved.
    """
    parsed = [parse_sprite_spec(raw) for raw in (specs or [])]
    if not parsed:
        return []
    cuts = list(spans) if spans else uniform_spans(panels, panel_w, gutter)
    if len(parsed) > CROWDED:
        warn(f"{len(parsed)} objects inlaid — the panorama is a picture, not a sprite "
             f"sheet. A hero plus two or three symbols reads better at thumbnail "
             f"size than a pile; keep it to {CROWDED}.")
    if not any(spec.get("role") == "hero" for spec in parsed):
        # The store shows screenshot 1 at full size and the rest as thumbnails,
        # so the protagonist leads unless the caller names one itself. Tagging
        # some *other* object — a board, a prop — must not quietly cost the set
        # its hero: only an explicit `@hero` does.
        lead = next((spec for spec in parsed if spec.get("role") != "board"), None)
        if lead is not None:
            lead["role"] = "hero"

    # Fixed placements claim their panels before auto props are distributed.
    # Without that look-ahead, `hero, prop, board` puts both of the latter on
    # panel 2 and leaves panel 3 as generic background. The default triptych is
    # a three-slide story, so a real game anchor belongs on every slide before
    # any one slide receives a second prop.
    fixed_load = [0] * panels
    for spec in parsed:
        role = spec.get("role")
        if "x" in spec:
            point = round(float(spec["x"]) * pano.width)
            fixed_panel = max(0, sum(1 for left, _ in cuts if left <= point) - 1)
        elif "panel" in spec:
            fixed_panel = int(spec["panel"]) - 1
        elif role == "hero":
            fixed_panel = 0
        elif role == "board":
            fixed_panel = panels // 2
        else:
            continue
        fixed_panel = max(0, min(panels - 1, fixed_panel))
        fixed_load[fixed_panel] += 1

    auto_load = fixed_load[:]

    placements: list[dict] = []
    prop_i = 0
    for spec in parsed:
        role = spec.get("role")
        hero, board = role == "hero", role == "board"
        art = load_image(spec["path"], "game object")
        if art.getchannel("A").getextrema()[0] == 255:
            warn(f"{spec['path']} has no transparency — run "
                 f"`python3 tools/cutout.py {spec['path']} --type sprite` first, or the "
                 "key art will show the sprite's background box")
        default_w = (HERO_W if hero else BOARD_W if board
                     else _PROP_W[prop_i % len(_PROP_W)])
        max_h = HERO_H if hero else BOARD_H if board else PROP_H
        w_frac = float(spec.get("w", default_w))
        h_frac = float(spec.get("h", max_h))
        source_w = art.width
        # `contain` fits inside both bounds, so which one binds is the design
        # decision. For the hero the height is the target and the width is the
        # cap (a tall figure filling the panel); for everything else it is the
        # other way round.
        art = contain(art, max(8, round(panel_w * w_frac)),
                      max(8, round(panel_h * h_frac)))
        if hero and art.height < panel_h * HERO_MIN_H and "h" not in spec:
            # A squat or wide cutout hits the width cap before it reaches full
            # height, and then the one screenshot the store shows at full size
            # is a landscape with a person in it again.
            warn(f"{Path(spec['path']).name} fills only "
                 f"{art.height / panel_h:.0%} of panel 1's height — the width cap "
                 f"({w_frac:.2f}× the panel) binds first on a cutout this wide. "
                 "Export the hero as a tall full-body figure, crop its empty "
                 "margins, or raise the cap with w= — the first slide wants the "
                 f"character at ~{HERO_H:.0%} of the panel height.")
        if art.width > source_w * 2:
            # Foreground scale is the whole point now, so a small in-game sprite
            # gets blown up much harder than it used to. Say so before it lands
            # soft on the one screenshot the store shows at full size.
            warn(f"{Path(spec['path']).name} is only {source_w}px wide and is being "
                 f"upscaled {art.width / source_w:.1f}× to {art.width}px — export the "
                 "asset larger, or draw this object into the panorama in Phase 1 "
                 "instead of compositing it")
        rotation = float(spec.get("rot", 0.0))
        if rotation:
            art = art.rotate(rotation, resample=Image.BICUBIC, expand=True)
        opacity = max(0.0, min(1.0, float(spec.get("opacity", 1.0))))
        if opacity < 1.0:
            art.putalpha(art.getchannel("A").point(lambda v: int(v * opacity)))

        if "x" in spec:
            cx = round(float(spec["x"]) * pano.width)
            # The panel an explicit x lands in — a point inside the allowance
            # after panel i still belongs to panel i, as it did when the cuts
            # were evenly spaced.
            panel = max(0, sum(1 for left, _ in cuts if left <= cx) - 1)
        else:
            if "panel" in spec:
                panel = int(spec["panel"]) - 1
            elif hero:
                panel = 0
            elif board:
                # The mechanic sits in the middle of the strip: away from the
                # hero's panel, and never on the last one, which the store
                # crops first on a narrow carousel.
                panel = panels // 2
            else:
                # Fill every split slide with a real game anchor before any
                # panel gets another prop. Prefer panels after the hero's in
                # reading order, so hero + two props becomes 1 / 2 / 3, while
                # hero + board + one prop becomes 1 / 2 / 3 as well.
                order = list(range(1, panels)) + [0]
                panel = min(order, key=lambda i: (auto_load[i], order.index(i)))
                auto_load[panel] += 1
            panel = max(0, min(panels - 1, panel))
            frac = (HERO_X if hero else BOARD_X if board
                    else _PROP_X[prop_i % len(_PROP_X)])
            cx = round(cuts[panel][0] + frac * panel_w)

        # Objects are anchored by the foot, not the centre: that is what makes
        # them stand on the scene's ground plane instead of floating in it.
        if "y" in spec:
            cy = round(float(spec["y"]) * pano.height)
        else:
            foot = (pano.height + float(spec["bleed"]) * art.height
                    if "bleed" in spec
                    else pano.height * (HERO_FOOT if hero else BOARD_FOOT if board
                                        else _PROP_FOOT[prop_i % len(_PROP_FOOT)]))
            cy = round(foot - art.height / 2)
        if not hero and not board:
            prop_i += 1

        left, right = cuts[panel]
        margin = round(panel_w * 0.04)
        if art.width > panel_w - 2 * margin:
            warn(f"{Path(spec['path']).name} is {art.width}px wide — wider than one "
                 f"{panel_w}px panel's safe band; scaling it down to fit")
            art = contain(art, panel_w - 2 * margin, round(panel_h * h_frac))
        half = art.width // 2
        lo, hi = left + half + margin, right - half - margin
        if not lo <= cx <= hi:
            moved = min(hi, max(lo, cx))
            warn(f"{Path(spec['path']).name} at x={cx}px overlapped a panel seam — "
                 f"moved to x={moved}px so the store's gutter cannot cut it in half")
            cx = moved

        placements.append({
            "art": art, "cx": cx, "cy": cy, "panel": panel, "hero": hero,
            "board": board, "name": Path(spec["path"]).name,
            "glow": max(0.0, float(spec.get("glow", 0.22 if board else 0.28))),
            "shadow": max(0.0, min(1.0, float(spec.get("shadow", 0.42)))),
            "contact": max(0.0, min(1.0, float(spec.get("contact", 0.62)))),
            "light": max(0.0, min(1.0, float(spec.get("light", light)))),
            # The hero gets the deepest foreground overlap, but props also sit
            # behind a small amount of scene furniture. Otherwise a correctly
            # lit prop still reads as an icon pasted onto the illustration.
            # The board stays unobscured because its cells must remain legible.
            "occlude": max(0.0, min(0.5, float(
                spec.get("occlude", HERO_OCCLUDE if hero else
                         0.0 if board else PROP_OCCLUDE)))),
        })

    anchors: list[list[str]] = [[] for _ in range(panels)]
    for p in placements:
        anchors[p["panel"]].append(p["name"])
    for i, names in enumerate(anchors):
        info(f"panel {i + 1} game anchors: {', '.join(names) if names else 'NONE'}")
    missing = [str(i + 1) for i, names in enumerate(anchors) if not names]
    if missing:
        warn(f"panel{'s' if len(missing) > 1 else ''} {', '.join(missing)} "
             "contain no real game object — every split slide needs an unmistakable "
             "anchor from assets/images/ built into its own scene (panel 1 hero, "
             "middle panel field, final panel reward/prop). Add another --sprite or "
             "move one with panel=; decorative background alone does not establish "
             "game continuity.")

    placed: list[str] = []
    # Farthest first: the smaller an object is the deeper it sits, so painting in
    # ascending size order lets the foreground overlap the midground the way a
    # drawn scene does, instead of whichever order the caller typed.
    for p in sorted(placements, key=lambda p: p["art"].width):
        art, cx, cy = p["art"], p["cx"], p["cy"]
        x0, y0 = cx - art.width // 2, cy - art.height // 2
        art = seat_in_scene(art, plate_patch(pano, x0, y0, art.width, art.height),
                            p["light"])

        if p["glow"]:
            radius = max(2.0, art.width * 0.22)
            bleed = int(radius * 2)
            padded = Image.new("RGBA", (art.width + 2 * bleed, art.height + 2 * bleed),
                               (0, 0, 0, 0))
            padded.alpha_composite(art, (bleed, bleed))
            mask = padded.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
            mask = mask.point(lambda v: int(min(255, v * p["glow"] * 1.6)))
            halo = Image.new("RGBA", padded.size, hex_rgba(glow_color)[:3] + (0,))
            halo.putalpha(mask)
            paste_clipped(pano, halo, cx - padded.width // 2, cy - padded.height // 2)

        foot = cy + art.height // 2
        if foot < pano.height:
            # An object cropped by the bottom edge has no visible floor to
            # shadow; one standing inside the frame does, and needs it.
            contact_shadow(pano, cx, foot, art.width, p["contact"])

        # Lifted BEFORE the paste, composited AFTER it: the object ends up
        # standing behind the scene's foreground instead of on top of the
        # whole illustration, which is the difference between a picture drawn
        # around the character and a character dropped onto a picture.
        front = scene_front(pano, x0, y0, art.width, art.height, p["occlude"])

        node, pad = ((art, 0) if p["shadow"] <= 0 else
                     drop_shadow(art, blur=max(4, round(art.width * 0.05)),
                                 dy=round(art.width * 0.02), opacity=p["shadow"]))
        paste_clipped(pano, node, cx - art.width // 2 - pad, cy - art.height // 2 - pad)
        if front is not None:
            layer, fx, fy = front
            paste_clipped(pano, layer, fx, fy)
        if p["occlude"] > 0 and front is None:
            warn(f"{p['name']} asked to be occluded but there is no scene under its "
                 "lowest band to close over it — it will read as a layer in front of "
                 "the picture. Move it up (y=/bleed=) or draw a foreground into the "
                 "panorama at that spot")
        role = "hero  " if p["hero"] else "board " if p["board"] else "prop  "
        seating = " + occluded by the foreground" if front is not None else ""
        placed.append(f"{role}{p['name']} → panel "
                      f"{p['panel'] + 1} @ {cx},{cy} ({art.width}px, "
                      f"{art.width / panel_w:.0%} of the panel, "
                      f"{art.height / panel_h:.0%} of its height){seating}")
    for line in placed:
        info(f"inlay  {line}")
    hero_p = next((p for p in placements if p["hero"]), None)
    if hero_p is not None:
        crown_report(pano, cuts[hero_p["panel"]],
                     hero_p["cy"] - hero_p["art"].height // 2,
                     hero_p["panel"] + 1)
    return placed


# ───────────────────────────── subcommands ──────────────────────────────────

def cmd_triptych(args) -> None:
    w, h = parse_size(args.size)
    n = args.panels
    if not 2 <= n <= 5:
        die(f"--panels {n} out of range (2..5)")
    if args.pano_only and not args.save_pano:
        die("--pano-only writes nothing without --save-pano PNG")

    # The concept panorama is deliberately TEXT-FREE. Typography set across a
    # panel boundary is cut by the store's gutters, and a lockup inside one
    # panel breaks the illusion that the panels are one picture. The words
    # belong on the showcase captions and the feature graphic.
    refused = [flag for flag, value in (
        ("--title", args.title), ("--tagline", args.tagline), ("--logo", args.logo),
        ("--title-panel", args.title_panel), ("--title-pos", args.title_pos),
    ) if value]
    if refused:
        die(f"{', '.join(refused)}: the concept panorama carries no text — it is one "
            "uninterrupted illustration.\n   Put the words on the game frames "
            "(`showcase --caption`) and the feature graphic (`banner --title/--tagline`).")

    gutter = parse_gutter(args.gutter, w)
    snap = parse_snap(args.seam_snap, w)
    src = load_image(args.src, "key art")

    # The panorama is composed WIDER than the panels it produces: the extra
    # `gutter` strip at every cut is discarded so the store's own gap between
    # screenshots stands in for it. Without that allowance the panels are
    # butt-joined and every object crossing a seam is displaced on the listing
    # page by the width of the carousel gutter.
    #
    # It is composed wider again by `snap` per seam, and that slack is what lets
    # the cuts slide onto quiet ground. A content-blind cut at exactly 1/3 and
    # 2/3 is what makes a panel stop halfway through a face — the allowance is
    # not too wide, it is being taken out of the wrong place.
    # Slack = room for the whole tiling to slide (2 radii, so the even split sits
    # in the middle of the search) plus room for each allowance to drift.
    slack = (2 * snap + (n - 1) * min(snap, round(gutter * SNAP_GAP_DRIFT))
             if snap else 0)
    pano_w, pano_h = w * n + gutter * (n - 1) + slack, h
    want, got = pano_w / pano_h, src.width / src.height
    if abs(want - got) / want > 0.35:
        warn(f"key art aspect {got:.2f} is far from the {n}-panel panorama {want:.2f} — "
             f"cover-crop will discard a lot of the picture")
    if src.width < pano_w * 0.35:
        warn(f"key art is {src.width}px wide for a {pano_w}px panorama "
             f"({pano_w / src.width:.1f}× upscale) — generate it as wide as the model allows")

    pano = cover(src, pano_w, pano_h, bias_x=args.offset, zoom=args.zoom)
    pano = pop_grade(pano, args.pop, vibrance=args.vibrance, lift=args.lift,
                     contrast=args.contrast, bloom=args.bloom)
    # The cuts are chosen on the art BEFORE the objects land on it: the objects
    # are then placed inside the panels those cuts define, so nothing is ever
    # seated against a seam that afterwards moves out from under it.
    spans = plan_panel_spans(pano, n, w, gutter, snap)
    inlay_sprites(pano, getattr(args, "sprite", []), n, w, h, gutter,
                  glow_color=args.sprite_glow_color, light=args.sprite_light,
                  spans=spans)
    seam_report(pano, spans)
    detail_report(pano, spans)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for i in range(0 if args.pano_only else n):
        left, right = spans[i]
        panel = pano.crop((left, 0, right, h))
        path = out_dir / f"{args.prefix}{i + 1:02d}.png"
        total += save_png(panel, path)
        ok(f"{path.name}  {w}×{h}")

    # The integrated panorama — graded, with the game's real objects seated into
    # it — is the picture the whole kit should share. Save it so the feature
    # graphic and the in-app backdrop are cut from the same art the panels are,
    # instead of from the bare model output that has none of the objects in it.
    if args.save_pano:
        pano_path = Path(args.save_pano)
        if pano_path.parent.resolve() == out_dir.resolve():
            warn(f"--save-pano writes into {out_dir} — `check` would count the panorama "
                 "as an upload asset. Keep it beside the art (art/keyart-integrated.png).")
        save_png(pano, Path(args.save_pano))
        ok(f"{Path(args.save_pano).name}  {pano_w}×{pano_h}  "
           + ("layout draft (reference image for `gpt_image.py edit` — not an "
              "upload asset, and not what `backdrop`/`banner` should read)"
              if args.pano_only else
              "integrated panorama (feed this to `banner --keyart` and `backdrop --src`)"))

    # Stitched preview — a cheap vision check that nothing important (a face,
    # the hero, a coin) is cut by a panel boundary. The gutters are painted in
    # so the preview shows what the STORE shows, gaps and all, rather than a
    # continuous picture the listing page will never display.
    if args.pano_only:
        info("--pano-only: layout draft written, no panels. Hand it to "
             "`gpt_image.py edit` with the objects' own files, then slice the "
             "picture that comes back.")
        return

    # The primary preview is the PROOF: the panels laid edge to edge exactly as
    # they were written, so what comes back is the picture itself if nothing was
    # discarded between them. The cut positions are marked with short ticks at
    # the very top and bottom rather than full-height lines, so the picture in
    # the middle is unobstructed for a vision pass.
    gaps = [spans[i][0] - spans[i - 1][1] for i in range(1, n)]
    stitched = Image.new("RGBA", (w * n + sum(gaps), pano_h), (14, 14, 18, 255))
    x = 0
    for i, (left, right) in enumerate(spans):
        stitched.paste(pano.crop((left, 0, right, h)), (x, 0))
        x += w + (gaps[i] if i < n - 1 else 0)
    marked = stitched.copy()
    tick = ImageDraw.Draw(marked)
    tick_h = max(8, round(pano_h * 0.02))
    x = 0
    for i in range(n - 1):
        x += w + gaps[i]
        for y0, y1 in ((0, tick_h), (pano_h - tick_h, pano_h)):
            tick.line([(x - gaps[i] // 2, y0), (x - gaps[i] // 2, y1)],
                      fill=(255, 0, 128, 255), width=3)
    scale = 1800 / marked.width
    save_png(marked.resize((1800, max(1, round(marked.height * scale))), RES),
             out_dir / "_panorama-preview.png")
    lost = sum(gaps)
    ok(f"_panorama-preview.png  the {n} panels laid edge to edge — "
       + ("they reassemble the panorama exactly, 0px discarded"
          if not lost else
          f"{lost}px of the picture is missing at the seams ({'/'.join(map(str, gaps))}px)"))

    # The secondary preview answers the opposite question: what the listing page
    # will look like once the store puts its own gap between the screenshots.
    # That gap is roughly 4-5% of a panel's width in both carousels; it is drawn
    # only to judge whether a seam survives it, and it is not a store asset.
    shown = [g or round(w * CAROUSEL_GAP) for g in gaps]
    carousel = Image.new("RGBA", (w * n + sum(shown), pano_h), (14, 14, 18, 255))
    x = 0
    for i, (left, right) in enumerate(spans):
        carousel.paste(pano.crop((left, 0, right, h)), (x, 0))
        x += w + (shown[i] if i < n - 1 else 0)
    scale = 1800 / carousel.width
    save_png(carousel.resize((1800, max(1, round(carousel.height * scale))), RES),
             out_dir / "_carousel-preview.png")
    ok(f"_carousel-preview.png  the same panels with the store's own gap between "
       f"them (~{shown[0]}px) — check that nothing important straddles a cut")

    info(f"panorama {pano_w}×{pano_h}, {total // 1024} KB across {n} panels"
         + (f", nothing discarded between them" if not lost
            else f", {'/'.join(map(str, gaps))}px discarded at the seams")
         + (f" (cuts snapped within ±{snap}px)" if snap else ""))
    if gutter:
        warn(f"--gutter {gutter}: a {gutter}px strip is thrown away at every cut, so the "
             "panels no longer reassemble into the whole picture and each one ends "
             "mid-object wherever the cut fell. Only do this for a publisher who has "
             "asked the panels to line up across the store's carousel gap.")


def _perspective_coeffs(dst, src) -> tuple:
    """Coefficients for Image.transform(PERSPECTIVE), mapping dst → src."""
    rows, rhs = [], []
    for (xd, yd), (xs, ys) in zip(dst, src):
        rows.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd])
        rhs.append(xs)
        rows.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd])
        rhs.append(ys)
    solved = np.linalg.solve(np.asarray(rows, dtype=np.float64),
                             np.asarray(rhs, dtype=np.float64))
    return tuple(solved)


def _slab_quads(w: int, h: int, yaw: float, pitch: float, depth: float,
                focal: float = 2.6):
    """Project a w×h slab of `depth` under `yaw`/`pitch` → (front, back) corners.

    A board photographed square-on is a decal no matter how well it is lit. Two
    rotations and a real perspective divide give it a near edge and a far edge,
    which is what makes the eye read it as an object standing in the scene.
    """
    ry, rx = math.radians(yaw), math.radians(pitch)
    cy, sy = math.cos(ry), math.sin(ry)
    cx, sx = math.cos(rx), math.sin(rx)
    f = focal * max(w, h)
    corners = ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))
    faces = []
    for z0 in (0.0, -depth * min(w, h)):
        face = []
        for x, y in corners:
            z = z0
            x, z = x * cy + z * sy, -x * sy + z * cy
            y, z = y * cx - z * sx, y * sx + z * cx
            scale = f / max(f * 0.2, f - z)
            face.append((x * scale, y * scale))
        faces.append(face)
    return faces


def _plate_geometry(w: int, h: int, yaw: float, pitch: float, depth: float):
    """Canvas size and the front/back quads, shifted into that canvas."""
    front, back = _slab_quads(w, h, yaw, pitch, depth)
    pts = front + (back if depth else front)
    pad = max(2, round(max(w, h) * 0.01))
    min_x, min_y = min(x for x, _ in pts) - pad, min(y for _, y in pts) - pad
    max_x, max_y = max(x for x, _ in pts) + pad, max(y for _, y in pts) + pad
    size = (max(8, math.ceil(max_x - min_x)), max(8, math.ceil(max_y - min_y)))
    shift = lambda quad: [(x - min_x, y - min_y) for x, y in quad]
    return size, shift(front), shift(back)


def plate_point(w: int, h: int, yaw: float, pitch: float, depth: float,
                x: float, y: float) -> tuple[float, float]:
    """Where a point on the flat plate lands once the plate is stood up.

    `to_perspective` warps the plate into a bigger canvas, so anything that has
    to meet the board *after* the warp — a symbol lifted out of its cell, say —
    needs the same mapping in the forward direction.
    """
    if not (yaw or pitch or depth):
        return float(x), float(y)
    _, front, _ = _plate_geometry(w, h, yaw, pitch, depth)
    c = _perspective_coeffs(((0, 0), (w, 0), (w, h), (0, h)), front)
    den = c[6] * x + c[7] * y + 1.0
    return ((c[0] * x + c[1] * y + c[2]) / den,
            (c[3] * x + c[4] * y + c[5]) / den)


def to_perspective(img: Image.Image, yaw: float, pitch: float, depth: float,
                   shade: float = 0.22) -> Image.Image:
    """Stand a flat plate up in 3D: perspective, a slab edge, and a light falloff."""
    if not (yaw or pitch or depth):
        return img
    w, h = img.size
    size, front, back = _plate_geometry(w, h, yaw, pitch, depth)

    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    if depth:
        arr = np.asarray(img.convert("RGBA"), dtype=np.float32)
        opaque = arr[..., 3] > 200
        base = (arr[..., :3][opaque].mean(axis=0) if opaque.any()
                else np.asarray([90.0, 90.0, 110.0]))
        # Top, sides, bottom fall away from the scene's top-left key light by
        # different amounts — one flat grey slab edge reads as cardboard.
        for i, dim in enumerate((0.62, 0.44, 0.28, 0.44)):
            poly = [front[i], front[(i + 1) % 4], back[(i + 1) % 4], back[i]]
            face = Image.new("RGBA", size, (0, 0, 0, 0))
            ImageDraw.Draw(face).polygon(
                poly, fill=tuple(int(c * dim) for c in base) + (255,))
            canvas.alpha_composite(face)

    warped = img.convert("RGBA").transform(
        size, Image.PERSPECTIVE,
        _perspective_coeffs(front, ((0, 0), (w, 0), (w, h), (0, h))),
        resample=Image.BICUBIC)
    if shade and yaw:
        # The receding half of the face sits further from the key light.
        ramp = gradient(size, [(0.0, (255, 255, 255, 255)),
                               (1.0, (255, 255, 255, round(255 * (1 - shade))))],
                        horizontal=True)
        if yaw < 0:
            ramp = ramp.transpose(Image.FLIP_LEFT_RIGHT)
        lit = np.asarray(warped, dtype=np.float32)
        lit[..., :3] *= (np.asarray(ramp.getchannel("A"),
                                    dtype=np.float32)[..., None] / 255.0)
        warped = Image.fromarray(np.clip(lit, 0, 255).astype(np.uint8), "RGBA")
    canvas.alpha_composite(warped)
    return canvas


def parse_rect(spec: str, w: int, h: int) -> tuple[int, int, int, int]:
    """`x,y,w,h` — fractions of the frame when <= 1, pixels otherwise."""
    parts = [c.strip() for c in str(spec).split(",")]
    if len(parts) != 4:
        die(f"--rect {spec!r}: expected x,y,w,h")
    try:
        nums = [float(v) for v in parts]
    except ValueError:
        die(f"--rect {spec!r}: every value must be a number")
    box = [round(n * s) if 0 <= n <= 1 else round(n)
           for n, s in zip(nums, (w, h, w, h))]
    x, y, bw, bh = box
    if bw < 8 or bh < 8:
        die(f"--rect {spec!r} selects {bw}×{bh}px — too small to be a play field")
    if not (0 <= x < w and 0 <= y < h):
        die(f"--rect {spec!r} starts outside the {w}×{h} frame")
    return x, y, min(bw, w - x), min(bh, h - y)


def parse_cells(spec: str, cols: int, rows: int) -> list[tuple[int, int]]:
    """`--win 1x2,2x2,3x2` — COLxROW, 1-based, in the order they pay."""
    cells: list[tuple[int, int]] = []
    for chunk in (c.strip() for c in str(spec).replace("×", "x").split(",")):
        if not chunk:
            continue
        try:
            col, row = (int(v) for v in chunk.lower().split("x"))
        except ValueError:
            die(f"--win {chunk!r}: expected COLxROW (1-based), e.g. 1x2,2x2,3x2")
        if not (1 <= col <= cols and 1 <= row <= rows):
            die(f"--win {chunk}: outside the {cols}x{rows} grid")
        if (col - 1, row - 1) in cells:
            die(f"--win {chunk}: listed twice")
        cells.append((col - 1, row - 1))
    if not cells:
        die("--win named no cells")
    return cells


def expand_to_fit(base: Image.Image, box: tuple[int, int, int, int]):
    """Grow a transparent canvas around `base` until `box` fits inside it.

    Returns (canvas, dx, dy) — the offset everything already on the canvas moved
    by, which is what a caller needs to place the thing that did not fit.
    """
    x0, y0, x1, y1 = box
    dx, dy = max(0, -x0), max(0, -y0)
    right, bottom = max(0, x1 - base.width), max(0, y1 - base.height)
    if not (dx or dy or right or bottom):
        return base, 0, 0
    canvas = Image.new("RGBA", (base.width + dx + right, base.height + dy + bottom),
                       (0, 0, 0, 0))
    canvas.alpha_composite(base, (dx, dy))
    return canvas, dx, dy


def cmd_boardplate(args) -> None:
    """Build the play field out of the game's REAL assets, as a cutout.

    This exists because of one specific rejection: a concept panel showed a
    reel grid the image model had invented — its own tiles, its own frames, its
    own symbol art — beside gameplay frames whose board looked nothing like it.
    The designer's note was that the two have to be the same, and a text prompt
    cannot produce "the same". Only the real files can.

    Two ways in, both exact:
      --from-shot  lift the field straight out of a captured gameplay frame
      --symbol     lay the shipped symbol PNGs into the real grid
    The result is a transparent PNG for `triptych --sprite plate.png@board`, so
    the mechanic in the key art is the mechanic in the app.

    The next note on the same kit was about the panel this plate lands on: the
    middle slide is boring. It was — a correct grid of correct symbols sitting
    at rest is a contact sheet, not a gameplay example. So the plate can be
    built at the moment the round PAYS: `--win` names the cells that hit, and
    they get the payline, the ring and the glow while the rest of the field
    falls back (`--dim`); `--lift` pops the middle winning symbol up out of its
    cell with its own shadow on the board. None of that invents anything — the
    symbols, the grid and the colours are still the game's own; it is the same
    field, caught one frame later.
    """
    out = Path(args.out)
    radius_f = max(0.0, min(0.5, args.radius))
    lift_plan = None

    if args.from_shot:
        if args.symbol:
            die("--from-shot and --symbol are two different ways to build the same "
                "plate — pass one of them")
        if not args.rect:
            die("--from-shot needs --rect x,y,w,h (fractions of the frame, or pixels) "
                "naming the play field inside it")
        if args.win:
            die("--win draws the win state onto a plate built from --symbol. A plate "
                "lifted from a frame already has whatever state that frame was in — "
                "capture the frame at the moment the round pays and lift that one.")
        shot = load_image(args.from_shot, "gameplay frame")
        x, y, w, h = parse_rect(args.rect, shot.width, shot.height)
        plate = shot.crop((x, y, x + w, y + h)).convert("RGBA")
        info(f"lifted {w}×{h}px of {Path(args.from_shot).name} — the field in the key "
             "art is now literally the field the app renders")
    else:
        if not args.symbol:
            die("boardplate needs either --from-shot + --rect, or one --symbol per "
                "distinct game symbol")
        try:
            cols, rows = (int(v) for v in
                          str(args.grid).lower().replace("×", "x").split("x"))
        except ValueError:
            die(f"--grid {args.grid!r}: expected COLSxROWS (e.g. 3x3, 5x3)")
        if not (1 <= cols <= 8 and 1 <= rows <= 8):
            die(f"--grid {args.grid}: out of range (1..8 in each direction)")
        cell = max(32, args.cell)
        gap = round(cell * max(0.0, args.gap))
        pad = round(cell * max(0.0, args.pad))
        w = cols * cell + (cols - 1) * gap + 2 * pad
        h = rows * cell + (rows - 1) * gap + 2 * pad

        panel_c = opt_rgba(args.panel)
        tile_c = opt_rgba(args.tile)
        border_c = opt_rgba(args.border)
        if not args.frame and not (panel_c or tile_c or border_c):
            warn("no --frame and no --panel/--tile/--border: the plate is being built "
                 "in neutral colours. Sample the game's own board — or pass the real "
                 "board asset as --frame — or the key art advertises a field the app "
                 "does not have")

        plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if args.frame:
            back = cover(load_image(args.frame, "board frame"), w, h)
            plate.alpha_composite(back.convert("RGBA"))
        elif panel_c:
            body = Image.new("RGBA", (w, h), panel_c)
            body.putalpha(rr_mask((w, h), round(min(w, h) * radius_f)))
            plate.alpha_composite(body)
        if border_c:
            stroke = max(2, round(cell * max(0.0, args.border_width)))
            ring = Image.new("RGBA", (w, h), border_c)
            ring.putalpha(rr_ring((w, h), round(min(w, h) * radius_f), stroke))
            plate.alpha_composite(ring)

        tile_r = round(cell * max(0.0, min(0.5, args.tile_radius)))
        inset = round(cell * max(0.0, min(0.4, args.symbol_pad)))
        symbols = [load_image(path, "game symbol") for path in args.symbol]
        for path, sym in zip(args.symbol, symbols):
            if sym.getchannel("A").getextrema()[0] == 255:
                warn(f"{path} has no transparency — run "
                     f"`python3 tools/cutout.py {path} --type sprite` first, or the "
                     "plate shows the symbol's background box")
        win = parse_cells(args.win, cols, rows) if args.win else []
        dim = max(0.0, min(0.9, args.dim)) if win else 0.0
        accent = (opt_rgba(args.win_color) or border_c or (255, 214, 122, 255))
        stroke = max(3, round(cell * 0.055))
        origin = {(c, r): (pad + c * (cell + gap), pad + r * (cell + gap))
                  for r in range(rows) for c in range(cols)}
        # Staggered so a short symbol list does not produce identical columns —
        # a real board is never a repeating stripe.
        drawn = {(c, r): symbols[(r * (cols + 1) + c) % len(symbols)]
                 for r in range(rows) for c in range(cols)}

        if tile_c:
            for cx, cy in origin.values():
                tile = Image.new("RGBA", (cell, cell), tile_c)
                tile.putalpha(rr_mask((cell, cell), tile_r))
                plate.alpha_composite(tile, (cx, cy))

        if win:
            # Under the symbols: the cells that pay light up and the payline runs
            # between them, the way a real board draws it — behind the art, not
            # across it.
            under = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            centres = [(origin[k][0] + cell // 2, origin[k][1] + cell // 2)
                       for k in win]
            if len(centres) > 1:
                ImageDraw.Draw(under).line(centres, fill=accent[:3] + (150,),
                                           width=stroke, joint="curve")
            for c, r in win:
                lit = Image.new("RGBA", (cell, cell), accent[:3] + (255,))
                lit.putalpha(rr_mask((cell, cell), tile_r).point(lambda v: v // 4))
                under.alpha_composite(lit, origin[(c, r)])
            # One blurred copy beneath it: a hit on a real board throws light onto
            # the panel around it, and that spill is most of what makes the frame
            # read as a moment instead of a diagram.
            spill = under.filter(ImageFilter.GaussianBlur(max(4, round(cell * 0.16))))
            spill.putalpha(spill.getchannel("A").point(lambda v: int(v * 0.85)))
            plate.alpha_composite(spill)
            plate.alpha_composite(under)

        for (c, r), (cx, cy) in origin.items():
            fit = contain(drawn[(c, r)], cell - 2 * inset, cell - 2 * inset)
            plate.alpha_composite(
                fit, (cx + (cell - fit.width) // 2, cy + (cell - fit.height) // 2))
            if dim and (c, r) not in win:
                # The losing cells fall back so the paying line is the first thing
                # read. Without this the win is a ring on a wall of equally loud
                # symbols, which is where "boring" came from.
                veil = Image.new("RGBA", (cell, cell), (5, 7, 16, 255))
                veil.putalpha(rr_mask((cell, cell), tile_r)
                              .point(lambda v: int(v * dim)))
                plate.alpha_composite(veil, (cx, cy))

        info(f"built a {cols}×{rows} field from {len(symbols)} real symbol "
             f"{'file' if len(symbols) == 1 else 'files'}")

        if win:
            # Over the symbols: only the cell's own frame, which is what the game
            # itself draws on top when a cell pays.
            for c, r in win:
                ring = Image.new("RGBA", (cell, cell), accent[:3] + (255,))
                ring.putalpha(rr_ring((cell, cell), tile_r, stroke))
                plate.alpha_composite(ring, origin[(c, r)])
            info(f"win state: {len(win)} cells pay "
                 f"({', '.join(f'{c + 1}x{r + 1}' for c, r in win)})"
                 + (f", the other cells dimmed {dim:.0%}" if dim else ""))
            if args.lift > 1.0:
                # The middle paying cell, so the symbol that rises sits on the
                # line rather than at one end of it. Planned here, composited
                # after the perspective: it is leaving the board's plane, so it
                # must not be warped into it.
                # Scaled against the symbol as the cell draws it, not against
                # the cell, so `--lift 1.45` means half again as big as the one
                # on the board — which is what a reader of the flag expects.
                c, r = win[len(win) // 2]
                lift_plan = (drawn[(c, r)], origin[(c, r)][0] + cell // 2,
                             origin[(c, r)][1] + cell // 2, cell,
                             min(3.0, args.lift) * (cell - 2 * inset) / cell, accent)
        else:
            warn("no --win: the plate is the field at rest, and the middle panel is "
                 "the listing's gameplay example. A correct grid with nothing "
                 "happening in it is what came back as 'boring' — name the cells that "
                 "pay (--win 1x2,2x2,3x2) so the panel shows the round resolving, and "
                 "--lift rides on it to pop the paying symbol out of the board.")

    if radius_f > 0:
        corner = rr_mask(plate.size, round(min(plate.size) * radius_f))
        plate.putalpha(Image.fromarray(
            (np.asarray(plate.getchannel("A"), dtype=np.float32)
             * (np.asarray(corner, dtype=np.float32) / 255.0)).astype(np.uint8), "L"))

    sheen = max(0.0, min(1.0, args.sheen))
    if sheen:
        # The glass a real board is read through. Masked by the plate's own
        # alpha so it never spills past the field's edge.
        glass = gradient(plate.size, [(0.0, (255, 255, 255, round(74 * sheen))),
                                      (0.45, (255, 255, 255, round(18 * sheen))),
                                      (0.46, (255, 255, 255, 0)),
                                      (1.0, (255, 255, 255, 0))])
        glass.putalpha(Image.fromarray(
            (np.asarray(glass.getchannel("A"), dtype=np.float32)
             * (np.asarray(plate.getchannel("A"), dtype=np.float32) / 255.0)
             ).astype(np.uint8), "L"))
        plate.alpha_composite(glass)

    flat_w, flat_h = plate.size
    plate = to_perspective(plate, args.yaw, args.pitch, max(0.0, args.depth))

    if lift_plan is not None:
        # A board where one symbol has broken its own plane is the difference
        # between a picture of a field and a picture of a round being won. It
        # is composited in the canvas the warp produced, at the cell's own
        # projected centre and the cell's own projected size, so it stays welded
        # to the board it came out of.
        sym, px, py, cell_px, scale, accent = lift_plan
        depth = max(0.0, args.depth)
        cx, cy = plate_point(flat_w, flat_h, args.yaw, args.pitch, depth, px, py)
        ex, ey = plate_point(flat_w, flat_h, args.yaw, args.pitch, depth,
                             px + cell_px / 2, py)
        span = max(16, round(2 * math.hypot(ex - cx, ey - cy)))
        art = contain(sym, round(span * scale), round(span * scale))
        node, _ = drop_shadow(art, blur=max(4, round(span * 0.06)),
                              dy=round(span * 0.10), opacity=0.55)
        halo_pad = max(round(span * 0.35), (node.width - art.width) // 2 + 2)
        layer = Image.new("RGBA", (art.width + 2 * halo_pad, art.height + 2 * halo_pad),
                          (0, 0, 0, 0))
        seed = Image.new("L", layer.size, 0)
        seed.paste(art.getchannel("A"), (halo_pad, halo_pad))
        halo = Image.new("RGBA", layer.size, accent[:3] + (255,))
        halo.putalpha(seed.filter(ImageFilter.GaussianBlur(max(2, halo_pad * 0.5)))
                      .point(lambda v: int(v * 0.6)))
        layer.alpha_composite(halo)
        layer.alpha_composite(node, ((layer.width - node.width) // 2,
                                     (layer.height - node.height) // 2))
        x0 = round(cx - layer.width / 2)
        y0 = round(cy - span * 0.34 - layer.height / 2)
        plate, dx, dy = expand_to_fit(
            plate, (x0, y0, x0 + layer.width, y0 + layer.height))
        plate.alpha_composite(layer, (x0 + dx, y0 + dy))
        info(f"lifted the paying symbol {args.lift:.2f}× out of its cell — the field "
             "is caught mid-round instead of standing at rest")

    if args.tilt:
        plate = plate.rotate(args.tilt, resample=Image.BICUBIC, expand=True)
    if not (args.yaw or args.pitch or args.depth):
        warn("--yaw/--pitch/--depth are all 0: the plate is square to the camera and "
             "flat, which is what reads as pasted on. Give it the perspective of the "
             "stage it will stand on")

    out.parent.mkdir(parents=True, exist_ok=True)
    size = save_png(plate, out, keep_alpha=True)
    ok(f"{out.name}  {plate.width}×{plate.height}  {size // 1024} KB  board plate")
    info(f"seat it with: triptych --sprite {out} @board  (real symbols, real layout — "
         "the model never draws the field)")


def cmd_showcase(args) -> None:
    w, h = parse_size(args.size)
    # Grade the ART, then push it back. The real game frame is never graded:
    # both stores require a screenshot to represent what the app actually
    # renders, so a dull gameplay frame is fixed in the game (see the
    # `backdrop` subcommand), never in post.
    backdrop = pop_grade(cover(load_image(args.bg, "background"), w, h), args.pop,
                         vibrance=args.vibrance, lift=args.lift,
                         contrast=args.contrast, bloom=args.bloom)
    canvas = treat_background(backdrop, args.bg_treatment)

    caption = (args.caption or "").strip()
    type_plan = TypePlan(args, display_text=caption)
    if caption:
        type_plan.report()

    cap_max = int(w * 0.095)
    pad_top = int(h * 0.030)
    rule_h = 0 if args.no_rule or not caption else max(3, round(h * 0.0035))
    rule_gap = int(h * 0.020) if rule_h else 0
    if caption:
        # The band follows the text instead of taking a fixed slice: a one-line
        # caption must not cost the phone the same height as a two-line one.
        _, _, cap_text_h, _, _ = fit_text(
            caption.upper() if type_plan.upper else caption, type_plan.display,
            int(w * 0.86), int(h * 0.12), cap_max, max_lines=2,
            tracking=type_plan.tracking)
        cap_h = pad_top + rule_h + rule_gap + cap_text_h + int(h * 0.032)
    else:
        cap_h = int(h * 0.040)
    bottom_margin = int(h * 0.038)
    avail_h = max(1, h - cap_h - bottom_margin)

    device = build_device(args.shot, round(w * args.scale), args.frame)
    shot_ar = device.height / device.width
    if shot_ar < 1.5:
        warn(f"{args.shot} is {shot_ar:.2f} tall/wide — that is not phone-shaped "
             "(a phone is ~2.0-2.2). Capture with web_verify.mjs --size 390x844.")

    if args.fit == "bleed":
        # Fill the canvas: the phone keeps its full width and the bottom runs off
        # the edge. Capped, so a very tall shot can never lose its whole lower half.
        max_bleed = 0.26
        if device.height * (1 - max_bleed) > avail_h:
            device = contain(device, device.width, int(avail_h / (1 - max_bleed)))
        top = cap_h if device.height > avail_h else cap_h + (avail_h - device.height) // 2
    else:  # contain — the whole device stays visible (nothing gets cropped)
        if device.height > avail_h:
            device = contain(device, device.width, avail_h)
        top = cap_h + max(0, (avail_h - device.height) // 2)

    shadowed, pad = drop_shadow(device, blur=max(6, round(w * 0.022)),
                                dy=round(w * 0.012), opacity=0.55)
    paste_clipped(canvas, shadowed, (w - shadowed.width) // 2, top - pad)

    if caption:
        scrim(canvas, (0, 0, w, int(cap_h * 1.45)), strength=args.scrim, from_top=True)
        c1 = hex_rgba(args.caption_color)
        c2 = opt_rgba(args.caption_color2)
        if rule_h:
            accent_rule(canvas, w // 2, pad_top, int(w * 0.13), rule_h,
                        opt_rgba(args.accent) or c2 or c1, c2)
        draw_text_block(
            canvas, caption,
            (int(w * 0.07), pad_top + rule_h + rule_gap, int(w * 0.86),
             max(1, cap_h - pad_top - rule_h - rule_gap - int(h * 0.032))),
            type_plan.display, c1, max_size=cap_max, valign="top", max_lines=2,
            colour2=c2, tracking=type_plan.tracking, uppercase=type_plan.upper,
            outline=type_plan.outline)

    size = save_png(canvas, Path(args.out))
    ok(f"{Path(args.out).name}  {w}×{h}  {size // 1024} KB  "
       f"[{args.fit}, device {device.width}×{device.height}]"
       + (f'  «{caption}»' if caption else ""))


def cmd_banner(args) -> None:
    w, h = parse_size(args.size)
    # A 3-panel panorama cover-cropped to 1024×500 keeps only its middle — which
    # is exactly where the hero is not, now that panel 1 leads with it. --offset
    # slides the crop back onto the protagonist.
    canvas = pop_grade(cover(load_image(args.keyart, "key art"), w, h,
                             bias_x=args.offset, zoom=args.zoom),
                       args.pop, vibrance=args.vibrance, lift=args.lift,
                       contrast=args.contrast, bloom=args.bloom)

    if args.shot:
        # Build at working resolution, then fit by HEIGHT — a banner device sized
        # by width alone ends up a postage stamp on a 1024×500 canvas.
        device = build_device(args.shot, round(h * 0.5), args.frame)
        device = contain(device, int(w * 0.32), int(h * 0.86))
        shadowed, pad = drop_shadow(device, blur=max(5, round(w * 0.014)),
                                    dy=round(h * 0.012), opacity=0.5)
        # Right side, inside Play's 924×432 safe area.
        cx = int(w * 0.82)
        canvas.alpha_composite(shadowed, (cx - shadowed.width // 2,
                                          (h - shadowed.height) // 2))
        canvas.alpha_composite(gradient((int(w * 0.42), h), [
            (0.0, (0, 0, 0, 0)), (1.0, (0, 0, 0, int(0.30 * 255)))
        ], horizontal=True), (w - int(w * 0.42), 0))

    if args.title or args.tagline:
        type_plan = TypePlan(args, display_text=args.title, body_text=args.tagline)
        type_plan.report()
        text_w = int(w * 0.50) if args.shot else int(w * 0.80)
        x = int(w * 0.06)
        # Hold full strength across the whole text column, then fade. A scrim
        # that is still fading where the words are is the classic unreadable-
        # tagline bug — the tagline sits low and light, so it needs the floor.
        veil = int(max(0.0, min(1.0, args.scrim)) * 255)
        veil_w = text_w + int(w * 0.16)
        canvas.alpha_composite(gradient((veil_w, h), [
            (0.0, (0, 0, 0, veil)),
            (float(text_w) / veil_w, (0, 0, 0, veil)),
            (1.0, (0, 0, 0, 0)),
        ], horizontal=True), (0, 0))
        title_c = hex_rgba(args.title_color)
        title_c2 = opt_rgba(args.title_color2)
        accent = opt_rgba(args.accent) or title_c2 or title_c
        block_h = int(h * 0.52)
        cursor = (h - block_h) // 2
        if args.title:
            _, drawn = draw_text_block(
                canvas, args.title, (x, cursor, text_w, int(h * 0.30)),
                type_plan.display, title_c, max_size=int(h * 0.26), valign="top",
                max_lines=2, colour2=title_c2, tracking=type_plan.tracking,
                uppercase=type_plan.upper, outline=type_plan.outline)
            cursor += drawn + int(h * 0.035)
            if not args.no_rule:
                accent_rule(canvas, x + text_w // 2, cursor, int(h * 0.18),
                            max(2, round(h * 0.008)), accent, title_c2)
                cursor += max(2, round(h * 0.008)) + int(h * 0.035)
        if args.tagline:
            draw_text_block(
                canvas, args.tagline, (x, cursor, text_w, int(h * 0.16)),
                type_plan.body, hex_rgba(args.tagline_color),
                max_size=int(h * 0.10), valign="top", max_lines=2, shadow=0.45)

    size = save_png(canvas, Path(args.out))
    ok(f"{Path(args.out).name}  {w}×{h}  {size // 1024} KB (feature graphic)")


BACKDROP_VARIANTS = {
    "menu": "full-strength key art behind the main menu / lobby",
    "game": "the same picture calmed so the live field, HUD and buttons win the eye",
    "splash": "key art with a heavier vignette, for the native splash screen",
}


def cmd_backdrop(args) -> None:
    """Turn the store key art into the app's OWN background.

    This is the fix for the most expensive storefront rejection: the first
    panels advertise a world (a god, a machine, a vault) that never appears once
    the app opens, so the listing reads as art bought for a different product.
    Exporting a portrait crop of the very same panorama as the game's background
    makes the two halves of the listing the same picture — and it costs one
    crop instead of one more art commission.

    Two treatments, because a background has two jobs: the menu wants the art at
    full strength, the gameplay screen wants it recognisable but behind the
    mechanic.
    """
    w, h = parse_size(args.size)
    variants = [v.strip().lower() for v in args.variants.split(",") if v.strip()]
    unknown = [v for v in variants if v not in BACKDROP_VARIANTS]
    if unknown:
        die(f"--variants {', '.join(unknown)}: choose from "
            f"{', '.join(BACKDROP_VARIANTS)}")
    if not variants:
        die("--variants is empty")

    src_art = load_image(args.src, "key art")
    if src_art.width > src_art.height * 1.2:
        info(f"key art is {src_art.width}×{src_art.height} — cropping the portrait "
             f"region at --offset {args.offset:+.2f}; that is which slice of the "
             "panorama the player will actually live inside")

    base = cover(src_art, w, h, bias_x=args.offset, zoom=args.zoom)
    base = pop_grade(base, args.pop, vibrance=args.vibrance, lift=args.lift,
                     contrast=args.contrast, bloom=args.bloom)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in variants:
        img = base.copy()
        if name == "game":
            img = calm(img, args.calm)
        img = vignette(img, args.vignette + (0.22 if name == "splash" else 0.0))
        path = out_dir / f"{args.prefix}_{name}.png"
        size = save_png(img, path)
        ok(f"{path.name}  {w}×{h}  {size // 1024} KB — {BACKDROP_VARIANTS[name]}")
        if size > 1_400_000:
            warn(f"{path.name} is {size // 1024} KB — a phone background this heavy "
                 "costs load time; re-run with --size 1080x1920")
    info("register the files in pubspec.yaml and point the menu/gameplay screens at "
         "them, or the storefront and the app still show different worlds")


def cmd_icon(args) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bg = hex_rgba(args.bg)

    master = cover(load_image(args.src, "icon art"), 1024, 1024)
    flat = Image.new("RGBA", (1024, 1024), bg)
    flat.alpha_composite(master)
    save_png(flat, out_dir / "app_icon.png")
    ok("app_icon.png  1024×1024 (launcher master, no alpha)")

    store = flat.resize((512, 512), RES)
    save_png(store, out_dir / "store_icon_512.png", keep_alpha=True)
    ok("store_icon_512.png  512×512 (Play Console listing icon)")

    if args.fg_src:
        fg_art = load_image(args.fg_src, "adaptive foreground art")
        if fg_art.getchannel("A").getextrema()[0] == 255:
            warn(f"{args.fg_src} has no transparency — run "
                 f"`python3 tools/cutout.py {args.fg_src} --type icon` first, "
                 "or Android will show a square inside the adaptive mask")
        # Android masks adaptive icons down to the inner 66%; keep the subject there.
        safe = int(1024 * 0.62)
        subject = contain(fg_art, safe, safe)
        fg = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        fg.alpha_composite(subject, ((1024 - subject.width) // 2, (1024 - subject.height) // 2))
        save_png(fg, out_dir / "app_icon_fg.png", keep_alpha=True)
        ok("app_icon_fg.png  1024×1024 (Android adaptive foreground, 62% safe zone)")
    else:
        warn("no --fg-src: skipping app_icon_fg.png — configure flutter_launcher_icons "
             "WITHOUT adaptive_icon_foreground, or Android will crop the artwork")

    info(f"adaptive background colour: {args.bg}")


def cmd_fonts(args) -> None:
    """Show what typography this machine can actually deliver, before compositing.

    Always run this with the real copy (--sample) before a listing. The default
    sample is Latin + digits, matching the English copy the studio ships; pass
    the actual strings when the game was requested in another language, since a
    face that is perfect for a Latin title may not cover that script at all.
    """
    system = [entry for d in FONT_DIRS for entry in _scan_fonts(d)]
    project = [entry for d in (args.font_dir or []) for entry in _scan_fonts(d)]
    pool = project or system
    charset = _charset(args.sample)
    info(f"indexed {len(system)} system face(s)"
         + (f" + {len(project)} in {', '.join(args.font_dir)}" if args.font_dir else ""))
    info(f"coverage probe: {args.sample!r}")

    characterful = 0
    for mood in ((args.type_mood,) if args.mood_only else tuple(TYPE_MOODS)):
        spec = TYPE_MOODS[mood]
        skipped: list[str] = []
        display = _best_face(pool, tuple(spec["display"]) + FALLBACK_FAMILIES,
                             "heavy", charset, skipped)
        body = _best_face(pool, tuple(spec["body"]) + FALLBACK_FAMILIES,
                          "regular", charset)
        generic = not display or any(g in _norm(Path(display).stem) for g in GENERIC_FACES)
        characterful += not generic
        print(f"{'⚠️ ' if generic else '✅'} {mood:8s} "
              f"display={Path(display).name if display else '—':30s}"
              f" body={Path(body).name if body else '—'}")
        if skipped:
            print(f"   no glyphs for the probe: {', '.join(skipped)}")
        if generic:
            print(f"   '{mood}' has no characterful face here — titles fall back to a UI font")

    if not characterful:
        warn("no display face on this machine can set that text — every store title would "
             "be an Arial clone. Install faces that cover the alphabet (apt-get install "
             "fonts-montserrat fonts-inter fonts-ebgaramond) or pass --font-dir with the "
             "game's own fonts.")


def cmd_check(args) -> None:
    d = Path(args.dir)
    if not d.is_dir():
        die(f"not a directory: {d}")
    files = sorted(p for p in d.glob("*.png") if not p.name.startswith("_"))
    if not files:
        die(f"no store PNGs in {d}")

    target = getattr(args, "store", "any")
    problems = 0
    shapes: dict[tuple[int, int], str] = {}
    for p in files:
        try:
            with Image.open(p) as im:
                w, h = im.size
                mode = im.mode
        except Exception as exc:
            print(f"❌ {p.name}: unreadable ({exc})")
            problems += 1
            continue
        size = p.stat().st_size
        play_ok, appstore_ok, note = store_verdict(w, h)
        flags = []
        if min(w, h) < PLAY_MIN_SIDE:
            flags.append(f"side <{PLAY_MIN_SIDE}px")
        if max(w, h) > PLAY_MAX_SIDE:
            flags.append(f"side >{PLAY_MAX_SIDE}px")
        if size > PLAY_MAX_BYTES:
            flags.append(f">{PLAY_MAX_BYTES // 1024 // 1024}MB")
        if mode not in ("RGB", "L"):
            # Play takes 24-bit PNG only; an alpha channel is a silent rejection.
            flags.append(f"{mode} (store PNGs must be 24-bit, no alpha)")
        if target == "play" and not play_ok:
            flags.append(note or "not a valid Play shape")
        if target == "appstore" and not appstore_ok:
            flags.append(note or "not an App Store display slot")
        if flags:
            problems += 1
            print(f"❌ {p.name}  {w}×{h} {mode} {size // 1024}KB — {', '.join(flags)}")
        else:
            badge = f"Play {'✅' if play_ok else '✖'} · App Store {'✅' if appstore_ok else '✖'}"
            print(f"✅ {p.name}  {w}×{h} {mode} {size // 1024}KB — {badge}")
        if p.name.startswith("store-"):
            shapes[(w, h)] = note

    if len(shapes) > 1:
        warn(f"screenshots have mixed sizes {sorted(shapes)} — one listing takes one size")
    for (w, h), note in shapes.items():
        if note:
            info(f"{w}×{h}: {note}")

    if problems:
        die(f"{problems} file(s) violate store constraints")
    ok(f"{len(files)} file(s) pass store constraints")


# ───────────────────────────── cli ──────────────────────────────────────────

def add_text_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--font", help="explicit TTF/OTF for display text (skips mood matching)")
    p.add_argument("--font-regular", help="explicit TTF/OTF for body text")
    p.add_argument("--font-dir", action="append", default=[], metavar="DIR",
                   help="directory holding the GAME's own fonts (e.g. assets/fonts). "
                        "Searched first and outranks every mood — listing type that "
                        "matches in-game type is the whole point. Repeatable.")
    p.add_argument("--type-mood", choices=tuple(TYPE_MOODS), default="bold",
                   help="typographic character: picks the face family order, letter "
                        "spacing and letter case (default bold)")
    p.add_argument("--tracking", type=float, default=None, metavar="EM",
                   help="letter spacing as a fraction of font size; overrides the mood")
    p.add_argument("--no-uppercase", action="store_true",
                   help="keep the text as written even if the mood sets caps")
    p.add_argument("--text-outline", type=float, default=0.0, metavar="EM",
                   help="outline width as a fraction of font size (0.03 ≈ a thin edge). "
                        "Default 0: over a scrim the blurred shadow is enough, and a "
                        "thick stroke is what makes titles look like clip art.")
    p.add_argument("--title-color", default="#FFFFFF")
    p.add_argument("--title-color2", default="",
                   help="second stop for a vertical gradient on the title — pass the "
                        "game's accent colour (e.g. #FFC64A for gold)")
    p.add_argument("--tagline-color", default="#F2F4FA")
    p.add_argument("--accent", default="",
                   help="accent-rule colour (default: the title gradient's end)")
    p.add_argument("--no-rule", action="store_true", help="omit the accent rule")
    p.add_argument("--scrim", type=float, default=0.72,
                   help="0..1 darkening behind text (default 0.72)")


def add_pop_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--pop", choices=tuple(POP_PRESETS), default=DEFAULT_POP,
                   help="colour grade for GENERATED art: a listing is judged as a "
                        "strip of thumbnails and raw model output reads flat there, "
                        f"so a grade is applied by default ({DEFAULT_POP}). Use "
                        "`off` only when the art was already graded upstream.")
    p.add_argument("--vibrance", type=float, default=None, metavar="F",
                   help="override the preset's saturation lift (weighted toward the "
                        "dull pixels, so vivid areas do not clip)")
    p.add_argument("--lift", type=float, default=None, metavar="F",
                   help="override the preset's midtone brightness (gamma; highlights "
                        "cannot blow out)")
    p.add_argument("--contrast", type=float, default=None, metavar="F",
                   help="override the preset's contrast")
    p.add_argument("--bloom", type=float, default=None, metavar="F",
                   help="override the preset's highlight glow — this is what reads as "
                        "'brighter' at thumbnail size")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="store_compose.py",
        description="Compose store-listing images (triptych / showcase / banner / icon).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("triptych",
                       help="slice one wide key art into N continuous panels (no text)")
    t.add_argument("--src", required=True, help="wide key-art PNG (no text baked in)")
    t.add_argument("--out", required=True, help="output directory")
    t.add_argument("--panels", type=int, default=3)
    t.add_argument("--size", default=DEFAULT_SCREEN_SIZE,
                   help=f"size of ONE panel: WxH or a preset "
                        f"({', '.join(SIZE_PRESETS)}). Default {DEFAULT_SCREEN_SIZE} "
                        f"(App Store 6.9\")")
    t.add_argument("--prefix", default="store-")
    t.add_argument("--zoom", type=float, default=1.0,
                   help="oversample factor (>1) creating slack for --offset")
    t.add_argument("--offset", type=float, default=0.0,
                   help="-1..1 horizontal crop bias; slides a face off a panel seam "
                        "without regenerating the art (needs --zoom > 1)")
    t.add_argument("--gutter", default=DEFAULT_GUTTER, metavar="PX|N%|auto",
                   help="OPT-IN seam allowance thrown away at every cut, so the store's "
                        "own carousel gap stands in for it. It costs the picture: the "
                        "panels stop reassembling and each ends mid-object wherever the "
                        f"cut fell. Default 0 — nothing discarded. `auto` = "
                        f"{GUTTER_REF_PX}px at {GUTTER_REF_W}px panels, scaled to --size")
    t.add_argument("--seam-snap", default=DEFAULT_SNAP, metavar="PX|N%|auto|off",
                   help="how far the tiling may slide so the cuts fall on quiet "
                        "columns instead of through a face, a coin or the board's edge. "
                        "The panorama is composed with that much slack and the picture's "
                        "own column energy picks the cuts. With the default lossless cut "
                        "this is the only lever there is — panel width is fixed and "
                        "nothing may be discarded, so the cuts move together (default "
                        f"auto = {SNAP_REF * 100:.0f}%% of a panel; off = the "
                        "content-blind even split)")
    t.add_argument("--sprite", action="append", default=[], metavar="PNG[@k=v,...]",
                   help="composite a REAL game object (a transparent PNG out of "
                        "assets/images/) into the concept art, so the panels advertise "
                        "objects the app actually contains. Every split panel must have "
                        "at least one game anchor; auto-placement fills an empty panel "
                        "before doubling up. Repeatable, and the FIRST "
                        "one is the hero unless a role flag says otherwise: it takes "
                        f"panel 1 at ~{HERO_H:.0%} of the panel HEIGHT (capped at "
                        f"{HERO_W:.2f}× its width), because that is the screenshot the "
                        "store shows at full size and the note was that the figure on "
                        "it has to be big. Flags: hero, "
                        "prop, board (a `boardplate` play field — the middle panel at "
                        f"~{BOARD_W:.2f}× the panel width, standing inside the frame). "
                        "Keys: x,y (0..1 of the panorama), w and h (fractions of one "
                        "panel — for the hero w is the cap and h is the target), "
                        "panel (1-based), rot, bleed (how far the foot runs past the "
                        "bottom edge), glow, shadow, contact, light, occlude (how much "
                        "of the object's height the scene's foreground closes back over "
                        f"— {HERO_OCCLUDE} for the hero, {PROP_OCCLUDE} for props, 0 for "
                        "the legible board), opacity. Omit x "
                        "and objects are auto-placed at graded depths, standing on the "
                        "ground plane and always clear of the seams.")
    t.add_argument("--sprite-glow-color", default="#FFFFFF", metavar="HEX",
                   help="halo colour behind inlaid objects — pass the game's accent so "
                        "they sit in the art instead of on top of it")
    t.add_argument("--sprite-light", type=float, default=DEFAULT_SPRITE_LIGHT,
                   metavar="F",
                   help="0..1 — how hard each object is pulled into the scene's own "
                        "light (colour cast from the art it covers + an edge "
                        f"light-wrap). Default {DEFAULT_SPRITE_LIGHT}; 0 pastes the "
                        "sprite flat, which is what reads as a sticker.")
    t.add_argument("--save-pano", metavar="PNG",
                   help="also write the full graded panorama WITH the objects inlaid, "
                        "so `banner` and `backdrop` can reuse the same integrated art")
    t.add_argument("--pano-only", action="store_true",
                   help="write only --save-pano: no panels, no preview. This is the "
                        "layout DRAFT pass, whose output is a reference image for "
                        "`gpt_image.py edit`, not an upload asset")
    add_pop_args(t)
    # Retired: the panorama is pure image. Still parsed so a stale caller gets a
    # sentence explaining where the words go, not `unrecognized arguments`.
    for dead in ("--title", "--tagline", "--logo", "--title-pos"):
        t.add_argument(dead, default="", help=argparse.SUPPRESS)
    t.add_argument("--title-panel", type=int, default=0, help=argparse.SUPPRESS)
    t.set_defaults(func=cmd_triptych)

    bp = sub.add_parser(
        "boardplate",
        help="the game's REAL play field as a transparent cutout, for `triptych --sprite`")
    bp.add_argument("--out", required=True, metavar="PNG")
    bp.add_argument("--from-shot", metavar="PNG",
                    help="lift the field out of a captured gameplay frame — the most "
                         "exact match there is, and the right choice on any run that "
                         "already has frames. Needs --rect")
    bp.add_argument("--rect", metavar="X,Y,W,H",
                    help="the play field inside --from-shot: fractions of the frame "
                         "when <= 1, pixels otherwise")
    bp.add_argument("--symbol", action="append", default=[], metavar="PNG",
                    help="a real symbol PNG out of assets/images/. Repeatable, in "
                         "reading order; a short list is staggered across the grid")
    bp.add_argument("--grid", default="3x3", metavar="COLSxROWS",
                    help="the game's own field shape (default 3x3)")
    bp.add_argument("--frame", metavar="PNG",
                    help="the game's real board/panel asset, used as the plate's "
                         "background instead of drawn colours")
    bp.add_argument("--panel", default="", metavar="HEX",
                    help="board background colour — sample it from the game's board")
    bp.add_argument("--tile", default="", metavar="HEX", help="per-cell tile colour")
    bp.add_argument("--border", default="", metavar="HEX", help="board edge colour")
    bp.add_argument("--border-width", type=float, default=0.045, metavar="F",
                    help="border thickness as a fraction of one cell")
    bp.add_argument("--cell", type=int, default=320, metavar="PX",
                    help="one cell's size; the plate is scaled down into the panorama, "
                         "so generate it larger than it will be shown")
    bp.add_argument("--gap", type=float, default=0.06, metavar="F",
                    help="gap between cells, as a fraction of one cell")
    bp.add_argument("--pad", type=float, default=0.09, metavar="F",
                    help="board padding around the cells, as a fraction of one cell")
    bp.add_argument("--tile-radius", type=float, default=0.16, metavar="F")
    bp.add_argument("--symbol-pad", type=float, default=0.12, metavar="F",
                    help="breathing room between a symbol and its cell edge")
    bp.add_argument("--radius", type=float, default=0.05, metavar="F",
                    help="the plate's own corner radius, as a fraction of its short side")
    bp.add_argument("--sheen", type=float, default=0.35, metavar="F",
                    help="0..1 glass highlight across the field; 0 for none")
    bp.add_argument("--yaw", type=float, default=-14.0, metavar="DEG",
                    help="turn the board around its vertical axis, so it has a near "
                         "edge and a far edge instead of facing the camera flat")
    bp.add_argument("--pitch", type=float, default=6.0, metavar="DEG",
                    help="tip the board away from the camera, so it stands on the "
                         "scene's ground plane rather than floating parallel to it")
    bp.add_argument("--depth", type=float, default=0.05, metavar="F",
                    help="slab thickness as a fraction of the board's short side; the "
                         "visible edge is what makes it an object and not a decal")
    bp.add_argument("--tilt", type=float, default=0.0, metavar="DEG",
                    help="roll the finished plate in the picture plane, after the "
                         "perspective, to match the stage it is standing on")
    bp.add_argument("--win", default="", metavar="CxR,CxR,...",
                    help="the cells that PAY, 1-based COLxROW in the order they pay "
                         "(e.g. 1x2,2x2,3x2). They get the payline, an accent ring and "
                         "the light it spills onto the panel, and the rest of the field "
                         "falls back (--dim). The middle panel of the listing is the "
                         "gameplay example: a correct grid at rest is the slide that "
                         "came back as boring, and this is what makes it a moment "
                         "without inventing anything the app does not have")
    bp.add_argument("--win-color", default="", metavar="HEX",
                    help="the game's own win/accent colour for the payline, rings and "
                         "glow (default: --border, then a warm gold)")
    bp.add_argument("--dim", type=float, default=0.35, metavar="F",
                    help="0..0.9 — how far the non-paying cells fall back, so the win "
                         "reads first. Only applies with --win")
    bp.add_argument("--lift", type=float, default=1.45, metavar="F",
                    help="scale of the paying symbol as it rises out of its cell, with "
                         "its own shadow landing on the board — the cue that says the "
                         "round is resolving, not posed. Composited after the "
                         "perspective, because it is leaving the board's plane. 1 or "
                         "less to keep the field flat; needs --win")
    bp.set_defaults(func=cmd_boardplate)

    s = sub.add_parser("showcase", help="real game frame in a phone on a themed background")
    s.add_argument("--shot", required=True)
    s.add_argument("--bg", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--size", default=DEFAULT_SCREEN_SIZE,
                   help=f"WxH or a preset ({', '.join(SIZE_PRESETS)}). "
                        f"Default {DEFAULT_SCREEN_SIZE} (App Store 6.9\")")
    s.add_argument("--caption", default="")
    s.add_argument("--caption-color", default="#FFFFFF")
    s.add_argument("--caption-color2", default="",
                   help="second stop for a vertical gradient on the caption")
    s.add_argument("--frame", choices=("ios", "android", "none"), default="ios")
    s.add_argument("--scale", type=float, default=0.82, help="device width as a fraction of canvas")
    s.add_argument("--fit", choices=("contain", "bleed"), default="contain",
                   help="contain = whole phone visible (default, crops nothing); "
                        "bleed = phone fills the canvas, bottom runs off the edge")
    s.add_argument("--bg-treatment", choices=("soft", "blur", "dim", "none"), default="soft")
    add_pop_args(s)
    add_text_args(s)
    s.set_defaults(func=cmd_showcase)

    b = sub.add_parser("banner", help="Google Play feature graphic")
    b.add_argument("--keyart", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--size", default="1024x500")
    b.add_argument("--shot", help="optional in-game frame for the device mockup")
    b.add_argument("--frame", choices=("ios", "android", "none"), default="ios")
    b.add_argument("--zoom", type=float, default=1.0,
                   help="oversample factor (>1) creating slack for --offset")
    b.add_argument("--offset", type=float, default=0.0,
                   help="-1..1 horizontal crop bias — which slice of a wide panorama "
                        "becomes the banner. The centre crop of a 3-panel panorama "
                        "misses the hero on panel 1 entirely; slide it until the hero "
                        "is in frame and clear of the title column and the device")
    b.add_argument("--title", default="")
    b.add_argument("--tagline", default="")
    add_pop_args(b)
    add_text_args(b)
    b.set_defaults(func=cmd_banner)

    d = sub.add_parser("backdrop",
                       help="export the key art as the GAME's own background so the "
                            "listing and the app show one world")
    d.add_argument("--src", required=True, help="the same key art the panels are cut from")
    d.add_argument("--out-dir", required=True, metavar="DIR",
                   help="normally assets/images/backgrounds")
    d.add_argument("--prefix", default="bg_keyart")
    d.add_argument("--size", default="1080x1920",
                   help=f"WxH or a preset ({', '.join(SIZE_PRESETS)}). This is an "
                        "in-app asset, so keep it phone-sized (default 1080x1920)")
    d.add_argument("--variants", default="menu,game",
                   help=f"comma-separated: {', '.join(BACKDROP_VARIANTS)} (default menu,game)")
    d.add_argument("--calm", type=float, default=0.45, metavar="F",
                   help="0..1 — how far the `game` variant is pushed behind the live "
                        "field (blur + dim + desaturation). Default 0.45")
    d.add_argument("--vignette", type=float, default=0.18, metavar="F",
                   help="0..1 corner darkening (default 0.18)")
    d.add_argument("--zoom", type=float, default=1.0,
                   help="oversample factor (>1) creating slack for --offset")
    d.add_argument("--offset", type=float, default=0.0,
                   help="-1..1 horizontal crop bias — which slice of a wide panorama "
                        "becomes the app's background")
    add_pop_args(d)
    d.set_defaults(func=cmd_backdrop)

    i = sub.add_parser("icon", help="launcher + store icon set")
    i.add_argument("--src", required=True, help="square icon artwork (full-bleed)")
    i.add_argument("--fg-src", help="transparent emblem for the Android adaptive foreground")
    i.add_argument("--out-dir", required=True)
    i.add_argument("--bg", default="#101018", help="adaptive/flatten background colour")
    i.set_defaults(func=cmd_icon)

    f = sub.add_parser("fonts", help="report which display faces this machine can use")
    f.add_argument("--font-dir", action="append", default=[], metavar="DIR",
                   help="also index the game's own fonts (e.g. assets/fonts)")
    f.add_argument("--type-mood", choices=tuple(TYPE_MOODS), default="bold")
    f.add_argument("--mood-only", action="store_true",
                   help="report just --type-mood instead of every mood")
    f.add_argument("--sample", default="Spin Collect Level Up 7",
                   help="the copy the listing will actually set — faces without glyphs "
                        "for it are excluded (default probes Latin + digits)")
    f.set_defaults(func=cmd_fonts)

    c = sub.add_parser("check", help="validate a finished store directory")
    c.add_argument("--dir", required=True)
    c.add_argument("--store", choices=("any", "play", "appstore"), default="any",
                   help="fail (not just report) when the shape is invalid for this "
                        "store: Play caps the long side at 2× the short one, the App "
                        "Store takes only its own display slots (default any)")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
