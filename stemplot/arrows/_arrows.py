import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.patches import FancyArrowPatch, Polygon
from matplotlib.patches import ConnectionPatch
from stemplot._axes import get_fig_aspect, merge_axes
from stemplot._style import simple_arrow, double_arrow
from stemplot._transform import Transform

def ax_add_arrow(ax, start, end, **kwargs):
    # default
    if 'arrowstyle' not in kwargs:
        kwargs['arrowstyle'] = 'simple'
    if 'mutation_scale' not in kwargs:
        kwargs['mutation_scale'] = 20
    if 'color' not in kwargs:
        kwargs['facecolor'] = '#413c39'
        kwargs['edgecolor'] = 'none'

    arrow = FancyArrowPatch(start, end, **kwargs)
    ax.add_patch(arrow)
    return arrow


def fig_add_arrow(fig, start, end, **kwargs):
    # add arrow by figure fraction coordinates
    # default
    if 'arrowstyle' not in kwargs:
        kwargs['arrowstyle'] = simple_arrow
    if 'mutation_scale' not in kwargs:
        kwargs['mutation_scale'] = 10
    if 'color' not in kwargs:
        kwargs['facecolor'] = '#413c39'
        kwargs['edgecolor'] = 'none'

    # get arrow length in inches
    w, h = fig.get_size_inches()
    dx = (start[0] - end[0]) * w
    dy = (start[1] - end[1]) * h
    L = np.sqrt(dx ** 2 + dy ** 2)  # in inches
    if 'shrinkA' in kwargs:
        # by default, unit of shrinkA is point
        shrinkA = kwargs['shrinkA']
        kwargs['shrinkA'] = shrinkA * 72 * L
    if 'shrinkB' in kwargs:
        shrinkB = kwargs['shrinkB']
        kwargs['shrinkB'] = shrinkB * 72 * L

    arrow = FancyArrowPatch(start, end, **kwargs)
    fig.add_artist(arrow)
    return arrow


def ax_get_position(ax, loc='lower left', s=None, transform=None):
    def _get_x(x, w, s=0):
        if s <= 1:
            return x
        elif np.logical_and(s > 1, s < 2):
            return w * (s - 1) + x
        elif np.logical_and(s >= 2, s < 3):
            return x + w
        else:
            return -w * (s - 4) + x

    def _get_y(y, h, s=0):
        if s <= 1:
            return h * (s) + y
        elif np.logical_and(s > 1, s < 2):
            return y + h
        elif np.logical_and(s >= 2, s < 3):
            return -h * (s - 3) + y
        else:
            return y

    loc_dict = {'lower left': 0, 'lower right': 3,
                'upper left': 1, 'upper right': 2,
                'top': 1.5, 'bottom': 3.5,
                'left': 0.5, 'right': 2.5,
                'center': (1.5, 0.5)}
    if s is None:
        s = loc_dict[loc]
    s = np.atleast_1d(s)
    if len(s) == 1:
        s1, s2 = s[0], s[0]
    else:
        s1, s2 = s[0], s[1]

    x, y, w, h = ax.get_position().bounds
    x1 = _get_x(x, w, s1)
    y1 = _get_y(y, h, s2)

    if transform in ['display', 'pixel']:
        x1, y1 = Transform(ax).transform((x1, y1), kind='fig2pixel')
        x2, y2 = Transform(ax).transform((x1+w, y1+h), kind='fig2pixel')
        w = abs(x1 - x2)
        h = abs(y1 - y2)
    elif transform in ['inch', 'inches']:
        x1, y1 = Transform(ax).transform((x1, y1), kind='fig2inch')
        x2, y2 = Transform(ax).transform((x1 + w, y1 + h), kind='fig2inch')
        w = abs(x1 - x2)
        h = abs(y1 - y2)

    return (x1, y1, w, h)


def estimate_loc1_loc2(ax1, ax2):
    if np.iterable(ax1):
        x1, y1 = np.array([ax_get_position(ax, loc='center', transform='display')[0:2] for ax in ax1]).mean(axis=0)
    else:
        x1, y1 = ax_get_position(ax1, loc='center', transform='display')[0:2]

    if np.iterable(ax2):
        x2, y2 = np.array([ax_get_position(ax, loc='center', transform='display')[0:2] for ax in ax2]).mean(axis=0)
    else:
        x2, y2 = ax_get_position(ax2, loc='center', transform='display')[0:2]

    dx = np.abs(x1 - x2)
    dy = np.abs(y1 - y2)

    if dx > dy:
        if x1 > x2:
            loc1, loc2 = 'left', 'right'
        else:
            loc1, loc2 = 'right', 'left'
    else:
        if y1 > y2:
            loc1, loc2 = 'bottom', 'top'
        else:
            loc1, loc2 = 'top', 'bottom'
    return (loc1, loc2)


