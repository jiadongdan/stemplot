import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from ..colors._colors import colors_from_lbs


def _update_signal(ax, p, **kwargs):
    if ax.lines:
        ax.clear()
        ax.plot(p, **kwargs)
    else:
        ax.plot(p, **kwargs)

def


class InteractiveSignals:

    def __init__(self, fig, xy, data, lbs=None, max_samples=15, mode=None, **kwargs):
        self.fig = fig
        self.ax_cluster = fig.axes[0]
        self.ax_patch = fig.axes[1]

        self.data = data
        self.xy = xy

        self.mode = mode

        if lbs is None:
            self.lbs_ = [0,]*len(self.data)
        else:
            self.lbs_ = lbs
        self.colors = colors_from_lbs(self.lbs_)

        self.path_collection = self.ax_cluster.scatter(xy[:, 0], xy[:, 1], c=self.colors, **kwargs)
        for e in np.unique(self.lbs_):
            x, y = xy[self.lbs_ == e].mean(axis=0)
            self.ax_cluster.text(x, y, s=e, transform=self.ax_cluster.transData)
        self.ax_cluster.axis('equal')


        self.max_samples = max_samples

        self.ind = None
        self.xy_selected = None

        self.lbs = np.array(len(self.data) * [-1])

        self.lasso = LassoSelector(self.ax_cluster, onselect=self.onselect)

    def onselect(self, event):
        path = Path(event)
        self.ind = np.nonzero(path.contains_points(self.X))[0]
        if self.ind.size != 0:
            self.xy_selected = self.xy[self.ind]

            if self.mode is None:
                pass
            elif self.mode is 'mean':
                pass

            self.fig.canvas.draw_idle()


def interactive_signals(xy, data, lbs=None, max_samples=15, **kwargs):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    app = InteractiveSignals(fig, xy, data, lbs, max_samples, **kwargs)
    return app