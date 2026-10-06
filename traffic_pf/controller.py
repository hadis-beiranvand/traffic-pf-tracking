"""Traffic logic. Ports controler.m (motion + turns), Ai.m (speed decisions)
and check.m / check1.m / check2.m / check3.m.

The MATLAB code re-loads inf.mat inside every helper; here all functions read
the shared ``world.cars`` directly, which is equivalent because MATLAB saved
the file after every car update.
"""
import math
import numpy as np

# The braking-distance test of Ai.m, ``max([pxn-a pyn-b]) > 200``, is only
# positive for cars heading 1 or 3 (moving towards smaller x / y), so a car that
# starts at rest heading 2 or 4 never moves. By default this is kept exactly as
# in the MATLAB code. use_symmetric_braking() uses abs() instead (my change,
# NOT in the thesis code; identical results on the thesis scenarios tried).
SYMMETRIC_BRAKING = False


def use_original_braking():
    global SYMMETRIC_BRAKING
    SYMMETRIC_BRAKING = False


def use_symmetric_braking():
    global SYMMETRIC_BRAKING
    SYMMETRIC_BRAKING = True


def _gap(pxn, pyn, a, b):
    if SYMMETRIC_BRAKING:
        return max(abs(pxn - a), abs(pyn - b))
    return max(pxn - a, pyn - b)


