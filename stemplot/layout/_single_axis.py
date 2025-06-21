from typing import Tuple, Union, Any
import matplotlib.figure
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

def generate_ax(
        fig: matplotlib.figure.Figure,
        width: float,
        height: float,
        **axes_kwargs: Any
) -> Axes:
    """
    Add a new Axes to `fig`, centered, with the exact width and height in inches.

    Parameters
    ----------
    fig
        The Figure to which the axes will be added.
    width
        Desired width of the axes, in inches. Must be > 0 and ≤ fig width.
    height
        Desired height of the axes, in inches. Must be > 0 and ≤ fig height.
    **axes_kwargs
        Passed directly to `fig.add_axes()` (e.g. facecolor, frameon, etc.).

    Returns
    -------
    ax
        The newly created Axes instance.

    Raises
    ------
    TypeError
        If `fig` is not a Matplotlib Figure.
    ValueError
        If width or height are non-positive or exceed the figure’s dimensions.
    """
    # --- Validation ---
    if not isinstance(fig, matplotlib.figure.Figure):
        raise TypeError(f"Expected a matplotlib.figure.Figure, got {type(fig)}")

    fig_w, fig_h = fig.get_size_inches()
    if width <= 0 or height <= 0:
        raise ValueError("`width` and `height` must both be positive")
    if width > fig_w or height > fig_h:
        raise ValueError(
            f"Requested size ({width}×{height} in) exceeds figure size ({fig_w:.1f}×{fig_h:.1f} in)"
        )

    # --- Compute normalized coords to center the axes ---
    frac_w = width / fig_w
    frac_h = height / fig_h
    left = (1 - frac_w) / 2
    bottom = (1 - frac_h) / 2

    # --- Create the Axes ---
    ax = fig.add_axes([left, bottom, frac_w, frac_h], **axes_kwargs)

    return ax


def set_xlabel_fontsize(ax: Axes, size: Union[float, str]) -> None:
    """
    Set the font size of the x-axis label on the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object whose x-label font size will be set.
    size : float or str
        Font size in points (e.g. 12) or named size (e.g. 'medium', 'large').
    """
    if not isinstance(ax, Axes):
        raise TypeError(f"Expected a matplotlib Axes, got {type(ax)}")
    ax.xaxis.label.set_fontsize(size)


def set_ylabel_fontsize(ax: Axes, size: Union[float, str]) -> None:
    """
    Set the font size of the y-axis label on the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object whose y-label font size will be set.
    size : float or str
        Font size in points (e.g. 12) or named size (e.g. 'medium', 'large').
    """
    if not isinstance(ax, Axes):
        raise TypeError(f"Expected a matplotlib.axes.Axes, got {type(ax)}")
    ax.yaxis.label.set_fontsize(size)


def set_xlabel(ax, text, **kwargs):
    if not isinstance(ax, Axes):
        raise TypeError(f"Expected a matplotlib.axes.Axes, got {type(ax)}")
    ax.set_xlabel(text, **kwargs)

def set_ylabel(ax, text, **kwargs):
    if not isinstance(ax, Axes):
        raise TypeError(f"Expected a matplotlib.axes.Axes, got {type(ax)}")
    ax.set_ylabel(text, **kwargs)