def _estimate_loc1_loc2(ax1, ax2):
    x1, y1, w1, h1 = ax_get_position(ax1, loc='center', transform='display')
    x2, y2, w2, h2 = ax_get_position(ax2, loc='center', transform='display')
    dx = np.abs(x1 - x2)
    dy = np.abs(y1 - y2)
    if dx > dy:
        if x1 > x2:
            loc1, loc2 = 'left', 'right'
        else:
            loc1, loc2 = 'right', 'left'
    else:
        if y1 > y2:
            loc1, loc2 = 'bottom', 'top'
        else:
            loc1, loc2 = 'top', 'bottom'
    return (loc1, loc2)

def _estimate_mode(loc1):
    if loc1 in ['top', 'bottom']:
        mode = 'v'
    elif loc1 in ['left', 'right']:
        mode = 'h'
    else:
        mode = None
    return mode


def connect_by_arrow(ax1, ax2, loc1=None, loc2=None, mode=None, **kwargs):
    if loc1 is None and loc2 is None:
        loc1, loc2 = _estimate_loc1_loc2(ax1, ax2)

    if mode is None:
        mode = _estimate_mode(loc1)

    if mode is None:
        x1, y1 = ax_get_position(ax1, loc=loc1)[0:2]
        x2, y2 = ax_get_position(ax2, loc=loc2)[0:2]
    elif mode == 'h':
        x1, y1 = ax_get_position(ax1, loc=loc1)[0:2]
        x2, y2 = ax_get_position(ax2, loc=loc2)[0:2]
        y2 = y1
    elif mode == 'v':
        x1, y1 = ax_get_position(ax1, loc=loc1)[0:2]
        x2, y2 = ax_get_position(ax2, loc=loc2)[0:2]
        x2 = x1

    arrow = fig_add_arrow(ax1.figure, (x1, y1), (x2, y2), **kwargs)
    return arrow


def align_arrows(arrow1, arrow2, mode=None):

    (x1, y1), (x2, y2) = arrow1._posA_posB
    (x3, y3), (x4, y4) = arrow2._posA_posB

    dx = np.abs(x1 + x2 - (x3 + x4))
    dy = np.abs(y1 + y2 - (y3 + y4))

    if mode is None:
        if dx > dy:
            mode = 'v'
        else:
            mode = 'h'

    if mode == 'h':
        posA = ((x1 + x2) / 2, y3)
        posB = ((x1 + x2) / 2, y4)
    elif mode == 'v':
        posA = (x3, (y1 + y2) / 2)
        posB = (x4, (y1 + y2) / 2)
    arrow2.set_positions(posA, posB)



# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Connected by branches
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def get_path_from_pts(start, end, mode='h', r=0.1, lamda=2, aspect_ratio=1.0, **kwargs):
    start = np.asarray(start)
    end = np.asarray(end)
    mid = (lamda * start + end) / (lamda + 1)

    xsign = np.sign(end[0] - start[0])
    ysign = np.sign(end[1] - start[1])

    dx = np.abs(start[0] - end[0])
    dy = np.abs(start[1] - end[1])

    print(dx, dy)
    L = np.min([dx * aspect_ratio, dy])
    Lx = L / aspect_ratio
    Ly = L

    if mode == 'h':
        p1 = np.array((mid[0], start[1]))
        p2 = np.array((mid[0], end[1]))
        # two control points from p1
        p1s = p1 + (-xsign * Lx * r, 0)
        p1e = p1 + (0, ysign * Ly * r)
        # two control points from p2
        p2s = p2 + (0, -ysign * Ly * r)
        p2e = p2 + (xsign * Lx * r, 0)
    elif mode == 'v':
        p1 = np.array((start[0], mid[1]))
        p2 = np.array((end[0], mid[1]))
        # two control points from p1
        p1s = p1 + (0, -ysign * Ly * r)
        p1e = p1 + (xsign * Lx * r, 0)
        # two control points from p2
        p2s = p2 + (-xsign * Lx * r, 0)
        p2e = p2 + (0, ysign * Ly * r)

    points = np.vstack([start, p1s, p1, p1e, p2s, p2, p2e, end, p2e, p2, p2s, p1e, p1, p1s, start])
    codes = [1, 2, 3, 3, 2, 3, 3, 2, 2, 3, 3, 2, 3, 3, 79]

    pp = PathPatch(Path(points, codes), **kwargs)

    return pp


