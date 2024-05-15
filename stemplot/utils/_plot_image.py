import numpy as np
from matplotlib.patches import Circle

def plot_image(ax, img=None, clip=False, keep_spine=True, **kwargs):
    if img is None:
        img = np.random.random((32, 32))
    h, w = img.shape[0:2]
    im = ax.imshow(img, **kwargs)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_visible(keep_spine)

    if clip == True:
        patch = Circle((0.5, 0.5), radius=0.5, transform=ax.transAxes)
        im.set_clip_path(patch)