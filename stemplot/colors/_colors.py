import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from ._color_data import tab20
from ._colormaps import get_cmap

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# color conversion
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def to_rgba(colors, alpha=None):
    rgba = np.array([mc.to_rgba(c, alpha) for c in colors if mc.is_color_like(c)])
    return rgba

def to_rgb(colors):
    rgba = np.array([mc.to_rgba(c) for c in colors if mc.is_color_like(c)])
    return rgba[:, 0:3]

def to_hex(colors, keep_alpha=False):
    hex = np.array([mc.to_hex(c, keep_alpha=keep_alpha) for c in colors if mc.is_color_like(c)])
    return hex


# this function is frequnetly used !!!
def colors_from_lbs(lbs, colors=None, xy=None, alpha_min=0.5):
    if colors is None:
        colors = np.array(tab20)
    else:
        colors = np.array(colors)
    lbs = np.array(lbs) % len(colors)

    c = to_rgba(colors[lbs])

    if xy is not None:
        xy_ = np.vstack([xy[lbs == e] - xy[lbs == e].mean(axis=0) for e in np.unique(lbs)])
        r = np.hypot(xy_[:, 0], xy_[:, 1])
        r = r / r.max()
        r[r < alpha_min] = alpha_min
        c[:, 3] = r
    return c


def colors_from_cmap(cmap, num=10, low=0., high=1., alpha=1.):
    cmap = get_cmap(cmap)
    N = np.linspace(low, high, num)
    rgba = cmap(N)
    rgba[:, 3] = alpha
    return rgba


