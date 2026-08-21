from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover - host without the imaging stack
    raise unittest.SkipTest("Pillow and numpy are not installed in this host environment")


SCRIPT = Path(__file__).resolve().parents[1] / "store_compose.py"
SPEC = importlib.util.spec_from_file_location("store_compose", SCRIPT)
assert SPEC and SPEC.loader
store_compose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(store_compose)


class GutterTests(unittest.TestCase):
    """The seam allowance is the whole point of slicing wider than the panels."""

    def test_auto_scales_with_the_panel_so_both_store_sets_match(self) -> None:
        self.assertEqual(store_compose.parse_gutter("auto", 1320), 100)
        self.assertEqual(store_compose.parse_gutter("auto", 1080), 82)

    def test_explicit_pixels_and_percentages(self) -> None:
        self.assertEqual(store_compose.parse_gutter("120", 1320), 120)
        self.assertEqual(store_compose.parse_gutter("10%", 1080), 108)
        self.assertEqual(store_compose.parse_gutter("0", 1080), 0)

    def test_nonsense_and_oversized_allowances_are_refused(self) -> None:
        for bad in ("abc", "-5", "400"):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                store_compose.parse_gutter(bad, 1080)

    def test_panels_are_spaced_by_the_allowance_not_butt_joined(self) -> None:
        # Panel 2 must start one gutter past where panel 1 ended, or the strip
        # the store's own gap stands in for was never discarded.
        self.assertEqual(store_compose.panel_span(0, 1080, 82), (0, 1080))
        self.assertEqual(store_compose.panel_span(1, 1080, 82), (1162, 2242))


class SpriteSpecTests(unittest.TestCase):
    def test_placement_keys_are_parsed(self) -> None:
        spec = store_compose.parse_sprite_spec("a/eagle.png@x=0.3,y=0.62,w=0.24,rot=-8")
        self.assertEqual(spec["path"], "a/eagle.png")
        self.assertAlmostEqual(spec["x"], 0.3)
        self.assertAlmostEqual(spec["rot"], -8.0)

    def test_bare_path_leaves_placement_to_the_auto_layout(self) -> None:
        self.assertEqual(store_compose.parse_sprite_spec("a/eagle.png"),
                         {"path": "a/eagle.png"})

    def test_unknown_or_non_numeric_keys_are_refused(self) -> None:
        for bad in ("a.png@z=4", "a.png@x=left", "@x=0.5"):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                store_compose.parse_sprite_spec(bad)


class PopGradeTests(unittest.TestCase):
    """Saturate and brighten — without clipping, which is the usual failure."""

    def _ramp(self) -> Image.Image:
        x = np.linspace(0.0, 1.0, 64, dtype=np.float32)[None, :, None]
        y = np.linspace(0.0, 1.0, 64, dtype=np.float32)[:, None, None]
        rgb = np.concatenate([x + 0.0 * y, 0.35 + 0.3 * y + 0.0 * x, 0.8 - 0.5 * x + 0.0 * y],
                             axis=-1)
        rgb = np.broadcast_to(rgb, (64, 64, 3))
        return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")

    @staticmethod
    def _stats(img: Image.Image) -> tuple[float, float, float]:
        a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
        luma = float((a * store_compose.LUMA).sum(axis=-1).mean())
        sat = float((a.max(axis=-1) - a.min(axis=-1)).mean())
        blown = float((a >= 0.999).all(axis=-1).mean())
        return luma, sat, blown

    def test_default_preset_lifts_light_and_colour(self) -> None:
        src = self._ramp()
        base_luma, base_sat, _ = self._stats(src)
        graded_luma, graded_sat, _ = self._stats(store_compose.pop_grade(src))
        self.assertGreater(graded_luma, base_luma)
        self.assertGreater(graded_sat, base_sat)

    def test_presets_are_monotonic(self) -> None:
        src = self._ramp()
        lumas = [self._stats(store_compose.pop_grade(src, p))[0]
                 for p in ("off", "soft", "vivid", "max")]
        self.assertEqual(lumas, sorted(lumas))

    def test_no_preset_blows_the_highlights_out(self) -> None:
        # A flat white patch is what a naive saturate+brighten destroys first.
        src = self._ramp()
        for preset in ("soft", "vivid", "max"):
            with self.subTest(preset=preset):
                self.assertLess(self._stats(store_compose.pop_grade(src, preset))[2], 0.02)

    def test_off_is_a_no_op_and_alpha_survives(self) -> None:
        src = self._ramp()
        np.testing.assert_array_equal(np.asarray(store_compose.pop_grade(src, "off")),
                                      np.asarray(src))
        translucent = src.copy()
        translucent.putalpha(128)
        self.assertEqual(store_compose.pop_grade(translucent, "vivid").getchannel("A")
                         .getextrema(), (128, 128))


class SeamReportTests(unittest.TestCase):
    def test_a_subject_on_the_cut_is_reported_as_hotter_than_the_picture(self) -> None:
        # Flat gradient with one hard-edged disc centred on the first seam:
        # the seam strip must measure busier than the panorama's average.
        panel_w, panel_h, gutter = 200, 400, 20
        pano = Image.new("RGBA", (panel_w * 3 + gutter * 2, panel_h), (40, 40, 60, 255))
        from PIL import ImageDraw
        seam = panel_w + gutter // 2
        ImageDraw.Draw(pano).ellipse([seam - 60, 140, seam + 60, 260], fill=(255, 210, 80, 255))

        messages: list[str] = []
        original = store_compose.warn
        store_compose.warn = messages.append  # type: ignore[assignment]
        try:
            store_compose.seam_report(pano, 3, panel_w, gutter)
        finally:
            store_compose.warn = original  # type: ignore[assignment]

        self.assertTrue(any("seam 1→2" in m for m in messages), messages)
        self.assertFalse(any("seam 2→3" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main()
