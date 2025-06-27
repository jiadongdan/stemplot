from ._utils import get_ax_aspect
from ._utils import get_fig_aspect
from ._utils import get_size_inches
from ._utils import ax_off
from ._utils import remove_axis_top_right
from ._layout import h_axes
from ._layout import get_top_from_axes
from ._layout import merge_axes
from ._layout import axes_from_ax
from ._single_axis import generate_ax
from ._single_axis import set_xlabel_fontsize
from ._single_axis import set_ylabel_fontsize
from ._ticks import remove_minor_ticks

__all__ = ['get_ax_aspect',
           'get_fig_aspect',
           'get_size_inches',
           'ax_off',
           'remove_axis_top_right',
           'h_axes',
           'get_top_from_axes',
           'merge_axes',
           'axes_from_ax',
           'generate_ax',
           'set_xlabel_fontsize',
           'set_ylabel_fontsize',
           'remove_minor_ticks',
           ]