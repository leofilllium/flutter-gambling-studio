#!/usr/bin/env python3
"""
store_compose.py — store-listing image compositor for the game studio.

Produces the full set of publishable listing images for ANY game the studio
makes (genre/theme agnostic — everything visual comes from the arguments):

  triptych  N vertical panels sliced out of ONE wide key-art panorama, so the
            first N store screenshots read as a single continuous picture when
            the store shows them side by side. This is a *conceptual* poster of
            the game world, not a screen of the app — and it carries NO TEXT:
            lettering across a panel boundary is cut by the store's gutters,
            and a lockup inside one panel breaks the single-picture illusion.
  showcase  a real in-game frame placed inside a drawn phone (bezel, notch,
            home indicator, glass glare, drop shadow) over a themed background,
            with the caption typography that sells the frame.
  banner    Google Play feature graphic (1024x500) — key art + optional device
            mockup + title lockup, laid out inside Play's safe area.
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

Typography is treated as display type, not UI labels: the face is chosen by
mood (or taken from the game's own assets/fonts via --font-dir), letter spacing
is tuned per mood, and text is rendered through an alpha mask so the fill can
be a gradient in the game's palette and the shadow can be a real blur.

Requires: Pillow + numpy (both already required by tools/cutout.py).

Examples:
  python3 tools/store_compose.py fonts --font-dir assets/fonts
  python3 tools/store_compose.py triptych --src keyart.png --out store/ \\
      --panels 3 --size 1320x2868
  python3 tools/store_compose.py showcase --shot raw/02-menu.png --bg keyart.png \\
      --out store/store-04.png --size 1320x2868 --caption "Ставка решает" \\
      --type-mood epic --caption-color "#FFF6DC" --caption-color2 "#F0B34A"
  python3 tools/store_compose.py showcase ... --size play   # 9:16 set for Play
  python3 tools/store_compose.py banner --keyart keyart.png --shot raw/02-menu.png \\
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

    This gate matters more than any other font choice here: the studio's UI
    language is Russian, and most display faces (Bodoni, Didot, Impact, Anton,
    Orbitron, Press Start 2P) ship Latin only. Without the check, a Cyrillic
    caption composites as a row of empty rectangles — which is exactly what it
    did before this existed.
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


# ───────────────────────────── subcommands ──────────────────────────────────

def cmd_triptych(args) -> None:
    w, h = parse_size(args.size)
    n = args.panels
    if not 2 <= n <= 5:
        die(f"--panels {n} out of range (2..5)")

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

    src = load_image(args.src, "key art")

    pano_w, pano_h = w * n, h
    want, got = pano_w / pano_h, src.width / src.height
    if abs(want - got) / want > 0.35:
        warn(f"key art aspect {got:.2f} is far from the {n}-panel panorama {want:.2f} — "
             f"cover-crop will discard a lot of the picture")
    if src.width < pano_w * 0.35:
        warn(f"key art is {src.width}px wide for a {pano_w}px panorama "
             f"({pano_w / src.width:.1f}× upscale) — generate it as wide as the model allows")

    pano = cover(src, pano_w, pano_h, bias_x=args.offset, zoom=args.zoom)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for i in range(n):
        panel = pano.crop((i * w, 0, (i + 1) * w, h))
        path = out_dir / f"{args.prefix}{i + 1:02d}.png"
        total += save_png(panel, path)
        ok(f"{path.name}  {w}×{h}")

    # Stitched preview with seam guides — cheap vision check that nothing
    # important (a face, the title) got cut by a panel boundary.
    preview = pano.resize((1800, max(1, round(1800 * pano_h / pano_w))), RES)
    guide = ImageDraw.Draw(preview)
    for i in range(1, n):
        x = round(preview.width * i / n)
        guide.line([(x, 0), (x, preview.height)], fill=(255, 0, 128, 255), width=3)
    save_png(preview, out_dir / "_panorama-preview.png")
    ok(f"_panorama-preview.png  stitched {n}-panel check (seams marked)")
    info(f"panorama {pano_w}×{pano_h}, {total // 1024} KB across {n} panels")


def cmd_showcase(args) -> None:
    w, h = parse_size(args.size)
    canvas = treat_background(cover(load_image(args.bg, "background"), w, h), args.bg_treatment)

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
    canvas = cover(load_image(args.keyart, "key art"), w, h)

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

    Always run this with the real copy (--sample) before a listing: a face that
    is perfect for a Latin title may have no Cyrillic at all, and the report is
    the cheap way to find that out.
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
    # Retired: the panorama is pure image. Still parsed so a stale caller gets a
    # sentence explaining where the words go, not `unrecognized arguments`.
    for dead in ("--title", "--tagline", "--logo", "--title-pos"):
        t.add_argument(dead, default="", help=argparse.SUPPRESS)
    t.add_argument("--title-panel", type=int, default=0, help=argparse.SUPPRESS)
    t.set_defaults(func=cmd_triptych)

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
    add_text_args(s)
    s.set_defaults(func=cmd_showcase)

    b = sub.add_parser("banner", help="Google Play feature graphic")
    b.add_argument("--keyart", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--size", default="1024x500")
    b.add_argument("--shot", help="optional in-game frame for the device mockup")
    b.add_argument("--frame", choices=("ios", "android", "none"), default="ios")
    b.add_argument("--title", default="")
    b.add_argument("--tagline", default="")
    add_text_args(b)
    b.set_defaults(func=cmd_banner)

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
    f.add_argument("--sample", default="Играй Собирай Level Up 7",
                   help="the copy the listing will actually set — faces without glyphs "
                        "for it are excluded (default probes Cyrillic + Latin + digits)")
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
