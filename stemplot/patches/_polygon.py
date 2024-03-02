import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path


def ax_add_gradient_polygon(ax, vertices, angle, cmap, resolution=100, **kwargs):
    """
    Add a gradient-filled polygon to a Matplotlib axis.

    Parameters:
    - ax: The Matplotlib axis to draw on.
    - vertices: Array of polygon vertices.
    - angle: The angle of the gradient in degrees.
    - cmap: The colormap of the gradient.
    - resolution: The resolution of the gradient meshgrid.
    - **kwargs: Additional keyword arguments for patch customization.
    """
    # Ensure vertices form a closed loop by appending the first vertex if necessary.
    vertices = np.vstack([vertices, vertices[0]]) if not np.array_equal(vertices[0], vertices[-1]) else vertices

    # Determine the bounding box of the vertices.
    min_x, min_y = np.min(vertices, axis=0)
    max_x, max_y = np.max(vertices, axis=0)

    # Create a meshgrid for the gradient.
    x = np.linspace(min_x, max_x, resolution)
    y = np.linspace(min_y, max_y, resolution)
    X, Y = np.meshgrid(x, y)

    # Calculate the gradient.
    angle_rad = np.deg2rad(angle)
    gradient = np.cos(angle_rad) * (X - min_x) / (max_x - min_x) + np.sin(angle_rad) * (Y - min_y) / (max_y - min_y)

    # Normalize the gradient to [0, 1].
    gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min())

    # Create a Path for the polygon.
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # Create and add a patch to clip the gradient.
    patch = patches.PathPatch(path, edgecolor='none', facecolor='none', **kwargs)
    ax.add_patch(patch)

    # Display the gradient and clip it with the polygon.
    ax.imshow(gradient, extent=(min_x, max_x, min_y, max_y), cmap=cmap, origin='lower', **kwargs)
    ax.images[-1].set_clip_path(patch)