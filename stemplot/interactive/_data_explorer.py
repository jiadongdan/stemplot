import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from ..colors._colors import colors_from_lbs


def _update_data(ax, data, plot_type):
    # Clear the existing content of the axis
    ax.clear()

    # Plot based on the type specified
    if plot_type == 'lines':
        # Assuming 'data' is a 1D array for a line plot
        ax.plot(data)
    elif plot_type == 'images':
        # Assuming 'data' is a 2D array for an image
        ax.imshow(data, aspect='auto')

    # Redraw the axis to show the updated plot
    ax.figure.canvas.draw_idle()


class DataExplorer:

    def __init__(self, fig, xy, data, lbs=None, mode=None, **kwargs):
        self.fig = fig
        self.ax_cluster = fig.axes[0]
        self.ax_patch = fig.axes[1]

        self.data = data
        self.xy = xy

        if len(data.shape) == 2:
            self.plot_type = 'lines'
        elif len(data.shape) == 3:
            self.plot_type = 'images'

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
                data_mean = self.data[self.ind].mean(axis=0)
                _update_data(self.ax_patch, data_mean, self.plot_type)

            self.fig.canvas.draw_idle()


def interactive_data(xy, data, lbs=None, **kwargs):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    app = DataExplorer(fig, xy, data, lbs, **kwargs)
    return app