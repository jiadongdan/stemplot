import warnings
import os

def save_fig(fig, filepath='fig.png', dpi=300, transparent=None, format=None, **savefig_kwargs):
    """
    Save a Matplotlib Figure with trimmed whitespace, supporting multiple formats.
    Defaults to transparent background for PNG, SVG, and PDF if not specified.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure object to save.
    filepath : str, optional
        Path and filename for the saved image (extension determines format, e.g., '.png', '.pdf').
    dpi : int, optional
        Resolution in dots per inch (default: 300).
    transparent : bool or None, optional
        Whether to save with a transparent background.
        If None, PNG, SVG, and PDF outputs default to True; other formats default to False.
    format : str or None, optional
        Explicit format string (e.g., 'png', 'pdf'). If None, inferred from `filepath` extension.
    **savefig_kwargs
        Any additional keyword arguments passed directly to `fig.savefig`.

    Examples
    --------
    >>> save_fig(fig, 'figure.png')
    >>> save_fig(fig, 'figure.svg')
    >>> save_fig(fig, 'figure.pdf', dpi=600)
    >>> save_fig(fig, 'figure.eps', transparent=False)
    """
    # Suppress tight_layout warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        try:
            fig.tight_layout(pad=0)
        except Exception:
            pass

    # Determine output format
    out_format = (format or os.path.splitext(filepath)[1].lstrip('.')).lower()

    # Set transparency default: True for PNG, SVG, and PDF; False otherwise, unless explicitly provided
    if transparent is None:
        transparent_flag = True if out_format in ('png', 'svg', 'pdf') else False
    else:
        transparent_flag = transparent

    # Build save parameters
    save_params = {
        'dpi': dpi,
        'transparent': transparent_flag,
        'bbox_inches': 'tight',
        'pad_inches': 0.05,
    }

    if format:
        save_params['format'] = format

    # Merge any additional kwargs
    save_params.update(savefig_kwargs)

    # Save the figure
    fig.savefig(filepath, **save_params)

