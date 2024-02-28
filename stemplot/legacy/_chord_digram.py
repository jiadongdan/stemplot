from collections.abc import Sequence
import matplotlib.patches as patches
from matplotlib.colors import ColorConverter, LinearSegmentedColormap
from matplotlib.path import Path
import scipy.sparse as ssp
from scipy.ndimage import gaussian_filter
import numpy as np

# https://codeberg.org/tfardet/mpl_chord_diagram

def _get_normed_line(mat, i, x, start, end, is_sparse):
    if is_sparse:
        row = mat.getrow(i).todense().A1
        return (row / x[i]) * (end - start)
    return (mat[i, :] / x[i]) * (end - start)
def dist(points):
    x1, y1 = points[0]
    x2, y2 = points[1]
    return np.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
def polar2xy(r, theta):
    return np.array([r*np.cos(theta), r*np.sin(theta)])


def linear_gradient(cstart, cend, n=10):
    '''
    Return a gradient list of `n` colors going from `cstart` to `cend`.
    '''
    s = np.array(ColorConverter.to_rgb(cstart))
    f = np.array(ColorConverter.to_rgb(cend))
    rgb_list = [s + (t / (n - 1))*(f - s) for t in range(n)]
    return rgb_list
def gradient(start, end, min_angle, color1, color2, meshgrid, mask, ax,
             alpha):
    '''
    Create a linear gradient from `start` to `end`, which is translationally
    invarient in the orthogonal direction.
    The gradient is then cliped by the mask.
    '''
    xs, ys = start
    xe, ye = end
    X, Y = meshgrid
    # get the distance to each point
    d2start = (X - xs)*(X - xs) + (Y - ys)*(Y - ys)
    d2end   = (X - xe)*(X - xe) + (Y - ye)*(Y - ye)
    dmax = (xs - xe)*(xs - xe) + (ys - ye)*(ys - ye)
    # blur
    smin = 0.015*len(X)
    smax = max(smin, 0.1*len(X)*min(min_angle/120, 1))
    sigma = np.clip(dmax*len(X), smin, smax)
    Z = gaussian_filter((d2end < d2start).astype(float), sigma=sigma)
    # generate the colormap
    n_bin = 100
    color_list = linear_gradient(color1, color2, n_bin)
    cmap = LinearSegmentedColormap.from_list("gradient", color_list, N=n_bin)
    im = ax.imshow(Z, interpolation='bilinear', cmap=cmap,
                   origin='lower', extent=[-1, 1, -1, 1], alpha=alpha)
    im.set_clip_path(mask)



