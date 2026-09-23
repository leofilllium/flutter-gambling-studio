from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_menu_lead.py"
SPEC = importlib.util.spec_from_file_location("check_menu_lead", SCRIPT)
assert SPEC and SPEC.loader
menu_lead = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(menu_lead)

STRETCH_TESTS = importlib.util.spec_from_file_location(
    "test_check_asset_stretch", Path(__file__).with_name("test_check_asset_stretch.py"))
assert STRETCH_TESTS and STRETCH_TESTS.loader
_stretch_tests = importlib.util.module_from_spec(STRETCH_TESTS)
STRETCH_TESTS.loader.exec_module(_stretch_tests)
write_png = _stretch_tests.write_png

MENU_WITH_LEAD = """
class MainMenu extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Stack(children: [
      Align(
        alignment: Alignment.center,
        child: Image.asset(GameAssets.spriteJoker, width: 260, height: 260),
      ),
      PlayButton(),
    ]);
  }
}
"""

MENU_WITHOUT_LEAD = """
class MainMenu extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Text('Harlequin Revel'),
      PlayButton(),
      SettingsButton(),
    ]);
  }
}
"""


class Project:
    """A throwaway game project laid out the way the studio generates one."""

    def __init__(self, tmp: str, *, lead_kind: str = "character",
                 menu_role: str = "dominant",
                 menu: str = MENU_WITH_LEAD, menu_path: str = "lib/screens/main_menu.dart",
                 record_asset: bool = True) -> None:
        self.root = Path(tmp)
        write_png(self.root / "assets/images/sprites/sprite_joker.png", 512, 512)
        write_png(self.root / "assets/images/backgrounds/background_menu.png", 1080, 1920)
        (self.root / "lib").mkdir(parents=True, exist_ok=True)
        (self.root / "lib/assets.dart").write_text(
            "class GameAssets {\n"
            "  static const String spriteJoker = "
            "'assets/images/sprites/sprite_joker.png';\n}\n", encoding="utf-8")
        target = self.root / menu_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(menu, encoding="utf-8")
        concept = self.root / "design/gdd/game-concept.md"
        concept.parent.mkdir(parents=True, exist_ok=True)
        asset_line = ("- Lead asset: `assets/images/sprites/sprite_joker.png`\n"
                      if record_asset else "")
        concept.write_text(
            "# Harlequin Revel\n\n## Visual lead\n"
            f"- lead_kind: {lead_kind}\n- menu_role: {menu_role}\n{asset_line}",
            encoding="utf-8")

    def audit(self, **kwargs):
        params = dict(lead_kind=None, menu_role=None, lead_asset=None,
                      min_side=120.0, extra_docs=[])
        params.update(kwargs)
        return menu_lead.audit(self.root, self.root / "lib",
                               self.root / "assets", **params)


class LeadDiscoveryTests(unittest.TestCase):
    def test_reads_lead_kind_and_asset_from_the_concept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, context = Project(tmp).audit()
            self.assertEqual(context["lead_kind"], "character")
            self.assertEqual(context["menu_role"], "dominant")
            self.assertTrue(context["lead_asset"].endswith("sprite_joker.png"))
            self.assertEqual(findings, [])

    def test_reads_a_bolded_lead_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            (project.root / "design/gdd/game-concept.md").write_text(
                "**lead_kind**: character\n"
                "**menu_role**: dominant\n"
                "- Lead asset: `assets/images/sprites/sprite_joker.png`\n",
                encoding="utf-8")
            _, context = project.audit()
            self.assertEqual(context["lead_kind"], "character")

    def test_undeclared_lead_kind_is_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            (project.root / "design/gdd/game-concept.md").write_text(
                "# Harlequin Revel\n\nmenu_role: dominant\n", encoding="utf-8")
            findings, context = project.audit()
            self.assertIsNone(context["lead_kind"])
            self.assertEqual([f.code for f in findings], ["lead-kind-undeclared"])
            self.assertEqual([f.severity for f in findings], ["MEDIUM"])

    def test_undeclared_menu_role_is_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            concept = project.root / "design/gdd/game-concept.md"
            concept.write_text(
                "lead_kind: character\n"
                "- Lead asset: `assets/images/sprites/sprite_joker.png`\n",
                encoding="utf-8")
            findings, context = project.audit()
            self.assertIsNone(context["menu_role"])
            self.assertEqual([f.code for f in findings], ["menu-role-undeclared"])


