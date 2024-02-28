import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def get_five_vertices(start, end, scale=0.2):
    start = np.array(start)
    end = np.array(end)
    mid = (start + end)/2
    L = np.abs(start[0] - end[0])
    p1 = np.array([start[0]+L*scale, start[1]])
    p2 = np.array([end[0]-L*scale, end[1]])
    return np.vstack([start, p1, mid, p2, end])

def get_flow_patch(s1, e1, s2, e2, scale=0.2, **kwargs):
    v1 = get_five_vertices(s1, e1, scale)
    v2 = get_five_vertices(s2, e2, scale)
    v2 = np.flipud(v2)
    verts = np.vstack([v1, v2])
    codes = [1, 3, 3, 3, 3, 2, 3, 3, 3, 3]
    path = Path(verts, codes)
    patch = PathPatch(path, **kwargs)
    return patch

def connect_by_flow_patch(rect1, rect2, f=0.5):
    pass