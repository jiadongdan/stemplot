import numpy as np
import matplotlib.pyplot as plt
import colorsys
import matplotlib.colors as mc


def is_cmap(cmap):
    valid_cmaps = plt.colormaps()
    if cmap in valid_cmaps:
        return True
    elif isinstance(cmap, mc.Colormap):
        return True
    else:
        return False


def color_palette(name, low=0., high=1., N=256):
    if mc.is_color_like(name):
        rgb = mc.to_rgb(name)
        hls = colorsys.rgb_to_hls(*rgb)
        palette = np.array([colorsys.hls_to_rgb(*(hls[0], i, hls[2])) for i in np.linspace(low, high, N)])
        cmap = mc.ListedColormap(palette)
    elif is_cmap(name):
        cmap = plt.get_cmap(name)
    else:
        raise ValueError('name is NOT a valid colormap or color name.')
    return cmap


def color_mix(c1, c2, mode='mix', gamma=None):
    # Validate mode and gamma parameters
    assert mode in ("mix", "blend"), "Mode must be 'mix' or 'blend'."
    assert gamma is None or gamma > 0, "Gamma must be positive."

    # Check if both colors are valid
    if not (mc.is_color_like(c1) and mc.is_color_like(c2)):
        raise ValueError("c1 and c2 must be valid color names.")

    # Convert colors to RGBA
    rgba1 = np.asarray(mc.to_rgba(c1))
    rgba2 = np.asarray(mc.to_rgba(c2))

    # Generate a linspace for the mixing parameter
    ts = np.linspace(0, 1, 256)

    if mode == "mix":
        if gamma in (1., None):
            rgba = (1 - ts[:, None]) * rgba1 + ts[:, None] * rgba2
        else:
            rgb = np.power((1 - ts[:, None]) * rgba1[:3] ** gamma + ts[:, None] * rgba2[:3] ** gamma, 1 / gamma)
            a = (1 - ts) * rgba1[3] + ts * rgba2[3]
            rgba = np.column_stack([rgb, a])
    elif mode == "blend":
        a = 1 - (1 - (1 - ts) * rgba1[3]) * (1 - rgba2[3])
        s = (1 - (1 - ts) * rgba1[3]) * rgba2[3] / a
        if gamma in (1., None):
            rgb = (1 - s[:, None]) * rgba1[:3] + s[:, None] * rgba2[:3]
        else:
            rgb = np.power((1 - s[:, None]) * rgba1[:3] ** gamma + s[:, None] * rgba2[:3] ** gamma, 1 / gamma)
        rgba = np.column_stack([rgb, a])

    # Create and return the colormap
    return mc.ListedColormap(rgba)


def get_cmap(name, low=0., high=1.0, N=256):
    return color_palette(name, low, high, N)


def get_cmap_from_colors(colors):
    return mc.ListedColormap(colors)

