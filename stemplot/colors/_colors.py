import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import hsv_to_rgb
from matplotlib.colors import to_rgba
from matplotlib import cm
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
    hex_color = np.array([mc.to_hex(c, keep_alpha=keep_alpha) for c in colors if mc.is_color_like(c)])
    return hex_color

def generate_colors_from_lbs(lbs, colors=None, cmap='coolwarm'):
    """
    Convert labels to RGBA colors.

    This function maps input labels to RGBA colors based on the number of unique labels. The color mapping
    strategy varies depending on the number of unique labels:

    - If the number of unique labels is less than 10, colors are selected from the 'tab10' colormap.
    - If the number of unique labels is between 10 and 20 (inclusive), colors are selected from the 'tab20' colormap.
    - If the number of unique labels is greater than 20, colors are generated using a specified colormap (default: 'coolwarm').
    - Alternatively, custom colors can be provided, which will be used directly if specified.

    Parameters:
    -----------
    lbs : array-like
        Input labels to be converted to colors. Can be a list, numpy array, or any iterable.

    colors : list of str or None, optional
        A list of color strings to be used for mapping labels. If provided, the number of colors should
        be at least equal to the number of unique labels. Default is None.

    cmap : str, optional
        The name of the colormap to use if the number of unique labels is greater than 20 and no custom colors
        are provided. Default is 'coolwarm'.

    Returns:
    --------
    lbs_colors : numpy.ndarray
        An array of RGBA colors corresponding to the input labels.

    Raises:
    -------
    ValueError
        If the number of provided colors is less than the number of unique labels.

    Example:
    --------
    >>> lbs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> colors = generate_colors_from_lbs(lbs)
    >>> print(colors)
    """
    if lbs is None:
        if colors is None:
            return 'C0'
        else:
            raise ValueError(
                "Labels are None, but colors are provided. Please provide valid labels or leave colors as None.")

    lbs = np.asarray(lbs)
    unique_labels = np.unique(lbs)
    num_unique_labels = len(unique_labels)

    # Determine color mapping strategy
    if num_unique_labels < 10:
        color_map = plt.get_cmap('tab10')
        rgba_colors = [color_map(i) for i in range(num_unique_labels)]
    elif num_unique_labels <= 20:
        color_map = plt.get_cmap('tab20')
        rgba_colors = [color_map(i) for i in range(num_unique_labels)]
    elif colors is not None:
        if len(colors) < num_unique_labels:
            raise ValueError("Number of provided colors is less than the number of unique labels.")
        rgba_colors = [to_rgba(color) for color in colors]
    else:
        color_map = cm.get_cmap(cmap)
        rgba_colors = [color_map(i / (num_unique_labels - 1)) for i in range(num_unique_labels)]

    # Map labels to colors
    label_to_color = {label: rgba_colors[i] for i, label in enumerate(unique_labels)}
    lbs_colors = np.array([label_to_color[label] for label in lbs])

    return lbs_colors


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