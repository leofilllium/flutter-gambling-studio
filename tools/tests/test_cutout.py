from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
