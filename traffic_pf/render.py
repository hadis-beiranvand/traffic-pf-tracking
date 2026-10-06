"""Draws the intersection and the cars (port of plotBGIMAGE.m).

The MATLAB code "films" its own figure (print -djpeg frame.jpg, then
imresize to 1000x1000) and the tracker works on that picture. We do the same
with matplotlib's Agg canvas, using the same default axes position as MATLAB,
so the sim-coordinate -> pixel mapping is exact.
"""
import io
import numpy as np
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

AXES_POS = (0.13, 0.11, 0.775, 0.815)     # MATLAB default axes position
FIG_W, FIG_H, DPI = 12, 9, 100            # 1200x900 px, like the saved frame.jpg
PT = 1.78                                 # scale of fonts etc. vs. a 100-dpi figure
MARKER_PT = 1.5                           # marker size scale (calibrated on frame.jpg)
LINE_PT = 1.3                             # line width in points (calibrated on frame.jpg)
IMG_SIZE = 1000                           # tracker image is 1000x1000

# sim (x, y) -> pixel in the resized 1000x1000 image:  px = MX*x + BX, py = MY*y + BY
MX = AXES_POS[2]
BX = IMG_SIZE * AXES_POS[0]
MY = -AXES_POS[3]
BY = IMG_SIZE * (1 - AXES_POS[1])

# MATLAB default colour order (marker edge colour of car 1, 2, ...)
_COLORS = ["#0072BD", "#D95319", "#EDB120", "#7E2F8E", "#77AC30", "#4DBEEE", "#A2142F"]

_SEGMENTS = [
    ([0, 300], [300, 300], "b"), ([700, 1000], [300, 300], "b"),
    ([0, 300], [400, 400], "b--"), ([700, 1000], [400, 400], "b--"),
    ([0, 300], [500, 500], "k"), ([700, 1000], [500, 500], "k"),
    ([0, 300], [600, 600], "r--"), ([700, 1000], [600, 600], "r--"),
    ([0, 300], [700, 700], "r"), ([700, 1000], [700, 700], "r"),
    ([300, 300], [0, 300], "r"), ([300, 300], [700, 1000], "r"),
    ([400, 400], [0, 300], "r--"), ([400, 400], [700, 1000], "r--"),
    ([500, 500], [0, 300], "k"), ([500, 500], [700, 1000], "k"),
    ([600, 600], [0, 300], "b--"), ([600, 600], [700, 1000], "b--"),
    ([700, 700], [0, 300], "b"), ([700, 700], [700, 1000], "b"),
    ([300, 300], [300, 700], "k"), ([300, 700], [300, 300], "k"),
    ([700, 700], [300, 700], "k"), ([300, 700], [700, 700], "k"),
    ([350, 350], [350, 650], "k"), ([350, 650], [350, 350], "k"),
    ([650, 650], [350, 650], "k"), ([350, 650], [650, 650], "k"),
]


def render_frame(cars, jpeg_roundtrip=True):
    """Return the 1000x1000x3 uint8 image the tracker sees."""
    fig = Figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes(AXES_POS)
    for xs, ys, style in _SEGMENTS:
        ax.plot(xs, ys, style, linewidth=LINE_PT)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ticks = list(range(0, 1001, 100))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.tick_params(direction="in", top=True, right=True, labelsize=7.5 * PT,
                   width=0.5 * PT, length=3 * PT)

    for i, car in enumerate(cars):
        if car.pen == 2 and car.fl2 == 0 and car.fl1 == 1:
            marks = [">", "<", "^", "v"]       # MATLAB had 'V' here (invalid marker)
        else:
            marks = ["<", ">", "v", "^"]
        # MATLAB clips by data point, not by marker extent: a marker whose centre
        # is inside the axes is drawn whole, one whose centre is outside is hidden.
        if 0 <= car.pxn <= 1000 and 0 <= car.pyn <= 1000:
            ax.plot([car.pxn], [car.pyn], marks[car.p1 - 1], linestyle="none",
                    markersize=(12 + car.s) * MARKER_PT, markerfacecolor="r",
                    markeredgecolor=_COLORS[i % len(_COLORS)],
                    markeredgewidth=0.5 * PT, clip_on=False)

    canvas.draw()
    img = Image.fromarray(np.asarray(canvas.buffer_rgba())[..., :3].copy())
    if jpeg_roundtrip:                         # print -djpeg frame.jpg / imread
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.BICUBIC)   # imresize
    return np.asarray(img).copy()