LW = 0.3
def chord_diagram(mat, names=None, order=None, width=0.1, pad=2., gap=0.03,
                  chordwidth=0.7, ax=None, colors=None, cmap=None, alpha=0.7,
                  use_gradient=False, chord_colors=None, show=False, **kwargs):
    """
    Plot a chord diagram.
    Parameters
    ----------
    mat : square matrix
        Flux data, mat[i, j] is the flux from i to j
    names : list of str, optional (default: no names)
        Names of the nodes that will be displayed (must be ordered as the
        matrix entries).
    order : list, optional (default: order of the matrix entries)
        Order in which the arcs should be placed around the trigonometric
        circle.
    width : float, optional (default: 0.1)
        Width/thickness of the ideogram arc.
    pad : float, optional (default: 2)
        Distance between two neighboring ideogram arcs. Unit: degree.
    gap : float, optional (default: 0)
        Distance between the arc and the beginning of the cord.
    chordwidth : float, optional (default: 0.7)
        Position of the control points for the chords, controlling their shape.
    ax : matplotlib axis, optional (default: new axis)
        Matplotlib axis where the plot should be drawn.
    colors : list, optional (default: from `cmap`)
        List of user defined colors or floats.
    cmap : str or colormap object (default: viridis)
        Colormap that will be used to color the arcs and chords by default.
        See `chord_colors` to use different colors for chords.
    alpha : float in [0, 1], optional (default: 0.7)
        Opacity of the chord diagram.
    use_gradient : bool, optional (default: False)
        Whether a gradient should be use so that chord extremities have the
        same color as the arc they belong to.
    chord_colors : str, or list of colors, optional (default: None)
        Specify color(s) to fill the chords differently from the arcs.
        When the keyword is not used, chord colors default to the colomap given
        by `colors`.
        Possible values for `chord_colors` are:
        * a single color (do not use an RGB tuple, use hex format instead),
          e.g. "red" or "#ff0000"; all chords will have this color
        * a list of colors, e.g. ``["red", "green", "blue"]``, one per node
          (in this case, RGB tuples are accepted as entries to the list).
          Each chord will get its color from its associated source node, or
          from both nodes if `use_gradient` is True.
    show : bool, optional (default: False)
        Whether the plot should be displayed immediately via an automatic call
        to `plt.show()`.
    kwargs : keyword arguments
        Available kwargs are:
        ================  ==================  ===============================
              Name               Type           Purpose and possible values
        ================  ==================  ===============================
        fontcolor         str or list         Color of the names
        fontsize          int                 Size of the font for names
        rotate_names      (list of) bool(s)   Rotate names by 90°
        sort              str                 Either "size" or "distance"
        zero_entry_size   float               Size of zero-weight reciprocal
        ================  ==================  ===============================
    """
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots()
    # copy matrix and set a minimal value for visibility of zero fluxes
    is_sparse = ssp.issparse(mat)
    if is_sparse:
        mat = mat.tocsr(copy=True)
    else:
        mat = np.array(mat, copy=True)
    # mat[i, j]:  i -> j
    num_nodes = mat.shape[0]
    # set entry size for zero entries that have a nonzero reciprocal
    min_deg  = kwargs.get("zero_entry_size", 0.5)
    min_deg *= mat.sum() / (360 - num_nodes*pad)
    if is_sparse:
        nnz = mat.nonzero()
        for i, j in zip(*nnz):
            if mat[j, i] == 0:
                mat[j, i] = min_deg
    else:
        zeros = np.argwhere(mat == 0)
        for (i, j) in zeros:
            if mat[j, i] != 0:
                mat[i, j] = min_deg
    # check name rotations
    rotate_names = kwargs.get("rotate_names", False)
    if isinstance(rotate_names, Sequence):
        assert len(rotate_names) == num_nodes, \
            "Wrong number of entries in 'rotate_names'."
    else:
        rotate_names = [rotate_names]*num_nodes
    # check order
    if order is not None:
        mat = mat[order][:, order]
        rotate_names = [rotate_names[i] for i in order]
        if names is not None:
            names = [names[i] for i in order]
        if colors is not None:
            colors = [colors[i] for i in order]
    # sum over rows
    x = mat.sum(axis=1).A1 if is_sparse else mat.sum(axis=1)
    # configure colors
    if colors is None:
        colors = np.linspace(0, 1, num_nodes)
    fontcolor = kwargs.get("fontcolor", "k")
    if isinstance(fontcolor, str):
        fontcolor = [fontcolor]*num_nodes
    else:
        assert len(fontcolor) == num_nodes, \
            "One fontcolor per node is required."
    if cmap is None:
        cmap = "viridis"
    if isinstance(colors, (list, tuple, np.ndarray)):
        assert len(colors) == num_nodes, "One color per node is required."
        # check color type
        first_color = colors[0]
        if isinstance(first_color, (int, float, np.integer)):
            cm = plt.get_cmap(cmap)
            colors = cm(colors)[:, :3]
        else:
            colors = [ColorConverter.to_rgb(c) for c in colors]
    else:
        raise ValueError("`colors` should be a list.")
    if chord_colors is None:
       chord_colors = colors
    else:
        try:
            chord_colors = [ColorConverter.to_rgb(chord_colors)] * num_nodes
        except ValueError:
            assert len(chord_colors) == num_nodes, \
                "If `chord_colors` is a list of colors, it should include " \
                "one color per node (here {} colors).".format(num_nodes)
    # find position for each start and end
    y = x / np.sum(x).astype(float) * (360 - pad*len(x))
    pos = {}
    arc = []
    nodePos = []
    rotation = []
    start = 0
    # compute all values and optionally apply sort
    for i in range(num_nodes):
        end = start + y[i]
        arc.append((start, end))
        angle = 0.5*(start+end)
        if -30 <= angle <= 180:
            angle -= 90
            rotation.append(False)
        else:
            angle -= 270
            rotation.append(True)
        nodePos.append(
            tuple(polar2xy(1.05, 0.5*(start + end)*np.pi/180.)) + (angle,))
        z = _get_normed_line(mat, i, x, start, end, is_sparse)
        # sort chords
        ids = None
        if kwargs.get("sort", "size") == "size":
            ids = np.argsort(z)
        elif kwargs["sort"] == "distance":
            remainder = 0 if num_nodes % 2 else -1
            ids  = list(range(i - int(0.5*num_nodes), i))[::-1]
            ids += [i]
            ids += list(range(i + int(0.5*num_nodes) + remainder, i, -1))
            # put them back into [0, num_nodes[
            ids = np.array(ids)
            ids[ids < 0] += num_nodes
            ids[ids >= num_nodes] -= num_nodes
        else:
            raise ValueError("Invalid `sort`: '{}'".format(kwargs["sort"]))
        z0 = start
        for j in ids:
            pos[(i, j)] = (z0, z0 + z[j])
            z0 += z[j]
        start = end + pad
    # plot
    for i in range(len(x)):
        color = colors[i]
        # plot the arcs
        start, end = arc[i]
        ideogram_arc(start=start, end=end, radius=1.0, color=color,
                     width=width, alpha=alpha, ax=ax)
        start, end = pos[(i, i)]
        chord_color = chord_colors[i]
        # plot self-chords
        if mat[i, i] > 0:
            self_chord_arc(start, end, radius=1 - width - gap,
                           chordwidth=0.7*chordwidth, color=chord_color,
                           alpha=alpha, ax=ax)
        # plot all other chords
        for j in range(i):
            cend = chord_colors[j]
            start1, end1 = pos[(i, j)]
            start2, end2 = pos[(j, i)]
            if mat[i, j] > 0 or mat[j, i] > 0:
                chord_arc(
                    start1, end1, start2, end2, radius=1 - width - gap,
                    chordwidth=chordwidth, color=chord_color, cend=cend,
                    alpha=alpha, ax=ax, use_gradient=use_gradient)
    # add names if necessary
    if names is not None:
        assert len(names) == num_nodes, "One name per node is required."
        prop = {
            "fontsize": kwargs.get("fontsize", 16*0.8),
            "ha": "center",
            "va": "center",
            "rotation_mode": "anchor"
        }
        for i, (pos, name, r) in enumerate(zip(nodePos, names, rotation)):
            rotate = rotate_names[i]
            pp = prop.copy()
            pp["color"] = fontcolor[i]
            if rotate:
                angle  = np.average(arc[i])
                rotate = 90
                if 90 < angle < 180 or 270 < angle:
                    rotate = -90
                if 90 < angle < 270:
                    pp["ha"] = "right"
                else:
                    pp["ha"] = "left"
            elif r:
                pp["va"] = "top"
            else:
                pp["va"] = "bottom"
            ax.text(pos[0], pos[1], name, rotation=pos[2] + rotate, **pp)
    # configure axis
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect(1)
    ax.axis('off')
    if show:
        plt.show()
    return nodePos
