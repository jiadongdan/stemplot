from ._color_data import cc
#from ._colors import colors_from_lbs
#from ._colors import generate_colors_from_lbs
#from ._colors import xy2colors
from ._colors_labels import colors_from_lbs
from ._colors_labels import reassign_lbs
from ._colormaps import color_palette
from ._colormaps import color_mix
from ._colormaps import get_cmap_from_colors


__all__ = ['cc',
           'colors_from_lbs',
           'reassign_lbs',
           'color_palette',
           'color_mix',
           'get_cmap_from_colors',
           ]
