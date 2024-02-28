import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def get_five_vertices(start, end, scale=0.2, mode='h'):
    start = np.array(start)
    end = np.array(end)
    mid = (start + end)/2
    x1, y1 = start
    x2, y2 = end
    # dx and dy have signs
    dx = x2 - x1
    dy = y2 - y1
    if mode == 'h':
        p1 = np.array([x1 + dx * scale, y1])
        p2 = np.array([x2 - dx * scale, y2])
        return np.vstack([start, p1, mid, p2, end])
    elif mode == 'v':
        p1 = np.array([x1, y1 + dy * scale])
        p2 = np.array([x2, y2 - dy * scale])
        return np.vstack([start, p1, mid, p2, end])
    else:
        raise ValueError("mode can only be either 'h' or 'v'")


def get_head_direction(start, end, mode):
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    if dx > 0 and dy > 0:
        if mode == 'h':
            direction = 'right'
        else:
            direction = 'up'
    elif dx > 0 and dy < 0:
        if mode == 'h':
            direction = 'right'
        else:
            direction = 'down'
    elif dx < 0 and dy > 0:
        if mode == 'h':
            direction = 'left'
        else:
            direction = 'up'
    elif dx < 0 and dy < 0:
        if mode == 'h':
            direction = 'left'
        else:
            direction = 'down'
    elif dx == 0 and dy > 0:
        direction = 'up'
    elif dx == 0 and dy < 0:
        direction = 'down'
    elif dy == 0 and dx > 0:
        direction = 'right'
    elif dy == 0 and dx < 0:
        direction = 'left'
    return direction

def get_head_pts(p1, p2, scale=0.5, direction='right'):
    x1, y1 = p1
    x2, y2 = p2
    dx = np.abs(x1 - x2)
    dy = np.abs(y1 - y2)
    lx = (0.5 + scale) * np.sqrt(3) * dy
    ly = (0.5 + scale) * np.sqrt(3) * dx
    if direction == 'right':
        if y1 > y2:
            q1 = (x1, y1+dy*scale)
            q2 = (x2, y2-dy*scale)
            q = (x1+lx, (y1+y2)/2)
        else:
            q1 = (x1, y1-dy*scale)
            q2 = (x2, y2+dy*scale)
            q = (x1+lx, (y1+y2)/2)
    elif direction == 'left':
        if y1 > y2:
            q1 = (x1, y1+dy*scale)
            q2 = (x2, y2-dy*scale)
            q = (x1-lx, (y1+y2)/2)
        else:
            q1 = (x1, y1-dy*scale)
            q2 = (x2, y2+dy*scale)
            q = (x1-lx, (y1+y2)/2)
    elif direction == 'up':
        if x1 > x2:
            q1 = (x1 + dx * scale, y1)
            q2 = (x2 - dx * scale, y2)
            q = ((x1 + x2) / 2, y1+ly)
        else:
            q1 = (x1 - dx * scale, y1)
            q2 = (x2 + dx * scale, y2)
            q = ((x1 + x2) / 2, y1 + ly)
    elif direction == 'down':
        if x1 > x2:
            q1 = (x1 + dx * scale, y1)
            q2 = (x2 - dx * scale, y2)
            q = ((x1 + x2) / 2, y1 - ly)
        else:
            q1 = (x1 - dx * scale, y1)
            q2 = (x2 + dx * scale, y2)
            q = ((x1 + x2) / 2, y1 - ly)

    return np.array([q1, q, q2])


def update_end_points(p1, p2, scale=0.5, direction='right'):
    x1, y1 = p1
    x2, y2 = p2
    dx = np.abs(x1 - x2)
    dy = np.abs(y1 - y2)
    lx = (0.5 + scale) * np.sqrt(3) * dy
    ly = (0.5 + scale) * np.sqrt(3) * dx

    if direction == 'right':
        return (x1-lx, y1), (x2-lx, y2)
    elif direction == 'left':
        return (x1+lx, y1), (x2+lx, y2)
    elif direction == 'up':
        return (x1, y1-ly), (x2, y2-ly)
    elif direction == 'down':
        return (x1, y1+ly), (x2, y2+ly)



def get_arrow_path(start, end, w1=0.015, w2=0.01, mode='h', scale=0.2, head_scale=0.5, **kwargs):
    direction = get_head_direction(start, end, mode)

    x1, y1 = start
    x2, y2 = end

    # two start points, s1 and s2
    s1 = (x1, y1 + w1 / 2)
    s2 = (x1, y1 - w1 / 2)

    # two end points, e1 and e2
    e1 = (x2, y2 + w2 / 2)
    e2 = (x2, y2 - w2 / 2)

    # update e1 and e2 due to head length
    e1, e2 = update_end_points(e1, e2, head_scale, direction)

    v1 = get_five_vertices(s1, e1, scale, mode)
    v2 = get_five_vertices(s2, e2, scale, mode)
    v2 = np.flipud(v2)

    v3 = get_head_pts(v1[-1], v2[0], direction=direction)
    verts = np.vstack([v1, v3, v2, v1[0]])
    codes = [1, 3, 3, 3, 3, 2, 2, 2, 2, 3, 3, 3, 3, 79]
    path = Path(verts, codes)
    patch = PathPatch(path, **kwargs)
    return patch