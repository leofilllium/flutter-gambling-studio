#!/usr/bin/env python3
"""
check_asset_stretch.py — find assets the game draws at a different aspect ratio
than the source file.

A stretched asset is one of the most visible "AI made this" tells: the jester
gets fat, the coin turns into an egg, the 64px icon is a squashed lozenge. It
survives every other gate — `dart analyze` is clean, the widget test passes,
the screenshot "has the sprite in it" — because nothing in the pipeline ever
compares the *drawn* box against the *source* box.

This tool does exactly that comparison, statically:

  1. INTRINSIC RATIO   — reads the real pixel dimensions out of every asset
                         file header (PNG IHDR / JPEG SOFn / WebP / SVG
                         viewBox). Standard library only, no Pillow needed.
  2. DRAW SITES        — scans Dart for the places that can actually distort
                         an image, not merely resize it:
                           * `BoxFit.fill` (Image/DecorationImage/FittedBox)
                           * Flame `size: Vector2(w, h)` on a sprite component
                             (Flame stretches to the given size — it does not
                             letterbox like Flutter's Image does)
                           * `Transform.scale(scaleX:, scaleY:)` with x != y
  3. VERDICT           — compares the drawn box ratio with the intrinsic ratio
                         and grades the deviation.

Deliberately NOT reported: `Image.asset(width: w, height: h)` with the default
fit. Flutter letterboxes there (fit defaults to BoxFit.scaleDown), so a
mismatched box wastes space but does not deform the artwork.

False positives are possible where the box is computed at runtime. Add
`stretch-ok` in a comment on the draw site to record a deliberate non-uniform
scale (a 9-slice panel, a full-bleed background) and the site is skipped.

Usage:
  python3 tools/check_asset_stretch.py
  python3 tools/check_asset_stretch.py --assets assets --lib lib \\
      --warn 0.05 --fail 0.10 \\
      --report production/runtime-screenshots/<ts>/asset-stretch.md --json -

Exit codes: 0 = no HIGH finding, 1 = at least one HIGH, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from typing import Iterable, NamedTuple

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
SCAN_LIMIT = 2000  # how far to look for the brackets of an enclosing call
CALL_LEVELS = 2    # `Image.asset(...)` plus its parent `SizedBox(...)`
SUPPRESS = "stretch-ok"


class Size(NamedTuple):
    width: float
    height: float

    @property
    def ratio(self) -> float:
        return self.width / self.height


class Finding(NamedTuple):
    severity: str  # HIGH | MEDIUM
    kind: str
    asset: str
    file: str
    line: int
    intrinsic: str
    drawn: str
    deviation: float | None
    note: str


# --------------------------------------------------------------------------
# intrinsic dimensions — header parsing, no imaging dependency
# --------------------------------------------------------------------------

def _png_size(data: bytes) -> Size | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return None
    width, height = struct.unpack(">II", data[16:24])
    return Size(float(width), float(height)) if width and height else None


def _jpeg_size(data: bytes) -> Size | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
           0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    i = 2
    end = len(data)
    while i + 3 < end:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if i + 4 > end:
            return None
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in sof:
            if i + 9 > end:
                return None
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return Size(float(width), float(height)) if width and height else None
        i += 2 + seg_len
    return None


def _webp_size(data: bytes) -> Size | None:
    if len(data) < 30 or not data.startswith(b"RIFF") or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return Size(float(width), float(height))
    if chunk == b"VP8 ":
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return Size(float(width), float(height)) if width and height else None
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return Size(float(width), float(height))
    return None


_SVG_LEN = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*(px|pt|mm|cm|in|pc)?\s*$", re.I)


def _svg_size(data: bytes) -> Size | None:
    head = data[:4096].decode("utf-8", "ignore")
    view_box = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', head)
    if view_box:
        parts = re.split(r"[\s,]+", view_box.group(1).strip())
        if len(parts) == 4:
            try:
                width, height = float(parts[2]), float(parts[3])
            except ValueError:
                width = height = 0.0
            if width > 0 and height > 0:
                return Size(width, height)
    attrs = {}
    for name in ("width", "height"):
        found = re.search(rf'\b{name}\s*=\s*["\']([^"\']+)["\']', head)
        if not found:
            return None
        match = _SVG_LEN.match(found.group(1))
        if not match:
            return None
        attrs[name] = float(match.group(1))
    if attrs["width"] > 0 and attrs["height"] > 0:
        return Size(attrs["width"], attrs["height"])
    return None


def intrinsic_size(path: Path) -> Size | None:
    """Read an asset's real dimensions from its header. None if unreadable."""
    try:
        data = path.read_bytes()[:65536]
    except OSError:
        return None
    for reader in (_png_size, _jpeg_size, _webp_size, _svg_size):
        size = reader(data)
        if size:
            return size
    return None


