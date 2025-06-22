import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def is_arial_installed():
    """
    Check whether the Arial font family is available to Matplotlib.

    Returns
    -------
    bool
        True if any registered font name contains "Arial", False otherwise.
    """
    return any("Arial" in font.name for font in fm.fontManager.ttflist)


def is_helvetica_installed():
    """
    Check whether the Helvetica font family is available to Matplotlib.

    Returns
    -------
    bool
        True if any registered font name contains "Helvetica", False otherwise.
    """
    return any("Helvetica" in font.name for font in fm.fontManager.ttflist)


def which_fonts(fig):
    """
    Scan a Matplotlib Figure, print each text string with its resolved font name,
    and return a dict mapping text → font.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to inspect.

    Returns
    -------
    dict[str, str]
        Mapping from text content to the font family name.
    """
    fonts = {}

    # 1) Any top-level fig.text
    for txt in fig.texts:
        name = txt.get_text()
        font = txt.get_fontproperties().get_name()
        print(f'Figure text "{name}" → {font}')
        fonts[name] = font

    # 2) Inspect each Axes
    for i, ax in enumerate(fig.get_axes(), start=1):
        # Titles & axis labels
        for label, txt in (("Title", ax.title),
                           ("X label", ax.xaxis.label),
                           ("Y label", ax.yaxis.label)):
            name = txt.get_text()
            font = txt.get_fontproperties().get_name()
            print(f'Axes {i} {label} "{name}" → {font}')
            fonts[name] = font

        # Tick labels
        for txt in ax.get_xticklabels():
            name = txt.get_text()
            font = txt.get_fontproperties().get_name()
            print(f'Axes {i} X-tick "{name}" → {font}')
            fonts[name] = font
        for txt in ax.get_yticklabels():
            name = txt.get_text()
            font = txt.get_fontproperties().get_name()
            print(f'Axes {i} Y-tick "{name}" → {font}')
            fonts[name] = font

        # Legend entries
        leg = ax.get_legend()
        if leg:
            for txt in leg.get_texts():
                name = txt.get_text()
                font = txt.get_fontproperties().get_name()
                print(f'Axes {i} Legend "{name}" → {font}')
                fonts[name] = font

    return fonts