# ---------------------------------------------------------------- controler.m
def controler(world):
    """Advance every car by one frame and update its free-space rectangles.

    Note: on a car's first frame controler.m compared its position with an empty
    value (or, for the first car, with a leftover global variable); the jump test
    is therefore skipped on a car's first frame here.
    """
    for car in world.cars:
        TT, v, pox, poy = car.TT, car.v, car.pox, car.poy
        a = car.a
        pxn, pyn = car.pxn, car.pyn      # None on the first frame
        pxnn, pynn = pxn, pyn
        p1 = car.p1
        pk1, pk2 = car.pk1.copy(), car.pk2.copy()

        TT += 1
        car.TT = TT

        def komaki():
            """Start a new motion segment from the current state."""
            nonlocal TT, v, pox, poy
            TT = 0
            car.TT = 0
            pox, poy = pxn, pyn
            v = car.vt
            car.v = car.vt
            car.pox, car.poy = pxn, pyn
            car.fl1 = 1

        if car.inside == 1:
            if car.pen == 1:
                pass
            elif car.pen == 2:                                   # U-turn
                if car.fl1 == 0 or car.fl2 == 0:
                    if car.p11 == 1:
                        if pxn < 600 and car.fl1 == 0:
                            p1 = 4; pk1 = -1 * pk1; pk2 = -1 * pk2; komaki()
                        if pyn < 400:
                            p1 = 2
                            pk1 = np.array([-1., +1, 0, 0]); pk2 = np.array([0., 0, -1, +1])
                            komaki(); car.fl2 = 1
                    elif car.p11 == 2:
                        if pxn > 400 and car.fl1 == 0:
                            p1 = 3; pk1 = -1 * pk1; pk2 = -1 * pk2; komaki()
                        if pyn > 600:
                            p1 = 1
                            pk1 = np.array([-1., +1, 0, 0]); pk2 = np.array([0., 0, -1, +1])
                            komaki(); car.fl2 = 1
                    elif car.p11 == 3:
                        if pyn < 600 and car.fl1 == 0:
                            p1 = 1; pk1 = -1 * pk1; pk2 = -1 * pk2; komaki()
                        if pxn > 600:
                            p1 = 4
                            pk1 = np.array([-1., +1, 0, 0]); pk2 = np.array([0., 0, -1, +1])
                            komaki(); car.fl2 = 1
                    elif car.p11 == 4:
                        if pyn > 400 and car.fl1 == 0:
                            p1 = 2; pk1 = -1 * pk1; pk2 = -1 * pk2; komaki()
                        if pxn < 400:
                            p1 = 3
                            pk1 = np.array([-1., +1, 0, 0]); pk2 = np.array([0., 0, -1, +1])
                            komaki(); car.fl2 = 1
            elif car.pen == 3:                                   # turn, type 3
                if car.fl1 == 0:
                    if p1 == 1:
                        if pxn < 400:
                            p1 = 3; komaki()
                        elif car.gozar == 1:
                            poy = -(car.v / 5) * TT + poy
                    elif p1 == 2:
                        if pxn > 600:
                            p1 = 4; komaki()
                        elif car.gozar == 1:
                            poy = (car.v / 5) * TT + poy
                    elif p1 == 3:
                        if pyn < 400:
                            p1 = 2; komaki()
                        elif car.gozar == 1:
                            pox = (car.v / 6) * TT + pox
                    elif p1 == 4:
                        if pyn > 600:
                            p1 = 1; komaki()
                        elif car.gozar == 1:
                            pox = -(car.v / 6) * TT + pox
            elif car.pen == 4:                                   # turn, type 4
                if car.fl1 == 0:
                    if p1 == 1:
                        if pxn < 600:
                            p1 = 4; komaki()
                    elif p1 == 2:
                        if pxn > 400:
                            p1 = 3; komaki()
                    elif p1 == 3:
                        if pyn < 600:
                            p1 = 1; komaki()
                    elif p1 == 4:
                        if pyn > 400:
                            p1 = 2; komaki()

            car.p1 = p1
            car.pk1 = pk1
            car.pk2 = pk2
            d = 0.5 * a * TT ** 2 + v * TT
            pxn = d * pk1[p1 - 1] + pox
            pyn = d * pk2[p1 - 1] + poy
            vt = a * TT + v
            car.pxn, car.pyn, car.vt = pxn, pyn, vt
        else:
            d = 0.5 * a * TT ** 2 + v * TT
            pxn = d * pk1[p1 - 1] + pox
            pyn = d * pk2[p1 - 1] + poy
            vt = a * TT + v
            car.pxn, car.pyn, car.vt = pxn, pyn, vt

        if vt <= 0 and a != 0 and vt < v:
            car.v = 0
            car.vt = 0
            car.a = 0

        # ---- free-space rectangles ahead of / around the car -----------------
        car.q = car.q1
        dx = 200
        qq = []
        if car.gozar == 1:
            q = car.q1
            for ij in range(q.shape[0]):
                if q[ij, 0] <= pxn <= q[ij, 1] and q[ij, 2] <= pyn <= q[ij, 3]:
                    if car.pen == 2:
                        if p1 == 1:
                            qq.append([pxn, min(pxn + dx, q[ij, 1]), q[ij, 2], q[ij, 3]])
                        elif p1 == 2:
                            qq.append([max(pxn - dx, q[ij, 0]), pxn, q[ij, 2], q[ij, 3]])
                        elif p1 == 3:
                            qq.append([q[ij, 0], q[ij, 1], pyn, min(pyn + dx, q[ij, 3])])
                        elif p1 == 4:
                            qq.append([q[ij, 0], q[ij, 1], max(pyn - dx, q[ij, 2]), pyn])
                    else:
                        if (car.pen == 3 and car.p1 != car.p11 and ij == 0
                                and q.shape[0] == 2):
                            car.q1 = np.delete(car.q1, ij, axis=0)
                        else:
                            if p1 == 1:
                                qq.append([max(pxn - dx, q[ij, 0]), pxn, q[ij, 2], q[ij, 3]])
                            elif p1 == 2:
                                qq.append([pxn, min(pxn + dx, q[ij, 1]), q[ij, 2], q[ij, 3]])
                            elif p1 == 3:
                                qq.append([q[ij, 0], q[ij, 1], max(pyn - dx, q[ij, 2]), pyn])
                            elif p1 == 4:
                                qq.append([q[ij, 0], q[ij, 1], pyn, min(pyn + dx, q[ij, 3])])
        else:
            dx = dx * 3 / 2
            q = car.q
            if car.inside == 1:
                if p1 == 1:
                    qq = [[max(pxn - dx, q[0, 0]), pxn, q[0, 2], q[0, 3]]]
                elif p1 == 2:
                    qq = [[pxn, min(pxn + dx, q[0, 1]), q[0, 2], q[0, 3]]]
                elif p1 == 3:
                    qq = [[q[0, 0], q[0, 1], max(pyn - dx, q[0, 2]), pyn]]
                elif p1 == 4:
                    qq = [[q[0, 0], q[0, 1], pyn, min(pyn + dx, q[0, 3])]]
        car.q = car.q1 if len(qq) == 0 else np.array(qq, dtype=float)

        if pxnn is not None and (abs(pxnn - pxn) >= 100 or abs(pynn - pyn) >= 100):
            car.v = 50
            car.vt = 0
            car.a = 0

        car.pnx.append(math.hypot(car.pox1 - pxn, car.poy1 - pyn))
        car.pny.append(pyn)


