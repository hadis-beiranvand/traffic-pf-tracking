"""The simulation/controller part is deterministic, so it must reproduce the
trajectories saved by the original MATLAB run (inf.mat) exactly.
Run:  python -m pytest tests   (or: python tests/test_against_matlab.py)
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from traffic_pf import controller                      # noqa: E402
from traffic_pf.car import World, build_cars          # noqa: E402
from traffic_pf.simulate import run                    # noqa: E402


def _check(original_braking):
    if original_braking:
        controller.use_original_braking()
    else:
        controller.use_symmetric_braking()
    ref = json.loads((ROOT / "examples" / "matlab_reference.json").read_text())
    specs = json.loads((ROOT / ref["scenario"]).read_text())
    world = World(build_cars(specs), seed=0)
    n = run(world, verbose=False)
    assert n == len(ref["cars"][0]["pnx"])
    for car, r in zip(world.cars, ref["cars"]):
        assert np.allclose(car.pnx, r["pnx"], atol=1e-5)
        assert np.allclose(car.pny, r["pny"], atol=1e-5)


def test_trajectories_match_matlab():
    _check(original_braking=True)      # default: exact MATLAB behaviour


def test_symmetric_braking_gives_same_result_here():
    _check(original_braking=False)     # optional --fix-braking, same 2-car result


if __name__ == "__main__":
    test_trajectories_match_matlab()
    test_symmetric_braking_gives_same_result_here()
    print("OK: identical to the MATLAB run (default and --fix-braking)")
