import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor

def plot_compare(imgs, size=18, cursor=False, **kwargs):
    # sklearn check_array is not recommended here
    # imgs = check_array(imgs, allow_nd=True)
    n = len(imgs)
    fig, axes = plt.subplots(1, n, figsize=(size, size/n), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        ax.imshow(imgs[i], **kwargs)
        ax.axis('off')
    fig.tight_layout()
    if cursor:
        multi = MultiCursor(fig.canvas, axes, color='r', lw=1, horizOn=True, vertOn=True)
        return multi