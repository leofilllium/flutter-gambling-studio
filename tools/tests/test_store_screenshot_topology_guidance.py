from pathlib import Path
import unittest


class StoreScreenshotTopologyGuidanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[2]
        cls.guidance = (
            repo / ".claude/skills/store-screenshots/SKILL.md"
        ).read_text(encoding="utf-8")
        cls.guidance_flat = " ".join(cls.guidance.split())

    def test_panorama_uses_capture_only_as_context_for_one_generated_scene(self) -> None:
        phase = self.guidance.split("## Phase 1 — composition and integrated art", 1)[1].split(
            "## Phase 2 — identity and critical-region review", 1
        )[0]
        required_contract = (
            "**context only**",
            "complete, coherent image",
            "three-quarter/3D view",
            "must not assemble its gameplay field",
            "do not substitute a composited field",
            "Recount the final exported topology",
        )
        for phrase in required_contract:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, phase)

        self.assertNotIn("tools/store_compose.py boardplate", phase)
        self.assertNotIn("--from-shot", phase)
        self.assertNotIn("deterministic project-derived layer", phase)
        self.assertIn("Reject any visible capture boundary", self.guidance)
        self.assertIn("the gameplay capture was reference-only", self.guidance)

    def test_feature_graphic_is_text_free_with_one_phone_on_the_right(self) -> None:
        required_contract = (
            "a banner with one phone on the right and no text",
            "no title, tagline, logo, wordmark, caption, badge or call to action",
            "`banner` refuses `--title`, `--tagline` and `--logo`",
            "`--shot` is required",
            "`--frame none` is refused",
            "a left side left blank for text is a failed banner",
        )
        for phrase in required_contract:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)
        self.assertNotIn("optional typography", self.guidance_flat)

    def test_angled_field_requires_contextual_embedding_cues(self) -> None:
        required_cues = (
            "a perspective transform alone is not evidence of integration",
            "structural reception",
            "recessed housing, altar or console",
            "photometric contact",
            "contact shadow plus local colour spill, light wrap or reflection",
            "spatial interaction",
            "foreground or atmospheric element crossing the housing edge",
            "at final panel size as well as in the continuous panorama",
        )
        for phrase in required_cues:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance_flat)

        perspective_only = self.guidance_flat.index(
            "a perspective transform alone is not evidence of integration"
        )
        structure = self.guidance_flat.index("structural reception", perspective_only)
        lighting = self.guidance_flat.index("photometric contact", structure)
        overlap = self.guidance_flat.index("spatial interaction", lighting)
        final_size = self.guidance_flat.index("at final panel size", overlap)
        self.assertLess(perspective_only, structure)
        self.assertLess(structure, lighting)
        self.assertLess(lighting, overlap)
        self.assertLess(overlap, final_size)


if __name__ == "__main__":
    unittest.main()
