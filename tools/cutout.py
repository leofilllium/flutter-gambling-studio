#!/usr/bin/env python3
"""
cutout.py — production-grade background removal for studio PNG assets.

Replaces the old `magick -fuzz 12% -transparent white` one-liner, which is a
*global* colour match and therefore:
  * punches holes through white highlights, eyes, chrome, foam, ice, glass;
  * yields binary alpha (jagged, aliased silhouettes at game size);
  * leaves the anti-aliased rim opaque → white halo on dark backgrounds;
  * never trims/normalises, so a sprite set has wildly different framing.

This tool instead does what a compositor does:

  1. KEY DETECTION      — reads the actual background colour off the border
                          ring (white, chroma magenta/green, anything flat)
                          and measures how flat it really is.
  2. CONNECTED FLOOD    — removes only background *reachable from the border*,
                          so interior key-coloured pixels (a white glint, a
                          green gem) are never eaten.
  3. FRACTIONAL MATTE   — estimates real 0..1 alpha in the ~2 px edge band by
                          unmixing the observed colour against the key and the
                          local foreground colour, blended with a geometric
                          ramp where unmixing is unreliable. No more staircase.
  4. DECONTAMINATION    — un-premultiplies the key out of the edge pixels, so
                          the white/green/magenta fringe disappears instead of
                          being baked in.
  5. DESPECKLE          — drops isolated 1–2 px islands left by the model.
  6. TRIM + NORMALISE   — crops to content and re-pads to a uniform square
                          canvas with a constant margin, so a whole sprite set
                          shares framing (resized on premultiplied alpha, which
                          is what stops the halo from creeping back in).

`rembg` is used as an *assist* when installed (it constrains the flood so a
white object on a white background cannot be eaten), never as the whole
pipeline — its raw output is blobby and binary at the edges.

Requires: numpy + Pillow.  Optional: rembg (auto-detected).

Usage:
  python3 tools/cutout.py assets/images/sprites/cherry.png --type sprite
  python3 tools/cutout.py --dir assets/images/sprites --type sprite
  python3 tools/cutout.py --dir assets/images/sprites --check      # audit only
  python3 tools/cutout.py in.png --key '#FF00FF' --json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment guard
    sys.stderr.write(
        f"✗ cutout.py requires numpy + Pillow ({exc}).\n"
        "  Debian/Ubuntu: apt-get install -y python3-numpy python3-pil\n"
        "  Otherwise:     pip install numpy pillow\n"
    )
    raise SystemExit(2)

Image.MAX_IMAGE_PIXELS = None

# Asset-type presets: output canvas + margin around the content.
# Backgrounds and full-bleed panels must never be keyed.
TYPE_PRESETS = {
    "sprite": dict(size=512, pad=0.04, cut=True),
    "symbol": dict(size=512, pad=0.04, cut=True),
    "wild": dict(size=512, pad=0.04, cut=True),
    "scatter": dict(size=512, pad=0.04, cut=True),
    "tile": dict(size=512, pad=0.02, cut=True),
    "item": dict(size=512, pad=0.04, cut=True),
    "icon": dict(size=256, pad=0.08, cut=True),
    "ui": dict(size=512, pad=0.04, cut=True),
    "ui_panel": dict(size=None, pad=None, cut=False),
    "background": dict(size=None, pad=None, cut=False),
    "scene": dict(size=None, pad=None, cut=False),
    "raw": dict(size=None, pad=0.0, cut=True),
}

# Recommended key colours, most reliable first. The subject's palette decides:
# pick the key furthest from it. Detection is generic — these are only what the
# generation prompt should ask for.
KEY_PRESETS = {
    "magenta": (255, 0, 255),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
}


# ---------------------------------------------------------------------------
# Small numpy helpers (integral-image box filters — O(N) at any radius)
# ---------------------------------------------------------------------------
def _box_sum(a: np.ndarray, r: int) -> tuple[np.ndarray, np.ndarray]:
    """Windowed sum of `a` over a (2r+1)² box, plus the per-pixel window size."""
    h, w = a.shape
    ii = np.zeros((h + 1, w + 1), dtype=np.float64)
    ii[1:, 1:] = np.cumsum(np.cumsum(a.astype(np.float64), axis=0), axis=1)
    y0 = np.clip(np.arange(h) - r, 0, h)
    y1 = np.clip(np.arange(h) + r + 1, 0, h)
    x0 = np.clip(np.arange(w) - r, 0, w)
    x1 = np.clip(np.arange(w) + r + 1, 0, w)
    total = (
        ii[np.ix_(y1, x1)] - ii[np.ix_(y0, x1)] - ii[np.ix_(y1, x0)] + ii[np.ix_(y0, x0)]
    )
    count = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    return total, count.astype(np.float64)


def box_mean(a: np.ndarray, r: int) -> np.ndarray:
    total, count = _box_sum(a, r)
    return total / np.maximum(count, 1.0)


def dilate(mask: np.ndarray, r: int) -> np.ndarray:
    if r <= 0:
        return mask
    total, _ = _box_sum(mask.astype(np.float64), r)
    return total > 0.5


def _propagate_axis(seed: np.ndarray, passable: np.ndarray, axis: int) -> np.ndarray:
    """Flood every passable run (along `axis`) that already contains a seed.

    Scanline flood fill, fully vectorised: a "run" is a maximal stretch of
    passable pixels in one row/column; it fills iff any pixel in it is seeded.
    """
    if axis == 0:
        seed, passable = seed.T, passable.T
    h, w = passable.shape
    # Run id = number of barriers seen so far on this line; unique per line.
    run = np.cumsum(~passable, axis=1) + (np.arange(h, dtype=np.int64) * (w + 1))[:, None]
    flat_run = run[passable]
    if flat_run.size == 0:
        out = np.zeros_like(seed)
        return out.T if axis == 0 else out
    n = int(flat_run.max()) + 1
    hit = np.bincount(flat_run, weights=seed[passable].astype(np.float64), minlength=n) > 0
    out = passable & hit[run]
    return out.T if axis == 0 else out


def flood_from_border(passable: np.ndarray) -> np.ndarray:
    """Background = passable pixels connected to the image border."""
    seed = np.zeros_like(passable)
    seed[0, :] = seed[-1, :] = True
    seed[:, 0] = seed[:, -1] = True
    seed &= passable
    for _ in range(64):
        grown = _propagate_axis(seed, passable, axis=1)
        grown = _propagate_axis(grown, passable, axis=0)
        if grown.sum() == seed.sum():
            return grown
        seed = grown
    return seed


# ---------------------------------------------------------------------------
# Key colour
# ---------------------------------------------------------------------------
def parse_key(spec: str | None) -> tuple[int, int, int] | None:
    if not spec or spec == "auto":
        return None
    if spec in KEY_PRESETS:
        return KEY_PRESETS[spec]
    s = spec.lstrip("#")
    if len(s) == 6:
        return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    raise ValueError(f"unrecognised --key: {spec!r} (use auto|white|magenta|green|blue|#RRGGBB)")


def detect_key(rgb: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Median colour of the border ring + how flat that ring is (p50/p95 spread)."""
    h, w = rgb.shape[:2]
    r = max(3, int(round(min(h, w) * 0.012)))
    ring = np.concatenate(
        [
            rgb[:r, :, :].reshape(-1, 3),
            rgb[-r:, :, :].reshape(-1, 3),
            rgb[:, :r, :].reshape(-1, 3),
            rgb[:, -r:, :].reshape(-1, 3),
        ]
    )
    key = np.median(ring, axis=0)
    dist = np.sqrt(((ring - key) ** 2).sum(axis=1))
    return key, float(np.percentile(dist, 50)), float(np.percentile(dist, 95))


