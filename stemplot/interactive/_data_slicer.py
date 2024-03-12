import numpy as np
import matplotlib.pyplot as plt
from sklearn.utils import check_array

class DataSlicer:
    def __init__(self, ax, data, **kwargs):
        self.ax = ax
        self.data = np.asarray(data)
        self.kwargs = kwargs
        self.ind = 0

        if self.data.ndim == 1 or (self.data.ndim == 2 and isinstance(self.data[0], (list, np.ndarray))):
            self.plot_type = 'points'
            self._init_points()
        elif self.data.ndim == 2:
            self.plot_type = 'lines'
            self._init_lines()
        elif self.data.ndim == 3:
            self.plot_type = 'images'
            self._init_images()
        else:
            raise ValueError("DataSlicer supports 1D points, 2D lines, or 3D images.")

        self.num_slices = len(self.data)
        self._update_xlabel()
        self.cid = self.ax.figure.canvas.mpl_connect('key_press_event', self.press_key)

    def _init_points(self):
        self.artist = self.ax.scatter(self.data[0][:, 0], self.data[0][:, 1], **self.kwargs)
        self._set_limits()

    def _init_lines(self):
        self.artist, = self.ax.plot(self.data[0], **self.kwargs)

    def _init_images(self):
        self.artist = self.ax.imshow(self.data[0], **self.kwargs)

    def _set_limits(self):
        points_stack = np.vstack(self.data)
        vmin, vmax = points_stack.min(), points_stack.max()
        margin = points_stack.ptp() * 0.05
        self.ax.set_xlim(vmin - margin, vmax + margin)
        self.ax.set_ylim(vmin - margin, vmax + margin)

    def _update_xlabel(self):
        self.ax.set_xlabel(f'slice {self.ind}', fontsize=14)

    def press_key(self, event):
        if event.key == 'right':
            self.ind = (self.ind + 1) % self.num_slices
        elif event.key == 'left':
            self.ind = (self.ind - 1) % self.num_slices

        self._update_data()
        self._update_xlabel()
        self.ax.figure.canvas.draw()

    def _update_data(self):
        if self.plot_type == 'images':
            self.artist.set_data(self.data[self.ind])
        elif self.plot_type == 'lines':
            self.artist.set_data(range(len(self.data[self.ind])), self.data[self.ind])
        elif self.plot_type == 'points':
            self.artist.set_offsets(self.data[self.ind])

def imshow(imgs, ax=None, **kwargs):
    ax = ax or plt.subplots(figsize=(7.2, 7.2))[1]
    imgs = check_array(imgs, allow_nd=True)

    shape = imgs.shape
    if len(shape) == 3 and shape[2] != 3:
        im = DataSlicer(ax, imgs, **kwargs)
    else:
        im = ax.imshow(imgs.squeeze(), **kwargs)  # Squeeze in case of single image

    if kwargs.get('hvlines', False):
        h, w = imgs.shape[:2]
        ax.axhline(h / 2, color='r')
        ax.axvline(w / 2, color='r')
    return im

def plot(lines, ax=None, **kwargs):
    ax = ax or plt.subplots(figsize=(7.2, 7.2))[1]
    ds = DataSlicer(ax, lines, **kwargs)
    return ds

def scatter(points, ax=None, **kwargs):
    ax = ax or plt.subplots(figsize=(7.2, 7.2))[1]
    sc = DataSlicer(ax, points, **kwargs)
    return sc
