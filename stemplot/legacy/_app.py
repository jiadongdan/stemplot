import numpy as np
from matplotlib.widgets import RectangleSelector

class CropApp:

    def __init__(self, ax, img):
        self.ax = ax
        self.fig = ax.figure
        self.img = img
        self.ax.imshow(img)
        self.press = self.fig.canvas.mpl_connect("key_press_event", self.press_key)

    def press_key(self, event):
        if event.key == "enter":
            x12 = np.rint(self.ax.get_xlim()).astype(int)
            y12 = np.rint(self.ax.get_ylim()).astype(int)
            xmin, xmax = np.min(x12), np.max(x12)
            ymin, ymax = np.min(y12), np.max(y12)
            if len(self.img.shape) == 2:
                print('[{}:{}, {}:{}]'.format(ymin, ymax, xmin, xmax))
            if len(self.img.shape) == 3:
                print('[{}:{}, {}:{}, :]'.format(ymin, ymax, xmin, xmax))


class FigCrop:

    def __init__(self, fig):
        self.fig = fig
        self.ax = self.fig.add_axes([0, 0, 1, 1], fc=[0, 0, 0, 0])
        self.selector = RectangleSelector(self.ax, self.onselect, useblit=True, interactive=True)

    def onselect(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print(f"({x1:3.2f}, {y1:3.2f}) --> ({x2:3.2f}, {y2:3.2f})")
        print(f"The buttons you used were: {eclick.button} {erelease.button}")