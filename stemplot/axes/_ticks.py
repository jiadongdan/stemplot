import matplotlib.ticker as mticker

def ax_remove_minor_ticks(ax, which='both'):
    """
    Remove minor ticks from the specified axis of the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to modify.
    which : {'x', 'y', 'both'}
        Which axis to remove minor ticks from.
    """
    if which in ('x', 'both'):
        ax.xaxis.set_minor_locator(mticker.NullLocator())
    if which in ('y', 'both'):
        ax.yaxis.set_minor_locator(mticker.NullLocator())

def ax_set_xticks(ax, ticks, labels=None):
    """
    Set the x-axis tick positions (and optionally labels) on the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to set the x-ticks.
    ticks : array-like
        Sequence of positions at which to place the ticks.
    labels : array-like, optional
        Sequence of labels to use at those positions. Must be same length as ticks.
    """
    # Ensure we have a sequence
    ticks = list(ticks)

    if labels is not None:
        if len(ticks) != len(labels):
            raise ValueError(f"‘ticks’ (len={len(ticks)}) and ‘labels’ (len={len(labels)}) must be the same length")
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)
    else:
        ax.set_xticks(ticks)

    return ax

def ax_set_yticks(ax, ticks, labels=None):
    """
    Set the y-axis tick positions (and optionally labels) on the given Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to set the y-ticks.
    ticks : array-like
        Sequence of positions at which to place the ticks.
    labels : array-like, optional
        Sequence of labels to use at those positions. Must be same length as ticks.
    """
    # Coerce to list so we can check length
    ticks = list(ticks)

    if labels is not None:
        if len(ticks) != len(labels):
            raise ValueError(
                f"'ticks' (len={len(ticks)}) and 'labels' (len={len(labels)}) must be the same length"
            )
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)
    else:
        ax.set_yticks(ticks)

    return ax

