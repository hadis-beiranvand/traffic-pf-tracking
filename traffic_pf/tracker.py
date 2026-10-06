"""Particle-filter + mean-shift tracker. Ports filter2.m (the per-car,
per-frame tracking routine) and its helpers Epac.m, P.m / Q.m, distance.m,
Weight.m, Weight1.m, Iteration1.m.

(The MATLAB file filter2.m has the same name as a MATLAB built-in function;
here it is ``track_car``.)

Pixel coordinates are 0-based (MATLAB's are 1-based); this shifts everything
by one pixel and changes nothing else.
"""
import math
import time
import numpy as np
from scipy.ndimage import convolve

from .render import MX, BX, MY, BY

SQ = 40            # half-size of the initial box, in pixels
SIGMA = 0.1        # "M" in filter2.m: width of the Bhattacharyya weight

# Experiment switches. Defaults reproduce the MATLAB behaviour exactly.
UPDATE_BOX = True  # False: never shrink/grow the tracking window
VAR_FLOOR = 0      # >0: lower bound for the particle variance (px^2)


def use_robust_settings():
    """Optional, NOT in the MATLAB original: keep the tracking window fixed and
    use a wider particle cloud (std ~40 px). In 10 test runs per car this gave
    0 lost cars and a median error of ~8 px, vs. frequent loss with the
    original settings (the window shrinks and the cloud cannot follow the
    80-unit jump a car makes when it enters the junction)."""
    global UPDATE_BOX, VAR_FLOOR
    UPDATE_BOX = False
    VAR_FLOOR = 1600


def mround(v):
    """MATLAB round(): halves away from zero."""
    return math.floor(v + 0.5) if v >= 0 else -math.floor(-v + 0.5)


# ------------------------------------------------------------------ helpers
def rgb2gray_u8(F):
    g = (0.298936021293775 * F[..., 0] + 0.587043074451121 * F[..., 1]
         + 0.114020904255103 * F[..., 2])
    return np.floor(g + 0.5)


def smooth_gray(F):
    """I = round(imfilter(double(rgb2gray(F)), ones(3)/9))  (zero padding)."""
    I = convolve(rgb2gray_u8(F), np.ones((3, 3)) / 9.0, mode="constant", cval=0.0)
    return np.floor(I + 0.5)


def epac(h, w):
    """Epanechnikov kernel (Epac.m), including its off-by-one centre."""
    assert h % 2 == 1 and w % 2 == 1
    h2, w2 = h // 2, w // 2
    ii = np.arange(1, 2 * h2 + 2)[:, None]
    jj = np.arange(1, 2 * w2 + 2)[None, :]
    d = ((ii - h2) / h2) ** 2 + ((jj - w2) / w2) ** 2
    out = np.where(d < 1, 1 - d, 0.0)
    return out / out.sum()


def kernel_hist(T, g):
    """P.m / Q.m: kernel-weighted, normalised 256-bin histogram."""
    h = np.bincount(T.astype(np.int64).ravel(), weights=g.ravel(), minlength=256)
    return h / h.sum()


def distance(p, q):
    """Bhattacharyya distance (distance.m)."""
    return math.sqrt(max(0.0, 1.0 - float(np.sqrt(p * q).sum())))


def weight(p, q, sigma=SIGMA):
    """Weight.m"""
    d = distance(p, q)
    return (1.0 / math.sqrt(2 * math.pi * sigma ** 2)) * math.exp(-d ** 2 / (2 * sigma ** 2))


def weight_map(q, p, I):
    """Weight1.m: per-pixel back-projection weight q/(p+q) where p > 0."""
    idx = I.astype(np.int64)
    pv, qv = p[idx], q[idx]
    W = np.zeros(I.shape)
    m = pv > 0
    W[m] = qv[m] / (pv[m] + qv[m])
    return W


def meanshift_step(yc, xc, Ht, Wt, W1, g):
    """Iteration1.m: one mean-shift step. Returns (shift, yc, xc)."""
    hh, ww = (Ht - 1) // 2, (Wt - 1) // 2
    rows = np.arange(yc - hh, yc + hh + 1)
    cols = np.arange(xc - ww, xc + ww + 1)
    w = W1[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1] * g
    r = w.sum()
    if r <= 0:                       # MATLAB would produce NaN here
        return 0.0, yc, xc
    y1 = mround((w * rows[:, None]).sum() / r)
    x1 = mround((w * cols[None, :]).sum() / r)
    return math.hypot(y1 - yc, x1 - xc), y1, x1


def crop(I, yc, xc, HHt, WWt):
    y0, y1, x0, x1 = yc - HHt, yc + HHt + 1, xc - WWt, xc + WWt + 1
    if y0 < 0 or x0 < 0 or y1 > I.shape[0] or x1 > I.shape[1]:
        raise IndexError(f"tracking window leaves the image (centre {xc},{yc})")
    return I[y0:y1, x0:x1]


