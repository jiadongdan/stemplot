import numpy as np
from colorsys import hls_to_rgb
from matplotlib.colors import hsv_to_rgb
from ._colorize_oklab import get_srgb1

# https://stackoverflow.com/a/17068226/5855131
def complex2hls(z, alpha=1.2, theta=0.):
    n,m = z.shape
    c = np.zeros((n,m,3))
    c[np.isinf(z)] = (1.0, 1.0, 1.0)
    c[np.isnan(z)] = (0.5, 0.5, 0.5)

    idx = ~(np.isinf(z) + np.isnan(z))
    H = (np.angle(z[idx]) + np.pi) / (2*np.pi)
    H = (H + 0.5 + theta/360.) % 1.0
    L = 1.0 - 1.0/(1.0+np.abs(z[idx])**alpha)
    c[idx] = [hls_to_rgb(h, l, 0.8) for h,l in zip(H,L)]
    return c

def complex2hsv(z, theta=0.):
    amp = np.abs(z)
    # HSV are values in range [0,1]
    h = (np.angle(z) + np.pi) / (2 * np.pi)
    h = (h + 0.5 + theta/360.) % 1.0
    s = 0.85 * np.ones_like(h)
    v = (amp -amp.min()) / np.ptp(amp)
    #v = amp/amp.max()
    return hsv_to_rgb(np.dstack((h,s,v)))


def colorize(z, colorspace='oklab', *args, **kwargs):
    if colorspace == 'oklab':
        rgb = get_srgb1(z, *args, **kwargs)
    elif colorspace == 'hls':
        rgb = complex2hls(z, *args, **kwargs)
    elif colorspace == 'hsv':
        rgb = complex2hsv(z, *args, **kwargs)
    else:
        raise ValueError('Invalid colorspace used!')
    return rgb



