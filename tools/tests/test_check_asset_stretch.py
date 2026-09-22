from __future__ import annotations

import importlib.util
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_asset_stretch.py"
SPEC = importlib.util.spec_from_file_location("check_asset_stretch", SCRIPT)
assert SPEC and SPEC.loader
stretch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stretch)


def write_png(path: Path, width: int, height: int) -> None:
    """A minimal but valid PNG of the requested size."""
    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b""))


class IntrinsicSizeTests(unittest.TestCase):
    def test_reads_png_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "sprite_joker.png"
            write_png(png, 512, 256)
            self.assertEqual(stretch.intrinsic_size(png), stretch.Size(512.0, 256.0))

    def test_reads_svg_viewbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "icon_bell.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" '
                           'viewBox="0 0 120 60"></svg>', encoding="utf-8")
            self.assertEqual(stretch.intrinsic_size(svg), stretch.Size(120.0, 60.0))

    def test_reads_svg_width_height_attributes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "icon_bar.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" '
                           'width="80px" height="40px"></svg>', encoding="utf-8")
            self.assertEqual(stretch.intrinsic_size(svg), stretch.Size(80.0, 40.0))

    def test_unreadable_file_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / "broken.png"
            junk.write_bytes(b"not an image")
            self.assertIsNone(stretch.intrinsic_size(junk))


class DeviationTests(unittest.TestCase):
    def test_identical_ratio_is_zero(self) -> None:
        self.assertAlmostEqual(stretch.deviation(2.0, 2.0), 0.0)

    def test_deviation_is_symmetric(self) -> None:
        self.assertAlmostEqual(stretch.deviation(2.0, 1.0), stretch.deviation(1.0, 2.0))
        self.assertAlmostEqual(stretch.deviation(2.0, 1.0), 1.0)