# ----------------------------------------------------------------- filter2.m
def track_car(F, fr, car, world, num):
    """Track one car in frame image F. Returns the (possibly annotated) image
    that is handed on to the next car, exactly like filter2.m."""
    im_w, im_h, N = world.im_width, world.im_height, world.N
    rng = world.rng

    # ---------------------------------------------------- first sight: init
    if car.flag == 0:
        pxn, pyn = car.pxn, car.pyn
        x0 = MX * pxn + BX - SQ
        x1 = MX * pxn + BX + SQ
        y0 = MY * pyn + BY + SQ
        y1 = MY * pyn + BY - SQ
        if not any(q < 90 or q > 910 for q in (x0, y0, x1, y1)):
            car.flag = 1
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            car.x0, car.y0, car.x1, car.y1 = mround(x0), mround(y0), mround(x1), mround(y1)
            xc = mround((x0 + x1) / 2)
            yc = mround((y0 + y1) / 2)
            Wt = x1 - x0 + 1
            Ht = y1 - y0 + 1
            HHt = mround(Ht / 2)
            WWt = mround(Wt / 2)
            Ht, Wt = 2 * HHt + 1, 2 * WWt + 1
            I = smooth_gray(F)
            T = crop(I, yc, xc, HHt, WWt)
            out = epac(Ht, Wt)
            car.Ht, car.HHt, car.Wt, car.WWt = Ht, HHt, Wt, WWt
            car.out = out
            car.xc, car.yc = xc, yc
            car.Variance_u = WWt * 20
            car.Variance_v = HHt * 20
            car.Tmodel = kernel_hist(T, out)
        return F

    # --------------------------------------------------------- tracking step
    t_start = time.perf_counter()
    A = F.copy()
    I = smooth_gray(F)
    Ht, HHt, Wt, WWt = car.Ht, car.HHt, car.Wt, car.WWt
    out, Tmodel = car.out, car.Tmodel
    xc, yc = car.xc, car.yc
    Variance_u, Variance_v = car.Variance_u, car.Variance_v
    g = np.ones_like(out)

    # edge detectors (3 columns / rows)
    Cl = np.zeros((Ht, 3)); Cr = np.zeros((Ht, 3))
    Ct = np.zeros((3, Wt)); Cb = np.zeros((3, Wt))
    Cl[:, 0], Cr[:, 0] = -2, 2
    Cl[:, 1], Cr[:, 1] = -1, -1
    Cl[:, 2], Cr[:, 2] = 2, -2
    Ct[0, :], Cb[0, :] = -2, 2
    Ct[1, :], Cb[1, :] = -1, -1
    Ct[2, :], Cb[2, :] = 2, -2

    # --- particles around the last position
    x = np.zeros(N)
    y = np.zeros(N)
    lo_x, hi_x = WWt, im_w - 1 - WWt
    lo_y, hi_y = HHt, im_h - 1 - HHt
    for i in range(N):
        u = math.sqrt(Variance_u) * rng.standard_normal()
        v = math.sqrt(Variance_v) * rng.standard_normal()
        x[i] = xc + u
        y[i] = yc + v
        while x[i] > hi_x or x[i] < lo_x:
            x[i] = xc + math.sqrt(Variance_u) * rng.standard_normal()
        while y[i] > hi_y or y[i] < lo_y:
            y[i] = yc + math.sqrt(Variance_v) * rng.standard_normal()

    Variance_x0 = x.max() - x.min()
    Variance_y0 = y.max() - y.min()
    Variance_x, Variance_y = Variance_x0, Variance_y0

    # --- iterate weighting + resampling until the cloud has contracted
    k = 0
    W = np.zeros(N)
    while Variance_x >= Variance_x0 / 4 and Variance_y >= Variance_y0 / 4 and k < 200:
        k += 1
        for i in range(N):
            C = crop(I, mround(y[i]), mround(x[i]), HHt, WWt)
            W[i] = weight(kernel_hist(C, out), Tmodel)
        W = W / W.sum()
        cs = np.cumsum(W)
        x_old, y_old = x.copy(), y.copy()
        for i in range(N):
            j = int(np.searchsorted(cs, rng.random(), side="left"))
            if j < N:                       # (MATLAB keeps the old value otherwise)
                x[i], y[i] = x_old[j], y_old[j]
        Variance_x = x.max() - x.min()
        Variance_y = y.max() - y.min()
        Variance_u = max(WWt * 10, VAR_FLOOR)
        Variance_v = max(HHt * 10, VAR_FLOOR)

    xc, yc = mround(x.mean()), mround(y.mean())

    # --- mean-shift refinement
    C = crop(I, yc, xc, HHt, WWt)
    W1 = weight_map(Tmodel, kernel_hist(C, out), I)
    e, c = 33.0, 0
    while c < 10 and e > 0.5:
        e, yc, xc = meanshift_step(yc, xc, Ht, Wt, W1, g)
        c += 1
        C = crop(I, yc, xc, HHt, WWt)
        W1 = weight_map(Tmodel, kernel_hist(C, out), I)

    # --- re-estimate the box from the four edges
    LXl, TXl = mround(xc - WWt - 0.2 * Wt), mround(xc - WWt + 0.2 * Wt)
    LXr, TXr = mround(xc + WWt - 0.2 * Wt), mround(xc + WWt + 0.2 * Wt)
    LYt, TYt = mround(yc - HHt - 0.2 * Ht), mround(yc - HHt + 0.2 * Ht)
    LYb, TYb = mround(yc + HHt - 0.2 * Ht), mround(yc + HHt + 0.2 * Ht)
    rows_c = np.arange(yc - HHt, yc + HHt + 1)
    cols_c = np.arange(xc - WWt, xc + WWt + 1)
    d3 = np.array([-1, 0, 1])

    def clip_r(a): return np.clip(a, 0, im_h - 1)
    def clip_c(a): return np.clip(a, 0, im_w - 1)

    best, Xl = -1e11, None
    for xx in range(LXl, TXl + 1):
        s = (Cl * W1[np.ix_(rows_c, clip_c(d3 + xx))]).sum()
        if s > best:
            best, Xl = s, xx
    best, Xr = -1e11, None
    for xx in range(LXr, TXr + 1):
        s = (Cr * W1[np.ix_(rows_c, clip_c(d3 + xx))]).sum()
        if s > best:
            best, Xr = s, xx
    best, Yt = -1e11, None
    for yy in range(LYt, TYt + 1):
        s = (Ct * W1[np.ix_(clip_r(d3 + yy), cols_c)]).sum()
        if s > best:
            best, Yt = s, yy
    best, Yb = -1e11, None
    for yy in range(LYb, TYb + 1):
        s = (Cb * W1[np.ix_(clip_r(d3 + yy), cols_c)]).sum()
        if s > best:
            best, Yb = s, yy

    HHHt = mround((Yb - Yt) / 2)
    WWWt = mround((Xr - Xl) / 2)
    if UPDATE_BOX and HHHt < 50 and HHHt > 7:
        if HHHt < 1.5 * HHt or HHHt > 0.8 * HHt:       # (always true, as in MATLAB)
            HHt = HHHt
            Ht = 2 * HHt + 1
    # NOTE: the MATLAB code has (WWWt<50)&&(WWWt<7) here -- probably meant
    # (WWWt>7), as in the height test above. Kept as is, so the width never changes.
    if WWWt < 50 and WWWt < 7:
        if WWWt < 1.5 * WWt or WWWt > 0.8 * WWt:
            WWt = WWWt
            Wt = 2 * WWt + 1

    out = epac(2 * HHt + 1, 2 * WWt + 1)
    t2 = time.perf_counter() - t_start

    # --- annotate: copy the tracked patch to the top-left corner, draw box+cross
    patch = A[max(yc - HHt, 0):yc + HHt + 1, max(xc - WWt, 0):xc + WWt + 1].copy()
    A[0:patch.shape[0], 0:patch.shape[1]] = patch
    def red(ys, xs):
        A[ys, xs, 0] = 255; A[ys, xs, 1] = 0; A[ys, xs, 2] = 0
    def green(ys, xs):
        A[ys, xs, 0] = 0; A[ys, xs, 1] = 255; A[ys, xs, 2] = 0
    ys_all = slice(max(yc - HHt, 0), yc + HHt + 1)
    xs_all = slice(max(xc - WWt, 0), xc + WWt + 1)
    for xx in (xc - WWt, xc, xc + WWt):
        red(ys_all, xx)
    for yy in (yc - HHt, yc + HHt):
        red(yy, xs_all)
    green(slice(max(yc - 10, 0), yc + 11), xc)
    green(yc, slice(max(xc - 10, 0), xc + 11))

    # --- store state
    car.Ht, car.HHt, car.Wt, car.WWt = Ht, HHt, Wt, WWt
    car.out = out
    car.xc, car.yc = xc, yc
    car.Variance_u, car.Variance_v = Variance_u, Variance_v
    world.t_hist[num][fr] = t2
    world.it_hist[num][fr] = k

    pxn, pyn = car.pxn, car.pyn
    if 240 < pxn < 760 and 240 < pyn < 760:
        car.inside = 1
    if (pxn > 760 or pxn < 240 or pyn > 760 or pyn < 240) and car.p1 == car.pe:
        car.inside = 0

    if car.inside == 0 and car.gozar == 0:
        return A
    return F
