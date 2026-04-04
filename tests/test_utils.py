import importlib.util
import pathlib

import numpy as np
import pytest

# Load _utils directly to avoid heavy top-level stemplot imports
_utils_path = pathlib.Path(__file__).parent.parent / "stemplot" / "patches" / "_utils.py"
_spec = importlib.util.spec_from_file_location("_utils", _utils_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_add_rounded_corners = _mod._add_rounded_corners


# --- Open path (closed=False) ---

def test_open_preserves_endpoints():
    """First and last points must be exactly unchanged."""
    x, y = _add_rounded_corners([0, 50, 50], [0, 0, 50], radius=10)
    assert (x[0], y[0]) == (0.0, 0.0)
    assert (x[-1], y[-1]) == (50.0, 50.0)


def test_open_output_within_bounding_box():
    """Rounded curve must not overshoot the original shape's extents."""
    x, y = _add_rounded_corners([0, 100, 100], [0, 0, 100], radius=20)
    assert x.min() >= 0 and x.max() <= 100
    assert y.min() >= 0 and y.max() <= 100


def test_open_more_points_than_input():
    """Bezier interpolation should produce more points than the 3 input vertices."""
    x, y = _add_rounded_corners([0, 50, 50], [0, 0, 50], radius=10)
    assert len(x) > 3


def test_open_zero_radius_no_rounding():
    """With radius=0 all corners fall below threshold, output matches input."""
    x_in = [0, 50, 50]
    y_in = [0, 0, 50]
    x, y = _add_rounded_corners(x_in, y_in, radius=0)
    np.testing.assert_allclose(x, x_in)
    np.testing.assert_allclose(y, y_in)


def test_open_radius_larger_than_segment_clamped():
    """A very large radius gets clamped to half the shortest segment — no crash."""
    x, y = _add_rounded_corners([0, 10, 10], [0, 0, 10], radius=1000)
    assert len(x) > 0
    assert not np.any(np.isnan(x)) and not np.any(np.isnan(y))


def test_open_collinear_points():
    """Collinear points form no real corner; output should still be valid."""
    x, y = _add_rounded_corners([0, 50, 100], [0, 0, 0], radius=10)
    assert len(x) > 0
    assert not np.any(np.isnan(x)) and not np.any(np.isnan(y))


# --- Closed polygon (closed=True) ---

def test_closed_point_count_rectangle():
    """Each of the 4 corners of a rectangle should produce 20 Bezier points."""
    x, y = _add_rounded_corners([0, 1, 1, 0], [0, 0, 1, 1], radius=0.1, closed=True)
    assert len(x) == 4 * 20


def test_closed_output_within_bounding_box():
    """Rounded closed polygon must not overshoot the original extents."""
    x, y = _add_rounded_corners([0, 1, 1, 0], [0, 0, 1, 1], radius=0.1, closed=True)
    assert x.min() >= 0 and x.max() <= 1
    assert y.min() >= 0 and y.max() <= 1


def test_closed_no_nan_or_inf():
    """Output must contain no NaN or infinite values."""
    x, y = _add_rounded_corners([0, 1, 1, 0], [0, 0, 1, 1], radius=0.2, closed=True)
    assert np.all(np.isfinite(x)) and np.all(np.isfinite(y))


def test_closed_zero_radius_sharp_corners():
    """With radius=0 all corners are below threshold; one point per corner."""
    x, y = _add_rounded_corners([0, 1, 1, 0], [0, 0, 1, 1], radius=0, closed=True)
    assert len(x) == 4
