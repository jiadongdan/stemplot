import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.collections import LineCollection
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from stemplot.colors._colormaps import get_cmap

def plot_image(ax, img=None, clip=False, keep_spine=True, **kwargs):
    if img is None:
        img = np.random.random((32, 32))
    h, w = img.shape[0:2]
    im = ax.imshow(img, **kwargs)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_visible(keep_spine)

    if clip == True:
        patch = patches.Circle((0.5, 0.5), radius=0.5, transform=ax.transAxes)
        im.set_clip_path(patch)


def plot_edges(ax, pts, edges, **kwargs):
    if 'color' not in kwargs:
        kwargs['color'] = '#2d3742ff'
    lines = np.array([(pts[i], pts[j]) for (i, j) in edges])
    segs = LineCollection(lines, **kwargs)
    ax.add_collection(segs)


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# rendered ball used as markers
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def render_ball(size=256, k=2, amb=0.2, color='C0'):
    # this is light source
    direction = np.array([-30, -30, 50])

    t = np.linspace(-1, 1, size)
    x, y = np.meshgrid(t, t)
    z2 = 1 - x ** 2 - y ** 2
    mask = (z2 < 0)
    z2[z2 < 0] = 0
    z = np.sqrt(z2)
    # v is norm vector
    v = np.stack((x, y, z))
    v = v.reshape(3, -1).T
    v = v / np.linalg.norm(v, axis=0)

    s = np.maximum(np.dot(v, direction), 0)
    lum = (np.power(s, k) + amb) / (1 + amb)
    # normalize to [0, 1]
    lum = (lum - lum.min()) / np.ptp(lum)
    # make rgba format
    rgb = get_cmap(color)(lum)
    img = rgb.reshape(size, size, 4)
    img[:, :, -1][mask] = 0
    return img


def imscatter(x, y, img=None, zoom=0.1, ax=None, **kwargs):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.2))
    if img is None:
        img = render_ball()
    im = OffsetImage(img, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False, **kwargs)
        artists.append(ax.add_artist(ab))
    ax.scatter(x, y, alpha=0)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# scale bar
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def add_scale_bar(ax, l, x=0.05, y=0.05, **kwargs):
    # l is length in pixel
    # transfrom x and y to data coordinates
    x, y = ax.transData.inverted().transform(ax.transAxes.transform((x, y)))
    if 'lw' not in kwargs and 'linewidth' not in kwargs:
        kwargs['lw'] = 2
    if 'c' not in kwargs and 'color' not in kwargs:
        kwargs['c'] = '#e4e1ca'
    ax.plot([x, x+l], [y, y], **kwargs)