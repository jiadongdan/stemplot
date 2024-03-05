import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path


def ax_add_gradient_polygon(ax, vertices, angle, cmap, resolution=100, alpha=None, **kwargs):
    """
    Add a gradient-filled polygon to a Matplotlib axis with an optional alpha gradient that follows the gradient angle.

    Parameters:
    - ax: The Matplotlib axis to draw on.
    - vertices: Array of polygon vertices.
    - angle: The angle of the gradient in degrees.
    - cmap: The colormap of the gradient.
    - resolution: The resolution of the gradient meshgrid.
    - alpha: None, float in [0, 1], or array-like with two values for alpha gradient.
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

    if alpha is None:
        alpha = 1  # Default alpha value.
    elif isinstance(alpha, (list, tuple, np.ndarray)) and len(alpha) == 2:
        # Create an alpha gradient that follows the specified angle.
        # Calculate the alpha values across the gradient direction.
        alpha_values = np.linspace(alpha[0], alpha[1], resolution)
        alpha_gradient = np.cos(angle_rad) * (X - min_x) / (max_x - min_x) + np.sin(angle_rad) * (Y - min_y) / (
                    max_y - min_y)
        alpha_gradient = (alpha_gradient - alpha_gradient.min()) / (alpha_gradient.max() - alpha_gradient.min())
        alpha = np.interp(alpha_gradient, (alpha_gradient.min(), alpha_gradient.max()), (alpha[0], alpha[1]))
    # Ensure alpha is applied as intended.
    kwargs['alpha'] = alpha

    # Create a Path for the polygon.
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # Create and add a patch to clip the gradient.
    patch = patches.PathPatch(path, edgecolor='none', facecolor='none')
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


def create_beam(p1, p2, p3, **kwargs):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    width = np.abs(x2 - x3)
    height = width / 2.

    # Base of the ellipse
    x0 = (x2 + x3) / 2
    y0 = (y2 + y3) / 2

    # Recalculate elements to ensure correct path creation
    a_value = width / 2
    b_value = height / 2

    ratio = a_value / b_value

    h = y1 - y0
    # p1 is below p2 and p3
    if y1 < y0:
        h_value = np.abs(y1 - y0)

        x_tangent_left = -a_value * np.sqrt(h_value ** 2 - b_value ** 2) / h_value
        y_tangent_left = -(h_value - (-b_value ** 2 + h_value ** 2) / h_value)
        x_tangent_right = a_value * np.sqrt(h_value ** 2 - b_value ** 2) / h_value
        y_tangent_right = y_tangent_left  # Same y-coordinate for both points

        theta_range1 = np.linspace(np.arctan2(y_tangent_right * ratio, x_tangent_right), 0, 100)
        theta_range2 = np.linspace(0, np.arctan2(y_tangent_left * ratio, x_tangent_left) + 2 * np.pi, 100)
        theta_range = np.hstack([theta_range1, theta_range2])
    else:
        # p1 is above p2 and p3
        h_value = np.abs(y1 - y0)

        x_tangent_left = -a_value * np.sqrt(h_value ** 2 - b_value ** 2) / h_value
        y_tangent_left = h_value - (-b_value ** 2 + h_value ** 2) / h_value
        x_tangent_right = a_value * np.sqrt(h_value ** 2 - b_value ** 2) / h_value
        y_tangent_right = y_tangent_left  # Same y-coordinate for both points

        theta_range1 = np.linspace(0, np.arctan2(y_tangent_right * ratio, x_tangent_right), 100)[::-1]
        theta_range2 = np.linspace(np.arctan2(y_tangent_left * ratio, x_tangent_left), 2 * np.pi, 100)[::-1]
        theta_range = np.hstack([theta_range1, theta_range2])

    x_ellipse = a_value * np.cos(theta_range)
    y_ellipse = b_value * np.sin(theta_range)

    # Combining vertices, starting and ending at P, including lower part of the ellipse
    vertices = np.vstack(([0, h],
                          [x_tangent_right, y_tangent_right],
                          np.column_stack((x_ellipse, y_ellipse)),
                          [x_tangent_left, y_tangent_left],
                          [0, h])) + [x0, y0]

    # Codes for the path
    codes = [Path.MOVETO] + [Path.LINETO] + [Path.LINETO] * (len(theta_range) + 1) + [Path.CLOSEPOLY]

    # Creating the path and the patch
    path = Path(vertices, codes)
    patch = patches.PathPatch(path, **kwargs)

    return patch


def plot_beam(ax, p1, p2, p3, cmap, **kwargs):
    # create pathpatch for beam
    patch = create_beam(p1, p2, p3)
    vertices = patch._path.vertices
    ax_add_gradient_polygon(ax, vertices=vertices, angle=90, cmap=cmap, **kwargs)