"""Car state, scenario set-up and the shared "world" state.

Ports inputcar.m and sakht.m. In the MATLAB code all state lives in the
struct array ``info.b`` which is saved to / loaded from inf.mat on every call.
Here the same fields live as attributes of :class:`Car` objects inside a
:class:`World`, so no files are needed.

Naming: MATLAB's field ``in`` is a Python keyword, so it is ``inside`` here.
Heading index ``p1``: 1 = moving -x, 2 = +x, 3 = -y, 4 = +y (as in pk1/pk2).
"""
import warnings

import numpy as np

# (initial heading p1, target heading pe) -> manoeuvre type ``pen``
# (the ``pend`` table of inputcar.m): 1 = keep heading, 2 = U-turn, 3/4 = turns
PEN_TABLE = {
    (1, 1): 1, (1, 2): 2, (1, 3): 3, (1, 4): 4,
    (2, 2): 1, (2, 1): 2, (2, 4): 3, (2, 3): 4,
    (3, 3): 1, (3, 4): 2, (3, 2): 3, (3, 1): 4,
    (4, 4): 1, (4, 3): 2, (4, 1): 3, (4, 2): 4,
}

# p = [600 1000; 400 0; 1000 400; 0 600]  (row p1 -> columns 1, 2)
_P = {1: (600, 1000), 2: (400, 0), 3: (1000, 400), 4: (0, 600)}
_PK1_START = {1: +1, 2: -1, 3: 0, 4: 0}
_PK2_START = {1: 0, 2: 0, 3: +1, 4: -1}

# sakht.m: free-space rectangles [xmin xmax ymin ymax] for each (p1, pe)
_SAKHT = [
    [[300, 700, 500, 700]],
    [[500, 700, 300, 700]],
    [[300, 700, 500, 700], [300, 500, 300, 700]],
    [[500, 700, 500, 700]],
    [[300, 500, 300, 700]],
    [[300, 700, 300, 500]],
    [[300, 500, 300, 500]],
    [[300, 700, 300, 500], [500, 700, 300, 700]],
    [[300, 500, 500, 700]],
    [[300, 500, 300, 700], [300, 700, 300, 500]],
    [[300, 500, 300, 700]],
    [[300, 700, 500, 700]],
    [[500, 700, 300, 700], [300, 700, 500, 700]],
    [[500, 700, 300, 500]],
    [[300, 700, 300, 500]],
    [[500, 700, 300, 700]],
]


def sakht(a, b):
    return np.array(_SAKHT[(a - 1) * 4 + (b - 1)], dtype=float)


class Car:
    """One vehicle. Field names follow info.b(n) of the MATLAB code."""

    def __init__(self, p1, p2, pe, a, v, s):
        pen = PEN_TABLE[(p1, pe)]
        po1 = _P[p1][1] + _PK1_START[p1] * p2   # start x
        po2 = _P[p1][0] + _PK2_START[p1] * p2   # start y
        q = sakht(p1, pe)

        # --- simulation state (inputcar.m) ---
        self.q = q
        self.q1 = q.copy()
        self.pox, self.poy = po1, po2        # origin of current motion segment
        self.pox1, self.poy1 = po1, po2      # fixed start point
        self.pnx, self.pny = [], []          # logged distance from start / y
        self.p1, self.pe, self.pen = p1, pe, pen
        self.p11 = p1                        # initial heading
        self.s, self.v, self.a = s, v, a
        self.flag = 0                        # tracker initialised?
        self.inside = 0                      # MATLAB: in
        self.fl1 = 0
        self.fl2 = 0
        self.pk1 = np.array([-1, +1, 0, 0], dtype=float)
        self.pk2 = np.array([0, 0, -1, +1], dtype=float)
        self.TT = 0
        self.gozar = 0                       # has been allowed to cross?
        # set by the controller
        self.pxn = None
        self.pyn = None
        self.vt = None
        # set by the tracker
        self.Ht = self.HHt = self.Wt = self.WWt = None
        self.out = None
        self.xc = self.yc = None
        self.Variance_u = self.Variance_v = None
        self.Tmodel = None                   # reference histogram (256,)
        self.x0 = self.y0 = self.x1 = self.y1 = None


class World:
    """Everything that MATLAB keeps in ``info`` besides the cars (info.g)."""

    def __init__(self, cars, n_particles=100, im_width=1000, im_height=1000,
                 seed=None):
        self.cars = cars
        self.N = n_particles
        self.im_width = im_width
        self.im_height = im_height
        self.rng = np.random.default_rng(seed)
        self.t_hist = [dict() for _ in cars]    # info.g.t(num, fr)
        self.it_hist = [dict() for _ in cars]   # info.g.Iteration(num, fr)


def build_cars(specs):
    """specs: list of dicts with keys street, position, goal_street,
    acceleration, speed, size  (the prompts of inputcar.m)."""
    cars, used = [], []
    for sp in specs:
        p1, p2 = int(sp["street"]), float(sp["position"])
        if any(u1 == p1 and abs(u2 - p2) < 50 for u1, u2 in used):
            # inputcar.m rejects this when typing cars in; the thesis scenario
            # (Table 4-1) has such cars, so from a file it is only a warning
            warnings.warn(f"car at position {p2} on street {p1} starts closer than 50 "
                          f"to another car on the same street")
        if (p1, int(sp["goal_street"])) not in PEN_TABLE:
            raise ValueError("street / goal_street must be in 1..4")
        used.append((p1, p2))
        cars.append(Car(p1, p2, int(sp["goal_street"]), float(sp["acceleration"]),
                        float(sp["speed"]), float(sp["size"])))
    return cars


def ask_cars():
    """Interactive version of inputcar.m (same questions)."""
    specs, used = [], []
    n = 0
    while True:
        n += 1
        p1 = int(input(f"Street of car{n} (1-4): "))
        p2 = float(input(f"Position of car{n} (0-500): "))
        if any(u1 == p1 and abs(u2 - p2) < 50 for u1, u2 in used):
            print("positions is Repetitious")
            n -= 1
            continue
        pe = int(input(f"Goal street of car{n} (1-4): "))
        a = float(input(f"Acceleration of car{n} (0-5): "))
        v = float(input(f"Initial speed of car{n} (0-10): "))
        s = float(input(f"Size of car{n} (0-5): "))
        used.append((p1, p2))
        specs.append(dict(street=p1, position=p2, goal_street=pe,
                          acceleration=a, speed=v, size=s))
        if int(input("More cars? 1/0: ")) == 0:
            return specs