def index_assets(root: Path) -> dict[str, Size]:
    """Map every asset path (posix, repo-relative) to its intrinsic size."""
    index: dict[str, Size] = {}
    if not root.is_dir():
        return index
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in IMAGE_SUFFIXES or not path.is_file():
            continue
        size = intrinsic_size(path)
        if size:
            index[path.as_posix()] = size
    return index


# --------------------------------------------------------------------------
# Dart scanning
# --------------------------------------------------------------------------

_CONST_RE = re.compile(
    r"static\s+const\s+String\s+(\w+)\s*=\s*['\"]([^'\"]+\.(?:png|jpe?g|webp|svg))['\"]",
    re.I)
_LITERAL_RE = re.compile(r"['\"]([^'\"]*\.(?:png|jpe?g|webp|svg))['\"]", re.I)
_MEMBER_RE = re.compile(r"\b(?:\w+\.)?(\w+)\b")

_NUM = r"([0-9]+(?:\.[0-9]+)?)"
_VECTOR2_RE = re.compile(r"\bsize\s*:\s*Vector2\(\s*" + _NUM + r"\s*,\s*" + _NUM + r"\s*\)")
_WH_RE = re.compile(r"\bwidth\s*:\s*" + _NUM + r"[^)]{0,200}?\bheight\s*:\s*" + _NUM,
                    re.S)
_HW_RE = re.compile(r"\bheight\s*:\s*" + _NUM + r"[^)]{0,200}?\bwidth\s*:\s*" + _NUM,
                    re.S)
_SCALE_XY_RE = re.compile(r"scaleX\s*:\s*" + _NUM + r"[^)]{0,200}?scaleY\s*:\s*" + _NUM,
                          re.S)
_BOXFIT_FILL_RE = re.compile(r"\bBoxFit\.fill\b")


