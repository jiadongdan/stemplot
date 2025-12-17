import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import os
import tempfile
from pathlib import Path
from PIL import Image, ImageSequence


def get_arrow_path(start, end, mode='line', radius=0):
    """
    Generates x and y coordinates for a path from start to end.

    Parameters:
    - start, end: tuples (x, y)
    - mode: 'line', 'hv', 'vh', 'hvh', 'vhv'
    - radius: radius for rounded corners (0 for sharp)
    """
    x1, y1 = start
    x2, y2 = end

    # --- 1. Generate Skeleton (Sharp Corners) ---
    if mode == 'line':
        x = [x1, x2]
        y = [y1, y2]

    elif mode == 'hv': # Horizontal -> Vertical
        x = [x1, x2, x2]
        y = [y1, y1, y2]

    elif mode == 'vh': # Vertical -> Horizontal
        x = [x1, x1, x2]
        y = [y1, y2, y2]

    elif mode == 'hvh': # Horiz -> Vert -> Horiz
        mid_x = (x1 + x2) / 2
        x = [x1, mid_x, mid_x, x2]
        y = [y1, y1, y2, y2]

    elif mode == 'vhv': # Vert -> Horiz -> Vert
        mid_y = (y1 + y2) / 2
        x = [x1, x1, x2, x2]
        y = [y1, mid_y, mid_y, y2]

    else:
        raise ValueError(f"Unknown mode: {mode}")

    # --- 2. Apply Rounded Corners ---
    if radius > 0 and mode != 'line':
        x, y = _add_rounded_corners(x, y, radius)

    return np.array(x), np.array(y)


def _add_rounded_corners(x_coords, y_coords, radius):
    """
    Internal helper to round corners using Quadratic Bezier curves.
    """
    points = np.column_stack([x_coords, y_coords])
    new_points = []

    # Start with the first point
    new_points.append(points[0])

    # Iterate over the intermediate corner points
    for i in range(1, len(points) - 1):
        prev_p = points[i-1]
        curr_p = points[i]
        next_p = points[i+1]

        # Calculate vectors for the two segments meeting at this corner
        vec_in = curr_p - prev_p
        vec_out = next_p - curr_p

        len_in = np.linalg.norm(vec_in)
        len_out = np.linalg.norm(vec_out)

        # Safety: Limit radius to half the shortest segment
        # to prevent the curve from overlapping with previous/next corners
        valid_radius = min(radius, len_in / 2, len_out / 2)

        # If segment is too short, treat as sharp corner
        if valid_radius < 1e-3:
            new_points.append(curr_p)
            continue

        # --- Geometry Calculation ---
        # 1. Find tangent points (start and end of the arc)
        # Move back from corner along input vector
        tan_in = curr_p - (vec_in / len_in) * valid_radius
        # Move forward from corner along output vector
        tan_out = curr_p + (vec_out / len_out) * valid_radius

        # 2. Generate smooth curve points (Quadratic Bezier)
        # This approximates a circular arc well enough for visuals
        t = np.linspace(0, 1, 20).reshape(-1, 1) # 20 points per corner

        # Bezier Formula: (1-t)^2*P0 + 2(1-t)t*P1 + t^2*P2
        # P0=tan_in, P1=curr_p (control), P2=tan_out
        curve = (1-t)**2 * tan_in + 2*(1-t)*t * curr_p + t**2 * tan_out

        # Add curve points (this automatically bridges the gap from the previous segment)
        new_points.extend(curve)

    # Add final point
    new_points.append(points[-1])

    # Return as separate x, y arrays
    result = np.array(new_points)
    return result[:, 0], result[:, 1]


