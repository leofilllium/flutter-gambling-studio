from __future__ import annotations

import argparse
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


class ReassemblyTests(unittest.TestCase):
    """The contract: lay the panels side by side and the picture comes back.

    Not a millimetre of it may be missing anywhere, so the default cut is
    butt-joined and slicing discards nothing between the panels.
    """

    PANEL_W, PANEL_H, PANELS = 240, 520, 3

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        for name in ("info", "ok", "warn"):
            original = getattr(store_compose, name)
            setattr(store_compose, name, lambda *_: None)
            self.addCleanup(setattr, store_compose, name, original)

    def _slice(self, **kwargs) -> tuple[list[Image.Image], Image.Image]:
        rng = np.random.default_rng(11)
        src = Image.fromarray(
            rng.integers(20, 235, (self.PANEL_H, self.PANEL_W * self.PANELS, 3),
                         dtype=np.uint8), "RGB").convert("RGBA")
        src_path = self.dir / "keyart.png"
        src.save(src_path)
        out = self.dir / "panels"
        pano_path = self.dir / "pano.png"
        args = argparse.Namespace(
            src=str(src_path), out=str(out), panels=self.PANELS,
            size=f"{self.PANEL_W}x{self.PANEL_H}", prefix="store-", zoom=1.0,
            offset=0.0, gutter=store_compose.DEFAULT_GUTTER, seam_snap="auto",
            sprite=[], sprite_glow_color="#FFFFFF",
            sprite_light=store_compose.DEFAULT_SPRITE_LIGHT,
            save_pano=str(pano_path), pano_only=False, pop="off", vibrance=None,
            lift=None, contrast=None, bloom=None, title=None, tagline=None,
            logo=None, title_panel=None, title_pos=None)
        for key, value in kwargs.items():
            setattr(args, key, value)
        store_compose.cmd_triptych(args)
        panels = [Image.open(out / f"store-{i + 1:02d}.png").convert("RGBA")
                  for i in range(self.PANELS)]
        return panels, Image.open(pano_path).convert("RGBA")

    def test_the_panels_laid_edge_to_edge_are_the_picture_again(self) -> None:
        panels, pano = self._slice()
        stitched = Image.new("RGBA", (self.PANEL_W * self.PANELS, self.PANEL_H))
        for i, panel in enumerate(panels):
            self.assertEqual(panel.size, (self.PANEL_W, self.PANEL_H))
            stitched.paste(panel, (i * self.PANEL_W, 0))

        # The stitch has to appear in the saved panorama verbatim: same pixels,
        # same order, nothing dropped between one panel and the next.
        wide = np.asarray(pano)
        want = np.asarray(stitched)
        offsets = [x for x in range(wide.shape[1] - want.shape[1] + 1)
                   if np.array_equal(wide[:, x:x + want.shape[1]], want)]
        self.assertTrue(offsets, "the panels do not reassemble the panorama")

    def test_an_explicit_allowance_is_still_available_and_does_cost_pixels(self) -> None:
        panels, pano = self._slice(gutter="20")
        stitched = Image.new("RGBA", (self.PANEL_W * self.PANELS, self.PANEL_H))
        for i, panel in enumerate(panels):
            stitched.paste(panel, (i * self.PANEL_W, 0))
        wide, want = np.asarray(pano), np.asarray(stitched)
        matches = [x for x in range(wide.shape[1] - want.shape[1] + 1)
                   if np.array_equal(wide[:, x:x + want.shape[1]], want)]
        self.assertFalse(matches, "an allowance was requested but nothing was discarded")

    def test_both_previews_are_written_and_neither_is_an_upload_asset(self) -> None:
        self._slice()
        out = self.dir / "panels"
        for name in ("_panorama-preview.png", "_carousel-preview.png"):
            self.assertTrue((out / name).is_file(), name)
        uploads = sorted(p.name for p in out.glob("*.png")
                         if not p.name.startswith("_"))
        self.assertEqual(uploads, ["store-01.png", "store-02.png", "store-03.png"])


