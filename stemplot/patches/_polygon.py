import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path


def ax_add_gradient_polygon(ax, vertices, angle, cmap):
    # Step 1: Determine the bounding box
    min_x, min_y = np.min(vertices, axis=0)
    max_x, max_y = np.max(vertices, axis=0)

    # Step 2: Create a mesh grid
    x = np.linspace(min_x, max_x, 100)
    y = np.linspace(min_y, max_y, 100)
    X, Y = np.meshgrid(x, y)

    # Step 3: Compute the directional gradient
    # Convert angle to radians and compute gradient
    angle_rad = np.deg2rad(angle)
    gradient = np.cos(angle_rad) * (X - min_x) / (max_x - min_x) + np.sin(angle_rad) * (Y - min_y) / (max_y - min_y)

    # Normalize gradient to [0, 1] range
    gradient = (gradient - np.min(gradient)) / (np.max(gradient) - np.min(gradient))

    # Step 4: Create a Path for the polygon
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # Step 5: Create a patch from the Path
    patch = patches.PathPatch(path, facecolor='none', lw=2)

    # Step 6: Clip the gradient with the polygon
    ax.imshow(gradient, extent=(min_x, max_x, min_y, max_y), cmap=cmap, origin='lower')
    ax.add_patch(patch)
    #ax.set_xlim(min_x, max_x)
    #ax.set_ylim(min_y, max_y)
    #ax.set_aspect('equal', adjustable='box')

    # Clip the gradient outside the polygon
    ax.images[-1].set_clip_path(patch)