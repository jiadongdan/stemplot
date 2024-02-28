import numpy as np
from ._axes import get_fig_aspect

def h_axes(fig, n=2, top=0.95, bottom=None, h=1, left=1 / 15, right=1 / 30, wspace=0.25, ratios=None):
    # process ratios
    if ratios is None:
        ratios = np.ones(n)
    elif np.isscalar(ratios):
        ratios = np.array([ratios] * n)
    elif np.iterable(ratios):
        ratios = np.array(ratios)
    # make sure n = len(ratios)
    n = len(ratios)

    aspect_ratio = get_fig_aspect(fig)

    # only to get lefts and rights
    gs_ = fig.add_gridspec(nrows=1, ncols=n, left=left, right=1 - right, bottom=0.1, top=0.2, wspace=wspace,
                           width_ratios=ratios)
    b, t, lefts, rights = gs_.get_grid_positions(fig)

    widths = rights - lefts

    # h is set relative to the width of first (leading) axis
    h = widths[0]*h

    if bottom is None:
        bottom = top - h * aspect_ratio
    gs = fig.add_gridspec(nrows=1, ncols=n, left=left, right=1 - right, bottom=bottom, top=bottom + h * aspect_ratio,
                          wspace=wspace,
                          width_ratios=ratios)
    # https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.gridspec.GridSpecBase.html#matplotlib.gridspec.GridSpecBase.subplots
    # axes = [fig.add_subplot(gs[0, col]) for col in range(n)]
    axes = gs.subplots()
    return axes

def get_top_from_axes(axes, hspace=0.25):
    y = np.array([ax.get_position().bounds[1] for ax in axes]).mean()
    h = np.array([ax.get_position().bounds[3] for ax in axes]).mean()
    return y - h*hspace