class ScanTests(unittest.TestCase):
    def _project(self, tmp: str, dart: str) -> tuple[Path, Path]:
        root = Path(tmp)
        write_png(root / "assets/images/sprites/sprite_joker.png", 512, 512)
        write_png(root / "assets/images/ui/ui_button.png", 300, 100)
        write_png(root / "assets/images/backgrounds/background_menu.png", 1024, 2048)
        (root / "lib").mkdir(parents=True, exist_ok=True)
        (root / "lib/screens.dart").write_text(dart, encoding="utf-8")
        return root / "assets", root / "lib"

    def _scan(self, dart: str) -> list[stretch.Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            assets_root, lib_root = self._project(tmp, dart)
            assets = stretch.index_assets(assets_root)
            findings, _ = stretch.scan_dart(lib_root, assets, 0.05, 0.10)
            return findings

    def test_flame_size_mismatch_is_high(self) -> None:
        findings = self._scan("""
            final joker = SpriteComponent(
              sprite: await Sprite.load('assets/images/sprites/sprite_joker.png'),
              size: Vector2(200, 100),
            );
        """)
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0].severity, "HIGH")
        self.assertEqual(findings[0].kind, "flame-size")
        self.assertAlmostEqual(findings[0].deviation, 1.0, places=6)

    def test_flame_size_matching_source_ratio_passes(self) -> None:
        self.assertEqual(self._scan("""
            final joker = SpriteComponent(
              sprite: await Sprite.load('assets/images/sprites/sprite_joker.png'),
              size: Vector2(128, 128),
            );
        """), [])

    def test_boxfit_fill_on_mismatched_box_is_high(self) -> None:
        findings = self._scan("""
            Image.asset(
              'assets/images/ui/ui_button.png',
              width: 120,
              height: 120,
              fit: BoxFit.fill,
            );
        """)
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0].kind, "boxfit-fill")
        self.assertEqual(findings[0].severity, "HIGH")

    def test_boxfit_fill_on_matching_box_passes(self) -> None:
        self.assertEqual(self._scan("""
            Image.asset(
              'assets/images/ui/ui_button.png',
              width: 240,
              height: 80,
              fit: BoxFit.fill,
            );
        """), [])

    def test_boxfit_fill_without_measurable_box_is_medium(self) -> None:
        findings = self._scan("""
            Image.asset('assets/images/backgrounds/background_menu.png',
                fit: BoxFit.fill);
        """)
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0].severity, "MEDIUM")
        self.assertEqual(findings[0].kind, "boxfit-fill-unmeasured")

    def test_suppression_comment_skips_the_site(self) -> None:
        self.assertEqual(self._scan("""
            // stretch-ok: 9-slice panel, deliberate non-uniform scale
            Image.asset('assets/images/ui/ui_button.png',
                width: 120, height: 120, fit: BoxFit.fill);
        """), [])

    def test_non_uniform_transform_scale_is_reported(self) -> None:
        findings = self._scan("""
            Transform.scale(
              scaleX: 1.0,
              scaleY: 1.4,
              child: Image.asset('assets/images/sprites/sprite_joker.png'),
            );
        """)
        self.assertEqual([f.kind for f in findings], ["transform-scale"])
        self.assertEqual(findings[0].severity, "HIGH")

    def test_uniform_scale_and_plain_sizing_are_not_reported(self) -> None:
        # Flutter letterboxes a mismatched width/height under the default fit,
        # so it is a layout smell, not distortion — and must not be flagged.
        self.assertEqual(self._scan("""
            Transform.scale(
              scale: 1.4,
              child: Image.asset('assets/images/ui/ui_button.png',
                  width: 120, height: 120),
            );
        """), [])

    def test_operators_do_not_leak_between_sibling_widgets(self) -> None:
        # Regression: a fixed character window let the BoxFit.fill of the next
        # widget in a children list condemn its innocent neighbour.
        findings = self._scan("""
            Column(children: [
              Image.asset('assets/images/backgrounds/background_menu.png',
                  fit: BoxFit.cover),
              Image.asset('assets/images/ui/ui_button.png',
                  width: 96, height: 96, fit: BoxFit.fill),
            ]);
        """)
        self.assertEqual(len(findings), 1, findings)
        self.assertTrue(findings[0].asset.endswith("ui_button.png"), findings[0])

    def test_suppression_does_not_leak_to_a_neighbouring_site(self) -> None:
        # Regression: one acknowledged 9-slice panel silenced every draw site
        # within 400 characters of it, in both directions.
        findings = self._scan("""
            Image.asset('assets/images/ui/ui_button.png',
                width: 96, height: 96, fit: BoxFit.fill);

            // stretch-ok: 9-slice frame
            Image.asset('assets/images/ui/ui_button.png',
                width: 300, height: 64, fit: BoxFit.fill);
        """)
        self.assertEqual([f.line for f in findings], [2], findings)

    def test_box_on_the_parent_call_is_considered(self) -> None:
        findings = self._scan("""
            SizedBox(
              width: 120,
              height: 40,
              child: Image.asset('assets/images/sprites/sprite_joker.png',
                  fit: BoxFit.fill),
            );
        """)
        self.assertEqual([f.kind for f in findings], ["boxfit-fill"])
        self.assertEqual(findings[0].drawn, "120x40")

    def test_asset_constants_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_png(root / "assets/images/sprites/sprite_joker.png", 512, 512)
            (root / "lib").mkdir(parents=True, exist_ok=True)
            (root / "lib/assets.dart").write_text(
                "class GameAssets {\n"
                "  static const String spriteJoker = "
                "'assets/images/sprites/sprite_joker.png';\n}\n",
                encoding="utf-8")
            (root / "lib/game.dart").write_text(
                "final c = SpriteComponent(\n"
                "  sprite: await Sprite.load(GameAssets.spriteJoker),\n"
                "  size: Vector2(300, 100),\n);\n",
                encoding="utf-8")
            assets = stretch.index_assets(root / "assets")
            findings, sites = stretch.scan_dart(root / "lib", assets, 0.05, 0.10)
            self.assertEqual(sites, 1)
            self.assertEqual([f.severity for f in findings], ["HIGH"])
            self.assertEqual(findings[0].asset,
                             (root / "assets/images/sprites/sprite_joker.png").as_posix())


class CliTests(unittest.TestCase):
    def _run(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--assets", str(root / "assets"),
             "--lib", str(root / "lib"), "--report", str(root / "report.md")],
            capture_output=True, text=True, timeout=60)

    def test_clean_project_exits_zero_and_reports_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_png(root / "assets/images/sprites/sprite_gem.png", 256, 256)
            (root / "lib").mkdir(parents=True)
            (root / "lib/game.dart").write_text(
                "final gem = SpriteComponent(\n"
                "  sprite: await Sprite.load('assets/images/sprites/sprite_gem.png'),\n"
                "  size: Vector2(64, 64),\n);\n", encoding="utf-8")
            result = self._run(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("**PASS**", (root / "report.md").read_text(encoding="utf-8"))

    def test_distorted_project_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_png(root / "assets/images/sprites/sprite_gem.png", 256, 256)
            (root / "lib").mkdir(parents=True)
            (root / "lib/game.dart").write_text(
                "final gem = SpriteComponent(\n"
                "  sprite: await Sprite.load('assets/images/sprites/sprite_gem.png'),\n"
                "  size: Vector2(160, 64),\n);\n", encoding="utf-8")
            result = self._run(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            report = (root / "report.md").read_text(encoding="utf-8")
            self.assertIn("**FAIL**", report)
            self.assertIn("sprite_gem.png", report)

    def test_missing_roots_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--assets", f"{tmp}/nope",
                 "--lib", f"{tmp}/nope"],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
