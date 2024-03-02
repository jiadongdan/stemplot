from matplotlib.patches import FancyArrowPatch

def ax_add_arrow(ax, start, end, **kwargs):
    # Set default values more efficiently
    kwargs.setdefault('arrowstyle', 'simple')
    kwargs.setdefault('mutation_scale', 20)
    kwargs.setdefault('color', '#413c39')  # Assuming you meant to set a default color
    # Note: If you intend to separately control facecolor and edgecolor,
    # adjust the logic accordingly and consider removing 'color'

    # Directly use 'color' if you want to set a default color,
    # or use 'facecolor' and 'edgecolor' for more control.
    # This example uses 'color' for simplicity.

    arrow = FancyArrowPatch(start, end, **kwargs)
    ax.add_patch(arrow)
    return arrow
