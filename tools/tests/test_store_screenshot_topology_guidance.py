from pathlib import Path
import unittest


class StoreScreenshotTopologyGuidanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[2]
        cls.guidance = (
            repo / ".claude/skills/store-screenshots/SKILL.md"
        ).read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
