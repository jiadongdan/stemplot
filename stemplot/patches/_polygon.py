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


def create_hollow_ellipse_half(center, width, height, ratio=0.5, half='upper', **kwargs):
    """
    Creates a PathPatch of either the upper or lower half of a hollow ellipse.

    Parameters:
    - center: Tuple (x, y) specifying the center of the ellipse.
    - width, height: Dimensions of the outer ellipse.
    - ratio: Size ratio of the inner ellipse relative to the outer one.
    - half: String specifying which half to generate ('upper' or 'lower').

    Returns:
    - A matplotlib.patches.PathPatch object.
    """
    # Determine theta range based on the desired half
    if half == 'upper':
        theta = np.linspace(0, np.pi, 100)
    elif half == 'lower':
        theta = np.linspace(np.pi, 2 * np.pi, 100)
    else:
        raise ValueError("Invalid value for 'half'. Choose 'upper' or 'lower'.")

    # Outer ellipse vertices
    outer_x = center[0] + width / 2 * np.cos(theta)
    outer_y = center[1] + height / 2 * np.sin(theta)

    # Inner ellipse vertices (reversed for correct path direction)
    inner_width, inner_height = width * ratio, height * ratio
    inner_x = center[0] + inner_width / 2 * np.cos(theta)[::-1]
    inner_y = center[1] + inner_height / 2 * np.sin(theta)[::-1]

    # Combine vertices
    vertices = np.vstack([np.column_stack([outer_x, outer_y]), np.column_stack([inner_x, inner_y])])

    # Define path codes
    codes = np.full(vertices.shape[0], Path.LINETO)
    codes[0] = Path.MOVETO  # Start of outer ellipse
    codes[100] = Path.MOVETO  # Start of inner ellipse

    # Create the Path and PathPatch
    path = Path(vertices, codes)
    patch = patches.PathPatch(path, **kwargs)  # Change fill=True if you want it filled

    return patch


def create_hollow_ellipse(center, width, height, ratio):
    """
    Generates a matplotlib path patch of a hollow ellipse.

    Parameters:
    - center: Tuple (x, y) specifying the center of the ellipse.
    - width: The total width of the outer ellipse.
    - height: The total height of the outer ellipse.
    - ratio: A float (0 < ratio < 1) specifying the size ratio of the inner ellipse relative to the outer ellipse.

    Returns:
    - A matplotlib.patches.PathPatch object representing the hollow ellipse.
    """
    # Ensure the ratio is valid
    if not (0 < ratio < 1):
        raise ValueError("Ratio must be between 0 and 1.")

    # Generate the outer ellipse
    theta = np.linspace(0, 2 * np.pi, 100)
    outer_x = center[0] + (width / 2) * np.cos(theta)
    outer_y = center[1] + (height / 2) * np.sin(theta)

    # Generate the inner ellipse scaled by the given ratio
    inner_x = center[0] + (width / 2 * ratio) * np.cos(-theta) # Note the direction to ensure proper Path direction
    inner_y = center[1] + (height / 2 * ratio) * np.sin(-theta)

    # Combine the paths
    vertices = np.concatenate([np.column_stack([outer_x, outer_y]), np.column_stack([inner_x, inner_y])])
    codes = np.full(len(vertices), Path.LINETO)
    codes[0] = Path.MOVETO
    codes[len(theta)] = Path.MOVETO

    path = Path(vertices, codes)
    patch = patches.PathPatch(path, fill=True, facecolor='lightgrey', edgecolor='black')

    return patch
