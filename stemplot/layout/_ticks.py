import matplotlib.ticker as mticker

def remove_minor_ticks(ax, which='both'):
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

