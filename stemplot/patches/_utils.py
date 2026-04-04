import numpy as np


def _add_rounded_corners(x_coords, y_coords, radius, closed=False):
    """
    Round corners of a polyline using quadratic Bezier curves.

    Parameters
    ----------
    x_coords, y_coords : array-like
        Coordinates of the path vertices.
    radius : float
        Corner rounding radius.
    closed : bool, optional
        If True, treat the path as a closed polygon (all corners rounded
        cyclically). If False (default), treat as an open polyline
        (start and end points are preserved unchanged).
    """
    points = np.column_stack([x_coords, y_coords])
    n = len(points)
    new_points = []

    if closed:
        for i in range(n):
            prev_p = points[(i - 1) % n]
            curr_p = points[i]
            next_p = points[(i + 1) % n]

            vec_in  = curr_p - prev_p
            vec_out = next_p - curr_p
            len_in  = np.linalg.norm(vec_in)
            len_out = np.linalg.norm(vec_out)

            valid_radius = min(radius, len_in / 2, len_out / 2)

            if valid_radius < 1e-3:
                new_points.append(curr_p)
                continue

            tan_in  = curr_p - (vec_in  / len_in)  * valid_radius
            tan_out = curr_p + (vec_out / len_out) * valid_radius

            t = np.linspace(0, 1, 20).reshape(-1, 1)
            curve = (1-t)**2 * tan_in + 2*(1-t)*t * curr_p + t**2 * tan_out
            new_points.extend(curve)
    else:
        new_points.append(points[0])
        for i in range(1, n - 1):
            prev_p = points[i - 1]
            curr_p = points[i]
            next_p = points[i + 1]

            vec_in  = curr_p - prev_p
            vec_out = next_p - curr_p
            len_in  = np.linalg.norm(vec_in)
            len_out = np.linalg.norm(vec_out)

            valid_radius = min(radius, len_in / 2, len_out / 2)

            if valid_radius < 1e-3:
                new_points.append(curr_p)
                continue

            tan_in  = curr_p - (vec_in  / len_in)  * valid_radius
            tan_out = curr_p + (vec_out / len_out) * valid_radius

            t = np.linspace(0, 1, 20).reshape(-1, 1)
            curve = (1-t)**2 * tan_in + 2*(1-t)*t * curr_p + t**2 * tan_out
            new_points.extend(curve)
        new_points.append(points[-1])

    result = np.array(new_points)
    return result[:, 0], result[:, 1]
