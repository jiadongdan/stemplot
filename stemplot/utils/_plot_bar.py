import numpy as np
def plot_bar(ax, data, labels, orientation='horizontal', bar_gap=0.2, **kwargs):
    """
    Plot a bar chart on the given Axes (ax), defaulting to a horizontal bar chart.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        A pre-created matplotlib Axes object (e.g., obtained via fig, ax = plt.subplots()).
    data : np.ndarray
        If it is a 1D array (shape = (n_labels,)), each label corresponds to a single bar.
        If it is a 2D array (shape = (n_legends, n_labels)),
        each label (i.e., each column) corresponds to multiple bars (one per legend).
    labels : list
        A list of labels for each group (or a single bar if data is 1D).
        If data is 1D, its length should match data.
        If data is 2D, its length should match data.shape[1], corresponding to each column as one group.
    orientation : str, optional
        The orientation of the bars. Defaults to 'horizontal'. Can also be 'vertical'.
    bar_gap : float, optional
        The gap between adjacent groups. The distance between the centers of adjacent groups is (1 + bar_gap).
    **kwargs : dict
        Other keyword arguments passed to matplotlib's bar or barh functions, e.g., color, edgecolor, etc.
        You can also pass 'bar_width' here to customize the bar width.
    """
    
    # Convert data to at least 2D for uniform processing
    data = np.atleast_2d(data)
    n_legends, n_labels = data.shape

    # Get bar_width from kwargs if provided, otherwise compute automatically
    bar_width = kwargs.pop('bar_width', None)
    if bar_width is None:
        bar_width = 0.8 / n_legends  # default automatic calculation
    
    # Compute the center positions for each group on the axis
    # The distance between adjacent group centers is (1 + bar_gap)
    group_positions = np.arange(n_labels) * (1 + bar_gap)
    
    # The total width occupied by all bars in a single group
    group_width = n_legends * bar_width
    
    if orientation == 'vertical':
        # Use ax.barh() for a vertical orientation in this code block
        # (it might sound contradictory, but let's follow this code's logic)
        for i in range(n_legends):
            # For the i-th row of data, compute the offset within the group
            # The entire group is centered at group_positions, so first shift left by group_width/2
            # Then shift right by (i+0.5)*bar_width to center each bar in its sub-interval
            offsets = group_positions - group_width / 2 + (i + 0.5) * bar_width
            
            ax.barh(
                offsets,            # y-coordinates of the bar centers
                data[i, :],        # bar lengths
                height=bar_width,
                label=None,         # legend can be set via ax.legend()
                **kwargs
            )
        # Set y-axis tick positions and labels
        ax.set_yticks(group_positions)
        ax.set_yticklabels(labels)
    
    elif orientation == 'horizontal':
        # Use ax.bar() for a horizontal orientation in this code block
        for i in range(n_legends):
            offsets = group_positions - group_width / 2 + (i + 0.5) * bar_width
            
            ax.bar(
                offsets,
                data[i, :],
                width=bar_width,
                label=None,
                **kwargs
            )
        # Set x-axis tick positions and labels
        ax.set_xticks(group_positions)
        ax.set_xticklabels(labels)
    else:
        raise ValueError('Invalid orientation.')

