import numpy as np
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path


class LassoMask:

    def __init__(self, fig, img, **kwargs):

        self.img = img

        self.fig = fig
        self.ax = fig.axes[0]

        self.ax.imshow(img, **kwargs)
        self.lasso = LassoSelector(self.ax, onselect=self.onselect, props=dict(color='red'))
        self.press = self.fig.canvas.mpl_connect("key_press_event", self.press_key)

        self.path = None
        self.mask = None

        x = np.arange(img.shape[1])
        y = np.arange(img.shape[0])
        X, Y = np.meshgrid(x, y)
        self.XY = np.array([X.ravel(), Y.ravel()]).T

    def onselect(self, event):
        self.path = Path(event)

    def press_key(self, event):
        if event.key == "enter":
            self.mask = self.path.contains_points(self.XY).reshape(self.img.shape)
            print('Finished!')