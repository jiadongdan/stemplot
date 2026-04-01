import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
def plot_radar(data, ax=None, **kwargs):
    """
    Plot a radar (spider) chart.

    Parameters
    ----------
    data : dict
        Keys are category labels, values are numeric scores.
        Example: {'Speed': 8, 'Power': 6, 'Accuracy': 9, 'Stamina': 7}
    ax : matplotlib.axes.Axes, optional
        Existing polar axes to draw on. If None, a new figure is created.
    **kwargs
        fill_alpha : float, default 0            Opacity of the filled polygon.
        color : str, default 'steelblue'
            Line and fill color.
        linewidth : float, default 2.0
            Width of the outline.
        linestyle : str, default '-'
            Style of the outline (e.g. '--', ':').
        marker : str, default 'o'
            Marker style at each vertex.
        markersize : float, default 6
            Size of the vertex markers.
        label : str, optional
            Legend label for this series.
        vmin : float, default 0
            Minimum value of the radial axis.
        vmax : float, default None
            Maximum value (inferred from data if None).
        axis_extend_ratio : float, default 1.1
            Ratio to extend the radial axis beyond vmax for visual padding.
        n_gridlines : int, default 5
            Number of concentric gridline rings.
        gridline_color : str, default 'gray'
            Color of the gridlines.
        gridline_alpha : float, default 0.4
            Opacity of the gridlines.
        gridline_linewidth : float, default 0.6
            Width of the gridlines.
        gridline_linestyle : str, default '--'
            Style of the gridlines.
        tick_color : str, default 'gray'
            Color of the tick labels.
        tick_linewidth : float, default 0.6
            Width of the tick labels lines.
        outer_frame : bool, default False
            Whether to show the outer frame circle.
        show_spines : bool, default False
            Whether to show the radial spine lines (the lines from center to edge).
        tick_fontsize : float, default 10
            Font size of the category labels.
        show_values : bool, default False
            Annotate each vertex with its numeric value.
        value_fontsize : float, default 9
            Font size of value annotations.

    Returns
    -------
    ax : matplotlib.axes.PolarAxes
        The axes the chart was drawn on.

    Examples
    --------
    >>> data = {'Speed': 8, 'Power': 6, 'Accuracy': 9, 'Stamina': 7, 'Agility': 5}
    >>> fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    >>> plot_radar(data, ax=ax, color='steelblue', label='Player A', show_values=True)
    >>> plt.legend(loc='upper right')
    >>> plt.show()
    """
    # ── Resolve kwargs ────────────────────────────────────────────────────────
    fill_alpha        = kwargs.get('fill_alpha',        0.25)
    color             = kwargs.get('color',             'steelblue')
    fill_area         = kwargs.get('fill_area',         True)
    fill_color        = kwargs.get('fill_color',        'gray')
    linewidth         = kwargs.get('linewidth',          2.0)
    linestyle         = kwargs.get('linestyle',          '-')
    marker            = kwargs.get('marker',             'o')
    markersize        = kwargs.get('markersize',          6)
    label             = kwargs.get('label',              None)
    vmin              = kwargs.get('vmin',                0)
    vmax              = kwargs.get('vmax',                None)
    axis_extend_ratio = kwargs.get('axis_extend_ratio', 1.1)
    n_gridlines       = kwargs.get('n_gridlines',         5)
    gridline_color    = kwargs.get('gridline_color',     'gray')
    gridline_alpha    = kwargs.get('gridline_alpha',      0.4)
    gridline_linewidth = kwargs.get('gridline_linewidth', 0.6)     # gridline linewidth
    gridline_linestyle = kwargs.get('gridline_linestyle', '-')     # gridline linestyle
    grid_fontsize     = kwargs.get('grid_fontsize',         9)
    tick_color        = kwargs.get('tick_color',         'black')  # tick color
    tick_linewidth    = kwargs.get('tick_linewidth',      0.8)     # tick linewidth
    outer_frame       = kwargs.get('outer_frame',       True)
    show_spines       = kwargs.get('show_spines',       False)
    tick_fontsize     = kwargs.get('tick_fontsize',      10)
    show_values       = kwargs.get('show_values',       False)
    value_fontsize    = kwargs.get('value_fontsize',      9)

    # ── Data preparation ──────────────────────────────────────────────────────
    categories = list(data.keys())
    values     = np.array(list(data.values()), dtype=float)
    N          = len(categories)

    if N < 3:
        raise ValueError("Radar chart requires at least 3 categories.")

    if vmax is None:
        vmax = float(np.ceil(values.max()))

    # Evenly-spaced angles; close the polygon by repeating the first point
    angles  = np.linspace(0, 2 * np.pi, N, endpoint=False)
    angles  = np.concatenate([angles, [angles[0]]])
    values  = np.concatenate([values, [values[0]]])

    # ── Axes setup ───────────────────────────────────────────────────────────
    if ax is None:
        fig, ax = plt.subplots(subplot_kw=dict(polar=True))

    ax.set_theta_offset(np.pi / 2)   # start at top
    ax.set_theta_direction(-1)        # clockwise

    max_axis_value = vmax * axis_extend_ratio
    ax.set_ylim(vmin, max_axis_value)

    grid_levels = np.linspace(vmin, vmax, n_gridlines + 1)[1:]

    if not outer_frame:
        grid_levels = grid_levels[:-1]

    if len(grid_levels) > 0:
        ax.set_yticks(grid_levels)
        ax.set_yticklabels(
            [f'{v:.4g}' for v in grid_levels],
            fontsize=grid_fontsize,
            color=tick_color
        )
        ax.yaxis.set_tick_params(labelcolor=tick_color, width=tick_linewidth)  # 设置刻度线宽
        ax.grid(color=gridline_color,
                linestyle=gridline_linestyle,
                linewidth=gridline_linewidth,
                alpha=gridline_alpha)
    else:
        ax.grid(color=gridline_color,
                linestyle=gridline_linestyle,
                linewidth=gridline_linewidth,
                alpha=gridline_alpha)

    # ── Remove spines (borders) ───────────────────────────────────────────────
    if not show_spines:
        ax.spines['polar'].set_visible(False)

    # ── Category labels ───────────────────────────────────────────────────────
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=tick_fontsize)

    # ── Plot line + fill ─────────────────────────────────────────────────────
    ax.plot(
        angles, values,
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        marker=marker,
        markersize=markersize,
        label=label,
        zorder=3
    )
    if fill_area:
        ax.fill(angles, values, color=fill_color, alpha=fill_alpha, zorder=2)

    # ── Optional value annotations ────────────────────────────────────────────
    if show_values:
        for angle, val in zip(angles[:-1], values[:-1]):
            extended_vmax = vmax * axis_extend_ratio
            x = (val / extended_vmax + 0.08) * np.cos(angle - np.pi / 2)
            y = (val / extended_vmax + 0.08) * np.sin(angle - np.pi / 2)
            ax.annotate(
                f'{val:.4g}',
                xy=(angle, val),
                fontsize=value_fontsize,
                ha='center', va='center',
                color=color
            )

    return ax