# --------------------------------------------------------------------- check*
def check(world, p1, pxn, pyn):
    """Number of cars (incl. the caller) in the lane strip ahead of the car."""
    if p1 == 1:
        s = (700, pxn + 20, 500, 700)
    elif p1 == 2:
        s = (pxn - 20, 300, 300, 500)
    elif p1 == 3:
        s = (300, 500, 700, pyn + 20)
    else:
        s = (500, 700, pyn - 20, 300)
    n = 0
    for c in world.cars:
        if s[0] < c.pxn < s[1] and s[2] < c.pyn < s[3]:
            n += 1
    return n


def check1(world, p1, pxn, pyn, num):
    """Returns (a, b): the point the car should brake towards."""
    s = [[700, 300, pxn, pxn],
         [pyn, pyn, 700, 300]]
    q = check(world, p1, pxn, pyn)
    a = s[0][p1 - 1]
    b = s[1][p1 - 1]
    if q > 1:
        f = [k for k, c in enumerate(world.cars) if c.p1 == p1 and k != num]
        g = [world.cars[k].pxn for k in f]
        g1 = [world.cars[k].pyn for k in f]
        # MATLAB concatenation: max([]) is [], i.e. contributes nothing
        row1 = ([max(g), min(g)] if g else []) + [pxn, pxn]
        row2 = [pyn, pyn] + ([max(g1), min(g1)] if g1 else [])
        a = row1[p1 - 1]          # IndexError where MATLAB also errors
        b = row2[p1 - 1]
    return a, b


def check2(world, p1, pxn, pyn, q, num):
    """1 if the car may enter the junction, 0 if it must wait."""
    me = world.cars[num]
    others = [k for k, c in enumerate(world.cars)
              if c.inside == 1 and k != num and c.gozar != 0]
    if me.gozar == 1:
        return 1
    k = 0
    for oi in others:
        o = world.cars[oi]
        g = o.q
        for i1 in range(g.shape[0]):
            for i2 in range(q.shape[0]):
                if ((q[i2, 0] >= g[i1, 1] or g[i1, 0] >= q[i2, 1]) or
                        (q[i2, 2] >= g[i1, 3] or g[i1, 2] >= q[i2, 3])):
                    pass                                  # rectangles disjoint
                else:
                    if p1 == o.p11 and (abs(pxn - o.pxn) >= 200 or abs(pyn - o.pyn) >= 200):
                        pass
                    else:
                        k += 1
    return 1 if k == 0 else 0


_LANES = [(0, 300, 500, 700), (700, 1000, 300, 500),
          (300, 500, 0, 300), (500, 700, 700, 1000)]


def check3(world, pxn, pyn, num):
    """1 if the car sits on an approach/exit arm and already has its goal heading."""
    car = world.cars[num]
    in_lane = any(l[0] < pxn < l[1] and l[2] < pyn < l[3] for l in _LANES)
    return 1 if (in_lane and car.p1 == car.pe) else 0


# ----------------------------------------------------------------------- Ai.m
def Ai(world):
    """Speed / acceleration decisions for every car."""
    for num, car in enumerate(world.cars):
        p1, pxn, pyn, vt, q = car.p1, car.pxn, car.pyn, car.vt, car.q

        def restart(v, a=0.0, TT=0):
            car.v, car.a, car.TT = v, a, TT
            car.pox, car.poy = car.pxn, car.pyn

        if car.inside == 0:
            if car.vt == 0:
                a_, b_ = check1(world, p1, pxn, pyn, num)
                if _gap(pxn, pyn, a_, b_) > 200:
                    restart(30, 0, 1)
            else:
                if check3(world, pxn, pyn, num) == 1:
                    restart(50, 0, 0)
                else:
                    if check(world, p1, pxn, pyn) > 1:
                        a_, b_ = check1(world, p1, pxn, pyn, num)
                        m = _gap(pxn, pyn, a_, b_)
                        if m > 200:
                            car.a = -(vt ** 2) / (2 * abs(m))
                            car.pox, car.poy = car.pxn, car.pyn
                            car.v = car.vt
                            car.TT = 0
                        else:
                            restart(0, 0, 0)
                    else:
                        restart(35, 0, 0)
        elif car.inside == 1:
            if check2(world, p1, pxn, pyn, q, num) == 0:
                restart(0, 0, 0)
            else:
                if car.gozar == 0:
                    car.pox, car.poy = car.pxn, car.pyn
                    car.TT = 1
                car.gozar = 1
                car.v = 40
                car.a = 0
