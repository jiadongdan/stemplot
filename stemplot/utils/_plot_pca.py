import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def _generate_colors(lbs, color_cycle=None):
    if color_cycle is None:
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if lbs is None:
        colors = color_cycle[0]
    else:
        colors= [color_cycle[e] for e in lbs]
    return colors

def plot_pca(X, dim=2, lbs=None, colors=None, **kwargs):
    if len(X.shape) == 3:
        data = X.reshape(X.shape[0], -1)
    elif len(X.shape) == 2:
        data = X
    X_pca = PCA(n_components=dim).fit_transform(data)
    colors = _generate_colors(lbs, colors)
    if 's' or 'size' not in kwargs:
        kwargs['s'] = 1
    if dim == 2:
        fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.2))
        ax.scatter(X_pca[:, 0], X_pca[:, 1], color=colors, **kwargs)
        ax.axis('equal')
    elif dim == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X_pca[:, 0], X_pca[:, 1], X_pca[:, 2], color=colors, **kwargs)