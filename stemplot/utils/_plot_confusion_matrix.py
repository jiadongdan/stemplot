import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def plot_confusion_matrix(mat, ax,
                          class_names=None,
                          diag_color='#a6cee3',
                          off_diag_color='#f0f0f0',
                          text_color='black',
                          fontsize=10,
                          edge_color='white',
                          lw=1.0):
    """
    Plot a confusion matrix on a given Axes using square patches—
    one color for diagonal cells and another for off-diagonal cells.
    X-axis labels are drawn on the top. Minor and major ticks are suppressed.

    Parameters
    ----------
    mat : array-like, shape (N, N)
        Confusion matrix to plot.
    ax : matplotlib.axes.Axes
        Axes on which to draw the matrix.
    class_names : list of str, optional
        Labels for the classes (length N). If None, integers 0..N-1 are used.
    diag_color : str or tuple
        Color for diagonal cells.
    off_diag_color : str or tuple
        Color for off-diagonal cells.
    text_color : str or tuple
        Color for the value annotations.
    fontsize : int
        Font size for class labels and cell values.
    edge_color : str or tuple
        Color for the square borders.
    lw : float
        Line width for the square borders.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes with the plotted confusion matrix.
    """
    mat = np.array(mat)
    n = mat.shape[0]
    if class_names is None:
        class_names = [str(i) for i in range(n)]

    ax.clear()
    ax.set_aspect('equal')
    ax.set_xlim(0, n)
    ax.set_ylim(n, 0)  # invert y-axis so row 0 is at the top

    # draw squares and numbers
    for i in range(n):
        for j in range(n):
            color = diag_color if i == j else off_diag_color
            rect = Rectangle((j, i), 1, 1,
                             facecolor=color,
                             edgecolor=edge_color,
                             linewidth=lw)
            ax.add_patch(rect)
            ax.text(j + 0.5, i + 0.5,
                    str(mat[i, j]),
                    ha='center', va='center',
                    color=text_color,
                    fontsize=fontsize)

    # configure ticks
    ticks = np.arange(n) + 0.5
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(class_names, fontsize=fontsize)
    ax.set_yticklabels(class_names, fontsize=fontsize)

    # move x-axis labels to top
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # suppress both major and minor ticks (no tick marks)
    ax.minorticks_off()
    ax.tick_params(axis='both', which='both', length=0)

    # remove all spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    return ax