# ------------ #
# Subfunctions #
# ------------ #
def initial_path(start, end, radius, width, factor=4/3):
    ''' First 16 vertices and 15 instructions are the same for everyone '''
    if start > end:
        start, end = end, start
    start *= np.pi/180.
    end   *= np.pi/180.
    # optimal distance to the control points
    # https://stackoverflow.com/questions/1734745/
    # how-to-create-circle-with-b%C3%A9zier-curves
    # use 16-vertex curves (4 quadratic Beziers which accounts for worst case
    # scenario of 360 degrees)
    inner = radius*(1-width)
    opt   = factor * np.tan((end-start)/ 16.) * radius
    inter1 = start*(3./4.)+end*(1./4.)
    inter2 = start*(2./4.)+end*(2./4.)
    inter3 = start*(1./4.)+end*(3./4.)
    verts = [
        polar2xy(radius, start),
        polar2xy(radius, start) + polar2xy(opt, start+0.5*np.pi),
        polar2xy(radius, inter1) + polar2xy(opt, inter1-0.5*np.pi),
        polar2xy(radius, inter1),
        polar2xy(radius, inter1),
        polar2xy(radius, inter1) + polar2xy(opt, inter1+0.5*np.pi),
        polar2xy(radius, inter2) + polar2xy(opt, inter2-0.5*np.pi),
        polar2xy(radius, inter2),
        polar2xy(radius, inter2),
        polar2xy(radius, inter2) + polar2xy(opt, inter2+0.5*np.pi),
        polar2xy(radius, inter3) + polar2xy(opt, inter3-0.5*np.pi),
        polar2xy(radius, inter3),
        polar2xy(radius, inter3),
        polar2xy(radius, inter3) + polar2xy(opt, inter3+0.5*np.pi),
        polar2xy(radius, end) + polar2xy(opt, end-0.5*np.pi),
        polar2xy(radius, end)
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]
    return start, end, verts, codes