class GutterTests(unittest.TestCase):
    """The opt-in seam allowance, for a publisher who asks the panels to line up."""

    def test_the_default_discards_nothing(self) -> None:
        self.assertEqual(store_compose.parse_gutter(store_compose.DEFAULT_GUTTER, 1320), 0)

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
        seam = panel_w + gutter // 2
        ImageDraw.Draw(pano).ellipse([seam - 60, 140, seam + 60, 260], fill=(255, 210, 80, 255))

        messages: list[str] = []
        original = store_compose.warn
        store_compose.warn = messages.append  # type: ignore[assignment]
        try:
            store_compose.seam_report(
                pano, store_compose.uniform_spans(3, panel_w, gutter))
        finally:
            store_compose.warn = original  # type: ignore[assignment]

        self.assertTrue(any("seam 1→2" in m for m in messages), messages)
        self.assertFalse(any("seam 2→3" in m for m in messages), messages)


class SeamSnapTests(unittest.TestCase):
    """The allowance is the publisher's; where it is taken out is the picture's.

    A content-blind cut at exactly 1/3 and 2/3 removes 100px from wherever the
    arithmetic lands, and when that is across a face the panel simply stops
    mid-object. The cuts are allowed to slide until they come out of calm
    ground instead.
    """

    PANEL_W, PANEL_H, GUTTER, PANELS = 400, 860, 30, 3
    SUBJECT_W = 60

    def _pano(self, subject_at: int | None):
        snap = store_compose.parse_snap("auto", self.PANEL_W)
        width = (self.PANEL_W * self.PANELS + self.GUTTER * (self.PANELS - 1)
                 + snap * (self.PANELS - 1))
        pano = Image.new("RGBA", (width, self.PANEL_H), (40, 40, 60, 255))
        if subject_at is not None:
            half = self.SUBJECT_W // 2
            ImageDraw.Draw(pano).ellipse(
                [subject_at - half, 300, subject_at + half, 560],
                fill=(255, 210, 80, 255))
        return pano, snap

    def test_radius_parsing(self) -> None:
        self.assertEqual(store_compose.parse_snap("auto", 1320), 158)
        self.assertEqual(store_compose.parse_snap("off", 1320), 0)
        self.assertEqual(store_compose.parse_snap("0", 1320), 0)
        self.assertEqual(store_compose.parse_snap("40", 1320), 40)
        self.assertEqual(store_compose.parse_snap("4%", 1000), 40)
        for bad in ("wide", "-5", "400"):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                store_compose.parse_snap(bad, 1000)

    def test_the_cut_slides_off_a_subject_sitting_on_the_nominal_seam(self) -> None:
        nominal = self.PANEL_W  # where an even split would cut
        pano, snap = self._pano(subject_at=nominal + self.GUTTER // 2)
        spans = store_compose.plan_panel_spans(
            pano, self.PANELS, self.PANEL_W, self.GUTTER, snap)

        # The discarded strip must clear the subject entirely, not merely shift.
        strip = (spans[0][1], spans[1][0])
        subject = (nominal + self.GUTTER // 2 - self.SUBJECT_W // 2,
                   nominal + self.GUTTER // 2 + self.SUBJECT_W // 2)
        self.assertTrue(strip[1] <= subject[0] or strip[0] >= subject[1],
                        f"strip {strip} still cuts the subject {subject}")
        for left, right in spans:
            self.assertEqual(right - left, self.PANEL_W)
        self.assertLessEqual(spans[-1][1], pano.width)

    def test_a_calm_picture_is_left_where_the_arithmetic_put_it(self) -> None:
        pano, snap = self._pano(subject_at=None)
        spans = store_compose.plan_panel_spans(
            pano, self.PANELS, self.PANEL_W, self.GUTTER, snap)
        for i in range(1, self.PANELS):
            self.assertEqual(spans[i][0] - spans[i - 1][1], self.GUTTER)

    def test_off_reproduces_the_even_split(self) -> None:
        pano, _ = self._pano(subject_at=self.PANEL_W)
        spans = store_compose.plan_panel_spans(
            pano, self.PANELS, self.PANEL_W, self.GUTTER, 0)
        self.assertEqual([r - l for l, r in spans], [self.PANEL_W] * self.PANELS)
        for i in range(1, self.PANELS):
            self.assertEqual(spans[i][0] - spans[i - 1][1], self.GUTTER)

    def test_the_allowance_stays_near_the_publisher_s_number(self) -> None:
        pano, snap = self._pano(subject_at=self.PANEL_W + self.GUTTER // 2)
        spans = store_compose.plan_panel_spans(
            pano, self.PANELS, self.PANEL_W, self.GUTTER, snap)
        for i in range(1, self.PANELS):
            gap = spans[i][0] - spans[i - 1][1]
            self.assertGreaterEqual(gap, 0)
            self.assertLessEqual(abs(gap - self.GUTTER), snap)


class DetailReportTests(unittest.TestCase):
    """"Too simple, too boring" is measurable, so it is measured."""

    PANEL_W, PANEL_H = 200, 400

    def _measure(self, pano: Image.Image, panels: int = 2):
        spans = store_compose.uniform_spans(panels, self.PANEL_W, 0)
        messages: list[str] = []
        original_warn, original_info = store_compose.warn, store_compose.info
        store_compose.warn = messages.append  # type: ignore[assignment]
        store_compose.info = lambda *_: None  # type: ignore[assignment]
        try:
            return store_compose.detail_report(pano, spans), messages
        finally:
            store_compose.warn = original_warn  # type: ignore[assignment]
            store_compose.info = original_info  # type: ignore[assignment]

    def test_a_gradient_with_one_shape_is_called_a_backdrop(self) -> None:
        pano = store_compose.gradient(
            (self.PANEL_W * 2, self.PANEL_H),
            [(0.0, (20, 24, 60, 255)), (1.0, (90, 40, 120, 255))])
        ImageDraw.Draw(pano).ellipse([60, 150, 200, 290], fill=(240, 200, 90, 255))
        shares, messages = self._measure(pano)
        self.assertTrue(all(share > store_compose.FLAT_SHARE for share in shares), shares)
        self.assertTrue(any("empty ground" in m for m in messages), messages)

    def test_a_populated_illustration_passes(self) -> None:
        rng = np.random.default_rng(7)
        noise = rng.integers(30, 220, (self.PANEL_H, self.PANEL_W * 2, 3), dtype=np.uint8)
        pano = Image.fromarray(noise, "RGB").convert("RGBA")
        shares, messages = self._measure(pano)
        self.assertTrue(all(share < store_compose.FLAT_SHARE for share in shares), shares)
        self.assertEqual(messages, [])


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

    def test_the_hero_is_sized_by_the_panel_s_height_not_its_width(self) -> None:
        # "the player on the first slide should be bigger — full height, but not
        # too much". A width-driven hero on a 300x640 panel came out barely 40%
        # of its height; the target is now the height itself.
        line = self._inlay(self._sprite("hero.png", (200, 420)))[0]
        share = int(line.split("of its height")[0].split(",")[-1].strip().rstrip("%"))
        self.assertGreaterEqual(share, 65, line)
        self.assertLessEqual(share, 80, line)   # the "not too much" half

    def test_the_hero_keeps_headroom_for_the_berth_s_ornament(self) -> None:
        # The band the note calls "decorative" is above the head: the hero may
        # not grow into it, and the picture may not leave it empty.
        line = self._inlay(self._sprite("hero.png", (200, 420)))[0]
        height = round(self.PANEL_H
                       * int(line.split("of its height")[0].split(",")[-1]
                             .strip().rstrip("%")) / 100)
        cy = int(line.split("@")[1].split(",")[1].split()[0])
        self.assertGreater(cy - height // 2, self.PANEL_H * 0.15, line)

    def test_a_squat_cutout_that_cannot_reach_full_height_is_called_out(self) -> None:
        self._inlay(self._sprite("hero.png", (420, 200)))
        self.assertTrue(any("of panel 1's height" in m for m in self.quiet_warnings),
                        self.quiet_warnings)

    def test_an_explicit_height_overrides_the_target(self) -> None:
        line = self._inlay(self._sprite("hero.png", (200, 420)) + "@h=0.4")[0]
        share = int(line.split("of its height")[0].split(",")[-1].strip().rstrip("%"))
        self.assertLessEqual(share, 42, line)

    def test_empty_sky_above_the_hero_s_head_is_called_out(self) -> None:
        # A flat panorama: the berth is a place to stand, not an ornament.
        self._inlay(self._sprite("hero.png", (200, 420)))
        self.assertTrue(any("empty sky" in m for m in self.quiet_warnings),
                        self.quiet_warnings)

    def test_an_ornamented_crown_band_passes(self) -> None:
        rng = np.random.default_rng(5)
        w = self.PANEL_W * self.PANELS + self.GUTTER * (self.PANELS - 1)
        pano = Image.fromarray(
            rng.integers(20, 235, (self.PANEL_H, w, 3), dtype=np.uint8),
            "RGB").convert("RGBA")
        store_compose.inlay_sprites(pano, [self._sprite("hero.png", (200, 420))],
                                    self.PANELS, self.PANEL_W, self.PANEL_H,
                                    self.GUTTER)
        self.assertFalse([m for m in self.quiet_warnings if "empty sky" in m],
                         self.quiet_warnings)

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


class BoardRoleTests(unittest.TestCase):
    """The mechanic in the key art must be the mechanic in the app.

    A model-drawn reel grid came back from review beside gameplay frames whose
    board looked nothing like it. `boardplate` builds the field out of the real
    files and the `board` role seats it; these pin the defaults that make that
    the short path.
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

    def _png(self, name: str, size: tuple[int, int]) -> str:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([0, 0, size[0] - 1, size[1] - 1],
                                    fill=(220, 40, 60, 255))
        path = self.dir / name
        img.save(path)
        return str(path)

    def _inlay(self, *specs: str) -> list[str]:
        w = self.PANEL_W * self.PANELS + self.GUTTER * (self.PANELS - 1)
        pano = Image.new("RGBA", (w, self.PANEL_H), (30, 90, 140, 255))
        return store_compose.inlay_sprites(pano, list(specs), self.PANELS,
                                           self.PANEL_W, self.PANEL_H, self.GUTTER)

    def _boardplate(self, **kwargs) -> Image.Image:
        out = self.dir / kwargs.pop("out", "board.png")
        args = argparse.Namespace(
            out=str(out), from_shot=None, rect=None, symbol=[], grid="3x3",
            frame=None, panel="", tile="", border="", border_width=0.045,
            cell=64, gap=0.06, pad=0.09, tile_radius=0.16, symbol_pad=0.12,
            radius=0.05, sheen=0.0, yaw=0.0, pitch=0.0, depth=0.0, tilt=0.0,
            win="", win_color="", dim=0.35, lift=1.45)
        for key, value in kwargs.items():
            setattr(args, key, value)
        store_compose.cmd_boardplate(args)
        with Image.open(out) as plate:
            return plate.convert("RGBA")

    def test_the_field_takes_the_middle_panel_at_foreground_size(self) -> None:
        # Not the hero's panel, not the last one the carousel crops first, and
        # big enough that a reviewer can see which game it is.
        line = next(l for l in self._inlay(
            self._png("hero.png", (200, 320)),
            self._png("board.png", (600, 600)) + "@board") if l.startswith("board"))
        self.assertIn("panel 2", line)
        width = int(line.split("(")[1].split("px")[0])
        self.assertGreaterEqual(width, self.PANEL_W * 0.6)

    def test_the_field_stands_inside_the_frame_instead_of_bleeding_off_it(self) -> None:
        # A board cropped by the bottom edge stops reading as a board.
        line = next(l for l in self._inlay(self._png("b.png", (600, 600)) + "@board")
                    if l.startswith("board"))
        cy = int(line.split("@")[1].split(",")[1].split()[0])
        height = 600 * int(line.split("(")[1].split("px")[0]) // 600
        self.assertLess(cy + height // 2, self.PANEL_H)

    def test_a_board_does_not_consume_a_prop_slot(self) -> None:
        # The board is the mechanic, not one of the two or three symbols, so it
        # must not push a prop off its depth in the fan-out.
        with_board = self._inlay(self._png("hero.png", (200, 320)),
                                 self._png("board.png", (600, 600)) + "@board",
                                 self._png("gem.png", (160, 160)))
        without = self._inlay(self._png("hero.png", (200, 320)),
                              self._png("gem.png", (160, 160)))
        gem = next(l for l in with_board if "gem.png" in l)
        plain = next(l for l in without if "gem.png" in l)
        self.assertEqual(gem.split("@")[1], plain.split("@")[1])

    def test_a_plate_is_built_from_the_real_symbol_files(self) -> None:
        red, green = (220, 40, 60), (40, 200, 90)
        for name, colour in (("s0.png", red), ("s1.png", green)):
            img = Image.new("RGBA", (128, 128), colour + (255,))
            img.save(self.dir / name)
        plate = self._boardplate(symbol=[str(self.dir / "s0.png"),
                                         str(self.dir / "s1.png")],
                                 grid="3x3", tile="#1E2A6B")
        arr = np.asarray(plate.convert("RGBA"))
        opaque = arr[arr[..., 3] > 250][:, :3]
        # Both shipped symbols survive into the plate untouched: this is the
        # whole point — the same objects, not similar ones.
        for colour in (red, green):
            self.assertTrue((np.abs(opaque.astype(int) - colour).sum(axis=1) < 12).any(),
                            f"{colour} is missing from the plate")

    def test_a_plate_lifted_from_a_frame_keeps_the_captured_pixels(self) -> None:
        shot = Image.new("RGBA", (400, 800), (10, 14, 40, 255))
        ImageDraw.Draw(shot).rectangle([100, 200, 299, 599], fill=(30, 44, 120, 255))
        shot.save(self.dir / "shot.png")
        plate = self._boardplate(out="lift.png", from_shot=str(self.dir / "shot.png"),
                                 rect="0.25,0.25,0.5,0.5", radius=0.0)
        self.assertEqual(plate.size, (200, 400))
        self.assertEqual(plate.convert("RGBA").getpixel((100, 200))[:3], (30, 44, 120))

    def test_tagging_the_board_does_not_cost_the_set_its_hero(self) -> None:
        # `@board` is a role flag, so an explicit-role check that is not
        # hero-specific would silently demote the protagonist to a prop and
        # leave panel 1 to whatever the fan-out put there.
        lines = self._inlay(self._png("hero.png", (200, 320)),
                            self._png("board.png", (600, 600)) + "@board")
        hero = next(line for line in lines if line.startswith("hero"))
        self.assertIn("hero.png", hero)
        self.assertIn("panel 1", hero)

    def _cell_luma(self, plate: Image.Image, col: int, row: int,
                   cell: int = 64) -> float:
        gap, pad = round(cell * 0.06), round(cell * 0.09)
        x = pad + col * (cell + gap)
        y = pad + row * (cell + gap)
        patch = np.asarray(plate.crop((x, y, x + cell, y + cell)).convert("RGB"),
                           dtype=np.float32)
        return float(patch.mean())

    def test_the_paying_cells_are_lit_and_the_rest_of_the_field_falls_back(self) -> None:
        # The middle panel is the listing's gameplay example, and a correct grid
        # with nothing happening in it is the slide that came back as boring.
        symbol = self._png("sym.png", (48, 48))
        rest = self._boardplate(out="rest.png", symbol=[symbol], panel="#141B3C",
                                tile="#1E2A6B", border="#F0B34A", lift=1.0)
        won = self._boardplate(out="won.png", symbol=[symbol], panel="#141B3C",
                               tile="#1E2A6B", border="#F0B34A", lift=1.0,
                               win="1x2,2x2,3x2", win_color="#FFD67A")
        self.assertGreater(self._cell_luma(won, 1, 1), self._cell_luma(rest, 1, 1))
        self.assertLess(self._cell_luma(won, 1, 0), self._cell_luma(rest, 1, 0))
        self.assertGreater(self._cell_luma(won, 1, 1), self._cell_luma(won, 1, 0))

    def test_the_paying_symbol_rises_out_of_its_cell(self) -> None:
        # A board where one symbol has broken its own plane reads as a round
        # resolving; a flat one reads as a diagram of a board.
        symbol = self._png("sym.png", (48, 48))
        flat = self._boardplate(out="flat.png", symbol=[symbol], panel="#141B3C",
                                win="1x2,2x2,3x2", lift=1.0)
        risen = self._boardplate(out="risen.png", symbol=[symbol], panel="#141B3C",
                                 win="1x2,2x2,3x2", lift=1.6)
        self.assertEqual(flat.size, risen.size)
        # The cell ABOVE the paying one is where the lift shows: the symbol is
        # standing in front of it now.
        moved = np.abs(np.asarray(risen.convert("RGB"), dtype=np.float32)[0:70]
                       - np.asarray(flat.convert("RGB"), dtype=np.float32)[0:70])
        self.assertGreater(float(moved.mean()), 4.0)

    def test_the_plate_grows_so_a_lifted_symbol_is_never_clipped(self) -> None:
        symbol = self._png("sym.png", (48, 48))
        flat = self._boardplate(out="flat-top.png", symbol=[symbol],
                                panel="#141B3C", win="1x1,2x1,3x1", lift=1.0)
        risen = self._boardplate(out="risen-top.png", symbol=[symbol],
                                 panel="#141B3C", win="1x1,2x1,3x1", lift=1.6)
        self.assertGreater(risen.height, flat.height)
        above = np.asarray(risen.crop((0, 0, risen.width,
                                       risen.height - flat.height))
                           .getchannel("A"), dtype=np.float32)
        self.assertGreater(float(above.max()), 200.0)

    def test_a_field_at_rest_is_called_out(self) -> None:
        self._boardplate(out="idle.png", symbol=[self._png("sym.png", (48, 48))],
                         panel="#141B3C")
        self.assertTrue(any("boring" in m for m in self.quiet_warnings),
                        self.quiet_warnings)

    def test_cells_outside_the_grid_or_repeated_are_refused(self) -> None:
        for bad in ("4x1", "1x9", "0x1", "1x2,1x2", "middle", ""):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                store_compose.parse_cells(bad, 3, 3)

    def test_a_lifted_frame_carries_its_own_win_state(self) -> None:
        # --win draws a win; a captured frame already has one, or the capture is
        # what needs fixing.
        shot = self._png("shot.png", (400, 400))
        with self.assertRaises(SystemExit):
            self._boardplate(out="shot-plate.png", from_shot=shot,
                             rect="0.25,0.25,0.5,0.5", win="1x2")

    def test_a_neutral_plate_is_called_out(self) -> None:
        # Generic colours would advertise a field the app does not have.
        self._boardplate(out="neutral.png", symbol=[self._png("s.png", (64, 64))])
        self.assertTrue(any("does not have" in m for m in self.quiet_warnings),
                        self.quiet_warnings)


class PerspectiveTests(unittest.TestCase):
    """"Not just inserted — it should look 3d."

    A plate square to the camera is a decal however well it is lit, so the
    board is turned, tipped and given a slab edge before it ever reaches the
    draft the finished picture is rendered from.
    """

    def _plate(self) -> Image.Image:
        img = Image.new("RGBA", (200, 200), (60, 90, 200, 255))
        ImageDraw.Draw(img).rectangle([40, 40, 159, 159], fill=(240, 200, 80, 255))
        return img

    def test_turning_the_board_gives_it_a_near_edge_and_a_far_edge(self) -> None:
        # Negative yaw swings the right side toward the viewer, so that edge is
        # taller on the canvas than the receding left one — and the sign flips
        # with the yaw.
        for yaw, nearer in ((-20, "right"), (20, "left")):
            out = store_compose.to_perspective(self._plate(), yaw=yaw, pitch=0,
                                               depth=0.0)
            columns = (np.asarray(out.getchannel("A")) > 8).sum(axis=0)
            left, right = columns[:12].max(), columns[-12:].max()
            near, far = ((right, left) if nearer == "right" else (left, right))
            self.assertGreater(near, far, f"yaw={yaw}")

    def test_depth_adds_a_slab_edge_outside_the_face(self) -> None:
        flat = store_compose.to_perspective(self._plate(), yaw=-20, pitch=6, depth=0.0)
        slab = store_compose.to_perspective(self._plate(), yaw=-20, pitch=6, depth=0.12)
        self.assertGreater((np.asarray(slab.getchannel("A")) > 8).sum(),
                           (np.asarray(flat.getchannel("A")) > 8).sum())

    def test_the_receding_half_is_darker_than_the_near_half(self) -> None:
        # Light falloff has to agree with the geometry, or the board reads as a
        # flat rectangle someone skewed.
        out = store_compose.to_perspective(self._plate(), yaw=-20, pitch=0, depth=0.0)
        arr = np.asarray(out.convert("RGBA"), dtype=np.float32)
        lit = arr[..., 3] > 250
        mid = out.width // 2
        far = arr[..., :3][:, :mid][lit[:, :mid]].mean()
        near = arr[..., :3][:, mid:][lit[:, mid:]].mean()
        self.assertGreater(near, far)

    def test_a_square_on_plate_is_left_untouched(self) -> None:
        plate = self._plate()
        np.testing.assert_array_equal(
            np.asarray(store_compose.to_perspective(plate, 0, 0, 0)),
            np.asarray(plate))


class OcclusionTests(unittest.TestCase):
    """"Not just insert a player" — the slide has to contain it.

    Light and a contact shadow make a cutout lit by the picture. Only the
    scene's own foreground closing back over its feet makes it stand inside
    the picture rather than on it.
    """

    def _pano(self) -> Image.Image:
        pano = Image.new("RGBA", (200, 200), (20, 40, 120, 255))
        # A foreground floor across the bottom third, the way Phase 1 is asked
        # to draw one.
        ImageDraw.Draw(pano).rectangle([0, 140, 199, 199], fill=(220, 150, 40, 255))
        return pano

    def test_the_foreground_comes_back_over_the_object(self) -> None:
        pano = self._pano()
        front = store_compose.scene_front(pano, 40, 20, 120, 180, 0.2)
        self.assertIsNotNone(front)
        layer, x, y = front
        self.assertEqual((x, y), (40, 164))
        rgb = np.asarray(layer.convert("RGB"), dtype=np.float32)
        # It is the floor that is lifted, not the sky.
        self.assertGreater(rgb[..., 0].mean(), rgb[..., 2].mean())

    def test_it_fades_in_so_there_is_no_cut_line(self) -> None:
        layer, _, _ = store_compose.scene_front(self._pano(), 40, 20, 120, 180, 0.2)
        alpha = np.asarray(layer.getchannel("A"), dtype=np.float32)
        self.assertLess(alpha[0].mean(), 8)
        self.assertGreater(alpha[-1].mean(), 240)

    def test_art_off_the_canvas_is_never_smeared_back(self) -> None:
        # The hero's feet run past the bottom edge on purpose. Edge-extended
        # rows would paint a band of the last visible pixel row over its shins.
        pano = self._pano()
        layer, _, y = store_compose.scene_front(pano, 40, 100, 120, 140, 0.3)
        self.assertLessEqual(y + layer.height, pano.height)

    def test_a_request_with_nothing_to_hide_behind_is_refused(self) -> None:
        pano = self._pano()
        self.assertIsNone(store_compose.scene_front(pano, 40, 205, 120, 100, 0.3))
        self.assertIsNone(store_compose.scene_front(pano, 40, 20, 120, 180, 0.0))


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
