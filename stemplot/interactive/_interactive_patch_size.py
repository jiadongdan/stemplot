import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, find_peaks
from skimage.transform import warp_polar
from skimage.filters import gaussian
from skimage.feature import peak_local_max


def standardize_image(image):
    """
    Standardize the image to have mean 0 and standard deviation 1.

    Parameters:
    image : numpy array
        The input 2D image.

    Returns:
    standardized_image : numpy array
        The standardized 2D image.
    """
    mean = np.mean(image)
    std = np.std(image)

    if std == 0:
        raise ValueError("Standard deviation is zero, can't standardize the image.")

    standardized_image = (image - mean) / std
    return standardized_image

def autocorrelation(image, mode='same', method='fft', standardize=True):
    # standardize the image
    if standardize is True:
        image = standardize_image(image)
    return correlate(image, image, mode=mode, method=method)

def radial_profile(data):
    i, j = np.unravel_index(np.argmax(data), shape=data.shape)
    line = warp_polar(data, center=(i, j)).mean(axis=0)[0:i]
    return line

def get_profile(image, standardize=True):
    autocorr = autocorrelation(image=image, standardize=standardize)
    line_profile = radial_profile(autocorr)
    return line_profile

def locate_one_point(img):
    pts = peak_local_max(img, min_distance=1)
    if len(pts) == 0:
        return None  # No peaks found

    center = np.array(img.shape) / 2
    distances = np.linalg.norm(pts - center, axis=1)
    closest_idx = np.argmin(distances)

    row, col = pts[closest_idx]
    return (col, row)

class InteractivePatchSize:

    def __init__(self, fig, img, **kwargs):

        self.fig = fig
        self.ax_img = fig.axes[0]
        self.ax_corr = fig.axes[1]
        self.ax_patch = fig.axes[2]
        self.ax_line = fig.axes[3]

        self.img = img
        imgf = gaussian(img, sigma=3)
        x, y = locate_one_point(imgf)
        self.img_corr = autocorrelation(img)
        self.line = get_profile(img)[0:len(img)//4]

        peaks, _ = find_peaks(self.line)

        self.ax_img.imshow(img)
        self.ax_img.axis('off')

        self.ax_corr.imshow(self.img_corr)
        self.ax_corr.axis('off')

        self.ax_line.plot(self.line)
        self.ax_line.plot(peaks, self.line[peaks], "x")

        self.patch_size = int(peaks[0]*np.sqrt(2))
        self.ax_patch.imshow(img[y-self.patch_size//2:y+self.patch_size//2+1, x-self.patch_size//2:x+self.patch_size//2+1])
        self.ax_patch.axis('off')

def interactive_patch_size(img):
    fig = plt.figure(layout="constrained")
    axes = fig.subplot_mosaic(
        """
        ABC
        DDD
        """
    )
    app = InteractivePatchSize(fig, img)
    return app