def get_arrow_head(x, y, head_length, head_width=1.0, clip_curve=True):
    """
    Construct a triangular arrow head at the end of a curve, robust to
    non-uniform / dense sampling near the end.

    Parameters
    ----------
    x, y : array-like, shape (N,)
        Curve coordinates.
    head_length : float
        Target arrow-head length measured *along the curve* (in data units).
    head_width : float, default 1.0
        Relative width factor; 1.0 → base width ≈ head_length.
    clip_curve : bool, default True
        If True, the curve is truncated so it ends at the arrow base.
        If False, the original curve (x, y) is returned unchanged.

    Returns
    -------
    new_x, new_y : np.ndarray
        Curve coordinates (possibly truncated if clip_curve=True).
    tip : (float, float)
        Tip of the arrow head (end of the original curve).
    left : (float, float)
        Left base vertex of the arrow head.
    right : (float, float)
        Right base vertex of the arrow head.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("x and y must be 1D arrays of the same length.")
    if x.size < 2:
        raise ValueError("Need at least two points to define a curve.")

    # Stack into points: P[0..N-1]
    P = np.column_stack((x, y))

    # Segment vectors and lengths
    seg_vecs = P[1:] - P[:-1]             # shape (N-1, 2)
    seg_lens = np.hypot(seg_vecs[:, 0], seg_vecs[:, 1])

    total_len = seg_lens.sum()
    if total_len == 0:
        raise ValueError("All points are identical; zero-length curve.")

    # Effective head length cannot exceed total curve length
    eff_head_len = min(head_length, total_len)

    # Arc-length position of the arrow base from the start
    s_base = total_len - eff_head_len

    # Cumulative lengths at each vertex: cum[i] = length up to P[i]
    cum = np.concatenate(([0.0], np.cumsum(seg_lens)))  # shape (N,)

    # Find segment containing s_base
    # We want index i such that cum[i] <= s_base <= cum[i+1]
    i = np.searchsorted(cum, s_base, side="right") - 1
    i = max(0, min(i, len(seg_lens) - 1))  # clamp just in case

    seg_len = seg_lens[i]
    if seg_len == 0:
        # degenerate segment; fall back to using last non-zero segment backwards
        j = np.max(np.where(seg_lens > 0)[0])
        i = int(j)
        seg_len = seg_lens[i]

    # Position of base along this segment
    s_in_seg = s_base - cum[i]
    t = s_in_seg / seg_len  # fraction along segment i → i+1

    base = P[i] + t * seg_vecs[i]   # base center of arrow head
    tip = P[-1]                     # end of the curve

    # Direction from base to tip (tangent for the arrow)
    dir_vec = tip - base
    L = np.hypot(dir_vec[0], dir_vec[1])
    if L == 0:
        raise ValueError("Tip and base coincide; cannot define arrow direction.")
    tx, ty = dir_vec / L

    # Perpendicular (left-hand)
    px, py = -ty, tx

    # Use the straight-line base→tip distance as actual head height
    head_h = L
    half_width = 0.5 * head_h * head_width

    left = (base[0] + half_width * px,
            base[1] + half_width * py)
    right = (base[0] - half_width * px,
             base[1] - half_width * py)

    head = np.array([tip, left, right])

    # Optionally truncate the curve so it stops at the base
    if clip_curve:
        new_P = np.vstack([P[:i+1], base])
        new_x, new_y = new_P[:, 0], new_P[:, 1]
    else:
        new_x, new_y = x.copy(), y.copy()

    return new_x, new_y, head

def get_arrow(start, end, radius, head_length, head_width=1.0, mode='line', clip_curve=True):
    x, y = get_arrow_path(start, end, mode=mode, radius=radius)
    x_new, y_new, head = get_arrow_head(x, y, head_length, head_width, clip_curve=clip_curve)
    return x_new, y_new, head


def gif_chroma_to_transparent(in_path, out_path, bg_rgb=(255, 0, 255)):
    """
    Convert a GIF with a solid background color to a GIF with transparency.

    Parameters
    ----------
    in_path : str or Path
        Input GIF with a uniform background (e.g. magenta).
    out_path : str or Path
        Output GIF with that background turned transparent.
    bg_rgb : tuple of (R, G, B)
        Background color to treat as transparent (0–255).
    """
    in_path = Path(in_path)
    out_path = Path(out_path)

    im = Image.open(in_path)

    frames = []
    r0, g0, b0 = bg_rgb

    for frame in ImageSequence.Iterator(im):
        fr = frame.convert("RGBA")
        data = fr.getdata()
        new_data = []
        for (r, g, b, a) in data:
            if (r, g, b) == (r0, g0, b0):
                new_data.append((r, g, b, 0))   # fully transparent
            else:
                new_data.append((r, g, b, a))
        fr.putdata(new_data)
        frames.append(fr)

    duration = im.info.get("duration", 50)

    frames[0].save(
        out_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
        disposal=2,   # clear to background between frames
    )


def flow_arrow_animation(
        x,
        y,
        head,
        dash_on_length=10,
        dash_off_length=5,
        interval=50,
        color="cornflowerblue",
        lw=3,
        ax_off=True,
        save_path=None,
        make_transparent=False,
        chroma_bg_rgb=(255, 0, 255),
):
    """
    Create a flowing dashed-line animation with an arrow head at the end
    of a given curve.

    If make_transparent=True and save_path is a GIF, this function:
      1) Renders a normal GIF on a chroma-key background (chroma_bg_rgb).
      2) Post-processes it so that chroma_bg_rgb becomes transparent.

    Parameters
    ----------
    x, y : array-like
        Coordinates of the curve.
    head : array-like, shape (3, 2)
        Triangle vertices of the arrow head in data coordinates.
    dash_on_length : float, optional
        Dash length (in points) for the visible segments.
    dash_off_length : float, optional
        Gap length (in points) for the invisible segments.
    interval : int, optional
        Delay between frames in milliseconds.
    color : str, optional
        Line and arrowhead color.
    lw : float, optional
        Line width.
    ax_off : bool, optional
        If True, turn off axes for a cleaner look.
    save_path : str or Path or None, optional
        If not None, save the animation to this path.
    make_transparent : bool, optional
        If True and save_path is a GIF, post-process to transparent GIF.
    chroma_bg_rgb : tuple of (R, G, B)
        Background color (0–255) used as chroma key when make_transparent=True.

    Returns
    -------
    fig : matplotlib.figure.Figure
    ax : matplotlib.axes.Axes
    ani : matplotlib.animation.FuncAnimation
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    head = np.asarray(head, dtype=float)

    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("x and y must be 1D arrays of the same length.")
    if x.size < 2:
        raise ValueError("Need at least two points for a curve.")
    if head.shape != (3, 2):
        raise ValueError("head must be an array of shape (3, 2).")

    # Decide rendering background
    if make_transparent:
        # Use chroma-key background (e.g. magenta) for post-processing
        bg_rgb = chroma_bg_rgb
    else:
        # Use white background for normal GIF
        bg_rgb = (255, 255, 255)

    # Convert 0–255 RGB to Matplotlib [0–1] floats
    bg_color = tuple(c / 255.0 for c in bg_rgb)

    # 1. Setup the Plot
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Add a small margin around data
    x_span = x.max() - x.min()
    y_span = y.max() - y.min()
    x_margin = 0.05 * (x_span if x_span > 0 else 1.0)
    y_margin = 0.1 * (y_span if y_span > 0 else 1.0)

    ax.set_xlim(x.min() - x_margin, x.max() + x_margin)
    ax.set_ylim(y.min() - y_margin, y.max() + y_margin)
    if ax_off:
        ax.axis("off")
    ax.set_aspect("equal", adjustable="box")

    # 2. Create Artists
    (line,) = ax.plot(x, y, color=color, lw=lw, antialiased=False)
    arrow_head = ax.fill(head[:, 0], head[:, 1], color=color, antialiased=False)[0]

    # 3. Dash pattern + animation config
    dash_pattern = (dash_on_length, dash_off_length)
    pattern_period = dash_on_length + dash_off_length

    def init():
        line.set_linestyle((0, dash_pattern))
        return line, arrow_head

    def update(frame):
        current_offset = -frame
        line.set_linestyle((current_offset, dash_pattern))
        return line, arrow_head

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=np.arange(0, pattern_period),
        init_func=init,
        interval=interval,
        blit=False,
        repeat=True,
    )

    # 4. Optional save
    if save_path is not None:
        save_path = Path(save_path)
        fps = max(1, int(1000 / interval))

        is_gif = save_path.suffix.lower() == ".gif"
        if not (make_transparent and is_gif):
            # Simple case: no transparency or non-GIF target
            ani.save(
                save_path,
                writer="pillow",
                fps=fps,
                savefig_kwargs={
                    "transparent": False,
                    "facecolor": bg_color,
                },
            )
        else:
            # Transparent GIF: save to temp with chroma background, then post-process
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_gif = Path(tmpdir) / "tmp_flow.gif"
                ani.save(
                    tmp_gif,
                    writer="pillow",
                    fps=fps,
                    savefig_kwargs={
                        "transparent": False,
                        "facecolor": bg_color,
                    },
                )
                gif_chroma_to_transparent(tmp_gif, save_path, bg_rgb=chroma_bg_rgb)

    return fig, ax, ani




