"""Make a demo GIF: the simulated camera image with the tracker's box on every car.

    python examples/make_demo_gif.py thesis_table_4_1.json demo_6cars nobox   # 6 cars, car numbers only
    python examples/make_demo_gif.py two_cars.json demo_2cars                 # 2 cars with tracker boxes
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from traffic_pf import tracker                                   # noqa: E402
from traffic_pf.car import World, build_cars                     # noqa: E402
from traffic_pf.render import MX, BX, MY, BY                     # noqa: E402
from traffic_pf.simulate import run                              # noqa: E402

scenario = sys.argv[1] if len(sys.argv) > 1 else "two_cars.json"
name = sys.argv[2] if len(sys.argv) > 2 else "demo"
boxes = not (len(sys.argv) > 3 and sys.argv[3] == "nobox")
COLORS = [(0, 170, 0), (255, 140, 0), (160, 0, 200), (0, 150, 220), (200, 0, 100), (90, 90, 90)]

frames, errors = [], []


def collect(fr, world, picture, tracked):
    img = Image.fromarray(picture)
    d = ImageDraw.Draw(img)
    for i, car in enumerate(world.cars):
        col = COLORS[i % len(COLORS)]
        if car.flag:
            errors.append(np.hypot(car.xc - (MX * car.pxn + BX), car.yc - (MY * car.pyn + BY)))
        if not boxes:                      # label the true car positions (simulation only)
            px, py = MX * car.pxn + BX, MY * car.pyn + BY
            if 0 <= px < 1000 and 0 <= py < 1000:
                d.text((px + 22, py - 30), f"car {i + 1}", fill=col)
        elif car.flag:
            d.rectangle([car.xc - car.WWt, car.yc - car.HHt, car.xc + car.WWt, car.yc + car.HHt],
                        outline=col, width=3)
            d.text((car.xc - car.WWt + 4, car.yc - car.HHt - 14), f"car {i + 1}", fill=col)
    d.text((20, 20), f"frame {fr}", fill=(0, 0, 0))
    frames.append(img.resize((500, 500), Image.LANCZOS))


tracker.use_robust_settings()
specs = json.loads((ROOT / "examples" / scenario).read_text())
world = World(build_cars(specs), seed=0)
run(world, verbose=False, on_frame=collect)
out = ROOT / "docs"
out.mkdir(exist_ok=True)
frames[0].save(out / f"{name}.gif", save_all=True, append_images=frames[1:], duration=300, loop=0)
frames[len(frames) // 2].save(out / f"{name}_frame.png")
e = np.array(errors)
print(f"{len(world.cars)} cars, {len(frames)} frames, median tracker error {np.median(e):.1f} px, share of car-frames with error > 40 px: {np.mean(e > 40):.0%}")
