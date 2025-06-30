import numpy as np

def ax_set_gradient_bg(ax, cmap='Blues', orientation='vertical'):
    """
    Fill the given Axes with a gradient background that spans the current data limits.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to which to apply the gradient background.
    cmap : str or Colormap, optional
        Name of the Matplotlib colormap (default: 'viridis').
    orientation : {'horizontal', 'vertical'}
        Direction of gradient. 'horizontal' → left-to-right,
        'vertical' → bottom-to-top.
    """
    # Generate a 1D gradient
    grad = np.linspace(0, 1, 256)
    if orientation in ['horizontal', 'h']:
        gradient = np.vstack((grad, grad))
    elif orientation in ['vertical', 'v']:
        gradient = np.vstack((grad, grad)).T
    else:
        raise ValueError("orientation must be 'horizontal' or 'vertical'")

    # Capture current data limits
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()

    # Draw gradient in data coordinates
    im = ax.imshow(
        gradient,
        aspect='auto',
        cmap=cmap,
        origin='lower',
        extent=(x0, x1, y0, y1),
        zorder=-1
    )

    # Restore original limits (imshow may reset them)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)

    return im

def ax_set_bg_color(ax, color):
    """
    Set the background color of the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes whose background color will be set.
    color : str or tuple
        A Matplotlib-compatible color specification (e.g., 'lightgray', '#f0f0f0', (0.9, 0.9, 0.9)).

    Returns
    -------
    matplotlib.axes.Axes
        The same Axes instance, for chaining.
    """
    # Set the face color (background) of the axes
    ax.set_facecolor(color)
    return ax