def ideogram_arc(start, end, radius=1., width=0.2, color="r", alpha=0.7,
                 ax=None):
    '''
    Draw an arc symbolizing a region of the chord diagram.
    Parameters
    ----------
    start : float (degree in 0, 360)
        Starting degree.
    end : float (degree in 0, 360)
        Final degree.
    radius : float, optional (default: 1)
        External radius of the arc.
    width : float, optional (default: 0.2)
        Width of the arc.
    ax : matplotlib axis, optional (default: not plotted)
        Axis on which the arc should be plotted.
    color : valid matplotlib color, optional (default: "r")
        Color of the arc.
    Returns
    -------
    verts, codes : lists
        Vertices and path instructions to draw the shape.
    '''
    start, end, verts, codes = initial_path(start, end, radius, width)
    opt    = 4./3. * np.tan((end-start)/ 16.) * radius
    inner  = radius*(1-width)
    inter1 = start*(3./4.) + end*(1./4.)
    inter2 = start*(2./4.) + end*(2./4.)
    inter3 = start*(1./4.) + end*(3./4.)
    verts += [
        polar2xy(inner, end),
        polar2xy(inner, end) + polar2xy(opt*(1-width), end-0.5*np.pi),
        polar2xy(inner, inter3) + polar2xy(opt*(1-width), inter3+0.5*np.pi),
        polar2xy(inner, inter3),
        polar2xy(inner, inter3),
        polar2xy(inner, inter3) + polar2xy(opt*(1-width), inter3-0.5*np.pi),
        polar2xy(inner, inter2) + polar2xy(opt*(1-width), inter2+0.5*np.pi),
        polar2xy(inner, inter2),
        polar2xy(inner, inter2),
        polar2xy(inner, inter2) + polar2xy(opt*(1-width), inter2-0.5*np.pi),
        polar2xy(inner, inter1) + polar2xy(opt*(1-width), inter1+0.5*np.pi),
        polar2xy(inner, inter1),
        polar2xy(inner, inter1),
        polar2xy(inner, inter1) + polar2xy(opt*(1-width), inter1-0.5*np.pi),
        polar2xy(inner, start) + polar2xy(opt*(1-width), start+0.5*np.pi),
        polar2xy(inner, start),
        polar2xy(radius, start),
    ]
    codes += [
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CLOSEPOLY,
    ]
    if ax is not None:
        path  = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color, alpha=alpha,
                                  edgecolor=color, lw=LW)
        ax.add_patch(patch)
    return verts, codes
