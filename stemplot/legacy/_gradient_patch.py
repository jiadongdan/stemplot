import numpy as np

def plot_gradient_image(ax, mode='h', flip=False, cmap_range=(0, 1), **kwargs):
    if mode == 'h':
        direction = 1
    elif mode == 'v':
        direction = 0
    else:
        raise ValueError("mode can only be 'h' or 'v'.")

    fig = ax.figure
    # get figure aspect ratio
    fig_w, fig_h = fig.get_size_inches()
    aspect_ratio = fig_w / fig_h

    x0, y0, W, H = ax.get_position().bounds
    W = W * aspect_ratio
    extent = [0, W / H, 0, 1]

    phi = direction * np.pi / 2
    v = np.array([np.cos(phi), np.sin(phi)])
    X = np.array([[v @ [1, 0], v @ [1, 1]],
                  [v @ [0, 0], v @ [0, 1]]])
    a, b = cmap_range
    X = a + (b - a) / X.max() * X

    if flip:
        if mode == 'h':
            X = np.fliplr(X)
        elif mode == 'v':
            X = np.flipud(X)
    im = ax.imshow(X, extent=extent, interpolation='bicubic',
                   vmin=0, vmax=1, **kwargs)
    return im