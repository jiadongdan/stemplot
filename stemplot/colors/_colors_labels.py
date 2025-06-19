import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import to_rgba
from typing import Sequence, Union, Any

ArrayLike = Union[Sequence[int], np.ndarray]

# Method 1
def reassign_labels_loop(lbs: ArrayLike) -> np.ndarray:
    """
    Reassign non-negative integer labels in `lbs` to consecutive integers [0..n_classes-1]
    in descending order of their frequency, using a loop-based mapping approach.
    Negative labels in the input are preserved as -1 in the output.
    """
    lbs_arr = np.asarray(lbs, dtype=int)
    mask = lbs_arr >= 0
    # If there are no non-negative labels, return a copy
    if not mask.any():
        return lbs_arr.copy()

    unique_labels, counts = np.unique(lbs_arr[mask], return_counts=True)
    # Sort labels by descending frequency
    sorted_labels = unique_labels[np.argsort(-counts)]
    mapping = {old: new for new, old in enumerate(sorted_labels)}

    # Initialize output with -1 and apply mapping
    new_lbs = np.full_like(lbs_arr, fill_value=-1)
    for old_label, new_label in mapping.items():
        new_lbs[lbs_arr == old_label] = new_label
    return new_lbs

# Method 2
def reassign_labels_vect(lbs: ArrayLike) -> np.ndarray:
    """
    Reassign non-negative labels in `lbs` to consecutive integers [0..n_classes-1]
    based on descending frequency, using a fully vectorized approach.
    Negative labels are mapped to -1.
    """
    lbs_arr = np.asarray(lbs, dtype=int)
    flat = lbs_arr.ravel()

    # Find unique values and inverse indices
    uniq_vals, inv_idx = np.unique(flat, return_inverse=True)
    counts = np.bincount(inv_idx)

    # Identify non-negative labels and sort by frequency
    nonneg_mask = uniq_vals >= 0
    nonneg_indices = np.where(nonneg_mask)[0]
    sorted_nonneg = nonneg_indices[np.argsort(-counts[nonneg_indices])]

    # Build new code mapping, defaulting to -1
    new_codes = np.full_like(uniq_vals, fill_value=-1)
    new_codes[sorted_nonneg] = np.arange(len(sorted_nonneg))

    # Map back to original shape
    return new_codes[inv_idx].reshape(lbs_arr.shape)

# Method 3: this is fastest overall
def reassign_labels_bincount(lbs: ArrayLike) -> np.ndarray:
    """
    Reassign non-negative integer labels in `lbs` to consecutive integers [0..n_classes-1]
    in descending order of frequency using np.bincount. Negative labels remain -1.
    """
    lbs_arr = np.asarray(lbs, dtype=int)
    flat = lbs_arr.ravel()
    mask_pos = flat >= 0
    # If there are no non-negative labels, return a copy
    if not mask_pos.any():
        return lbs_arr.copy()

    vals = flat[mask_pos]
    mn, mx = vals.min(), vals.max()
    shift = -mn if mn < 0 else 0

    # Count frequencies over the shifted range
    freq = np.bincount(vals + shift)
    # Sort labels by descending frequency
    sorted_indices = np.argsort(-freq)

    # Create new code array and map
    new_codes = np.full_like(freq, fill_value=-1)
    new_codes[sorted_indices] = np.arange(len(sorted_indices))

    # Build output and reshape
    new_flat = np.full_like(flat, fill_value=-1)
    new_flat[mask_pos] = new_codes[vals + shift]
    return new_flat.reshape(lbs_arr.shape)

def reassign_lbs(lbs, method='bincount'):
    if method == 'loop':
        return reassign_labels_loop(lbs)
    elif method == 'vect':
        return reassign_labels_vect(lbs)
    elif method == 'bincount':
        return reassign_labels_bincount(lbs)


def colors_from_lbs(
        lbs: ArrayLike,
        colors: Union[Sequence[Any], np.ndarray, None] = None,
        cmap: str = 'coolwarm',
        outlier_color: Any = 'grey'
) -> np.ndarray:
    """
    Convert integer labels in `lbs` to RGBA colors, with an `outlier_color` for negatives.

    - Non-negative labels are mapped to consecutive colors in order of unique label appearance:
      * <10 labels → 'tab10'
      * 10–20 labels → 'tab20'
      * >20 labels → specified `cmap`
    - Negative labels receive `outlier_color`.

    Args:
        lbs: array-like of integer labels.
        colors: optional sequence of color specs to use instead of colormaps.
        cmap: colormap name for >20 labels when `colors` is None.
        outlier_color: color spec for labels < 0.

    Returns:
        An array of shape (*lbs.shape, 4) of RGBA floats in [0,1].
    """
    if lbs is None:
        raise ValueError("`lbs` must be provided and cannot be None.")

    lbs_arr = np.asarray(lbs, dtype=int)
    flat = lbs_arr.ravel()

    unique_labels = np.unique(flat)
    pos_labels = unique_labels[unique_labels >= 0]
    n_pos = pos_labels.size

    # Generate colors for non-negative labels
    if colors is None:
        if n_pos < 10:
            cmap_obj = plt.get_cmap('tab10')
            rgba_list = [cmap_obj(i) for i in range(n_pos)]
        elif n_pos <= 20:
            cmap_obj = plt.get_cmap('tab20')
            rgba_list = [cmap_obj(i) for i in range(n_pos)]
        else:
            cmap_obj = cm.get_cmap(cmap)
            rgba_list = [cmap_obj(i / (n_pos - 1)) for i in range(n_pos)]
    else:
        if len(colors) < n_pos:
            raise ValueError(f"Provided colors ({len(colors)}) fewer than positive labels ({n_pos}).")
        rgba_list = [to_rgba(c) for c in colors[:n_pos]]

    # Build mapping including outlier
    label_to_color = {lab: rgba_list[i] for i, lab in enumerate(pos_labels)}
    label_to_color[-1] = to_rgba(outlier_color)

    # Assign colors
    out_flat = np.array([label_to_color.get(lbl, label_to_color[-1]) for lbl in flat])
    return out_flat.reshape(*lbs_arr.shape, 4)