def chord_arc(start1, end1, start2, end2, radius=1.0, pad=2, chordwidth=0.7,
              ax=None, color="r", cend="r", alpha=0.7, use_gradient=False):
    '''
    Draw a chord between two regions (arcs) of the chord diagram.
    Parameters
    ----------
    start1 : float (degree in 0, 360)
        Starting degree.
    end1 : float (degree in 0, 360)
        Final degree.
    start2 : float (degree in 0, 360)
        Starting degree.
    end2 : float (degree in 0, 360)
        Final degree.
    radius : float, optional (default: 1)
        External radius of the arc.
    chordwidth : float, optional (default: 0.2)
        Width of the chord.
    ax : matplotlib axis, optional (default: not plotted)
        Axis on which the chord should be plotted.
    color : valid matplotlib color, optional (default: "r")
        Color of the chord or of its beginning if `use_gradient` is True.
    cend : valid matplotlib color, optional (default: "r")
        Color of the end of the chord if `use_gradient` is True.
    alpha : float, optional (default: 0.7)
        Opacity of the chord.
    use_gradient : bool, optional (default: False)
        Whether a gradient should be use so that chord extremities have the
        same color as the arc they belong to.
    Returns
    -------
    verts, codes : lists
        Vertices and path instructions to draw the shape.
    '''
    chordwidth2 = chordwidth
    dtheta1 = min((start1 - end2) % 360, (end2 - start1) % 360)
    dtheta2 = min((end1 - start2) % 360, (start2 - end1) % 360)
    start1, end1, verts, codes = initial_path(start1, end1, radius, chordwidth)
    start2, end2, verts2, _ = initial_path(start2, end2, radius, chordwidth)
    chordwidth2 *= np.clip(0.4 + (dtheta1 - 2*pad) / (15*pad), 0.2, 1)
    chordwidth *= np.clip(0.4 + (dtheta2 - 2*pad) / (15*pad), 0.2, 1)
    rchord  = radius * (1-chordwidth)
    rchord2 = radius * (1-chordwidth2)
    verts += [polar2xy(rchord, end1), polar2xy(rchord, start2)] + verts2
    verts += [
        polar2xy(rchord2, end2),
        polar2xy(rchord2, start1),
        polar2xy(radius, start1),
    ]
    codes += [
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]
    if ax is not None:
        path = Path(verts, codes)
        if use_gradient:
            # find the start and end points of the gradient
            points, min_angle = None, None
            if dtheta1 < dtheta2:
                points = [
                    polar2xy(radius, start1),
                    polar2xy(radius, end2),
                ]
                min_angle = dtheta1
            else:
                points = [
                    polar2xy(radius, end1),
                    polar2xy(radius, start2),
                ]
                min_angle = dtheta1
            # make the patch
            patch = patches.PathPatch(path, facecolor="none",
                                      edgecolor="none", lw=LW)
            ax.add_patch(patch)  # this is required to clip the gradient
            # make the grid
            x = y = np.linspace(-1, 1, 100)
            meshgrid = np.meshgrid(x, y)
            gradient(points[0], points[1], min_angle, color, cend, meshgrid,
                     patch, ax, alpha)
        else:
            patch = patches.PathPatch(path, facecolor=color, alpha=alpha,
                                      edgecolor=color, lw=LW)
            idx = 16
            ax.add_patch(patch)
    return verts, codes
def self_chord_arc(start, end, radius=1.0, chordwidth=0.7, ax=None,
                   color=(1,0,0), alpha=0.7):
    start, end, verts, codes = initial_path(start, end, radius, chordwidth)
    rchord = radius * (1 - chordwidth)
    verts += [
        polar2xy(rchord, end),
        polar2xy(rchord, start),
        polar2xy(radius, start),
    ]
    codes += [
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]
    if ax is not None:
        path  = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color, alpha=alpha,
                                  edgecolor=color, lw=LW)
        ax.add_patch(patch)
    return verts, codes