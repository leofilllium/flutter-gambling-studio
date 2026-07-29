#!/usr/bin/env python3
"""
store_compose.py — store-listing image compositor for the game studio.

Produces the full set of publishable listing images for ANY game the studio
makes (genre/theme agnostic — everything visual comes from the arguments):

  triptych  N vertical panels sliced out of ONE wide key-art panorama, so the
            first N store screenshots read as a single continuous picture when
            the store shows them side by side. This is a *conceptual* poster of
            the game world, not a screen of the app.
  showcase  a real in-game frame placed inside a drawn phone (bezel, notch,
            home indicator, glass glare, drop shadow) over a themed background.
  banner    Google Play feature graphic (1024x500) — key art + optional device
            mockup + optional title, laid out inside Play's safe area.
  icon      launcher/store icon set derived from generated art: 1024 master,
            1024 adaptive foreground (subject inside Android's 66% safe zone),
            512 store icon.
  check     validates a finished directory against store constraints.

Why a tool instead of inline ImageMagick: rounded corners, notches, glare,
fractional-alpha shadows and auto-fitted text are exactly the steps that
silently degrade when written as one-off `convert` incantations. Here they are
deterministic, testable and identical across every game.

Requires: Pillow + numpy (both already required by tools/cutout.py).

Examples:
  python3 tools/store_compose.py triptych --src keyart.png --out store/ \\
      --panels 3 --size 1242x2688 --title "Zeus Slots" --tagline "Match. Chain. Ascend."
  python3 tools/store_compose.py showcase --shot raw/02-menu.png --bg keyart.png \\
      --out store/store-04.png --size 1242x2688 --caption "Собери комбо"
  python3 tools/store_compose.py banner --keyart keyart.png --shot raw/02-menu.png \\
      --out store/feature-graphic-1024x500.png --title "Zeus Slots"
  python3 tools/store_compose.py icon --src icon_art.png --fg-src emblem.png \\
      --out-dir assets/branding --bg "#2A0E4F"
"""

from __future__ import annotations

import argparse
import math
import sys
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

FONTS_BOLD = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)
FONTS_REGULAR = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
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
    try:
        w, h = str(text).lower().replace("×", "x").split("x")
        size = (int(w), int(h))
    except Exception:
        die(f"bad --size {text!r}; expected WIDTHxHEIGHT, e.g. 1242x2688")
    if size[0] < 16 or size[1] < 16:
        die(f"--size {text!r} is too small")
    return size


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
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


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

def find_font(explicit: str | None, bold: bool) -> str | None:
    if explicit:
        if not Path(explicit).is_file():
            die(f"--font not found: {explicit}")
        return explicit
    for candidate in (FONTS_BOLD if bold else FONTS_REGULAR):
        if Path(candidate).is_file():
            return candidate
    return None