def connect_by_branches(ax, axes, loc1=None, loc2=None, mode='h', r=0.15, lamda=2, **kwargs):

    if loc1 is None and loc2 is None:
        loc1, loc2 = estimate_loc1_loc2(ax, axes)

    fig = ax.figure
    ratio = get_fig_aspect(fig)
    p1 = ax_get_position(ax, loc=loc1)[0:2]
    for ax_ in axes:
        p2 = ax_get_position(ax_, loc=loc2)[0:2]
        pp = get_path_from_pts(p1, p2, mode=mode, aspect_ratio=ratio, r=r, lamda=lamda, **kwargs)
        fig.add_artist(pp)


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Connected by line
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# Connected by gradient image
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def gradient_image(ax, direction=1, cmap_range=(0, 1), **kwargs):
    fig = ax.figure
    aspect_ratio = get_fig_aspect(fig)
    x0, y0, W, H = ax.get_position().bounds
    W = W * aspect_ratio
    extent = [0, W / H, 0, 1]

    phi = direction * np.pi / 2
    v = np.array([np.cos(phi), np.sin(phi)])
    X = np.array([[v @ [1, 0], v @ [1, 1]],
                  [v @ [0, 0], v @ [0, 1]]])
    a, b = cmap_range
    X = a + (b - a) / X.max() * X
    im = ax.imshow(X, extent=extent, interpolation='bicubic',
                   vmin=0, vmax=1, **kwargs)
    return im


def plot_gradient_patch(ax, pts, cmap='gray', direction=1):
    im = gradient_image(ax, direction=direction, cmap_range=(0, 1), alpha=0.5, cmap=cmap, zorder=-2)

    patch = Polygon(pts, transform=ax.transAxes, )
    im.set_clip_path(patch)
    ax.axis('off')


def connect_by_gradient(ax1, ax2, loc1=None, loc2=None, cmap='gray', direction=0):
    def _expand_loc(loc1):
        if loc1 in ['left', 'right']:
            locs1 = ['lower ' + loc1, 'upper ' + loc1]
        elif loc1 == 'top':
            locs1 = ['upper left', 'upper right']
        else:
            locs1 = ['lower left', 'lower right']
        return locs1

    def _sort_by_angle(pts):
        pts_ = pts - pts.mean(axis=0)
        angles = np.arctan2(pts_[:, 1], pts_[:, 0])
        return pts[np.argsort(angles)]

    if loc1 is None and loc2 is None:
        loc1, loc2 = _estimate_loc1_loc2(ax1, ax2)

    locs1 = _expand_loc(loc1)
    locs2 = _expand_loc(loc2)

    x1, y1 = ax_get_position(ax1, loc=locs1[0])[0:2]
    x2, y2 = ax_get_position(ax1, loc=locs1[1])[0:2]
    x3, y3 = ax_get_position(ax2, loc=locs2[0])[0:2]
    x4, y4 = ax_get_position(ax2, loc=locs2[1])[0:2]

    xmin = np.min([x1, x2, x3, x4])
    ymin = np.min([y1, y2, y3, y4])
    w = np.ptp([x1, x2, x3, x4])
    h = np.ptp([y1, y2, y3, y4])

    ax_ = ax1.figure.add_axes([xmin, ymin, w, h])
    ax_.set_fc([0, 0, 0, 0])

    # plot the semi-transparent patch
    pts = np.array([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    pts = _sort_by_angle(pts)
    # convert fig fraction to ax data
    pts_ = Transform(ax_).transform(pts, kind='fig2data')

    plot_gradient_patch(ax_, pts_, cmap=cmap, direction=direction)
    return ax_


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# connect by gradient arrow
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def fig_add_gradient_arrow(fig):
    pass


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# connect by angle
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
def connect_by_angle(fig, start, end, coords='figure fraction', coordsB=None, axesA=None, axesB=None, angleA=0, angleB=10, rad=5, **kwargs):
    connectionstyle = 'angle, angleA={}, angleB={}, rad={}'.format(angleA, angleB, rad)
    cp = ConnectionPatch(start, end, coords, connectionstyle=connectionstyle, **kwargs)
    fig.add_artist(cp)