import numpy as np
from matplotlib.transforms import Bbox
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
from ._transform import  Transform

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# function related to  figure and axes size
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def get_size_inches(ax):
    fig_w, fig_h = ax.figure.get_size_inches()
    w, h = ax.get_position().bounds[2:]
    ax_w, ax_h = (fig_w * w, fig_h * h)
    return ax_w, ax_h

def get_ax_aspect(ax):
    w, h = get_size_inches(ax)
    return w / h

def get_fig_aspect(fig):
    fig_w, fig_h = fig.get_size_inches()
    return fig_w / fig_h


def ax_off(axes, keep_spine=True):
    # ax_off() is preferred, since ax.axis('off') disallows ax.set_xlabels() to display
    if not np.iterable(axes):
        axes = [axes, ]
    for ax in axes:
        # remove ticks
        ax.set_xticks([])
        ax.set_yticks([])
        # remove tick labels
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

        # set spine visibility
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_visible(keep_spine)


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Create new axes
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def make_ax(fig, x, y, w=0.1, hrel=1):
    ratio = get_fig_aspect(fig)
    h = w*hrel*ratio
    x1 = x - w/2.
    y1 = y - h/2.
    ax = fig.add_axes([x1, y1, w, h])
    return ax


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Translation of axes
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=


def shift_ax(ax, left=0, right=0, top=0, bottom=0):
    x0, y0, w, h = ax.get_position().bounds
    x = x0 + right - left
    y = y0 + top - bottom
    if ax._label == 'inset_axes':
        ip = InsetPosition(ax._axes, [x, y, w, h])
        ax.set_axes_locator(ip)
    else:
        ax.set_position([x, y, w, h])


def shift_axes(axes, left=0, right=0, bottom=0, top=0):
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        shift_ax(ax, left, right, bottom, top)

# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Resize of axes
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def ax_resize(ax, top=0, bottom=0, left=0, right=0):
    x, y, w, h = ax.get_position().bounds
    w_new = w + (left + right) * w
    h_new = h + (top + bottom) * h
    x_new = x - right * w
    y_new = y - bottom * h
    ax.set_position([x_new, y_new, w_new, h_new])


def ax_resize_h(ax, ratio=1, va='center'):
    x, y, w, h = ax.get_position().bounds
    aspect_ratio = get_fig_aspect(ax.figure)
    h_new = w*ratio*aspect_ratio
    if va == 'center':
        y_new = y + h/2 - h_new/2
    elif va == 'top':
        y_new = y + h - h_new
    elif va == 'bottom':
        y_new = y
    else:
        raise ValueError('Invalid values for va.')
    ax.set_position([x, y_new, w, h_new])


def ax_resize_h(ax, ratio=1):
    x, y, w, h = ax.get_position().bounds
    aspect_ratio = get_fig_aspect(ax.figure)
    h_new = w*ratio*aspect_ratio
    ax.set_position([x, y, w, h_new])

def _get_new_x(x, w_old, w_new, ha=None):
    if ha in [None, 'center']:
        x += (w_old - w_new) / 2
    elif ha == 'right':
        x += (w_old - w_new)
    elif ha == 'left':
        x += 0
    return x


def _get_new_y(y, h_old, h_new, va=None):
    if va in [None, 'center']:
        y += (h_old - h_new) / 2
    elif va == 'top':
        y += (h_old - h_new)
    elif va == 'bottom':
        y += 0
    return y


def ax_rescale(axes, scale=0.8, ha=None, va=None):
    axes = np.atleast_1d(axes).ravel()

    for ax in axes:
        ax_w, ax_h = get_size_inches(ax)
        fig_w, fig_h = ax.figure.get_size_inches()
        w_new, h_new = ax_w * scale / fig_w, ax_h * scale / fig_h

        # get new x and y
        x, y, w_old, h_old = ax.get_position().bounds
        x_new = _get_new_x(x, w_old, w_new, ha)
        y_new = _get_new_y(y, h_old, h_new, va)

        ax.set_position([x_new, y_new, w_new, h_new])


def auto_square(axes, ha=None, va=None):
    axes = np.atleast_1d(axes).ravel()

    for ax in axes:
        # get new width and height
        ax_w, ax_h = get_size_inches(ax)
        d = np.minimum(ax_w, ax_h)
        fig_w, fig_h = ax.figure.get_size_inches()
        w_new, h_new = d / fig_w, d / fig_h

        # get new x and y
        x, y, w_old, h_old = ax.get_position().bounds
        x_new = _get_new_x(x, w_old, w_new, ha)
        y_new = _get_new_y(y, h_old, h_new, va)

        ax.set_position([x_new, y_new, w_new, h_new])


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Merge and split
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def merge_axes(axes, remove=False):
    bboxes = [ax.get_position() for ax in axes.ravel()]
    bbox = Bbox.union(bboxes)
    ax_union = axes.ravel()[0].figure.add_axes(bbox.bounds)

    if remove:
        for ax_ in axes.ravel():
            ax_.remove()
    return ax_union


def axes_from_ax(ax, nrows, ncols, wspace=0.1, hspace=0.1,
                 width_ratios=None, height_ratios=None, remove=False, hide=True):
    fig = ax.figure
    left, bottom, right, top = ax.get_position().extents
    # use gridspec here
    gs = fig.add_gridspec(nrows, ncols, left=left, right=right, bottom=bottom, top=top,
                          wspace=wspace, hspace=hspace,
                          width_ratios=width_ratios, height_ratios=height_ratios)
    # convert gridspec to subplots
    axes = gs.subplots()
    if remove:
        ax.remove()
    else:
        if hide:
            ax_off(ax, keep_spine=False)
    return axes


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Inset axes
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
def make_inset_ax(ax, x=None, y=None, zoom=0.2, w=None, h=None, transform=None, loc=None):
    if transform is None:
        transform = ax.transAxes

    if w is None and h is None:
        ratio = get_ax_aspect(ax)
        if transform is ax.transAxes:
            w = zoom
            h = zoom * ratio
        elif transform is ax.transData:
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()
            d = (xmax - xmin) / 2 + (ymax - ymin) / 2
            w = zoom * d
            h = zoom * ratio * d

    if loc == 'lower right':
        x, y = 1-w/2, h/2
    elif loc == 'lower left':
        x, y = w/2, h/2
    elif loc == 'upper right':
        x, y = 1-w/2, 1-h/2
    elif loc == 'upper left':
        x, y = w/2, 1-h/2

    axins = ax.inset_axes([x - w / 2, y - h / 2, w, h], transform=transform)

    return axins

def make_local_view(ax, axin):
    # get axin data limits
    x, y, w, h = axin.get_position().bounds
    x1, y1 = Transform(axin._axes).transform([x, y], kind='fig2data')
    x2, y2 = Transform(axin._axes).transform([x+w, y+h], kind='fig2data')
    # set xlim and ylim
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Align axes
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def align_axes(ax1, ax2, ha=None, va=None):
    x1, y1, w1, h1 = ax1.get_position().bounds
    x2, y2, w2, h2 = ax2.get_position().bounds

    if ha == 'left':
        x2 = x1
    elif ha == 'right':
        x2 = x1 + w1 - w2
    elif ha == 'center':
        x2 = x1 + w1 / 2 - w2 / 2
    if va == 'top':
        y2 = y1 + h1 - h2
    elif va == 'bottom':
        y2 = y1
    elif va == 'center':
        y2 = y1 + h1 / 2 - h2 / 2
    ax2.set_position([x2, y2, w2, h2])