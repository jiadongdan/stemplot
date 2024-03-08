import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter

def fast_kde(xy, bins=30, sigma=2, xlim=None, ylim=None):
    """
    Generate a smooth 2D density plot by combining 2D histogram and KDE.

    Parameters:
    - xy: A two-dimensional array where the first column is x and the second column is y.
    - bins: The number of bins for the histogram in both dimensions (can be a scalar or [bins_x, bins_y]).
    - sigma: The standard deviation for the Gaussian filter for initial smoothing (applied to histogram).
    - xlim: The limits for the x-axis as a tuple (xmin, xmax). Estimated from data if None.
    - ylim: The limits for the y-axis as a tuple (ymin, ymax). Estimated from data if None.
    """
    x = xy[:, 0]
    y = xy[:, 1]

    # Estimate xlim and ylim from data if not provided
    if xlim is None:
        xlim = (np.min(x) - 1, np.max(x) + 1)
    if ylim is None:
        ylim = (np.min(y) - 1, np.max(y) + 1)

    # Compute the 2D histogram
    h, xedges, yedges = np.histogram2d(x, y, bins=bins, range=[xlim, ylim], density=True)

    # Apply Gaussian filter to smooth the histogram slightly
    h_smooth = gaussian_filter(h, sigma=sigma)

    # Calculate bin centers
    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2
    X, Y = np.meshgrid(xcenters, ycenters)

    # Flatten the grid and create a new array with the positions to evaluate the KDE
    positions = np.vstack([X.ravel(), Y.ravel()])

    # Evaluate the KDE on the positions
    # Use the flattened, smoothed histogram as weights for KDE fitting
    kernel = gaussian_kde(positions, weights=h_smooth.ravel())
    Z = np.reshape(kernel(positions).T, X.shape)

    return X, Y, Z


def plot_density(points, ax=None, bins=30, sigma=2, xlim=None, ylim=None, **kwargs):

    if ax is None:
        fig, ax = plt.subplots(figsize=(7.2, 7.2))

    X, Y, Z = fast_kde(points, bins=bins)

    # Set default kwargs for contourf
    contourf_defaults = {'levels': np.linspace(0, Z.max(), 25), 'cmap': 'Greys', 'alpha': 0.8}

    # If user has provided any kwargs, use them, otherwise use the defaults
    contourf_kwargs = {**contourf_defaults, **kwargs}

    # Plot KDE
    contour = ax.contourf(X, Y, Z, **contourf_kwargs)

    # Handling colorbar separately to ensure it's only added if requested
    if kwargs.get('colorbar', False):  # Default to True if not specified
        plt.colorbar(contour, ax=ax, label='Density')