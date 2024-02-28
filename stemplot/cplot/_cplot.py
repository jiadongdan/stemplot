import numpy as np
import matplotlib.pyplot as plt
from typing import Callable

from ._colorize_oklab import get_srgb1

def cplot(z,
          ax = None,
          abs_scaling: Callable[[np.ndarray], np.ndarray] = lambda r: r / (r + 1),
          saturation_adjustment: float = 1.28,):

    rgb_vals = get_srgb1(z, abs_scaling=abs_scaling, saturation_adjustment=saturation_adjustment)

    # set nan values to white
    assert rgb_vals.shape[-1] == 3
    is_nan = np.any(np.isnan(rgb_vals), axis=-1)
    rgb_vals[is_nan] = [1.0, 1.0, 1.0]

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.2))

    ax.imshow(rgb_vals)