# ---------------------------------------------------------------------------
# rembg assist (optional)
# ---------------------------------------------------------------------------
# One subprocess for the whole batch: loading the ~180 MB ONNX model costs more
# than the inference, so paying it once per run instead of once per file is the
# difference between seconds and minutes on a 15-sprite set.
_REMBG_SNIPPET = """
import sys
from pathlib import Path
from rembg import remove, new_session
session = new_session(sys.argv[1])
for pair in sys.argv[2:]:
    src, dst = pair.split("::", 1)
    try:
        Path(dst).write_bytes(remove(Path(src).read_bytes(), session=session))
    except Exception as exc:
        print(f"rembg failed on {src}: {exc}", file=sys.stderr)
"""

_REMBG_RUNNER: str | None | tuple = ()  # () = not probed yet


def find_rembg() -> str | None:
    """An interpreter that can `import rembg`, or 'cli', or None. Probed once."""
    global _REMBG_RUNNER
    if _REMBG_RUNNER != ():
        return _REMBG_RUNNER  # type: ignore[return-value]
    _REMBG_RUNNER = None
    for cand in (os.environ.get("REMBG_PYTHON"), "/opt/rembg/bin/python3", sys.executable):
        if not cand or not Path(cand).exists():
            continue
        try:
            probe = subprocess.run([cand, "-c", "import rembg"], capture_output=True, timeout=300)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            _REMBG_RUNNER = cand
            return _REMBG_RUNNER
    if shutil.which("rembg"):
        _REMBG_RUNNER = "cli"
    return _REMBG_RUNNER


