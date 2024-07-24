from matplotlib.patches import FancyBboxPatch
from stemplot.layout._utils import get_fig_aspect,  get_ax_aspect


def ax_add_fancybox(ax, p1, p2, pad=0.03, transform='data', **kwargs):
    if 'fc' not in kwargs:
        kwargs['fc'] = 'none'
    if 'ls' not in kwargs:
        kwargs['ls'] = '--'

    x1, y1 = p1
    x2, y2 = p2
    w = abs(x1 - x2)
    h = abs(y1 - y2)
    x0 = min(x1, x2)
    y0 = min(y1, y2)
    aspect_ratio = get_ax_aspect(ax)
    boxstyle = "round, pad={}, rounding_size={}".format(pad, pad)
    if transform == 'data':
        fancybox = FancyBboxPatch((x0, y0), w, h, boxstyle=boxstyle,
                                  **kwargs)
    else:
        fancybox = FancyBboxPatch((x0, y0), w, h, boxstyle=boxstyle, mutation_aspect=aspect_ratio,
                                  transform=ax.transAxes,
                                  **kwargs)
    ax.add_patch(fancybox)


def fig_add_fancybox(fig, p1, p2, pad=0.03, **kwargs):
    if 'fc' not in kwargs:
        kwargs['fc'] = 'none'
    if 'ls' not in kwargs:
        kwargs['ls'] = '--'

    x1, y1 = p1
    x2, y2 = p2
    w = abs(x1 - x2)
    h = abs(y1 - y2)
    x0 = min(x1, x2)
    y0 = min(y1, y2)

    aspect_ratio = get_fig_aspect(fig)
    boxstyle = "round, pad={}, rounding_size={}".format(pad, pad)
    fancybox = FancyBboxPatch((x0, y0), w, h, boxstyle=boxstyle, mutation_aspect=aspect_ratio,
                              transform=fig.transFigure, **kwargs)
    fig.add_artist(fancybox)


def ax2fancybox(ax, pad=0.03, **kwargs):
    fig = ax.figure
    aspect_ratio = get_fig_aspect(fig)
    x1, y1, x2, y2 = ax.get_position().extents
    p1 = (x1+pad, y1+pad * aspect_ratio)
    p2 = (x2-pad, y2-pad * aspect_ratio)
    fig_add_fancybox(fig, p1, p2, pad=pad, **kwargs)
    #ax.axis('off')