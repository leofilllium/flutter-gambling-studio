from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw
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

    def test_role_flags_are_parsed_without_a_value(self) -> None:
        self.assertEqual(store_compose.parse_sprite_spec("a/eagle.png@hero"),
                         {"path": "a/eagle.png", "role": "hero"})
        spec = store_compose.parse_sprite_spec("a/gem.png@prop,w=0.3,bleed=0.06")
        self.assertEqual(spec["role"], "prop")
        self.assertAlmostEqual(spec["bleed"], 0.06)

    def test_unknown_or_non_numeric_keys_are_refused(self) -> None:
        for bad in ("a.png@z=4", "a.png@x=left", "@x=0.5", "a.png@villain"):
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


class InlayTests(unittest.TestCase):
    """The designer's two notes: hero on the first screen, objects built in.

    Both were defaults problems, not caller problems — a bare `--sprite a.png`
    used to land a fifth-of-a-panel sticker wherever the cycle put it. These
    pin the defaults that fixed that.
    """

    PANEL_W, PANEL_H, GUTTER, PANELS = 300, 640, 30, 3

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.quiet_warnings: list[str] = []
        for name, replacement in (("info", lambda *_: None), ("ok", lambda *_: None),
                                  ("warn", self.quiet_warnings.append)):
            original = getattr(store_compose, name)
            setattr(store_compose, name, replacement)
            self.addCleanup(setattr, store_compose, name, original)

    def _sprite(self, name: str, size: tuple[int, int]) -> str:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([0, 0, size[0] - 1, size[1] - 1],
                                    fill=(220, 40, 60, 255))
        path = self.dir / name
        img.save(path)
        return str(path)

    def _pano(self) -> Image.Image:
        w = self.PANEL_W * self.PANELS + self.GUTTER * (self.PANELS - 1)
        return Image.new("RGBA", (w, self.PANEL_H), (30, 90, 140, 255))

    def _inlay(self, *specs: str) -> list[str]:
        return store_compose.inlay_sprites(
            self._pano(), list(specs), self.PANELS, self.PANEL_W, self.PANEL_H,
            self.GUTTER)

    def test_the_first_object_leads_on_panel_one_as_the_hero(self) -> None:
        # Screenshot 1 is the only one the store shows at full size, so an
        # unannotated set must still put the protagonist there.
        lines = self._inlay(self._sprite("hero.png", (200, 320)),
                            self._sprite("gem.png", (160, 160)))
        hero = next(line for line in lines if line.startswith("hero"))
        self.assertIn("hero.png", hero)
        self.assertIn("panel 1", hero)
        self.assertTrue(all("panel 1" not in line for line in lines
                            if not line.startswith("hero")), lines)

    def test_an_explicit_role_flag_beats_the_first_object_rule(self) -> None:
        lines = self._inlay(self._sprite("gem.png", (160, 160)),
                            self._sprite("hero.png", (200, 320)) + "@hero")
        hero = next(line for line in lines if line.startswith("hero"))
        self.assertIn("hero.png", hero)
        self.assertIn("panel 1", hero)

    def test_objects_are_big_enough_to_read_in_a_thumbnail_strip(self) -> None:
        # "far too small" was the note. The hero owns most of its panel and no
        # supporting object drops back to sticker size.
        lines = self._inlay(self._sprite("hero.png", (200, 320)),
                            self._sprite("gem.png", (160, 160)),
                            self._sprite("coin.png", (160, 160)))
        widths = {line.split()[1]: int(line.split("(")[1].split("px")[0])
                  for line in lines}
        self.assertGreaterEqual(widths["hero.png"], self.PANEL_W * 0.5)
        for name in ("gem.png", "coin.png"):
            self.assertGreaterEqual(widths[name], self.PANEL_W * 0.25, name)

    def test_objects_stand_on_the_ground_instead_of_floating_mid_panel(self) -> None:
        line = self._inlay(self._sprite("hero.png", (200, 320)))[0]
        cy = int(line.split("@")[1].split(",")[1].split()[0])
        self.assertGreater(cy, self.PANEL_H * 0.5)

    def test_a_crowd_of_objects_is_called_out(self) -> None:
        self._inlay(*(self._sprite(f"o{i}.png", (160, 160))
                      for i in range(store_compose.CROWDED + 1)))
        self.assertTrue(any("sprite sheet" in m for m in self.quiet_warnings),
                        self.quiet_warnings)

    def test_placing_everything_off_panel_one_is_called_out(self) -> None:
        self._inlay(self._sprite("gem.png", (160, 160)) + "@panel=2",
                    self._sprite("coin.png", (160, 160)) + "@panel=3")
        self.assertTrue(any("panel 1" in m for m in self.quiet_warnings),
                        self.quiet_warnings)

    def test_an_object_never_straddles_a_seam(self) -> None:
        lines = self._inlay(self._sprite("hero.png", (200, 320)) + "@x=0.33")
        cx = int(lines[0].split("@")[1].split(",")[0])
        width = int(lines[0].split("(")[1].split("px")[0])
        left, right = store_compose.panel_span(0, self.PANEL_W, self.GUTTER)
        self.assertGreaterEqual(cx - width // 2, left)
        self.assertLessEqual(cx + width // 2, right)


class SeatingTests(unittest.TestCase):
    """"Not worked into the design" — pasted on, not lit by the scene."""

    def _art(self) -> Image.Image:
        img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([10, 10, 109, 109], fill=(200, 40, 40, 255))
        return img

    def test_the_object_picks_up_the_light_it_is_standing_in(self) -> None:
        art = self._art()
        plate = Image.new("RGBA", art.size, (40, 120, 240, 255))
        seated = store_compose.seat_in_scene(art, plate, 0.5)
        before = np.asarray(art, dtype=np.float32)
        after = np.asarray(seated, dtype=np.float32)
        opaque = before[..., 3] > 250
        self.assertGreater(after[..., 2][opaque].mean(), before[..., 2][opaque].mean())
        # The cutout keeps its own shape: light integration must not eat alpha.
        np.testing.assert_array_equal(after[..., 3], before[..., 3])

    def test_the_rim_takes_more_of_the_scene_than_the_core(self) -> None:
        art = self._art()
        plate = Image.new("RGBA", art.size, (40, 120, 240, 255))
        after = np.asarray(store_compose.seat_in_scene(art, plate, 0.6),
                           dtype=np.float32)
        before = np.asarray(art, dtype=np.float32)
        shift = np.abs(after[..., :3] - before[..., :3]).sum(axis=-1)
        core = shift[52:68, 52:68].mean()          # centre of the disc
        rim = shift[58:62, 12:16].mean()           # just inside its left edge
        self.assertGreater(rim, core)

    def test_zero_light_is_a_no_op_so_the_flat_paste_stays_reachable(self) -> None:
        art = self._art()
        plate = Image.new("RGBA", art.size, (40, 120, 240, 255))
        np.testing.assert_array_equal(
            np.asarray(store_compose.seat_in_scene(art, plate, 0.0)), np.asarray(art))

    def test_a_contact_shadow_darkens_the_ground_at_the_foot(self) -> None:
        pano = Image.new("RGBA", (200, 200), (180, 180, 180, 255))
        before = np.asarray(pano.convert("RGB"), dtype=np.float32).mean()
        store_compose.contact_shadow(pano, 100, 140, 80, 0.7)
        arr = np.asarray(pano.convert("RGB"), dtype=np.float32)
        self.assertLess(arr.mean(), before)
        # Darkest at the contact point, not spread over the whole panel.
        self.assertLess(arr[140, 100].mean(), arr[40, 100].mean() - 20)


if __name__ == "__main__":
    unittest.main()
