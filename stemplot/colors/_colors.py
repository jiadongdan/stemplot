import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import hsv_to_rgb
from ._color_data import tab20
from ._colormaps import get_cmap

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# color conversion from old code
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


def generate_colors_from_lbs(lbs, colors=None):
    if colors is None:
        colors = np.array(tab20)
    else:
        colors = np.array(colors)
    lbs = np.array(lbs) % len(colors)
    return colors[lbs]


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



def xy2colors(xy, v=0.9, h=None, s=None, return_rgb=True):
    """
    Converts xy coordinates to colors in HSV or RGB format.

    Parameters:
    - xy (numpy.ndarray): The xy coordinates.
    - return_rgb (bool): Flag to determine if the output should be in RGB format. Defaults to True.

    Returns:
    - numpy.ndarray: Colors in HSV or RGB format.
    """
    # Calculate the angles from xy coordinates
    if h is None:
        angles = (np.arctan2(xy[:, 1], xy[:, 0]) + np.pi) / (2 * np.pi)
    else:
        angles = np.array([1.]*len(xy)) * h

    # Compute the radius and normalize it
    if s is None:
        radius = np.hypot(xy[:, 0], xy[:, 1])
        max_radius = np.max(radius)
        if max_radius > 0:
            radius = radius / max_radius
    else:
        radius = np.array([1.] * len(xy)) * s

    # Construct the HSV color representation
    hsv_colors = np.vstack([angles, radius, np.ones_like(radius) * v]).T

    # Convert to RGB if required
    if return_rgb:
        return hsv_to_rgb(hsv_colors)
    else:
        return hsv_colors

# Remember to import numpy before using this function.