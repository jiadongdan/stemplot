import numpy as np
import matplotlib.pyplot as plt

def plot_heatmap(data, ax=None, grid=None, grid_kw={}, ticks=True, texts=False, reorder=True, **kwargs):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.2))

    im = ax.imshow(data, **kwargs)

    if ticks:
        ax.set_xticks(np.arange(data.shape[1]))
        ax.set_yticks(np.arange(data.shape[0]))
    else:
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

    if texts:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                # here this is data
                data = np.round(data, 3)
                text = ax.text(j, i, data[i, j], ha="center", va="center", color="k", fontsize=8)
    else:
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

    if grid is None:
        if data.shape[0] > 15:
            grid = False
        else:
            grid = True
    else:
        grid = grid
    if grid:
        ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
        if not grid_kw:
            grid_kw = dict(color='white', lw=0.5)
        ax.grid(which='minor', axis='both', **grid_kw)
        ax.tick_params(which="both", bottom=False, left=False)
    else:
        ax.set_xticks([])
        ax.set_yticks([])

    return im