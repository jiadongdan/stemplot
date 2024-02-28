import string

def ax_add_text(ax, x=None, y=None, s=None, loc=None, **kwargs):
    if loc is None:
        if 'ha' not in kwargs:
            kwargs['ha'] = 'center'
        if 'va' not in kwargs:
            kwargs['va'] = 'center'
        ax.text(x=x, y=y, s=s, **kwargs)
    else:
        if loc == 'top left':
            ax.text(x=0., y=1., s=s, ha='left', va='bottom', transform=ax.transAxes, **kwargs)
        elif loc == 'top center':
            x, y = 0.5, 1
            ax.text(x=0.5, y=1., s=s, ha='center', va='bottom', transform=ax.transAxes, **kwargs)
        elif loc == 'top right':
            ax.text(x=1., y=1., s=s, ha='right', va='bottom', transform=ax.transAxes, **kwargs)
        else:
            ax.text(x=x, y=y, s=s, ha='right', va='bottom', transform=ax.transAxes, **kwargs)



def auto_letters(artists, letters=None, uppercase=False, pad=0.03, **kwargs):
    font_letter = {'family': 'Arial', 'color': 'black', 'weight': 'bold', 'size': 8,}
    n = len(artists)
    if letters is None:
        if uppercase:
            letters = list(string.ascii_uppercase)[0:n]
        else:
            letters = list(string.ascii_lowercase)[0:n]
    else:
        if uppercase:
            letters = [letter.upper() for letter in letters]
        else:
            letters = [letter.lower() for letter in letters]
    ts = []
    for letter, ax in zip(letters, artists):
        t = ax.text(x=-0.01, y=1., s=letter, ha='right', va='top', transform=ax.transAxes, fontdict=font_letter, **kwargs)
        ts.append(t)
    return ts


def fig_add_letter(fig, x, y, s='a', **kwargs):
    font_letter = {'family': 'Arial', 'color': 'black', 'weight': 'bold', 'size': 8,}
    if 'fontdict' not in kwargs:
        kwargs['fontdict'] = font_letter
    if 'transform' not in kwargs:
        kwargs['transform'] = fig.transFigure
    fig.text(x, y, s=s, ha='left', va='top', **kwargs)


def fig_add_text(fig, x, y, s, **kwargs):
    if 'ha' not in kwargs:
        kwargs['ha'] = 'center'
    if 'va' not in kwargs:
        kwargs['va'] = 'center'
    if 'transform' not in kwargs:
        kwargs['transform'] = fig.transFigure
    fig.text(x, y, s, **kwargs)

