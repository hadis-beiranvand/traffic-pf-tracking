"""Main loop (port of myfilter.m): simulate, film, track, decide, repeat.

    python -m traffic_pf.simulate                       # example scenario
    python -m traffic_pf.simulate --scenario my.json    # your own cars
    python -m traffic_pf.simulate --interactive         # type the cars in
"""
import argparse
import json
from pathlib import Path

import numpy as np

from .car import World, build_cars, ask_cars
from .controller import controler, Ai
from .render import render_frame
from . import controller, tracker
from .tracker import track_car

DEFAULT_SCENARIO = Path(__file__).resolve().parent.parent / "examples" / "two_cars.json"


def run(world, out_dir=None, save_frames=False, jpeg=True, max_frames=500,
        verbose=True, on_frame=None):
    """Run until every car has crossed and left the junction. Returns #frames.

    on_frame(fr, world, picture, tracked_picture) is called after every frame."""
    out_dir = Path(out_dir) if out_dir else None
    if out_dir and save_frames:
        (out_dir / "frames").mkdir(parents=True, exist_ok=True)
        import matplotlib.pyplot as plt

    fr = 1
    while True:
        controler(world)                              # plotBGIMAGE -> controler
        F0 = render_frame(world.cars, jpeg_roundtrip=jpeg)
        F = F0
        for num, car in enumerate(world.cars):        # F = filter2(F, fr, num)
            F = track_car(F, fr, car, world, num)
        if on_frame:
            on_frame(fr, world, F0, F)
        if out_dir and save_frames:
            plt.imsave(out_dir / "frames" / f"frame_{fr:03d}.png", F)
        Ai(world)
        if verbose:
            print(f"frame {fr:3d}: " + "  ".join(
                f"car{i + 1}=({c.pxn:6.1f},{c.pyn:6.1f}) in={c.inside} gozar={c.gozar}"
                for i, c in enumerate(world.cars)))
        fr += 1
        if all(c.gozar == 1 for c in world.cars) and all(c.inside == 0 for c in world.cars):
            break
        if fr > max_frames:
            print("stopped: max_frames reached")
            break
    return fr - 1


def history_matrix(hist, n_frames):
    """info.g.t / info.g.Iteration as (cars x frames), zero where not tracked."""
    m = np.zeros((len(hist), n_frames))
    for i, d in enumerate(hist):
        for fr, val in d.items():
            m[i, fr - 1] = val
    return m


def save_results(world, n_frames, out_dir, show=False):
    import matplotlib
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = np.arange(1, n_frames + 1)
    names = [f"car{i + 1}" for i in range(len(world.cars))]
    t = history_matrix(world.t_hist, n_frames)
    it = history_matrix(world.it_hist, n_frames)
    dist = np.array([c.pnx for c in world.cars])
    pny = np.array([c.pny for c in world.cars])

    for fname, data, ylabel in [("time_per_frame.png", t, "Time (s)"),
                                ("iterations_per_frame.png", it, "Iteration"),
                                ("distance_vs_frame.png", dist, "Distance from start")]:
        plt.figure()
        for row, name in zip(data, names):
            plt.plot(frames, row, label=name)
        plt.xlabel("Frame"); plt.ylabel(ylabel); plt.legend()
        plt.savefig(out_dir / fname, dpi=120)
    np.savez(out_dir / "results.npz", pnx=dist, pny=pny, time=t, iterations=it)
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", default=str(DEFAULT_SCENARIO), help="JSON file with the cars")
    ap.add_argument("--interactive", action="store_true", help="type the cars in (like inputcar.m)")
    ap.add_argument("--out", default="output", help="folder for plots / frames / results.npz")
    ap.add_argument("--save-frames", action="store_true", help="save the tracking view of every frame")
    ap.add_argument("--show", action="store_true", help="open the result plots")
    ap.add_argument("--seed", type=int, default=None, help="random seed of the particle filter")
    ap.add_argument("--particles", type=int, default=100)
    ap.add_argument("--robust-tracker", action="store_true",
                    help="fixed window + wider particle cloud (more reliable, but differs from the thesis code)")
    ap.add_argument("--fix-braking", action="store_true",
                    help="symmetric braking test so cars at rest heading 2/4 can start (not in the MATLAB code)")
    ap.add_argument("--no-jpeg", action="store_true", help="skip the JPEG round-trip of the frame")
    args = ap.parse_args()

    if args.fix_braking:
        controller.use_symmetric_braking()
    if args.robust_tracker:
        tracker.use_robust_settings()
    specs = ask_cars() if args.interactive else json.loads(Path(args.scenario).read_text())
    world = World(build_cars(specs), n_particles=args.particles, seed=args.seed)
    n = run(world, args.out, args.save_frames, jpeg=not args.no_jpeg)
    save_results(world, n, args.out, show=args.show)
    print(f"done: {n} frames, results in {args.out}/")


if __name__ == "__main__":
    main()
