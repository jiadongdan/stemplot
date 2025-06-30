def remove_axis_top_right(ax):
    # set spine visibility
    for axis in ['top', 'right']:
        ax.spines[axis].set_visible(False)