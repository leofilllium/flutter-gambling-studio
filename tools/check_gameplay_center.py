#!/usr/bin/env python3
"""
check_gameplay_center.py — is the live play field actually centered?

`.claude/docs/gameplay-screen-contract.md` requires the mechanic to be the
dominant, integrated surface on the gameplay screen. Dominance alone does not
guarantee balance: a field that is 88% of the width but shoved hard against
one edge reads as lopsided even though it "passes" the size threshold, and
every other gate lets it through — the analyzer is clean, the widget test
only checks the field is on-screen and above the size floor, and a screenshot
"has the field in it" whether or not it is centered.

By default the play field's horizontal center should coincide with the
viewport's horizontal center — same rule as V19's menu-lead centering, and
for the same reason: an off-center composition without a design reason reads
as unintentional, not deliberate.

This tool does the static half of the check:

  1. LAYOUT ARCHETYPE — reads the recorded `L1`-`L6` layout archetype (and any
                        recorded narrow-mechanic/thumb-rail exception) out of
                        `design/art-direction.md`.
  2. GAMEPLAY SURFACE — finds every `Key('gameplaySurface')` site (the
                        mandatory hook from `gameplay-screen-contract.md`) and
                        walks its ancestor widgets for an explicit horizontal
                        offset: an off-center `Align`/`Alignment`, asymmetric
                        `Padding`, or a `Positioned` pinned to one edge or
                        given unequal `left`/`right` insets.

What it cannot do is judge true on-screen position — that depends on runtime
constraints (parent size, safe-area insets, `Expanded` siblings) this tool
does not evaluate. That is the vision pass on the idle/active game
screenshots, and it is not optional.

Usage:
  python3 tools/check_gameplay_center.py
  python3 tools/check_gameplay_center.py --lib lib \\
      --report production/runtime-screenshots/<ts>/gameplay-center.md

Exit codes: 0 = no HIGH finding, 1 = at least one HIGH, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_asset_stretch import _call_bounds  # noqa: E402  (sibling tool)

DESIGN_DOCS = (
    "design/art-direction.md",
    "design/gdd/game-concept.md",
)
ANCESTOR_LEVELS = 5  # how many enclosing widgets to walk out from the key

_KEY_RE = re.compile(r"Key\(\s*['\"]gameplaySurface['\"]\s*\)")
_LAYOUT_RE = re.compile(r"\bL([1-6])\b")
_EXCEPTION_RE = re.compile(
    r"narrow[- ]mechanic|thumb[- ]rail|gameplay[- ]offset|field[- ]offset", re.I)

_SIGNED_NUM = r"(-?[0-9]+(?:\.[0-9]+)?)"
_IDENT_RE = re.compile(r"([A-Za-z_][\w.]*)\s*$")
_ALIGN_NAMED_RE = re.compile(
    r"\balignment\s*:\s*Alignment(?:Directional)?\.(\w+)")
_ALIGN_XY_RE = re.compile(
    r"\balignment\s*:\s*Alignment\(\s*" + _SIGNED_NUM + r"\s*,\s*" + _SIGNED_NUM + r"\s*\)")
_OFFCENTER_NAMES = {
    "centerLeft", "centerRight", "topLeft", "topRight",
    "bottomLeft", "bottomRight", "centerStart", "centerEnd",
}

_EDGEINSETS_ONLY_RE = re.compile(r"EdgeInsets\.only\(([^)]*)\)")
_EDGEINSETS_LTRB_RE = re.compile(
    r"EdgeInsets\.fromLTRB\(\s*" + _SIGNED_NUM + r"\s*,\s*" + _SIGNED_NUM
    + r"\s*,\s*" + _SIGNED_NUM + r"\s*,\s*" + _SIGNED_NUM + r"\s*\)")
_LEFT_KV_RE = re.compile(r"\bleft\s*:\s*" + _SIGNED_NUM)
_RIGHT_KV_RE = re.compile(r"\bright\s*:\s*" + _SIGNED_NUM)


def _preceding_call_name(text: str, open_at: int) -> str:
    """The identifier (with dots) immediately before an opening paren.

    `_call_bounds` hands back spans starting AT the `(` itself, so the widget
    name (`Align`, `Positioned`, `Positioned.fill`, ...) has to be recovered
    by looking just before it.
    """
    match = _IDENT_RE.search(text[:open_at])
    return match.group(1) if match else ""


class Finding(NamedTuple):
    severity: str  # HIGH | MEDIUM
    code: str
    file: str
    line: int
    detail: str


def read_docs(root: Path, extra: list[str]) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for name in list(DESIGN_DOCS) + extra:
        path = root / name if not Path(name).is_absolute() else Path(name)
        if path.is_file():
            try:
                docs.append((path.as_posix(), path.read_text(encoding="utf-8",
                                                             errors="ignore")))
            except OSError:
                continue
    return docs


def find_layout_archetype(docs: list[tuple[str, str]]) -> str | None:
    for _, text in docs:
        match = _LAYOUT_RE.search(text)
        if match:
            return f"L{match.group(1)}"
    return None


def has_recorded_exception(docs: list[tuple[str, str]]) -> bool:
    return any(_EXCEPTION_RE.search(text) for _, text in docs)


def gameplay_surface_sites(lib_root: Path) -> list[tuple[Path, int]]:
    sites: list[tuple[Path, int]] = []
    for path in sorted(lib_root.rglob("*.dart")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in _KEY_RE.finditer(text):
            sites.append((path, match.start()))
    return sites


def _padding_signal(name: str, span: str,
                    warn_px: float, fail_px: float) -> tuple[str, str, str] | None:
    if name != "Padding":
        return None
    only = _EDGEINSETS_ONLY_RE.search(span)
    if only:
        left_m = _LEFT_KV_RE.search(only.group(1))
        right_m = _RIGHT_KV_RE.search(only.group(1))
        if not (left_m or right_m):
            return None
        left = float(left_m.group(1)) if left_m else 0.0
        right = float(right_m.group(1)) if right_m else 0.0
    else:
        ltrb = _EDGEINSETS_LTRB_RE.search(span)
        if not ltrb:
            return None
        left, right = float(ltrb.group(1)), float(ltrb.group(3))
    diff = abs(left - right)
    if diff >= fail_px:
        severity = "HIGH"
    elif diff >= warn_px:
        severity = "MEDIUM"
    else:
        return None
    return ("padding-asymmetric", severity,
            f"`Padding` around the gameplay surface has left/right insets {left:g}/"
            f"{right:g} — roughly {diff:g} logical px asymmetric.")


def _positioned_signal(name: str, span: str,
                       warn_px: float, fail_px: float) -> tuple[str, str, str] | None:
    if name != "Positioned":  # excludes Positioned.fill and unrelated calls
        return None
    left_m = _LEFT_KV_RE.search(span)
    right_m = _RIGHT_KV_RE.search(span)
    if left_m and right_m:
        diff = abs(float(left_m.group(1)) - float(right_m.group(1)))
        if diff >= fail_px:
            severity = "HIGH"
        elif diff >= warn_px:
            severity = "MEDIUM"
        else:
            return None
        return ("positioned-asymmetric", severity,
                f"`Positioned` pins the field with left={left_m.group(1)}/"
                f"right={right_m.group(1)} — roughly {diff:g} logical px asymmetric.")
    if left_m or right_m:
        return ("positioned-pinned-edge", "MEDIUM",
                "`Positioned` pins the field to one edge only (`left` xor `right`, "
                "no matching `width`/opposite inset) — confirm this does not leave "
                "it off-center at runtime.")
    return None


def _align_signal(name: str, span: str) -> tuple[str, str, str] | None:
    if name not in ("Align", "AlignDirectional"):
        return None
    named = _ALIGN_NAMED_RE.search(span)
    if named:
        align_name = named.group(1)
        if align_name in _OFFCENTER_NAMES:
            return (f"align-{align_name}", "HIGH",
                    f"`Alignment.{align_name}` pins the gameplay surface fully "
                    "toward one edge instead of the default center.")
        return None  # centered or an unrecognised name — not confidently a signal
    xy = _ALIGN_XY_RE.search(span)
    if xy:
        x = float(xy.group(1))
        if abs(x) >= 0.3:
            severity = "HIGH"
        elif abs(x) >= 0.1:
            severity = "MEDIUM"
        else:
            return None
        return ("align-xy", severity,
                f"`Alignment(x: {x:g}, ...)` offsets the gameplay surface off-center "
                "(0.0 is centered, ±1.0 is a full edge).")
    return None


def audit(root: Path, lib_root: Path, warn_px: float, fail_px: float,
         extra_docs: list[str]) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    docs = read_docs(root, extra_docs)
    archetype = find_layout_archetype(docs)
    exception_recorded = has_recorded_exception(docs)
    sites = gameplay_surface_sites(lib_root)
    context = {
        "layout_archetype": archetype,
        "exception_recorded": exception_recorded,
        "sites": [{"file": p.as_posix(), "line": text_line(p, o)}
                  for p, o in sites],
    }

    if not sites:
        findings.append(Finding(
            "MEDIUM", "gameplay-surface-not-found", "-", 0,
            "No `Key('gameplaySurface')` found under "
            f"{lib_root.as_posix()}. That key is a mandatory hook per "
            "gameplay-screen-contract.md — without it this check cannot run, "
            "and neither can the widget-test geometry check. Judge centering "
            "visually instead."))
        return findings, context

    if archetype is None:
        findings.append(Finding(
            "MEDIUM", "layout-archetype-undeclared", "-", 0,
            "No `L1`-`L6` layout archetype recorded in design/art-direction.md. "
            "The concept is required to record one; centering is judged "
            "against the default (centered) composition until it does."))

    for path, offset in sites:
        text = path.read_text(encoding="utf-8", errors="ignore")
        line = text.count("\n", 0, offset) + 1
        bounds = _call_bounds(text, offset, levels=ANCESTOR_LEVELS)
        signal = None
        signal_file_line = (path.as_posix(), line)
        for start, end in bounds:  # innermost ancestor first
            span = text[start:end]
            name = _preceding_call_name(text, start)
            signal = (_align_signal(name, span)
                      or _positioned_signal(name, span, warn_px, fail_px)
                      or _padding_signal(name, span, warn_px, fail_px))
            if signal:
                break
        if signal is None:
            continue
        code, severity, detail = signal
        if severity == "HIGH" and exception_recorded:
            severity = "MEDIUM"
            detail += (" A narrow-mechanic/thumb-rail exception is recorded in the "
                       "design docs — confirm it actually justifies this offset "
                       "before treating it as intentional.")
        elif archetype and exception_recorded is False:
            detail += (f" Layout archetype {archetype} does not by itself excuse an "
                       "off-center field; record a reason in "
                       "design/art-direction.md if this is deliberate.")
        findings.append(Finding(severity, code,
                                signal_file_line[0], signal_file_line[1], detail))

    return findings, context


def text_line(path: Path, offset: int) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return text.count("\n", 0, offset) + 1


def render_report(findings: list[Finding], context: dict,
                  warn_px: float, fail_px: float) -> str:
    highs = [f for f in findings if f.severity == "HIGH"]
    mediums = [f for f in findings if f.severity == "MEDIUM"]
    verdict = "FAIL" if highs else ("CONCERNS" if mediums else "PASS")
    lines = [
        "# Gameplay-field centering audit (V20)",
        "",
        f"- Verdict: **{verdict}** (static half only)",
        f"- Layout archetype: **{context.get('layout_archetype') or 'undeclared'}**",
        f"- Recorded off-center exception: {'yes' if context.get('exception_recorded') else 'no'}",
        f"- `gameplaySurface` sites: "
        + (", ".join(f"`{s['file']}:{s['line']}`" for s in context["sites"])
           or "none found"),
        f"- Asymmetry thresholds: MEDIUM at {warn_px:g} logical px, HIGH at {fail_px:g}",
        "",
    ]
    if not findings:
        lines += ["No static off-center signal on the gameplay surface.", ""]
    else:
        lines += ["| Severity | Check | Site | Detail |", "|---|---|---|---|"]
        for f in sorted(findings, key=lambda x: 0 if x.severity == "HIGH" else 1):
            detail = f.detail.replace("|", "\\|")
            site = f"`{f.file}:{f.line}`" if f.line else "-"
            lines.append(f"| {f.severity} | `{f.code}` | {site} | {detail} |")
        lines.append("")
    lines += [
        "Static analysis only. It proves an *explicit* off-center widget exists on "
        "an ancestor of the gameplay surface; it cannot resolve true on-screen "
        "position from runtime constraints (parent size, safe-area insets, "
        "`Expanded` siblings). Confirm on `03-game-idle.png` and "
        "`04-game-action.png` at 390×844 and 1440×900: the field's horizontal "
        "center should sit inside the middle 60% of the viewport width, unless "
        "the recorded layout archetype and a documented reason justify otherwise.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live play field is centered by default.")
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument("--lib", default="lib", help="Dart source root")
    parser.add_argument("--doc", action="append", default=[],
                        help="an extra design doc to read (repeatable)")
    parser.add_argument("--warn-px", type=float, default=16.0,
                        help="MEDIUM at this left/right asymmetry (default: 16)")
    parser.add_argument("--fail-px", type=float, default=48.0,
                        help="HIGH at this left/right asymmetry (default: 48)")
    parser.add_argument("--report", help="write the markdown report here")
    parser.add_argument("--json", help="write JSON here ('-' for stdout)")
    args = parser.parse_args(argv)

    if args.warn_px <= 0 or args.fail_px <= 0 or args.fail_px < args.warn_px:
        print("error: need 0 < --warn-px <= --fail-px", file=sys.stderr)
        return 2

    root, lib_root = Path(args.root), Path(args.lib)
    if not lib_root.is_dir():
        print(f"error: Dart root not found: {lib_root}", file=sys.stderr)
        return 2

    findings, context = audit(root, lib_root, args.warn_px, args.fail_px, args.doc)
    report = render_report(findings, context, args.warn_px, args.fail_px)

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    if args.json:
        payload = json.dumps({"context": context,
                              "findings": [f._asdict() for f in findings]}, indent=2)
        if args.json == "-":
            print(payload)
        else:
            Path(args.json).write_text(payload, encoding="utf-8")
    print(report)
    return 1 if any(f.severity == "HIGH" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
