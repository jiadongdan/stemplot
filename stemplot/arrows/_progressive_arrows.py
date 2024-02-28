import numpy as np
import matplotlib.pyplot as plt
from ..colors._colors import colors_from_cmap

def get_h_progressive_bar(start, end, w, **kwargs):
    x1, y1 = start
    x2, y2 = end

    p1 = (x1, y1 - w / 2)
    p2 = (x1 + w / 2, (y1 + y2) / 2)
    p3 = (x1, y1 + w / 2)
    p4 = (x2, y2 + w / 2)
    p5 = (x2 + w / 2, (y1 + y2) / 2)
    p6 = (x2, y2 - w / 2)
    pts = np.array([p1, p2, p3, p4, p5, p6])

    poly = plt.Polygon(pts, **kwargs)

    return poly

def fig_add_progressive_hbar(fig, start, end, ratios, colors=None, low=0, high=1, w=0.05):
    if colors is None:
        colors = colors_from_cmap('summer', len(ratios), low=low, high=high)

    start = np.array(start)
    end = np.array(end)
    lamds = np.cumsum(ratios/np.sum(ratios))[0:-1]
    pts = np.array([start]+[start*(1-s)+end*s for s in lamds] + [end])
    ijs = np.lib.stride_tricks.sliding_window_view(range(len(pts)), 2)
    for idx, (i, j) in enumerate(ijs):
        p1 = pts[i]
        p2 = pts[j]
        p3 = p2.copy()
        p3[0] -= 0.01
        pp = get_h_progressive_bar(start=p1, end=p3, w=w, color=colors[idx])
        fig.add_artist(pp)