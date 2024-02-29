import numpy as np
from matplotlib.transforms import Bbox

def h_axes(fig, n=2, top=0.95, bottom=None, h='max', left=0.06, right=0.04, wspace=0.25, ratios=None):
    """
    Create a horizontal array of axes within a figure with specified layout configurations.

    Parameters:
    - fig: The Matplotlib figure object in which the axes are to be created.
    - n: The number of subplots (axes) to create. Default is 2.
    - top: The top position of the subplot(s) in figure coordinates (0 to 1). Default is 0.95.
    - bottom: The bottom position of the subplot(s). If None, it is calculated based on the height and aspect ratio.
    - h: Specifies the height strategy of the subplots. It can be 'max', 'min', 'mean', a specific ratio (float between 0 and 1), or an integer index to select the width for the height calculation. Default is 'max'.
    - left: The left position of the first subplot in figure coordinates. Default is 0.06.
    - right: The right margin of the figure in figure coordinates. Default is 0.04.
    - wspace: The amount of width reserved for space between subplots, expressed as a fraction of the average axis width. Default is 0.25.
    - ratios: The width ratios of the subplots. Determines the relative widths of subplots if they are not equally sized.

    Returns:
    - A list of axes objects created within the figure.
    """
    # Validate and process input ratios
    ratios = np.ones(n) if ratios is None else np.array([ratios] * n if np.isscalar(ratios) else ratios)

    # Calculate aspect ratio of the figure for height adjustment
    fig_aspect = fig.get_figwidth() / fig.get_figheight()

    # Initial GridSpec to get widths for height calculations
    temp_gs = fig.add_gridspec(nrows=1, ncols=n, left=left, right=1 - right, bottom=0.1, top=top, wspace=wspace,
                               width_ratios=ratios)
    _, _, lefts, rights = temp_gs.get_grid_positions(fig)

    widths = rights - lefts

    # Determine height based on specified method
    if isinstance(h, str):
        h = {'min': widths.min(), 'max': widths.max(), 'mean': widths.mean()}.get(h, widths.max())
    elif 0 < h < 1:
        h = h * widths.mean()
    else:
        h = widths[min(len(widths) - 1, int(h))]

    # Calculate bottom if not provided
    if bottom is None:
        bottom = top - h * fig_aspect

    # Final GridSpec for axes creation
    gs = fig.add_gridspec(nrows=1, ncols=n, left=left, right=1 - right, bottom=bottom, top=bottom + h * fig_aspect,
                          wspace=wspace, width_ratios=ratios)

    # Create and return the axes
    return gs.subplots()


def get_top_from_axes(axes, vspace=0.25):
    """
    Calculate the top position for a new set of axes based on the existing axes.

    This function computes the average top position of the provided axes,
    adjusted by a specified vertical spacing (vspace).

    Parameters:
    - axes: List or array of Matplotlib axes objects.
    - vspace: Vertical spacing factor to adjust the top position. It's a fractional
              part of the average axes height to be subtracted from the mean top position.

    Returns:
    - The calculated top position for the new axes.
    """
    if not axes:
        raise ValueError("The 'axes' list is empty. Please provide valid Matplotlib axes objects.")

    # Extract the vertical positions and heights of the axes
    positions = np.array([ax.get_position().bounds for ax in axes])
    bottoms = positions[:, 1]
    heights = positions[:, 3]

    # Calculate the mean bottom position and height
    mean_bottom = bottoms.mean()
    mean_height = heights.mean()

    # Adjust the top position based on the average height and the vertical spacing
    adjusted_top = mean_bottom + mean_height * (1 - vspace)

    return adjusted_top

def axes_from_ax(ax, nrows, ncols, wspace=0.1, hspace=0.1, width_ratios=None, height_ratios=None, remove=False, hide=True):
    """
    Create a grid of subplots within the bounds of an existing axis.

    Parameters:
    - ax: The original axis object from which to base the new grid.
    - nrows: Number of rows in the grid.
    - ncols: Number of columns in the grid.
    - wspace: The amount of width reserved for blank space between subplots.
    - hspace: The amount of height reserved for white space between subplots.
    - width_ratios: Relative widths of the columns. None means equal width.
    - height_ratios: Relative heights of the rows. None means equal height.
    - remove: If True, the original axis is removed from the figure.
    - hide: If True (and remove is False), the original axis is hidden (ticks and spines are removed).

    Returns:
    - A 2D NumPy array of axes objects corresponding to the grid.
    """
    fig = ax.figure
    # Extract the position of the original axis to use for the new GridSpec
    left, bottom, right, top = ax.get_position().extents

    # Create GridSpec within the bounds of the original axis
    gs = fig.add_gridspec(nrows, ncols, left=left, right=right, bottom=bottom, top=top,
                          wspace=wspace, hspace=hspace,
                          width_ratios=width_ratios, height_ratios=height_ratios)

    # Create subplots from GridSpec
    axes = gs.subplots()

    # Option to remove the original axis
    if remove:
        ax.remove()
    elif hide:
        # Hide the original axis by removing ticks, labels, and spines
        ax.set_xticks([])
        ax.set_yticks([])
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    return axes


def merge_axes(axes, remove=False):
    """
    Merge multiple Matplotlib axes into a single axis by creating a new axis that
    encompasses the combined area of all provided axes. Optionally removes the original axes.

    Parameters:
    - axes: An array-like collection of Matplotlib axes to be merged.
    - remove: Boolean, if True, the original axes will be removed from the figure.

    Returns:
    - ax_union: A new Matplotlib axis object that represents the merged area of the input axes.
    """
    if not axes.size:
        raise ValueError("No axes provided for merging.")

    # Flatten the axes array to simplify processing
    axes_flat = np.array(axes).ravel()

    # Ensure there are axes to merge
    if len(axes_flat) == 0:
        raise ValueError("The 'axes' parameter is empty. At least one axis is required.")

    # Calculate the union of all bounding boxes from the provided axes
    bboxes = [ax.get_position() for ax in axes_flat]
    bbox_union = Bbox.union(bboxes)

    # Create a new axis that covers the entire area of the merged bounding boxes
    ax_union = axes_flat[0].figure.add_axes(bbox_union.bounds)

    # Optionally remove the original axes
    if remove:
        for ax in axes_flat:
            ax.remove()

    return ax_union

