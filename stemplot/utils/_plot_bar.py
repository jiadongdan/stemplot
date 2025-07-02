import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

def plot_bar(
        ax,
        data,
        labels,
        orientation='vertical',
        bar_gap=0.2,
        colors=None,
        **kwargs
):
    """
    Plot a bar chart on the given Axes, with optional per-legend colors.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Pre-created Axes object.
    data : array_like, shape (n_labels,) or (n_legends, n_labels)
        1D: one bar per label; 2D: one group per column, with n_legends bars each.
    labels : list of str, length n_labels
        The group labels.
    orientation : {'horizontal','vertical'}
        'horizontal' → ax.bar; 'vertical' → ax.barh.
    bar_gap : float
        Spacing between groups; center-to-center distance is 1+bar_gap.
    colors : None, single color, or sequence of length n_legends
        If None, use whatever you pass in kwargs (or default cmap). If a single
        color or a list/array, each legend-row i will use colors[i].
    **kwargs
        Other bar/barh kwargs (e.g. edgecolor, alpha, linewidth).

    """
    data = np.atleast_2d(data)
    n_legends, n_labels = data.shape

    # pop out bar_width if you want custom widths
    bar_width = kwargs.pop('bar_width', None) or (0.8 / n_legends)

    # prepare colors array
    if colors is None:
        # rely on kwargs.get('color', None)
        use_colors = [kwargs.pop('color', None)] * n_legends
    else:
        # allow single color or list of length n_legends
        if isinstance(colors, (list, tuple, np.ndarray)):
            if len(colors) != n_legends:
                raise ValueError(f"colors must have length {n_legends}")
            use_colors = colors
        else:
            use_colors = [colors] * n_legends

    group_positions = np.arange(n_labels) * (1 + bar_gap)
    group_width     = n_legends * bar_width

    if orientation == 'vertical':
        # vertical bars: use ax.bar
        for i in range(n_legends):
            offsets = group_positions - group_width/2 + (i+0.5)*bar_width
            bars = ax.bar(
                    offsets,
                    data[i, :],
                    width=bar_width,
                    color=use_colors[i],
                    **kwargs
            )
        ax.set_xticks(group_positions)
        ax.set_xticklabels(labels)

    elif orientation == 'horizontal':
        # horizontal bars: use ax.barh
        for i in range(n_legends):
            offsets = group_positions - group_width/2 + (i+0.5)*bar_width
            bars = ax.barh(
                    offsets,
                    data[i, :],
                    height=bar_width,
                    color=use_colors[i],
                    **kwargs
            )
        ax.set_yticks(group_positions)
        ax.set_yticklabels(labels)

    else:
        raise ValueError("orientation must be 'horizontal' or 'vertical'")

    return bars


def plot_gradient_bar(ax, heights, width=0.7, cmap='viridis'):
    x = np.arange(len(heights))
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    for xi, hi in zip(x, heights):
        ax.imshow(
            grad,
            extent=(xi - width/2, xi + width/2, 0, hi),
            origin='lower',
            aspect='auto',
            cmap=plt.get_cmap(cmap),
            norm=Normalize(0, 1),
            clip_on=True,
        )
        ax.add_patch(plt.Rectangle(
            (xi - width/2, 0), width, hi,
            fill=False, edgecolor='black', linewidth=0.5
        ))
    ax.set_xlim(-width, len(heights)-1 + width)
    ax.set_ylim(0, max(heights) * 1.05)