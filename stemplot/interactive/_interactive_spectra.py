import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from ..colors._colors import colors_from_lbs


def _update_data(ax, data):
    # Clear the existing content of the axis
    ax.clear()
    ax.plot(data)
    # Redraw the axis to show the updated plot
    ax.figure.canvas.draw_idle()


def _update_img(ax, data):
    # Clear the existing content of the axis
    ax.clear()
    # Assuming 'data' is a 2D array for an image
    ax.imshow(data)
    # Redraw the axis to show the updated plot
    ax.figure.canvas.draw_idle()


class SpectraExplorer:

    def __init__(self, fig, xy, X, img, lbs=None, **kwargs):
        self.fig = fig

        self.ax_img = fig.axes[0]
        self.ax_xy = fig.axes[1]
        self.ax_spectrum = fig.axes[2]

        self.img = img
        self.xy = xy
        self.X = X

        if lbs is None:
            self.lbs_ = [0, ] * len(self.xy)
        else:
            self.lbs_ = lbs
        self.colors = colors_from_lbs(self.lbs_)

        self.ax_img.imshow(self.img)

        self.path_collection = self.ax_xy.scatter(self.xy[:, 0], self.xy[:, 1], c=self.colors, **kwargs)
        for e in np.unique(self.lbs_):
            x, y = self.xy[self.lbs_ == e].mean(axis=0)
            self.ax_xy.text(x, y, s=e, transform=self.ax_xy.transData)
        self.ax_xy.axis('equal')

        self.ind = None
        self.xy_selected = None
        self.X_selected = None

        self.lbs = np.array(len(self.xy) * [-1])

        self.lasso = LassoSelector(self.ax_xy, onselect=self.onselect)

    def onselect(self, event):
        path = Path(event)
        self.ind = np.nonzero(path.contains_points(self.xy))[0]
        if self.ind.size != 0:
            self.xy_selected = self.xy[self.ind]
            self.X_selected = self.X[self.ind]
            ind_y, ind_x = np.unravel_index(self.ind, shape=self.img.shape)
            mask = np.zeros_like(self.img)
            mask[ind_y, ind_x] = 1

            _update_img(self.ax_img, self.img * mask)
            spectra_mean = self.X[self.ind].mean(axis=0)
            _update_data(self.ax_spectrum, spectra_mean)

            self.fig.canvas.draw_idle()


def interactive_spectra(xy, X, img, lbs=None, **kwargs):
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    app = SpectraExplorer(fig, xy, X, img, lbs, **kwargs)
    return app