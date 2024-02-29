def get_size_inches(ax):
    """
    Calculate the size of an Axes object in inches.

    Parameters:
    - ax: Matplotlib Axes object.

    Returns:
    - Tuple (width, height) representing the size of the Axes in inches.
    """
    # Get the figure size in inches
    fig_w, fig_h = ax.figure.get_size_inches()
    # Get the relative position of the Axes within the figure
    bbox = ax.get_position()
    # Calculate the absolute size in inches
    return (fig_w * bbox.width, fig_h * bbox.height)


def get_ax_aspect(ax):
    """
    Calculate the aspect ratio of an Axes object.

    Parameters:
    - ax: Matplotlib Axes object.

    Returns:
    - The aspect ratio (width / height) of the Axes.
    """
    w, h = get_size_inches(ax)
    return w / h


def get_fig_aspect(fig):
    """
    Calculate the aspect ratio of a Figure object.

    Parameters:
    - fig: Matplotlib Figure object.

    Returns:
    - The aspect ratio (width / height) of the Figure.
    """
    fig_w, fig_h = fig.get_size_inches()
    return fig_w / fig_h
