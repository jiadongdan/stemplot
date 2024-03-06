import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import LeaveOneOut

def perform_kde(points, sample_fraction=0.1, bandwidth=1.0):
    """
    Perform kernel density estimation on a set of 2D points.

    Parameters:
    - points: numpy array of shape (n_samples, 2) representing the 2D points.
    - sample_fraction: fraction of the points to sample if n_samples is large.
    - bandwidth: the bandwidth of the kernel.

    Returns:
    - kde: the kernel density estimate model.
    """
    n_samples = len(points)

    # Sample the points if the dataset is large
    if n_samples > 10000:  # threshold for what we consider "large"
        sample_size = int(n_samples * sample_fraction)
        sampled_indices = np.random.choice(n_samples, size=sample_size, replace=False)
        sampled_points = points[sampled_indices]
    else:
        sampled_points = points

    # Perform grid search to find the best bandwidth if not specified
    if bandwidth is None:
        params = {'bandwidth': np.logspace(-1, 1, 20)}
        grid = GridSearchCV(KernelDensity(), params, cv=LeaveOneOut())
        grid.fit(sampled_points)
        best_bandwidth = grid.best_estimator_.bandwidth
    else:
        best_bandwidth = bandwidth

    # Fit the KDE model
    kde = KernelDensity(bandwidth=best_bandwidth, kernel='gaussian')
    kde.fit(sampled_points)

    return kde


def plot_density(points, kde=None, ax=None, grid_size=100, xlim=None, ylim=None, **kwargs):
    """
    Visualize the kernel density estimation.

    Parameters:
    - kde: the kernel density estimate model.
    - points: numpy array of shape (n_samples, 2) representing the 2D points.
    - ax: matplotlib Axes object. If None, a new figure and axis will be created.
    - grid_size: size of the grid on which to evaluate the KDE.
    - xlim: tuple (min, max), limits for the x-axis.
    - ylim: tuple (min, max), limits for the y-axis.
    - **kwargs: additional keyword arguments to pass to the plt.contourf function.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7.2, 7.2))

    if kde is None:
        kde = perform_kde(points)

    if xlim is None:
        xlim = (points[:, 0].min() - 1, points[:, 0].max() + 1)
    if ylim is None:
        ylim = (points[:, 1].min() - 1, points[:, 1].max() + 1)

    # Create grid
    xgrid = np.linspace(xlim[0], xlim[1], grid_size)
    ygrid = np.linspace(ylim[0], ylim[1], grid_size)
    X, Y = np.meshgrid(xgrid, ygrid)
    xy_sample = np.vstack([X.ravel(), Y.ravel()]).T

    # Evaluate KDE on grid
    Z = np.exp(kde.score_samples(xy_sample))  # log density
    Z = Z.reshape(X.shape)

    # Set default kwargs for contourf
    contourf_defaults = {'levels': np.linspace(0, Z.max(), 25), 'cmap': 'Reds', 'alpha': 0.5}

    # If user has provided any kwargs, use them, otherwise use the defaults
    contourf_kwargs = {**contourf_defaults, **kwargs}

    # Plot KDE
    contour = ax.contourf(X, Y, Z, **contourf_kwargs)

    # Handling colorbar separately to ensure it's only added if requested
    if kwargs.get('colorbar', False):  # Default to True if not specified
        plt.colorbar(contour, ax=ax, label='Density')

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)