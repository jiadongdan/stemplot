import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.colors import to_rgba


def _add_rounded_corners(x_coords, y_coords, radius):
    """
    Internal helper to round corners using Quadratic Bezier curves.
    Handles closed polygons correctly by treating corners as cyclic.
    """
    points = np.column_stack([x_coords, y_coords])
    n = len(points)
    new_points = []

    for i in range(n):
        prev_p = points[(i - 1) % n]
        curr_p = points[i]
        next_p = points[(i + 1) % n]

        vec_in  = curr_p - prev_p
        vec_out = next_p - curr_p
        len_in  = np.linalg.norm(vec_in)
        len_out = np.linalg.norm(vec_out)

        valid_radius = min(radius, len_in / 2, len_out / 2)

        if valid_radius < 1e-3:
            new_points.append(curr_p)
            continue

        tan_in  = curr_p - (vec_in  / len_in)  * valid_radius
        tan_out = curr_p + (vec_out / len_out) * valid_radius

        t = np.linspace(0, 1, 20).reshape(-1, 1)
        curve = (1-t)**2 * tan_in + 2*(1-t)*t * curr_p + t**2 * tan_out
        new_points.extend(curve)

    result = np.array(new_points)
    return result[:, 0], result[:, 1]


def draw_rounded_trapezoid(ax,
                           x_center, y_center,
                           top_width, bottom_width, height,
                           radius=10,
                           rotation=0,
                           closed=True,
                           **kwargs):
    """
    Draw a trapezoid with rounded corners on a matplotlib Axes.
    """
    half_b = bottom_width / 2
    half_t = top_width   / 2
    half_h = height      / 2

    bl = np.array([x_center - half_b, y_center - half_h])
    br = np.array([x_center + half_b, y_center - half_h])
    tr = np.array([x_center + half_t, y_center + half_h])
    tl = np.array([x_center - half_t, y_center + half_h])

    unique = np.array([bl, br, tr, tl])
    x_u, y_u = unique[:, 0], unique[:, 1]

    # Directly pass the 4 corners — no manual wrapping needed
    x_r, y_r = _add_rounded_corners(x_u, y_u, radius)

    # Apply rotation around (x_center, y_center)
    if rotation != 0:
        angle_rad = np.deg2rad(rotation)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        x_shifted = x_r - x_center
        y_shifted = y_r - y_center

        x_r = cos_a * x_shifted - sin_a * y_shifted + x_center
        y_r = sin_a * x_shifted + cos_a * y_shifted + y_center

    # Build a closed matplotlib Path and return a PathPatch
    verts = np.column_stack([x_r, y_r])
    if closed:
        verts = np.vstack([verts, verts[0]])
        codes = ([Path.MOVETO]
                 + [Path.LINETO] * (len(verts) - 2)
                 + [Path.CLOSEPOLY])
    else:
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)

    path  = Path(verts, codes)
    patch = mpatches.PathPatch(path, **kwargs)
    ax.add_patch(patch)
    return patch


def draw_rounded_trapezoid_transition(ax,
                                      x_center, y_center,
                                      top_width, bottom_width, height,
                                      radius=10,
                                      rotation=0,
                                      closed=True,
                                      gradient=None,
                                      **kwargs):

    half_b = bottom_width / 2
    half_t = top_width   / 2
    half_h = height      / 2

    bl = np.array([x_center - half_b, y_center - half_h])
    br = np.array([x_center + half_b, y_center - half_h])
    tr = np.array([x_center + half_t, y_center + half_h])
    tl = np.array([x_center - half_t, y_center + half_h])

    unique = np.array([bl, br, tr, tl])
    x_u, y_u = unique[:, 0], unique[:, 1]

    # Directly pass the 4 corners — no manual wrapping needed
    x_r, y_r = _add_rounded_corners(x_u, y_u, radius)

    # Apply rotation
    if rotation != 0:
        angle_rad = np.deg2rad(rotation)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        x_shifted = x_r - x_center
        y_shifted = y_r - y_center
        x_r = cos_a * x_shifted - sin_a * y_shifted + x_center
        y_r = sin_a * x_shifted + cos_a * y_shifted + y_center

    # Build path
    verts = np.column_stack([x_r, y_r])
    if closed:
        verts = np.vstack([verts, verts[0]])
        codes = ([Path.MOVETO]
                 + [Path.LINETO] * (len(verts) - 2)
                 + [Path.CLOSEPOLY])
    else:
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)

    path = Path(verts, codes)

    # Solid fill (no gradient)
    if gradient is None:
        patch = mpatches.PathPatch(path, **kwargs)
        ax.add_patch(patch)
        return patch

    # Gradient fill via imshow + clip_path
    color1 = to_rgba(gradient.get("color1", "white"))
    color2 = to_rgba(gradient.get("color2", "black"))
    direction = gradient.get("direction", "vertical")

    n = 256
    colors = np.array([
        np.linspace(color1[i], color2[i], n) for i in range(4)
    ]).T  # (n, 4)

    if direction == "vertical":
        img = colors[::-1].reshape(n, 1, 4)
    else:
        img = colors.reshape(1, n, 4)

    x_min, y_min = verts[:, 0].min(), verts[:, 1].min()
    x_max, y_max = verts[:, 0].max(), verts[:, 1].max()

    im = ax.imshow(
        img,
        extent=[x_min, x_max, y_min, y_max],
        aspect="auto",
        origin="lower",
        zorder=kwargs.get("zorder", 1),
        transform=ax.transData,
    )

    # Clip the gradient image to the trapezoid shape
    clip_patch = mpatches.PathPatch(path, transform=ax.transData, facecolor="none")
    ax.add_patch(clip_patch)
    im.set_clip_path(clip_patch)

    # Draw the edge separately if edgecolor is specified
    edge_kwargs = {
        "facecolor": "none",
        "edgecolor": kwargs.get("edgecolor", "none"),
        "linewidth": kwargs.get("linewidth", 1),
        "zorder": kwargs.get("zorder", 1),
    }
    edge_patch = mpatches.PathPatch(path, **edge_kwargs)
    ax.add_patch(edge_patch)

    return im