def rembg_masks(paths: list[Path], runner: str) -> dict[Path, np.ndarray]:
    """Alpha masks for `paths`, keyed by path. Missing entries just mean no assist."""
    model = os.environ.get("REMBG_MODEL", "isnet-general-use")
    out: dict[Path, np.ndarray] = {}
    with tempfile.TemporaryDirectory() as tmp:
        targets = {p: Path(tmp) / f"{i}.png" for i, p in enumerate(paths)}
        if runner == "cli":
            cmds = [["rembg", "i", "-m", model, str(s), str(d)] for s, d in targets.items()]
        else:
            args = [f"{s}::{d}" for s, d in targets.items()]
            cmds = [[runner, "-c", _REMBG_SNIPPET, model, *args]]
        for cmd in cmds:
            try:
                subprocess.run(cmd, capture_output=True, timeout=1800)
            except (OSError, subprocess.TimeoutExpired):
                continue
        for src, dst in targets.items():
            if not dst.exists():
                continue
            try:
                arr = np.asarray(Image.open(dst).convert("RGBA"), dtype=np.float64)
                out[src] = arr[:, :, 3] / 255.0
            except Exception:
                continue
    return out


# ---------------------------------------------------------------------------
# Core matte
# ---------------------------------------------------------------------------
def build_matte(
    rgb: np.ndarray,
    key: np.ndarray,
    *,
    tolerance: float,
    band: int,
    rembg_mask: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return (alpha 0..1, decontaminated rgb, stats)."""
    dist_to_key = np.sqrt(((rgb - key) ** 2).sum(axis=2))
    key_chroma = key - key.mean()
    key_norm = float(np.sqrt((key_chroma * key_chroma).sum()))
    is_chroma_key = key_norm > 30.0  # magenta/green/blue vs white/grey

    # 1. Coarse background: near-key AND reachable from the border.
    passable = dist_to_key <= tolerance
    bg = flood_from_border(passable)

    # 2. rembg assist — it cannot *add* background, only veto it. This is what
    #    saves a white chicken on a white background from being eaten.
    if rembg_mask is not None and rembg_mask.shape == bg.shape:
        confident_fg = rembg_mask > 0.65
        bg &= ~confident_fg

    fg = ~bg

    # 3. Local foreground colour estimate (weighted blur over fg pixels only),
    #    used both for unmixing and for stabilising very low-alpha pixels.
    fg_f = fg.astype(np.float64)
    radius = max(3, band * 3)
    density = box_mean(fg_f, radius)  # how much solid foreground is nearby
    fg_est = np.stack(
        [box_mean(rgb[:, :, c] * fg_f, radius) / np.maximum(density, 1e-6) for c in range(3)],
        axis=2,
    )

    # 4. Fractional alpha along the silhouette. Two estimators:
    #    a) unmix   — project the observed colour onto the key→foreground axis.
    #                 Exact, but needs a believable local foreground colour.
    #    b) geometry — smooth ramp off the flood mask. The safety net for when
    #                 the object's colour IS the key colour (white on white).
    delta = fg_est - key
    denom = (delta * delta).sum(axis=2)
    a_unmix = np.clip(((rgb - key) * delta).sum(axis=2) / np.maximum(denom, 1e-6), 0.0, 1.0)
    a_geo = box_mean(fg_f, band)

    trust = np.clip((density - 0.15) / 0.35, 0.0, 1.0) * np.clip(
        (np.sqrt(denom) - 40.0) / 60.0, 0.0, 1.0
    )
    edge = dilate(bg, band) & dilate(fg, band)
    alpha = np.where(edge, trust * a_unmix + (1.0 - trust) * a_geo, fg_f)

    # A *chroma* key (magenta/green/blue) also licenses a prior the flood mask
    # cannot express: the subject is never this colour, so distance from the key
    # bounds coverage. That recovers translucent elements anywhere in the frame
    # — glows, sparkles, smoke, flame tips — which a band-limited matte would
    # leave fully opaque and key-tinted. A white/grey key gets no such prior.
    scale = None
    if is_chroma_key:
        core = dist_to_key[fg & (density > 0.9)]
        scale = float(np.percentile(core, 70)) if core.size else float(dist_to_key.max())
        a_dist = np.clip(dist_to_key / max(scale, 1e-6), 0.0, 1.0)
        # Only where the pixel's own chroma leans toward the key — that is the
        # signature of background showing through. A solid warm object (flame,
        # red comb) points elsewhere in colour space and keeps its alpha.
        k_dir = key_chroma / key_norm
        chroma = rgb - rgb.mean(axis=2, keepdims=True)
        align = (chroma * k_dir).sum(axis=2) / np.maximum(
            np.sqrt((chroma * chroma).sum(axis=2)), 1e-6
        )
        gate = np.clip((align - 0.45) / 0.35, 0.0, 1.0)
        alpha = (1.0 - gate) * alpha + gate * np.minimum(alpha, a_dist)

    # Squelch sensor/compression noise in the flat background, keep the ramp.
    alpha = np.clip((alpha - 0.04) / 0.96, 0.0, 1.0)
    alpha[bg & (dist_to_key < tolerance * 0.5)] = 0.0

    # 5. Despeckle: drop pixels with almost no opaque neighbours (model noise),
    #    without eroding thin legitimate detail (a feather tip keeps ≥3).
    solid = alpha > 0.5
    neighbours = _box_sum(solid.astype(np.float64), 1)[0] - solid
    alpha[solid & (neighbours <= 2)] = 0.0

    # 6. Decontaminate: un-premultiply the key out of partial pixels, so the
    #    fringe is the object's colour, not a blend with the background.
    out_rgb = rgb.copy()
    partial = (alpha > 0.02) & (alpha < 0.98)
    if partial.any():
        a = alpha[partial][:, None]
        unmix = (rgb[partial] - (1.0 - a) * key) / np.maximum(a, 0.08)
        # Below ~15% coverage the unmix is numerically unstable — lean on the
        # local foreground estimate instead, where one exists.
        has_neighbour = (density[partial] > 0.1)[:, None]
        fallback = np.where(has_neighbour, fg_est[partial], unmix)
        lean = np.clip((a - 0.05) / 0.15, 0.0, 1.0)
        out_rgb[partial] = np.clip(lean * unmix + (1.0 - lean) * fallback, 0.0, 255.0)

    # 7. Despill: mop up residual key tint left when the alpha estimate is a
    #    little off. Step 6 already removes the compositing spill analytically,
    #    so this is weighted by how much background was mixed in (1-alpha) —
    #    despilling opaque pixels would just paint the object the key's
    #    complement (magenta key → green cast).
    if is_chroma_key:
        k_dir = key_chroma / key_norm
        touched = alpha < 0.98
        px = out_rgb[touched]
        spill = ((px - px.mean(axis=1, keepdims=True)) * k_dir).sum(axis=1)
        excess = np.maximum(spill - 25.0, 0.0) * (1.0 - alpha[touched])
        out_rgb[touched] = np.clip(px - excess[:, None] * k_dir, 0.0, 255.0)

    stats = {
        "bg_fraction": float(bg.mean()),
        "soft_pixels": int(((alpha > 0.05) & (alpha < 0.95)).sum()),
        "key_separation": None if scale is None else round(scale, 1),
        "rembg_assist": rembg_mask is not None,
    }
    return alpha, out_rgb, stats


# ---------------------------------------------------------------------------
# Framing
# ---------------------------------------------------------------------------
def trim_pad_resize(rgba: np.ndarray, pad: float | None, size: int | None) -> np.ndarray:
    """Crop to content, re-pad to a square with a constant margin, resize.

    Resizing happens on *premultiplied* alpha — resampling straight RGBA drags
    background-coloured pixels back into the edge and re-creates the halo.
    """
    alpha = rgba[:, :, 3]
    ys, xs = np.nonzero(alpha > 8)
    if ys.size == 0:
        return rgba
    if pad is not None:
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        content = rgba[y0:y1, x0:x1]
        side = max(content.shape[0], content.shape[1])
        canvas_side = int(round(side * (1.0 + 2.0 * pad)))
        canvas = np.zeros((canvas_side, canvas_side, 4), dtype=rgba.dtype)
        oy = (canvas_side - content.shape[0]) // 2
        ox = (canvas_side - content.shape[1]) // 2
        canvas[oy : oy + content.shape[0], ox : ox + content.shape[1]] = content
        rgba = canvas

    if size and rgba.shape[0] != size:
        img = rgba.astype(np.float64)
        a = img[:, :, 3:4] / 255.0
        premul = np.concatenate([img[:, :, :3] * a, img[:, :, 3:4]], axis=2)
        resized = np.asarray(
            Image.fromarray(premul.round().clip(0, 255).astype(np.uint8), "RGBA").resize(
                (size, size), Image.LANCZOS
            ),
            dtype=np.float64,
        )
        a2 = resized[:, :, 3:4] / 255.0
        straight = np.concatenate(
            [np.clip(resized[:, :, :3] / np.maximum(a2, 1e-3), 0, 255), resized[:, :, 3:4]],
            axis=2,
        )
        rgba = straight.round().clip(0, 255).astype(np.uint8)
    return rgba


# ---------------------------------------------------------------------------
# Audit (used by /asset-review AR6)
# ---------------------------------------------------------------------------
def audit(path: Path) -> dict:
    img = Image.open(path).convert("RGBA")
    arr = np.asarray(img, dtype=np.float64)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3] / 255.0
    total = alpha.size
    transparent = float((alpha < 0.02).mean())
    soft = float(((alpha > 0.05) & (alpha < 0.95)).sum())

    solid = alpha > 0.8
    empty = alpha < 0.2
    boundary = solid & dilate(empty, 1)
    interior = solid & ~dilate(empty, 2)
    n_boundary = int(boundary.sum())

    issues: list[str] = []
    if transparent < 0.01:
        issues.append("NO_ALPHA")
    # A properly matted edge has roughly one soft pixel per boundary pixel.
    if n_boundary and soft / n_boundary < 0.5:
        issues.append("HARD_EDGE")
    fringe = None
    if n_boundary and interior.any():
        white_dist_edge = float(np.sqrt(((rgb[boundary] - 255.0) ** 2).sum(axis=1)).mean())
        white_dist_core = float(np.sqrt(((rgb[interior] - 255.0) ** 2).sum(axis=1)).mean())
        fringe = white_dist_core - white_dist_edge
        if fringe > 45:
            issues.append("WHITE_FRINGE")

    ys, xs = np.nonzero(alpha > 0.03)
    bbox_fill = (
        float(((ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)) / total) if ys.size else 0.0
    )
    return {
        "file": str(path),
        "size": list(img.size),
        "transparent": round(transparent, 4),
        "soft_pixels": int(soft),
        "boundary_pixels": n_boundary,
        "fringe_score": None if fringe is None else round(fringe, 1),
        "bbox_fill": round(bbox_fill, 3),
        "issues": issues,
        "verdict": "PASS" if not issues else ("FAIL" if "NO_ALPHA" in issues else "WARN"),
    }


# ---------------------------------------------------------------------------
# Per-file driver
# ---------------------------------------------------------------------------
def process(path: Path, args, mask: np.ndarray | None = None) -> dict:
    preset = TYPE_PRESETS[args.type]
    if not preset["cut"] and not args.force:
        return {"file": str(path), "verdict": "SKIP", "reason": f"type={args.type} is never keyed"}
    if args.no_trim:
        preset = {**preset, "size": None, "pad": None}

    img = Image.open(path).convert("RGBA")
    arr = np.asarray(img, dtype=np.float64)
    rgb, alpha_in = arr[:, :, :3], arr[:, :, 3] / 255.0

    size = args.size if args.size is not None else preset["size"]
    pad = args.pad if args.pad is not None else preset["pad"]

    result: dict = {"file": str(path), "source_size": list(img.size)}

    # Already transparent (some models honour "transparent background") — keep
    # that alpha and only normalise the framing. Decontaminate ONLY if the file
    # actually has a light fringe: unmixing correctly-matted translucent art
    # (a 30%-alpha glow) would wash it out.
    if float((alpha_in < 0.02).mean()) > 0.02:
        alpha, out_rgb = alpha_in, rgb
        fringe = audit(path)["fringe_score"]
        result["method"] = "refine-existing-alpha"
        result["fringe_score"] = fringe
        partial = (alpha > 0.02) & (alpha < 0.98)
        if fringe is not None and fringe > 45 and partial.any():
            result["method"] += "+defringe"
            a = alpha[partial][:, None]
            out_rgb = rgb.copy()
            out_rgb[partial] = np.clip(
                (rgb[partial] - (1.0 - a) * 255.0) / np.maximum(a, 0.15), 0.0, 255.0
            )
    else:
        key_override = parse_key(args.key)
        key, _spread50, spread95 = detect_key(rgb)
        if key_override is not None:
            key = np.array(key_override, dtype=np.float64)
        result["key"] = [int(round(c)) for c in key]
        result["border_spread_p95"] = round(spread95, 1)

        if args.rembg == "on" and mask is None:
            return {**result, "verdict": "FAIL", "reason": "--rembg on but rembg produced no mask"}

        # A non-flat border means this is a scene, not a keyed asset.
        if spread95 > 70 and mask is None and not args.force:
            return {
                **result,
                "verdict": "FAIL",
                "reason": (
                    f"background is not flat (border spread p95={spread95:.0f}); "
                    "regenerate on a flat key colour, install rembg, or pass --force"
                ),
            }

        tolerance = args.tolerance
        if tolerance is None:
            tolerance = float(np.clip(spread95 * 2.0 + 14.0, 26.0, 96.0))
        result["tolerance"] = round(tolerance, 1)
        result["method"] = "flood+matte" + ("+rembg" if mask is not None else "")

        alpha, out_rgb, stats = build_matte(
            rgb, key, tolerance=tolerance, band=args.band, rembg_mask=mask
        )
        result.update(stats)

    coverage = float((alpha > 0.02).mean())
    result["coverage"] = round(coverage, 4)
    if coverage > 0.995:
        return {**result, "verdict": "FAIL", "reason": "nothing was removed — background not detected"}
    if coverage < 0.005:
        return {**result, "verdict": "FAIL", "reason": "almost everything was removed — key colour is wrong"}

    rgba = np.concatenate(
        [out_rgb.round().clip(0, 255), (alpha * 255.0).round().clip(0, 255)[:, :, None]], axis=2
    ).astype(np.uint8)
    rgba = trim_pad_resize(rgba, pad, size)

    if args.dry_run:
        return {**result, "verdict": "DRY-RUN", "output_size": list(rgba.shape[:2])}

    if args.backup:
        backup = path.with_suffix(".orig.png")
        if not backup.exists():
            shutil.copy2(path, backup)
    dest = Path(args.out) if args.out else path
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(dest, "PNG", optimize=True)

    post = audit(dest)
    result["output_size"] = list(post["size"])
    result["issues"] = post["issues"]
    result["verdict"] = "PASS" if not post["issues"] else "WARN"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Clean background removal for game assets")
    ap.add_argument("files", nargs="*", help="PNG files to process")
    ap.add_argument("--dir", help="process every *.png in this directory")
    ap.add_argument("--type", default="sprite", choices=sorted(TYPE_PRESETS),
                    help="asset type preset (backgrounds/panels are skipped)")
    ap.add_argument("--key", default="auto",
                    help="background key: auto|white|magenta|green|blue|#RRGGBB")
    ap.add_argument("--tolerance", type=float, default=None,
                    help="colour distance treated as background (default: adaptive)")
    ap.add_argument("--band", type=int, default=2, help="edge band width in px (default 2)")
    ap.add_argument("--size", type=int, default=None, help="output canvas size (overrides preset)")
    ap.add_argument("--pad", type=float, default=None,
                    help="margin as a fraction of content size (overrides preset)")
    ap.add_argument("--no-trim", action="store_true", help="keep the original framing")
    ap.add_argument("--rembg", default="auto", choices=["auto", "on", "off"])
    ap.add_argument("--out", help="write here instead of in place (single file only)")
    ap.add_argument("--backup", action="store_true", help="keep the original as *.orig.png")
    ap.add_argument("--force", action="store_true", help="key even a non-flat background")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="audit existing alpha, write nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    try:
        parse_key(args.key)
    except ValueError as exc:
        ap.error(str(exc))

    paths = [Path(f) for f in args.files]
    if args.dir:
        paths += sorted(Path(args.dir).glob("*.png"))
    paths = [p for p in paths if not p.name.endswith(".orig.png")]
    if not paths:
        ap.error("no input files (pass PNG paths or --dir)")
    if args.out and len(paths) > 1:
        ap.error("--out takes a single input file (every file would overwrite the same path)")

    missing = [p for p in paths if not p.exists()]
    present = [p for p in paths if p.exists()]

    # One rembg pass for the whole batch, before any per-file work.
    masks: dict[Path, np.ndarray] = {}
    if present and not args.check and args.rembg != "off" and TYPE_PRESETS[args.type]["cut"]:
        runner = find_rembg()
        if runner:
            masks = rembg_masks(present, runner)
        elif args.rembg == "on":
            ap.error("--rembg on but rembg is not installed (set REMBG_PYTHON or install it)")

    results = [{"file": str(p), "verdict": "FAIL", "reason": "file not found"} for p in missing]
    for p in present:
        try:
            results.append(audit(p) if args.check else process(p, args, masks.get(p)))
        except Exception as exc:  # keep the batch going, report honestly
            results.append({"file": str(p), "verdict": "FAIL", "reason": f"{type(exc).__name__}: {exc}"})

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "✗", "SKIP": "⏭ ", "DRY-RUN": "·"}
        for r in results:
            extra = r.get("reason") or ", ".join(r.get("issues", [])) or r.get("method", "")
            size = "×".join(str(v) for v in r.get("output_size", r.get("size", [])))
            print(f"{icon.get(r['verdict'], '?')} {Path(r['file']).name:28s} {size:>9s}  {extra}")
        bad = [r for r in results if r["verdict"] == "FAIL"]
        warn = [r for r in results if r["verdict"] == "WARN"]
        print(
            f"\ncutout: {len(results)} file(s) — "
            f"{len(results) - len(bad) - len(warn)} clean, {len(warn)} warn, {len(bad)} failed"
        )
    return 1 if any(r["verdict"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
