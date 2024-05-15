# Version should always be readily available.
__version__ = '0.1.0'

# Lazy loading for sub-packages.
class _LazyLoader:
    def __init__(self, package_name):
        self._package_name = package_name
        self._module = None

    def _load(self):
        if self._module is None:
            self._module = __import__(self._package_name, globals(), locals(), ['*'])
        return self._module

    def __getattr__(self, name):
        module = self._load()
        return getattr(module, name)

    def __dir__(self):
        module = self._load()
        return dir(module)

# Setup lazy loading for sub-packages.
colors = _LazyLoader('stemplot.colors')
arrows = _LazyLoader('stemplot.arrows')
layout = _LazyLoader('stemplot.layout')

# Explicit imports for frequently used functions or classes
# These are assumed to be lightweight and commonly used enough to justify immediate loading.
from stemplot.colors._colors import colors_from_lbs  # Assuming colors_from_lbs is lightweight
from stemplot.layout._layout import h_axes
from stemplot.patches._polygon import ax_add_gradient_polygon
from stemplot.utils._plot_density import plot_density
from stemplot.interactive._data_explorer import interactive_data
from stemplot.interactive._data_slicer import imshow
from stemplot.interactive._data_slicer import plot
from stemplot.utils._plot_pca import plot_pca


__all__ = ['colors',
           'arrows',
           'layout',
           'colors_from_lbs',
           'h_axes',
           'ax_add_gradient_polygon',
           'plot_density',
           'interactive_data',
           'imshow',
           'plot',
           'plot_pca',
           ]