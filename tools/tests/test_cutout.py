from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
except ImportError:
    raise unittest.SkipTest("numpy is not installed in this host environment")


SCRIPT = Path(__file__).resolve().parents[1] / "cutout.py"
SPEC = importlib.util.spec_from_file_location("cutout", SCRIPT)
assert SPEC and SPEC.loader
cutout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cutout)


class FloodFillTests(unittest.TestCase):
    def test_trailing_barrier_does_not_index_past_hit_table(self) -> None:
        passable = np.array(
            [
                [True, False],
                [True, False],
            ],
            dtype=bool,
        )
        seed = passable.copy()
        result = cutout._propagate_axis(seed, passable, axis=1)
        np.testing.assert_array_equal(result, passable)


class InputCollectionTests(unittest.TestCase):
    def test_positional_directory_expands_sorted_png_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            (directory / "b.png").write_bytes(b"")
            (directory / "a.png").write_bytes(b"")
            (directory / "notes.txt").write_text("ignored", encoding="utf-8")

            paths = cutout.collect_paths([str(directory)], None)

            self.assertEqual([path.name for path in paths], ["a.png", "b.png"])

    def test_missing_directory_is_retained_for_file_not_found_reporting(self) -> None:
        missing = Path("does-not-exist")

        self.assertEqual(cutout.collect_paths([], str(missing)), [missing])


if __name__ == "__main__":
    unittest.main()
