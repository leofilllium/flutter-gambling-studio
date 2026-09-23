from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_gameplay_center.py"
SPEC = importlib.util.spec_from_file_location("check_gameplay_center", SCRIPT)
assert SPEC and SPEC.loader
gameplay_center = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gameplay_center)


class LayoutDirectionTests(unittest.TestCase):
    def test_classification_codes_are_not_mistaken_for_recipes(self) -> None:
        docs = [("concept.md", "Category: C1\nMathematical model: M1\n")]
        self.assertIsNone(gameplay_center.find_layout_direction(docs))

    def test_reads_codes_from_an_explicit_recipe_line(self) -> None:
        docs = [("art-direction.md", "Recipe: F3 + C5 + H4 + O1 + R2\n")]
        self.assertEqual(
            gameplay_center.find_layout_direction(docs),
            "recipe F3+C5+H4+O1+R2",
        )

    def test_alignment_declaration_is_a_layout_direction(self) -> None:
        docs = [("art-direction.md", "Primary field alignment: centered\n")]
        self.assertEqual(
            gameplay_center.find_layout_direction(docs),
            "recipe alignment declared",
        )

    def test_legacy_archetype_remains_readable(self) -> None:
        docs = [("art-direction.md", "Legacy layout: L4\n")]
        self.assertEqual(
            gameplay_center.find_layout_direction(docs),
            "legacy L4",
        )

    def test_intentional_offset_reason_is_detected(self) -> None:
        docs = [(
            "art-direction.md",
            "Primary field alignment: intentionally offset because controls form an edge rail\n",
        )]
        self.assertTrue(gameplay_center.has_recorded_exception(docs))


if __name__ == "__main__":
    unittest.main()