def asset_constants(lib_root: Path) -> dict[str, str]:
    """`GameAssets.spriteCherry` style constants → the asset path they hold."""
    constants: dict[str, str] = {}
    for path in sorted(lib_root.rglob("*.dart")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name, value in _CONST_RE.findall(text):
            constants[name] = value.lstrip("./")
    return constants


def _resolve(candidate: str, assets: dict[str, Size]) -> str | None:
    """Match a Dart-side path against the indexed assets, tolerating prefixes."""
    candidate = candidate.lstrip("./")
    if candidate in assets:
        return candidate
    for known in assets:
        if known.endswith("/" + candidate) or candidate.endswith("/" + known):
            return known
    tail = candidate.rsplit("/", 1)[-1]
    matches = [k for k in assets if k.rsplit("/", 1)[-1] == tail]
    return matches[0] if len(matches) == 1 else None


def deviation(drawn: float, intrinsic: float) -> float:
    """Symmetric aspect-ratio deviation: 0.0 identical, 0.25 = a quarter off."""
    if drawn <= 0 or intrinsic <= 0:
        return 0.0
    return max(drawn / intrinsic, intrinsic / drawn) - 1.0


def _grade(dev: float, warn: float, fail: float) -> str | None:
    if dev >= fail:
        return "HIGH"
    if dev >= warn:
        return "MEDIUM"
    return None


def _call_bounds(text: str, index: int,
                 levels: int = CALL_LEVELS) -> list[tuple[int, int]]:
    """Bounds of the call expressions wrapping `index`, innermost first.

    A fixed character window is useless here: it happily picks up the
    `BoxFit.fill` of the *next* widget in a `children:` list. Walking the
    brackets gives the actual draw site — `Image.asset(...)` — and one level
    out, which is where `SizedBox`/`SpriteComponent`/`Transform.scale` keep the
    box the asset is forced into.
    """
    bounds: list[tuple[int, int]] = []
    cursor = index
    for _ in range(levels):
        depth = 0
        open_at = -1
        low = max(0, cursor - SCAN_LIMIT)
        for i in range(cursor - 1, low - 1, -1):
            char = text[i]
            if char == ')':
                depth += 1
            elif char == '(':
                if depth == 0:
                    open_at = i
                    break
                depth -= 1
        if open_at < 0:
            break
        depth = 0
        close_at = -1
        high = min(len(text), open_at + SCAN_LIMIT)
        for i in range(open_at, high):
            char = text[i]
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    close_at = i + 1
                    break
        if close_at < 0:
            break
        bounds.append((open_at, close_at))
        cursor = open_at
    return bounds


def _span_text(text: str, span: tuple[int, int], offset: int,
               references: list[int]) -> str:
    """The span's source with every *sibling* asset's subtree blanked out.

    One level out from `Image.asset(...)` is usually the widget holding its box
    — but it can also be a `Column(children: [...])`, and then the neighbour's
    `BoxFit.fill` would be blamed on this asset. Blanking the other assets'
    enclosing calls keeps the parent level useful without that cross-talk.
    """
    start, end = span
    chunk = list(text[start:end])
    for other in references:
        if other == offset or not (start <= other < end):
            continue
        sibling = _call_bounds(text, other, levels=1)
        if not sibling:
            continue
        s_start, s_end = sibling[0]
        s_start, s_end = max(s_start, start), min(s_end, end)
        if s_start >= s_end or s_start <= offset < s_end:
            continue
        for i in range(s_start - start, s_end - start):
            chunk[i] = ' '
    return ''.join(chunk)


def _suppressed(text: str, index: int) -> bool:
    """True when `stretch-ok` marks this draw site.

    Scoped to the reference's own line plus the unbroken run of comment lines
    directly above it, so one acknowledged 9-slice panel cannot silence the
    statements around it.
    """
    lines = text.splitlines()
    line_no = text.count("\n", 0, index)
    if line_no >= len(lines):
        return False
    if SUPPRESS in lines[line_no]:
        return True
    for i in range(line_no - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped.startswith("//"):
            return False
        if SUPPRESS in stripped:
            return True
    return False


def _references(text: str, assets: dict[str, Size],
                constants: dict[str, str]) -> Iterable[tuple[int, str]]:
    """Yield (offset, resolved asset path) for every asset mention in a file."""
    for match in _LITERAL_RE.finditer(text):
        resolved = _resolve(match.group(1), assets)
        if resolved:
            yield match.start(), resolved
    if not constants:
        return
    for match in _MEMBER_RE.finditer(text):
        value = constants.get(match.group(1))
        if not value:
            continue
        resolved = _resolve(value, assets)
        if resolved:
            yield match.start(), resolved


def scan_dart(lib_root: Path, assets: dict[str, Size],
              warn: float, fail: float) -> tuple[list[Finding], int]:
    constants = asset_constants(lib_root)
    findings: list[Finding] = []
    seen: set[tuple[str, int, str, str]] = set()
    sites = 0

    for path in sorted(lib_root.rglob("*.dart")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        references = sorted({o for o, _ in _references(text, assets, constants)})
        for offset, asset in _references(text, assets, constants):
            if _suppressed(text, offset):
                continue
            spans = [_span_text(text, bound, offset, references)
                     for bound in _call_bounds(text, offset)]
            if not spans:
                continue
            line = text.count("\n", 0, offset) + 1
            source = assets[asset]
            intrinsic = f"{source.width:g}x{source.height:g}"
            counted = False

            def first(pattern: re.Pattern[str]) -> re.Match[str] | None:
                for span in spans:
                    found = pattern.search(span)
                    if found:
                        return found
                return None

            box = first(_VECTOR2_RE)
            if box:
                counted = True
                drawn = Size(float(box.group(1)), float(box.group(2)))
                dev = deviation(drawn.ratio, source.ratio)
                severity = _grade(dev, warn, fail)
                if severity:
                    findings.append(Finding(
                        severity, "flame-size", asset, path.as_posix(), line,
                        intrinsic, f"{drawn.width:g}x{drawn.height:g}", dev,
                        "Flame stretches a sprite to `size:` — match the source "
                        "ratio or derive one side from the other"))

            fill = first(_BOXFIT_FILL_RE)
            if fill:
                counted = True
                wh = first(_WH_RE)
                hw = first(_HW_RE)
                drawn = None
                if wh:
                    drawn = Size(float(wh.group(1)), float(wh.group(2)))
                elif hw:
                    drawn = Size(float(hw.group(2)), float(hw.group(1)))
                if drawn:
                    dev = deviation(drawn.ratio, source.ratio)
                    severity = _grade(dev, warn, fail)
                    if severity:
                        findings.append(Finding(
                            severity, "boxfit-fill", asset, path.as_posix(), line,
                            intrinsic, f"{drawn.width:g}x{drawn.height:g}", dev,
                            "BoxFit.fill deforms to the box — use BoxFit.contain "
                            "or BoxFit.cover, or fix the box ratio"))
                else:
                    findings.append(Finding(
                        "MEDIUM", "boxfit-fill-unmeasured", asset, path.as_posix(),
                        line, intrinsic, "computed at runtime", None,
                        "BoxFit.fill on a box this tool cannot measure — confirm "
                        "in the screenshot, or mark it `stretch-ok`"))

            scale = first(_SCALE_XY_RE)
            if scale:
                counted = True
                sx, sy = float(scale.group(1)), float(scale.group(2))
                dev = deviation(sx, sy)
                severity = _grade(dev, warn, fail)
                if severity:
                    findings.append(Finding(
                        severity, "transform-scale", asset, path.as_posix(), line,
                        intrinsic, f"scaleX {sx:g} / scaleY {sy:g}", dev,
                        "Non-uniform Transform.scale deforms the asset"))

            if counted:
                sites += 1

    unique: list[Finding] = []
    for finding in findings:
        key = (finding.file, finding.line, finding.asset, finding.kind)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    order = {"HIGH": 0, "MEDIUM": 1}
    unique.sort(key=lambda f: (order[f.severity], -(f.deviation or 0), f.file, f.line))
    return unique, sites


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def render_report(findings: list[Finding], assets: int, sites: int,
                  warn: float, fail: float) -> str:
    highs = [f for f in findings if f.severity == "HIGH"]
    mediums = [f for f in findings if f.severity == "MEDIUM"]
    verdict = "FAIL" if highs else ("CONCERNS" if mediums else "PASS")
    lines = [
        "# Asset distortion audit (V18)",
        "",
        f"- Verdict: **{verdict}**",
        f"- Assets indexed: {assets}",
        f"- Distorting draw sites inspected: {sites}",
        f"- HIGH: {len(highs)} · MEDIUM: {len(mediums)}",
        f"- Thresholds: MEDIUM at {warn:.0%} deviation, HIGH at {fail:.0%}",
        "",
    ]
    if not findings:
        lines += ["No asset is drawn at a distorted aspect ratio.", ""]
    else:
        lines += [
            "| Severity | Asset | Source | Drawn as | Deviation | Site | Fix |",
            "|---|---|---|---|---|---|---|",
        ]
        for f in findings:
            dev = f"{f.deviation:.0%}" if f.deviation is not None else "—"
            lines.append(
                f"| {f.severity} | `{f.asset}` | {f.intrinsic} | {f.drawn} | "
                f"{dev} | `{f.file}:{f.line}` | {f.note} |")
        lines.append("")
    lines += [
        "Static analysis only: it cannot see a box computed from constraints at "
        "runtime. Confirm each finding — and every character/hero asset — by "
        "reading the source file and the runtime screenshot together.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report assets drawn at a distorted aspect ratio.")
    parser.add_argument("--assets", default="assets",
                        help="asset root to index (default: assets)")
    parser.add_argument("--lib", default="lib",
                        help="Dart source root to scan (default: lib)")
    parser.add_argument("--warn", type=float, default=0.05,
                        help="MEDIUM at this aspect deviation (default: 0.05)")
    parser.add_argument("--fail", type=float, default=0.10,
                        help="HIGH at this aspect deviation (default: 0.10)")
    parser.add_argument("--report", help="write the markdown report here")
    parser.add_argument("--json", help="write JSON findings here ('-' for stdout)")
    args = parser.parse_args(argv)

    if args.warn <= 0 or args.fail <= 0 or args.fail < args.warn:
        print("error: need 0 < --warn <= --fail", file=sys.stderr)
        return 2

    assets_root, lib_root = Path(args.assets), Path(args.lib)
    if not assets_root.is_dir():
        print(f"error: asset root not found: {assets_root}", file=sys.stderr)
        return 2
    if not lib_root.is_dir():
        print(f"error: Dart root not found: {lib_root}", file=sys.stderr)
        return 2

    assets = index_assets(assets_root)
    findings, sites = scan_dart(lib_root, assets, args.warn, args.fail)
    report = render_report(findings, len(assets), sites, args.warn, args.fail)

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    if args.json:
        payload = json.dumps(
            {"assets": len(assets), "sites": sites,
             "findings": [f._asdict() for f in findings]}, indent=2)
        if args.json == "-":
            print(payload)
        else:
            Path(args.json).write_text(payload, encoding="utf-8")
    print(report)
    return 1 if any(f.severity == "HIGH" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
