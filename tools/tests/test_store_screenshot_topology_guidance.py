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

    def test_exact_topology_has_bounded_deterministic_fallback(self) -> None:
        required_contract = (
            "count- and order-sensitive gameplay geometry",
            "After one bounded recovery",
            "exact real board/field plate and shipped sprites",
            "complete exact field layer rather than redrawing its cells",
            "not permission to paste an unintegrated rectangular screenshot",
            "Recount the final exported topology",
        )
        for phrase in required_contract:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.guidance)

        integration_start = self.guidance.index(
            "Treat count- and order-sensitive gameplay geometry"
        )
        recovery = self.guidance.index("After one bounded recovery", integration_start)
        deterministic = self.guidance.index("exact real board/field plate", recovery)
        final_audit = self.guidance.index("Recount the final exported topology", deterministic)
        self.assertLess(integration_start, recovery)
        self.assertLess(recovery, deterministic)
        self.assertLess(deterministic, final_audit)

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
