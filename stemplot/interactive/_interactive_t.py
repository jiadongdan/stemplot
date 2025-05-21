import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class InteractiveThreshold:

    def __init__(self, fig, X, img, pts, ps, n_bins=30, **kwargs):
        # 1) PCA projection
        self.xy = pca(X)

        # 2) per-point scalar from ps
        size = ps.shape[1] // 2
        self.data = ps[:, size-1:size+2, size-1:size+2].mean(axis=(1, 2))
        self.ps   = ps

        # 3) axes
        self.fig        = fig
        self.ax_cluster = fig.axes[0]
        self.ax_hist    = fig.axes[1]
        self.ax_class0  = fig.axes[2]
        self.ax_class1  = fig.axes[3]

        # 4) initial threshold & mask
        init_thr   = np.median(self.data)
        self.t     = init_thr
        self.lbs   = self.data > self.t   # Boolean mask: True → class1, False → class0

        # 5) scatter colored by initial lbs
        scatter_colors = ['C1' if flag else 'C0' for flag in self.lbs]
        self.scatter = self.ax_cluster.scatter(
            self.xy[:, 0], self.xy[:, 1],
            c=scatter_colors,
            s=5,
            edgecolor='none',
            **kwargs
        )
        self.ax_cluster.set_title('PCA Cluster (thresholded)')
        self.ax_cluster.set_xlabel('PC1')
        self.ax_cluster.set_ylabel('PC2')

        # 6) main histogram
        self.n, self.bins, self.patches = self.ax_hist.hist(
            self.data,
            bins=n_bins,
            edgecolor='white'
        )
        self.ax_hist.set_title('Data Histogram')
        # dashed vertical line at threshold
        self.vline = self.ax_hist.axvline(self.t, color='gray', linestyle='--')

        # 7) slider aligned with ax_hist
        hist_pos = self.ax_hist.get_position()
        slider_height = 0.03
        pad = 0.01
        slider_ax = fig.add_axes([
            hist_pos.x0,
            hist_pos.y0 - pad - slider_height,
            hist_pos.width,
            slider_height
        ], facecolor='lightgoldenrodyellow')

        x0, x1 = self.ax_hist.get_xlim()
        self.slider = Slider(
            ax=slider_ax,
            label='Threshold',
            valmin=x0,
            valmax=x1,
            valinit=init_thr,
        )
        self.slider.on_changed(self._on_threshold_change)

        # initial class images
        self._draw_class_images()

    def _draw_class_images(self):
        """Compute & plot mean ps-image for each class with bottom text labels."""
        # Class 0: data ≤ threshold
        self.ax_class0.cla()
        if np.any(~self.lbs):
            mean0 = self.ps[~self.lbs].mean(axis=0)
            self.ax_class0.imshow(mean0)
        self.ax_class0.axis('off')
        # text label at bottom
        self.ax_class0.text(
            0.5, -0.05,
            'class 0 ≤ thr',
            transform=self.ax_class0.transAxes,
            ha='center',
            va='top',
            fontsize=8
        )

        # Class 1: data > threshold
        self.ax_class1.cla()
        if np.any(self.lbs):
            mean1 = self.ps[self.lbs].mean(axis=0)
            self.ax_class1.imshow(mean1)
        self.ax_class1.axis('off')
        # text label at bottom
        self.ax_class1.text(
            0.5, -0.05,
            'class 1 > thr',
            transform=self.ax_class1.transAxes,
            ha='center',
            va='top',
            fontsize=8
        )

    def _on_threshold_change(self, val):
        # 1) update threshold & mask
        self.t   = val
        self.lbs = self.data > self.t

        # 2) recolor histogram
        for left, patch in zip(self.bins[:-1], self.patches):
            patch.set_facecolor('C1' if left > self.t else 'C0')
        # update dashed line position
        self.vline.set_xdata([self.t])

        # 3) recolor scatter
        new_colors = ['C1' if flag else 'C0' for flag in self.lbs]
        self.scatter.set_facecolors(new_colors)

        # 4) redraw class-mean images
        self._draw_class_images()

        self.fig.canvas.draw_idle()


def interactive_t(X, img, pts, ps, **kwargs):
    fig, _ = plt.subplot_mosaic(
        [['a', 'a', 'b', 'b'],
         ['a', 'a', 'c', 'd']],
        figsize=(12, 6)
    )
    app = InteractiveThreshold(fig, X, img, pts, ps, **kwargs)
    return app