import numpy as np
from typing import Callable
from numpy.typing import ArrayLike

# code modified from link below:
# https://github.com/nschloe/cplot/blob/52ffb4dc15a671f7c35c6f559511f2154cbf1a7c/src/cplot/_colors.py#L75

def get_srgb1(
    z: ArrayLike,
    abs_scaling: Callable[[np.ndarray], np.ndarray] = lambda x: x / (x + 1),
    saturation_adjustment: float = 1.28,
) -> np.ndarray:

    z = np.asarray(z)

    angle = np.arctan2(z.imag, z.real)
    absval_scaled = abs_scaling(np.abs(z))

    # We may have NaNs, so don't be too strict here.
    # assert np.all(absval_scaled >= 0)
    # assert np.all(absval_scaled <= 1)

    # from .create import find_max_srgb_radius
    # r0 = find_max_srgb_radius(oklab, L=0.5)
    r0 = 0.08499547839164734
    r0 *= saturation_adjustment

    # Rotate the angles such a "green" color represents positive real values. The
    # rotation is chosen such that the ratio g/(r+b) (in rgb) is the largest for the
    # point 1.0.
    offset = 0.8936868 * np.pi
    # Map (r, angle) to a point in the color space; bicone mapping similar to what
    # HSL looks like <https://en.wikipedia.org/wiki/HSL_and_HSV>.
    rd = r0 - r0 * 2 * abs(absval_scaled - 0.5)
    ok_coords = np.array(
        [
            absval_scaled,
            rd * np.cos(angle + offset),
            rd * np.sin(angle + offset),
        ]
    )
    xyz100 = oklab_to_xyz100(ok_coords)
    srgb1 = xyz100_to_srgb1(xyz100)

    return np.moveaxis(srgb1, 0, -1)


def oklab_to_xyz100(lab: np.ndarray) -> np.ndarray:
    M1 = np.array(
        [
            [0.8189330101, 0.3618667424, -0.1288597137],
            [0.0329845436, 0.9293118715, 0.0361456387],
            [0.0482003018, 0.2643662691, 0.6338517070],
        ]
    )
    M1inv = np.linalg.inv(M1)
    M2 = np.array(
        [
            [0.2104542553, +0.7936177850, -0.0040720468],
            [+1.9779984951, -2.4285922050, +0.4505937099],
            [+0.0259040371, +0.7827717662, -0.8086757660],
        ]
    )
    M2inv = np.linalg.inv(M2)
    # original code used npx.dot. Here I replaced npx.dot with np.tensordot
    return np.tensordot(M1inv, np.tensordot(M2inv, lab, 1) ** 3, 1) * 100


def _xyy_to_xyz100(xyy: np.ndarray) -> np.ndarray:
    x, y, Y = xyy
    return np.array([Y / y * x, Y, Y / y * (1 - x - y)]) * 100


def npx_solve(A: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Solves a linear equation system with a matrix of shape (n, n) and an array of
    shape (n, ...). The output has the same shape as the second argument.
    """
    # https://stackoverflow.com/a/48387507/353337
    x = np.asarray(x)
    return np.linalg.solve(A, x.reshape(x.shape[0], -1)).reshape(x.shape)


def xyz100_to_srgb_linear(xyz: np.ndarray) -> np.ndarray:
    primaries_xyy = np.array(
        [
            [0.64, 0.33, 0.2126],
            [0.30, 0.60, 0.7152],
            [0.15, 0.06, 0.0722],
        ]
    )
    invM = _xyy_to_xyz100(primaries_xyy.T)
    whitepoint_correction = True
    if whitepoint_correction:
        # The above values are given only approximately, resulting in the fact that
        # SRGB(1.0, 1.0, 1.0) is only approximately mapped into the reference
        # whitepoint D65. Add a correction here.
        whitepoints_cie1931_d65 = np.array([95.047, 100, 108.883])
        correction = whitepoints_cie1931_d65 / np.sum(invM, axis=1)
        invM = (invM.T * correction).T
    invM /= 100

    # https://en.wikipedia.org/wiki/SRGB#The_forward_transformation_(CIE_XYZ_to_sRGB)
    # https://www.color.org/srgb.pdf
    out = npx_solve(invM, xyz) / 100
    out = out.clip(0.0, 1.0)
    return out


def xyz100_to_srgb1(xyz: np.ndarray) -> np.ndarray:
    srgb = xyz100_to_srgb_linear(xyz)
    # gamma correction:
    a = 0.055
    is_smaller = srgb <= 0.0031308
    srgb[is_smaller] *= 12.92
    srgb[~is_smaller] = (1 + a) * srgb[~is_smaller] ** (1 / 2.4) - a
    return srgb