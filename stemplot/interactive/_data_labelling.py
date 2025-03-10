import numpy as np
#from statistics import mode
import matplotlib.pyplot as plt
from scipy.stats import mode
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

from ..colors._colors import generate_colors_from_lbs
from ..colors._colors import to_hex
from ..colors._colormaps import color_palette

from skimage.registration import phase_cross_correlation
from skimage.morphology import disk
from skimage.transform import rotate, warp_polar
from sklearn.utils import check_random_state
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA


def normalize(x, low=0., high=1.):
    return (x - x.min())/(x.max() - x.min())
def string_to_number(input_str):
    if input_str in ['0', '1']:
        return int(input_str)
    elif input_str in ['b',]:
        return -1

def pca(data):
    aa = PCA(n_components=2)
    res = aa.fit_transform(data)
    return res

def labels_to_colors(lbs):
    three_colors = np.array(['#1f77b4', '#ff7f0e', '#2d3742'])
    return three_colors[lbs]

def _update_pts(ax, pts, **kwargs):
    if ax.collections: # ax.collections is not empty
        ax.collections[0].set_offsets(pts)
    else:
        ax.scatter(pts[:, 0], pts[:, 1], **kwargs)


def _update_mean_patch(ax, p, cmap, clip=True):
    if ax.images:  # ax.images not empty
        ax.images[0].set_data(p)
        ax.images[0].set_cmap(cmap)
    else:
        ax.imshow(p, cmap=cmap)
    if clip:
        c = plt.Circle((p.shape[0] / 2 - 0.25, p.shape[1] / 2 - 0.25), radius=p.shape[0] / 2, transform=ax.transData)
        ax.images[0].set_clip_path(c)

def _update_color(ax, colors):
    """
    Update scatter plot colors.
    If colors are numerical values, updates colormap.
    If colors are valid matplotlib color names or RGB tuples, updates facecolor.
    Raises a ValueError if no scatter plot is found.
    """
    if not ax.collections:
        raise ValueError("No scatter plot found in the given axis.")

    sc = ax.collections[0]  # Get scatter plot object
    if isinstance(colors, (list, np.ndarray)) and isinstance(colors[0], (int, float)):
        sc.set_array(np.array(colors))  # Update colormap values
    else:
        sc.set_color(colors)  # Update explicit colors

class BinaryDataLabelling:

    def __init__(self, fig, X, img, pts, ps, lbs, clip=True, **kwargs):
        xy = pca(X)

        self.fig = fig
        self.ax_img = fig.axes[0]
        self.ax_cluster = fig.axes[1]
        self.ax_patch = fig.axes[2]

        if lbs is None:
            self.lbs_ = np.array([-1] * len(pts))
        else:
            self.lbs_ = lbs.copy()
        # use generate_colors_from_lbs, colors_from_lbs will not work, colors_from_lbs will produce rgba array, np.unique function will make it not working
        self.colors = labels_to_colors(self.lbs_)

        self.path_collection = self.ax_cluster.scatter(xy[:, 0], xy[:, 1], c=self.colors, **kwargs)
        self.ax_cluster.axis('equal')
        self.ax_img.imshow(img)
        self.ax_img.axis('off')
        self.ax_patch.set_xlim(0 - 0.5, ps.shape[2] - 0.5)
        self.ax_patch.set_ylim(ps.shape[1] - 0.5, 0 - 0.5)

        self.img = img
        self.pts = pts
        self.X = X
        self.xy = xy
        self.ps = ps
        self.clip = clip

        self.ind = None
        self.xy_selected = None
        self.pts_selected = None

        self.lbs = np.array(len(self.pts) * [-1])

        self.num_clusters = 0

        self.lasso = LassoSelector(self.ax_cluster, onselect=self.onselect)
        self.press = self.fig.canvas.mpl_connect("key_press_event", self.assign_labels)

    def onselect(self, event):
        path = Path(event)
        self.ind = np.nonzero(path.contains_points(self.xy))[0]
        if self.ind.size != 0:
            self.pts_selected = self.pts[self.ind]
            self.xy_selected = self.xy[self.ind]

            # mode now only support numeric type
            #c = mode(self.colors[self.ind])[0][0]
            cs, cnts = np.unique(self.colors[self.ind], return_counts=True)
            c = cs[np.argmax(cnts)]
            # update pts
            _update_pts(self.ax_img, self.pts_selected, color='r', s=3)
            # update mean patch
            p = self.ps[self.ind].mean(axis=0)
            _update_mean_patch(self.ax_patch, p, cmap=color_palette(c), clip=self.clip)
            # if draw_idle() is used, lasso path will be destroyed. To keep the lasso path, use draw()
            self.fig.canvas.draw()
            # self.fig.canvas.draw_idle()

    # assign labels
    def assign_labels(self, event):
        if event.key in ["0", "1", "b"]:
            if self.ind.any(): # seld.ind is NOT empty
                self.lbs[self.ind] = string_to_number(event.key)
                # update colors
                _update_color(self.ax_cluster, labels_to_colors(self.lbs))
                self.fig.canvas.draw_idle()
                print("One cluster has been selected.")
        elif event.key in ["enter",]:
            mask0 = self.lbs == 0
            mask1 = self.lbs == 1
            mask = self.lbs == -1

            f0 = self.X[mask0].mean(axis=0)
            f1 = self.X[mask1].mean(axis=0)

            s0 = cosine_similarity([f0], self.X[mask]).ravel()
            s1 = cosine_similarity([f1], self.X[mask]).ravel()
            s0 = normalize(s0)
            s1 = normalize(s1)

            idx = np.where(mask)[0]
            self.lbs[idx[s0 - s1 > 0.5]] = 0
            self.lbs[idx[s1 - s0 > 0.5]] = 1

            # update colors
            _update_color(self.ax_cluster, labels_to_colors(self.lbs))
            self.fig.canvas.draw_idle()

def interactive_binary(xy, img, pts, ps, lbs=None, clip=True, **kwargs):
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    app = BinaryDataLabelling(fig, xy, img, pts, ps, lbs, clip, **kwargs)
    return app

