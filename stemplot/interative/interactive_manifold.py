import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from ..colors._colors import colors_from_lbs
from ..colors._colormaps import color_palette


def _update_mean_signal(ax, p,):
    if ax.lines:  # ax.images not empty
        ax.clear()
        ax.plot(p)
    else:
        ax.plot(p)

def _update_mean_patch(ax, p, cmap, clip=True):
    if ax.images:  # ax.images not empty
        ax.images[0].set_data(p)
        ax.images[0].set_cmap(cmap)
    else:
        ax.imshow(p, cmap=cmap)
    if clip:
        c = plt.Circle((p.shape[0] / 2 - 0.25, p.shape[1] / 2 - 0.25), radius=p.shape[0] / 2, transform=ax.transData)
        ax.images[0].set_clip_path(c)


class InteractiveSignals:

    def __init__(self, fig, X, data, lbs=None, **kwargs):
        self.fig = fig
        self.ax_cluster = fig.axes[0]
        self.ax_patch = fig.axes[1]

        self.X = X
        self.data = data

        if len(self.data.shape) == 2:
            self.data_dim = 1
        elif len(self.data.shape) == 3:
            self.data_dim = 2

        if lbs is None:
            self.lbs_ = [0,]*len(self.data)
        else:
            self.lbs_ = lbs
        self.colors = colors_from_lbs(self.lbs_)

        self.path_collection = self.ax_cluster.scatter(X[:, 0], X[:, 1], c=self.colors, **kwargs)
        for e in np.unique(self.lbs_):
            x, y = X[self.lbs_ == e].mean(axis=0)
            self.ax_cluster.text(x, y, s=e, transform=self.ax_cluster.transData)
        self.ax_cluster.axis('equal')


        self.ind = None
        self.X_selected = None

        self.lbs = np.array(len(self.data) * [-1])

        self.num_clusters = 0

        self.lasso = LassoSelector(self.ax_cluster, onselect=self.onselect)
        self.press = self.fig.canvas.mpl_connect("key_press_event", self.press_key)

    def onselect(self, event):
        path = Path(event)
        self.ind = np.nonzero(path.contains_points(self.X))[0]
        if self.ind.size != 0:
            self.X_selected = self.X[self.ind]

            # mode now only support numeric type
            #c = mode(self.colors[self.ind])[0][0]
            cs, cnts = np.unique(self.colors[self.ind], return_counts=True, axis=0)
            c = cs[np.argmax(cnts)]
            # update mean patch
            #p = self.ps[self.ind].mean(axis=0)
            idx = np.random.choice(len(self.ind), 1)[0]
            p = self.data[self.ind][idx]
            if self.data_dim == 1:
                _update_mean_signal(self.ax_patch, p)
            elif self.data_dim == 2:
                _update_mean_patch(self.ax_patch, p, cmap=color_palette(c))

            self.fig.canvas.draw_idle()

    def press_key(self, event):
        if event.key == "enter":
            if self.ind.any():
                self.lbs[self.ind] = self.num_clusters
                self.num_clusters += 1
                print("One cluster has been selected.")


def interactive_signals(X, ps, lbs=None, **kwargs):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    app = InteractiveSignals(fig, X, ps, lbs, **kwargs)
    return app



