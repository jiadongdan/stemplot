import numpy as np


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# numerical array like: list, tuple
# * numpy array: 1D, 2D, 3D
# * a list of array_like
# * a tuple of array_like
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def is_1d_array(data):
    if isinstance(data, np.ndarray) and len(data.shape) == 1:
        return True
    else:
        return False

def is_2d_array(data):
    if isinstance(data, np.ndarray) and len(data.shape) == 2:
        return True
    else:
        return False

def is_3d_array(data):
    if isinstance(data, np.ndarray) and len(data.shape) == 3:
        return True
    else:
        return False

def to_image_data(data):
    if is_2d_array(data):
        return np.array([data,])
    elif is_3d_array(data):
        return data
    elif np.iterable(data):
        sizes = [len(e) if hasattr(e, '__len__') else 1 for e in data]
        if np.std(sizes) == 0:
            return np.array(data)
        else:
            return np.array(data, dtype=object)
    else:
        raise ValueError('Not valid image data format.')


# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=
# image placeholder
# =-=-=-=-=-=-=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=--=-=-=-=

def get_placeholder_image(shape=(256, 256)):
    h, w = shape
    img = np.ones((h, w, 3), dtype=int)*204
    return img

def plot_placeholder_image(ax, shape, show_lines=False, **kwargs):
    img = get_placeholder_image(shape)
    ax.imshow(img)
    h, w = shape
    if show_lines:
        ax.plot([0, 1], [0, 1], transform=ax.transAxes, color='#9e9e9e')
        ax.plot([0, 1], [1, 0], transform=ax.transAxes, color='#9e9e9e')
    ax.text(0.5, 0.5, s='{}x{}'.format(h, w), color='#2d3742', ha='center', va='center', transform=ax.transAxes,
            zorder=5, **kwargs)
    ax.axis('off')

