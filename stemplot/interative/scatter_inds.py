import numpy as np
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path


class FastInds:

    def __init__(self, fig, pts, **kwargs):

        self.pts = pts
        self.inds = None

        self.fig = fig
        self.ax = fig.axes[0]

        self.ax.scatter(self.pts[:, 0], self.pts[:, 1], **kwargs)
        self.lasso = LassoSelector(self.ax, onselect=self.onselect)
        self.press = self.fig.canvas.mpl_connect("key_press_event", self.press_key)

    def onselect(self, event):
        path = Path(event)
        self.inds = np.nonzero(path.contains_points(self.pts))[0]
        if self.inds.size != 0:
            self.pts_selected = self.pts[self.inds]


    def press_key(self, event):
        if event.key == "enter":
            if self.inds.any():
                print(self.inds)