def load_font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def wrap_lines(text: str, font, draw: ImageDraw.ImageDraw, max_w: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            probe = f"{current} {word}".strip()
            if not current or draw.textlength(probe, font=font) <= max_w:
                current = probe
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return [ln for ln in lines if ln != ""] or [""]


def fit_text(text: str, font_path: str | None, max_w: int, max_h: int,
             max_size: int, min_size: int = 14, spacing: float = 1.16,
             max_lines: int = 3):
    """Largest font size at which `text` wraps inside max_w×max_h and max_lines."""
    scratch = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

    def measure(size: int):
        font = load_font(font_path, size)
        lines = wrap_lines(text, font, scratch, max_w)
        line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
        step = int(line_h * spacing)
        widest = max(scratch.textlength(ln, font=font) for ln in lines)
        return font, lines, len(lines) * step, step, widest

    lo, hi, best = min_size, max(min_size, max_size), None
    while lo <= hi:
        mid = (lo + hi) // 2
        font, lines, total, step, widest = measure(mid)
        if total <= max_h and widest <= max_w and len(lines) <= max_lines:
            best = (font, lines, total, step)
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        font, lines, total, step, _ = measure(min_size)
        best = (font, lines, total, step)
    return best


def draw_text_block(base: Image.Image, text: str, box: tuple[int, int, int, int],
                    font_path: str | None, colour, max_size: int,
                    valign: str = "center", stroke: int = 0,
                    stroke_colour=(0, 0, 0, 210), max_lines: int = 3) -> tuple[int, int]:
    """Draw auto-fitted, centred, shadowed text inside box=(x,y,w,h).

    Returns (top, height) of the drawn block so callers can stack elements.
    """
    x, y, w, h = box
    if not text.strip():
        return (y, 0)
    font, lines, total, step = fit_text(text, font_path, w, h, max_size, max_lines=max_lines)
    top = y if valign == "top" else (y + h - total if valign == "bottom" else y + (h - total) // 2)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    shadow_off = max(2, font.size // 22)
    cy = top
    for line in lines:
        lw = draw.textlength(line, font=font)
        lx = x + (w - lw) / 2
        draw.text((lx + shadow_off, cy + shadow_off), line, font=font, fill=(0, 0, 0, 150))
        draw.text((lx, cy), line, font=font, fill=colour,
                  stroke_width=stroke, stroke_fill=stroke_colour if stroke else None)
        cy += step
    base.alpha_composite(layer)
    return (top, total)


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

def brand_block(canvas: Image.Image, box: tuple[int, int, int, int], title: str,
                tagline: str, logo_path: str | None, args) -> None:
    """Title / tagline / emblem lockup drawn inside one panel of the panorama."""
    px, py, pw, ph = box
    bold = find_font(args.font, bold=True)
    regular = find_font(args.font_regular or args.font, bold=False)

    pos = args.title_pos
    block_h = int(ph * 0.30)
    fade = int(ph * 0.14)
    block_y = {"top": int(ph * 0.07),
               "center": (ph - block_h) // 2}.get(pos, ph - block_h - int(ph * 0.08))

    # The scrim runs to the panel edge on the text's side, so the lockup never
    # sits in the fading part of the gradient.
    if pos == "top":
        scrim(canvas, (px, py, pw, block_y + block_h + fade), strength=args.scrim,
              from_top=True, ramp=fade / max(1, block_y + block_h + fade))
    elif pos == "center":
        scrim(canvas, (px, py + block_y - fade, pw, block_h + 2 * fade),
              strength=args.scrim * 0.85, from_top=True, ramp=0.30)
        scrim(canvas, (px, py + block_y - fade, pw, fade), strength=args.scrim * 0.85,
              from_top=False, ramp=0.95)
    else:
        top = py + block_y - fade
        scrim(canvas, (px, top, pw, ph - (top - py)), strength=args.scrim,
              from_top=False, ramp=fade / max(1, ph - (top - py)))

    cursor = py + block_y
    side = int(pw * 0.08)
    inner_w = pw - 2 * side

    if logo_path:
        logo = load_image(logo_path, "logo")
        logo = contain(logo, int(pw * 0.40), int(ph * 0.125))
        canvas.alpha_composite(logo, (px + (pw - logo.width) // 2, cursor))
        cursor += logo.height + int(ph * 0.016)

    if title:
        _, drawn = draw_text_block(
            canvas, title.upper(), (px + side, cursor, inner_w, int(ph * 0.13)),
            bold, hex_rgba(args.title_color), max_size=int(pw * 0.20),
            valign="top", stroke=max(2, int(pw * 0.004)), max_lines=2,
        )
        cursor += drawn + int(ph * 0.018)

    if tagline:
        draw_text_block(
            canvas, tagline, (px + side, cursor, inner_w, int(ph * 0.09)),
            regular, hex_rgba(args.tagline_color), max_size=int(pw * 0.070),
            valign="top", max_lines=2,
        )


def cmd_triptych(args) -> None:
    w, h = parse_size(args.size)
    n = args.panels
    if not 2 <= n <= 5:
        die(f"--panels {n} out of range (2..5)")
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
    if args.title or args.tagline or args.logo:
        idx = max(1, min(args.title_panel, n)) - 1
        brand_block(pano, (idx * w, 0, w, h), args.title or "", args.tagline or "",
                    args.logo, args)

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
    bold = find_font(args.font, bold=True)
    cap_max = int(w * 0.095)
    if caption:
        # The band follows the text instead of taking a fixed slice: a one-line
        # caption must not cost the phone the same height as a two-line one.
        _, _, cap_text_h, _ = fit_text(caption, bold, int(w * 0.86), int(h * 0.12),
                                       cap_max, max_lines=2)
        cap_h = cap_text_h + int(h * 0.052)
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
        scrim(canvas, (0, 0, w, int(cap_h * 1.35)), strength=args.scrim, from_top=True)
        pad_t = int(h * 0.026)
        draw_text_block(canvas, caption,
                        (int(w * 0.07), pad_t, int(w * 0.86), max(1, cap_h - 2 * pad_t)),
                        bold, hex_rgba(args.caption_color), max_size=cap_max,
                        valign="center", stroke=max(2, int(w * 0.003)), max_lines=2)

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
        text_w = int(w * 0.50) if args.shot else int(w * 0.80)
        x = int(w * 0.06)
        canvas.alpha_composite(gradient((text_w + int(w * 0.10), h), [
            (0.0, (0, 0, 0, int(0.55 * 255))), (1.0, (0, 0, 0, 0))
        ], horizontal=True), (0, 0))
        block_h = int(h * 0.46)
        y = (h - block_h) // 2
        cursor = y
        if args.title:
            _, drawn = draw_text_block(
                canvas, args.title.upper(), (x, cursor, text_w, int(h * 0.30)),
                find_font(args.font, bold=True), hex_rgba(args.title_color),
                max_size=int(h * 0.26), valign="top", stroke=max(2, int(h * 0.006)),
                max_lines=2)
            cursor += drawn + int(h * 0.04)
        if args.tagline:
            draw_text_block(
                canvas, args.tagline, (x, cursor, text_w, int(h * 0.16)),
                find_font(args.font_regular or args.font, bold=False),
                hex_rgba(args.tagline_color), max_size=int(h * 0.10), valign="top")

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


def cmd_check(args) -> None:
    d = Path(args.dir)
    if not d.is_dir():
        die(f"not a directory: {d}")
    files = sorted(p for p in d.glob("*.png") if not p.name.startswith("_"))
    if not files:
        die(f"no store PNGs in {d}")

    problems = 0
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
        flags = []
        if min(w, h) < PLAY_MIN_SIDE:
            flags.append(f"side <{PLAY_MIN_SIDE}px")
        if max(w, h) > PLAY_MAX_SIDE:
            flags.append(f"side >{PLAY_MAX_SIDE}px")
        if size > PLAY_MAX_BYTES:
            flags.append(f">{PLAY_MAX_BYTES // 1024 // 1024}MB")
        if flags:
            problems += 1
            print(f"❌ {p.name}  {w}×{h} {mode} {size // 1024}KB — {', '.join(flags)}")
        else:
            print(f"✅ {p.name}  {w}×{h} {mode} {size // 1024}KB")

    sizes = set()
    for p in files:
        if p.name.startswith("store-"):
            with Image.open(p) as im:
                sizes.add(im.size)
    if len(sizes) > 1:
        warn(f"screenshots have mixed sizes {sorted(sizes)} — stores expect one consistent size")

    if problems:
        die(f"{problems} file(s) violate store constraints")
    ok(f"{len(files)} file(s) pass store constraints")


# ───────────────────────────── cli ──────────────────────────────────────────

def add_text_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--font", help="TTF for headings (default: Liberation/DejaVu/Arial Bold)")
    p.add_argument("--font-regular", help="TTF for body text")
    p.add_argument("--title-color", default="#FFFFFF")
    p.add_argument("--tagline-color", default="#F2F4FA")
    p.add_argument("--scrim", type=float, default=0.72,
                   help="0..1 darkening behind text (default 0.72)")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="store_compose.py",
        description="Compose store-listing images (triptych / showcase / banner / icon).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("triptych", help="slice one wide key art into N continuous panels")
    t.add_argument("--src", required=True, help="wide key-art PNG (no text baked in)")
    t.add_argument("--out", required=True, help="output directory")
    t.add_argument("--panels", type=int, default=3)
    t.add_argument("--size", default="1242x2688", help="size of ONE panel (default 1242x2688)")
    t.add_argument("--prefix", default="store-")
    t.add_argument("--title", default="")
    t.add_argument("--tagline", default="")
    t.add_argument("--logo", help="transparent emblem PNG placed above the title")
    t.add_argument("--title-panel", type=int, default=1,
                   help="1-based panel that carries the lockup (default 1)")
    t.add_argument("--title-pos", choices=("top", "center", "bottom"), default="bottom")
    t.add_argument("--zoom", type=float, default=1.0,
                   help="oversample factor (>1) creating slack for --offset")
    t.add_argument("--offset", type=float, default=0.0,
                   help="-1..1 horizontal crop bias; slides a face off a panel seam "
                        "without regenerating the art (needs --zoom > 1)")
    add_text_args(t)
    t.set_defaults(func=cmd_triptych)

    s = sub.add_parser("showcase", help="real game frame in a phone on a themed background")
    s.add_argument("--shot", required=True)
    s.add_argument("--bg", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--size", default="1242x2688")
    s.add_argument("--caption", default="")
    s.add_argument("--caption-color", default="#FFFFFF")
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

    c = sub.add_parser("check", help="validate a finished store directory")
    c.add_argument("--dir", required=True)
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
