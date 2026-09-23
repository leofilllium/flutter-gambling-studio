#!/usr/bin/env python3
"""
check_menu_lead.py — is the game's declared visual lead actually on the main menu?

`quality-bar.md` §1: the menu implements its documented memorable idea and
M/O/R recipe. The storefront's visual lead is not automatically the runtime
menu centerpiece, so design docs record `menu_role: dominant | supporting |
absent` separately from `lead_kind`.

This tool does the static half of the check:

  1. LEAD KIND     — reads `lead_kind: character | object | mechanic` out of
                     the design docs (the concept is required to record it).
  2. MENU ROLE     — reads whether that lead is dominant, supporting, or absent.
  3. LEAD ASSET    — reads the recorded lead asset path.
  4. MENU SOURCE   — for dominant/supporting character roles, finds the menu
                     source and checks the recorded asset is actually drawn.

What it cannot do is judge whether the lead is *visible* — clipped by an edge,
buried behind the button stack, or shrunk to a cameo by a runtime constraint.
That is the vision pass on `02-menu.png`, and it is not optional.

**An object- or mechanic-led game must not gain a character to satisfy this
check.** A documented absent role must not be "fixed" by forcing the store lead
into a menu recipe that does not call for it.

Usage:
  python3 tools/check_menu_lead.py
  python3 tools/check_menu_lead.py --lead-kind character \\
      --lead-asset assets/images/sprites/sprite_joker.png \\
      --report production/runtime-screenshots/<ts>/menu-lead.md

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
from check_asset_stretch import (  # noqa: E402  (sibling tool, same directory)
    _NUM, _call_bounds, _resolve, asset_constants, index_assets,
)

DESIGN_DOCS = (
    "design/gdd/game-concept.md",
    "design/art-direction.md",
    "design/asset-manifest.md",
)
MENU_GLOBS = ("**/main_menu.dart", "**/main_menu_screen.dart",
              "**/menu_screen.dart", "**/main_menu/*.dart")

_LEAD_KIND_RE = re.compile(
    r"lead[_ ]?kind[^A-Za-z]{0,8}(character|object|mechanic)", re.I)
_MENU_ROLE_RE = re.compile(
    r"(?:menu[_ ]?role|main menu role)[^A-Za-z]{0,8}(dominant|supporting|absent)",
    re.I)
_LEAD_ASSET_RE = re.compile(
    r"\blead[^\n]{0,120}?((?:assets|images)/[\w./-]+\.(?:png|jpe?g|webp|svg))", re.I)
_SIZE_RE = re.compile(r"\bsize\s*:\s*Vector2\(\s*" + _NUM + r"\s*,\s*" + _NUM + r"\s*\)")
_WIDTH_RE = re.compile(r"\bwidth\s*:\s*" + _NUM)
_HEIGHT_RE = re.compile(r"\bheight\s*:\s*" + _NUM)


class Finding(NamedTuple):
    severity: str  # HIGH | MEDIUM
    code: str
    detail: str


def read_docs(root: Path, extra: list[str]) -> list[tuple[str, str]]:
    """(path, text) for every design doc that exists."""
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


def find_lead_kind(docs: list[tuple[str, str]]) -> str | None:
    for _, text in docs:
        match = _LEAD_KIND_RE.search(text)
        if match:
            return match.group(1).lower()
    return None


def find_menu_role(docs: list[tuple[str, str]]) -> str | None:
    for _, text in docs:
        match = _MENU_ROLE_RE.search(text)
        if match:
            return match.group(1).lower()
    return None


def find_lead_asset(docs: list[tuple[str, str]], assets: dict) -> str | None:
    for _, text in docs:
        for match in _LEAD_ASSET_RE.finditer(text):
            resolved = _resolve(match.group(1), assets)
            if resolved:
                return resolved
    return None


def menu_sources(lib_root: Path) -> list[Path]:
    found: list[Path] = []
    for pattern in MENU_GLOBS:
        found.extend(p for p in lib_root.glob(pattern) if p.is_file())
    return sorted(set(found))


def lead_references(menu_files: list[Path], asset: str,
                    constants: dict[str, str],
                    assets: dict) -> list[tuple[Path, int, str]]:
    """Every place a menu file draws the lead asset: (file, line, call source)."""
    names = {name for name, value in constants.items()
             if _resolve(value, assets) == asset}
    tail = asset.rsplit("/", 1)[-1]
    hits: list[tuple[Path, int, str]] = []
    for path in menu_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        offsets = [m.start() for m in re.finditer(re.escape(tail), text)]
        for name in names:
            offsets += [m.start() for m in re.finditer(rf"\b{re.escape(name)}\b", text)]
        for offset in sorted(set(offsets)):
            bounds = _call_bounds(text, offset)
            call = text[bounds[-1][0]:bounds[-1][1]] if bounds else ""
            hits.append((path, text.count("\n", 0, offset) + 1, call))
    return hits


def largest_literal_side(call: str) -> float | None:
    """The biggest literal dimension in a draw call, when there is one."""
    sides: list[float] = []
    vector = _SIZE_RE.search(call)
    if vector:
        sides += [float(vector.group(1)), float(vector.group(2))]
    for pattern in (_WIDTH_RE, _HEIGHT_RE):
        match = pattern.search(call)
        if match:
            sides.append(float(match.group(1)))
    return max(sides) if sides else None


def audit(root: Path, lib_root: Path, assets_root: Path, lead_kind: str | None,
          menu_role: str | None, lead_asset: str | None, min_side: float,
          extra_docs: list[str]) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    assets = index_assets(assets_root)
    docs = read_docs(root, extra_docs)
    kind = (lead_kind or find_lead_kind(docs) or "").lower() or None
    role = (menu_role or find_menu_role(docs) or "").lower() or None
    asset = lead_asset or find_lead_asset(docs, assets)
    if lead_asset:
        asset = _resolve(lead_asset, assets) or lead_asset
    menus = menu_sources(lib_root)
    context = {"lead_kind": kind, "menu_role": role, "lead_asset": asset,
               "menu_sources": [p.as_posix() for p in menus],
               "references": []}

    if kind is None:
        findings.append(Finding(
            "MEDIUM", "lead-kind-undeclared",
            "No `lead_kind: character | object | mechanic` in the design docs. "
            "The concept is required to record it; read the concept and pass "
            "--lead-kind, then judge the menu visually."))
    if role is None:
        findings.append(Finding(
            "MEDIUM", "menu-role-undeclared",
            "No `menu_role: dominant | supporting | absent` in the design docs. "
            "Record the role from the main menu's M recipe; do not infer that the "
            "storefront lead must be the runtime centerpiece."))
    if not menus:
        findings.append(Finding(
            "MEDIUM", "menu-source-not-found",
            f"No main-menu source under {lib_root.as_posix()} "
            f"({', '.join(MENU_GLOBS)}). Verify the menu visually instead."))

    if role in (None, "absent"):
        return findings, context

    if kind != "character":
        if kind in ("object", "mechanic"):
            context["note"] = (
                f"{kind}-led game: inspect the recorded menu recipe visually. "
                "Do NOT add a character, mascot, hand or player silhouette to "
                "satisfy this gate — that is its own defect.")
        return findings, context

    if not asset:
        findings.append(Finding(
            "MEDIUM", "lead-asset-unrecorded",
            "The menu uses the character lead but no lead asset path is recorded in the "
            "design docs. Record it, or pass --lead-asset."))
        return findings, context
    if asset not in assets:
        findings.append(Finding(
            "HIGH", "lead-asset-missing",
            f"The declared character lead `{asset}` is not in "
            f"{assets_root.as_posix()}."))
        return findings, context
    if not menus:
        return findings, context

    constants = asset_constants(lib_root)
    hits = lead_references(menus, asset, constants, assets)
    context["references"] = [{"file": p.as_posix(), "line": n} for p, n, _ in hits]
    if not hits:
        findings.append(Finding(
            "HIGH", "lead-absent-from-menu",
            f"The character lead `{asset}` has menu_role `{role}` but is never drawn by the main menu "
            f"({', '.join(p.as_posix() for p in menus)}). The menu has to show "
            "the character as documented."))
        return findings, context

    sides = [(p, n, largest_literal_side(call)) for p, n, call in hits]
    measured = [s for _, _, s in sides if s is not None]
    if role == "dominant" and measured and max(measured) < min_side:
        biggest = max(measured)
        findings.append(Finding(
            "MEDIUM", "lead-drawn-small",
            f"The character lead is drawn at {biggest:g} logical px at most "
            f"({min_side:g} expected for a dominant role). Confirm in 02-menu.png "
            "that it reads as the menu's focal point and not as an icon."))
    return findings, context


def render_report(findings: list[Finding], context: dict, min_side: float) -> str:
    highs = [f for f in findings if f.severity == "HIGH"]
    mediums = [f for f in findings if f.severity == "MEDIUM"]
    verdict = "FAIL" if highs else ("CONCERNS" if mediums else "PASS")
    lines = [
        "# Main-menu lead audit (V19)",
        "",
        f"- Verdict: **{verdict}** (static half only)",
        f"- Declared lead: **{context.get('lead_kind') or 'undeclared'}**"
        + (f" — `{context['lead_asset']}`" if context.get("lead_asset") else ""),
        f"- Runtime menu role: **{context.get('menu_role') or 'undeclared'}**",
        f"- Menu sources: {', '.join(f'`{m}`' for m in context['menu_sources']) or 'none found'}",
        f"- Lead drawn in the menu at: "
        + (", ".join(f"`{r['file']}:{r['line']}`" for r in context["references"])
           or "no draw site found"),
        f"- Dominant-role size heuristic: {min_side:g} logical px",
        "",
    ]
    if context.get("note"):
        lines += [f"> {context['note']}", ""]
    if not findings:
        lines += ["No static problem with the menu lead.", ""]
    else:
        lines += ["| Severity | Check | Detail |", "|---|---|---|"]
        for f in sorted(findings, key=lambda x: 0 if x.severity == "HIGH" else 1):
            detail = f.detail.replace("|", "\\|")  # keep the table from splitting
            lines.append(f"| {f.severity} | `{f.code}` | {detail} |")
        lines.append("")
    lines += [
        "Static analysis only. For dominant/supporting character roles it proves "
        "the menu draws the declared asset; it cannot judge attention order, "
        "clipping, or the overall M/O/R recipe. Confirm on `02-menu.png` at "
        "390×844 and 1440×900.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that the declared visual lead is on the main menu.")
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument("--lib", default="lib", help="Dart source root")
    parser.add_argument("--assets", default="assets", help="asset root")
    parser.add_argument("--lead-kind", choices=["character", "object", "mechanic"],
                        help="override the lead kind read from the design docs")
    parser.add_argument("--menu-role", choices=["dominant", "supporting", "absent"],
                        help="override the runtime menu role read from the design docs")
    parser.add_argument("--lead-asset", help="override the lead asset path")
    parser.add_argument("--doc", action="append", default=[],
                        help="an extra design doc to read (repeatable)")
    parser.add_argument("--min-side", type=float, default=120.0,
                        help="dominant-role size heuristic in logical px (default: 120)")
    parser.add_argument("--report", help="write the markdown report here")
    parser.add_argument("--json", help="write JSON here ('-' for stdout)")
    args = parser.parse_args(argv)

    root, lib_root = Path(args.root), Path(args.lib)
    assets_root = Path(args.assets)
    if not lib_root.is_dir():
        print(f"error: Dart root not found: {lib_root}", file=sys.stderr)
        return 2
    if not assets_root.is_dir():
        print(f"error: asset root not found: {assets_root}", file=sys.stderr)
        return 2

    findings, context = audit(root, lib_root, assets_root, args.lead_kind,
                              args.menu_role, args.lead_asset, args.min_side,
                              args.doc)
    report = render_report(findings, context, args.min_side)

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