class MenuLeadTests(unittest.TestCase):
    def test_character_absent_from_the_menu_is_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = Project(tmp, menu=MENU_WITHOUT_LEAD).audit()
            self.assertEqual([f.code for f in findings], ["lead-absent-from-menu"])
            self.assertEqual(findings[0].severity, "HIGH")

    def test_character_drawn_in_the_menu_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, context = Project(tmp).audit()
            self.assertEqual(findings, [])
            self.assertEqual(len(context["references"]), 1)

    def test_a_cameo_sized_lead_is_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cameo = MENU_WITH_LEAD.replace("width: 260, height: 260",
                                           "width: 48, height: 48")
            findings, _ = Project(tmp, menu=cameo).audit()
            self.assertEqual([f.code for f in findings], ["lead-drawn-small"])
            self.assertEqual(findings[0].severity, "MEDIUM")

    def test_supporting_lead_may_be_cameo_sized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cameo = MENU_WITH_LEAD.replace("width: 260, height: 260",
                                           "width: 48, height: 48")
            findings, context = Project(
                tmp, menu_role="supporting", menu=cameo).audit()
            self.assertEqual(findings, [])
            self.assertEqual(context["menu_role"], "supporting")

    def test_absent_role_does_not_force_store_lead_into_menu(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, context = Project(
                tmp, menu_role="absent", menu=MENU_WITHOUT_LEAD).audit()
            self.assertEqual(findings, [])
            self.assertEqual(context["menu_role"], "absent")

    def test_menu_is_found_in_every_structure_variant(self) -> None:
        for path in ("lib/screens/main_menu.dart", "lib/ui/screens/main_menu.dart",
                     "lib/presentation/screens/main_menu.dart",
                     "lib/interface/screens/main_menu.dart",
                     "lib/menus/main_menu.dart"):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                findings, context = Project(tmp, menu_path=path).audit()
                self.assertEqual(context["menu_sources"],
                                 [(Path(tmp) / path).as_posix()])
                self.assertEqual(findings, [])

    def test_missing_menu_source_is_medium_not_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = Project(tmp, menu_path="lib/screens/game_screen.dart").audit()
            self.assertEqual([f.code for f in findings], ["menu-source-not-found"])
            self.assertEqual(findings[0].severity, "MEDIUM")

    def test_missing_lead_asset_file_is_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            findings, _ = project.audit(
                lead_asset="assets/images/sprites/sprite_absent.png")
            self.assertEqual([f.code for f in findings], ["lead-asset-missing"])
            self.assertEqual(findings[0].severity, "HIGH")

    def test_unrecorded_lead_asset_is_medium(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = Project(tmp, menu=MENU_WITHOUT_LEAD,
                                  record_asset=False).audit()
            self.assertEqual([f.code for f in findings], ["lead-asset-unrecorded"])
            self.assertEqual(findings[0].severity, "MEDIUM")


class ObjectAndMechanicLeadTests(unittest.TestCase):
    def test_object_lead_is_not_required_to_show_a_character(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, context = Project(tmp, lead_kind="object",
                                        menu=MENU_WITHOUT_LEAD).audit()
            self.assertEqual(findings, [])
            self.assertIn("Do NOT add a character", context["note"])

    def test_mechanic_lead_is_not_required_to_show_a_character(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, context = Project(tmp, lead_kind="mechanic",
                                        menu=MENU_WITHOUT_LEAD).audit()
            self.assertEqual(findings, [])
            self.assertIn("mechanic-led", context["note"])


class CliTests(unittest.TestCase):
    def _run(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root),
             "--lib", str(root / "lib"), "--assets", str(root / "assets"),
             "--report", str(root / "menu-lead.md"), *extra],
            capture_output=True, text=True, timeout=60)

    def test_menu_with_the_lead_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            result = self._run(project.root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("**PASS**",
                          (project.root / "menu-lead.md").read_text(encoding="utf-8"))

    def test_menu_without_the_lead_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp, menu=MENU_WITHOUT_LEAD)
            result = self._run(project.root)
            self.assertEqual(result.returncode, 1, result.stdout)
            report = (project.root / "menu-lead.md").read_text(encoding="utf-8")
            self.assertIn("**FAIL**", report)
            self.assertIn("lead-absent-from-menu", report)

    def test_lead_kind_override_wins_over_the_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp, lead_kind="character", menu=MENU_WITHOUT_LEAD)
            result = self._run(project.root, "--lead-kind", "object")
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_report_table_survives_pipes_in_the_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Project(tmp)
            (project.root / "design/gdd/game-concept.md").write_text(
                "# Harlequin Revel\n", encoding="utf-8")
            self._run(project.root)
            report = (project.root / "menu-lead.md").read_text(encoding="utf-8")
            row = next(line for line in report.splitlines()
                       if line.startswith("| MEDIUM"))
            self.assertEqual(row.count("|") - row.count("\\|"), 4, row)

    def test_missing_roots_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--lib", f"{tmp}/nope",
                 "--assets", f"{tmp}/nope"],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
