import numpy as np
from typing import Callable, Dict, Optional, Tuple

from mesh import Mesh

Resolution = Tuple[int, int]


def resolution(target: np.array) -> Resolution:
    shape = target.shape
    return shape[1], shape[0]


def edge_function(p0, p1, p2):
    ''' Calculates the signed area of the triangle (p0, p1, p2).
        The sign of the value tells which side of the line p0p1 that p2 lies.
        Defined as the cross product of <p2-p0> and <p1-p0>
    '''
    #return (p2.x - p0.x) * (p1.y - p0.y) - (p2.y - p0.y) * (p1.x - p0.x)
    return (p2[0] - p0[0]) * (p1[1] - p0[1]) - (p2[1] - p0[1]) * (p1[0] - p0[0])


def edge(p0, p1, p2):
    return np.cross(p2 - p0, p1 - p0)


def contains_point(p0, p1, p2, p):
    ''' Calculates the barycentric coordinates of the given point.
        Returns true if the point is inside this triangle,
        along with the color of that point calculated by interpolating the color
        of the triangle's vertices with the barycentric coordintes.
        Also returns the z-value of the point interpolated from the triangle's vertices.
    '''
    area = edge_function(p0, p1, p2)
    w0 =  edge_function(p1, p2, p)
    w1 = edge_function(p2, p0, p)
    w2 = edge_function(p0, p1, p)

    if area == 0:
        return False

    # Barycentric coordinates are calculated as the areas of the three sub-triangles divided
    # by the area of the whole triangle.
    alpha = w0 / area
    beta = w1 / area
    gamma = w2 / area

    return alpha >= 0 and beta >= 0 and gamma >= 0


def get_screen(clip: np.array, r: Resolution) -> np.array:
    width, height = r
    center = np.array([width / 2, height / 2, 0])
    scale = np.array([width / 2, -height / 2, 1])
    return center + clip * scale


def extend(vertices: np.array) -> np.array:
    return np.hstack([vertices, np.ones((len(vertices), 1))])


def to_clip(points: np.array) -> np.array:
    """Transforms vertices to clip space"""
    W = points[:, 3]
    return np.divide(points[:, :3], W[:, None])


def transform(matrix: np.array, vertices: np.array) -> np.array:
    return to_clip(np.dot(matrix, extend(vertices).T).T)


def draw_triangle(
        target: np.array,
        z_buffer: np.array,
        triangle: np.array,  # 3 rows with one vertex each
        fragment_shader: Callable,
        varying: Dict[str, np.array]):
    # drop z coordinate
    p0, p1, p2 = [p[:2] for p in triangle]

    # compute area 
    area = edge(p0, p1, p2)

    if area == 0:
        return

    width, height = resolution(target)
    xmin = int(max(min(p0[0], p1[0], p2[0]), 0))
    xmax = int(min(max(p0[0], p1[0], p2[0]), width)) + 1
    ymin = int(max(min(p0[1], p1[1], p2[1]), 0))
    ymax = int(min(max(p0[1], p1[1], p2[1]), height)) + 1

    x, y = np.meshgrid(range(xmin, xmax), range(ymin, ymax), indexing='xy')
    p = np.vstack([x.ravel(), y.ravel()]).T
    # Barycentric coordinates are calculated as the areas of the three sub-triangles divided
    # by the area of the whole triangle.
    barycentric = np.vstack([
        edge(p1, p2, p),
        edge(p2, p0, p),
        edge(p0, p1, p)
    ]).T / area

    # Find all indices of rows where all columns are positive
    is_inside = np.all(barycentric >= 0, axis=-1)

    # Fill pixels
    if not is_inside.any():  # numpy indexing does not like empty indices
        return

    # interpolate z
    z = np.sum(barycentric[is_inside] * triangle[:, 2].T, axis=1)[:, None]
    
    sx, sy = np.hsplit(p[is_inside], 2)
    zok = (z_buffer[sy, sx] > z).ravel()
    if not zok.any():
        return

    #import sys
    #print(zok.shape, sx.shape, sy.shape, barycentric[is_inside][zok].shape, file=sys.stderr)        

    # Interpolate vertex attributes
    interpolated = {k: np.sum(barycentric[is_inside][zok] * v, axis=1) for k, v in varying.items()}

    # Fill pixels
    xx, yy = sx[zok], sy[zok]
    target[yy, xx] = np.clip(255 * fragment_shader(interpolated).reshape(-1, 1, 3), 0, 255)
    z_buffer[yy, xx] = z[zok]


class Program:
    def __init__(self, vertex_shader, fragment_shader):
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader

    def render(self, target: np.array, z_buffer: np.array, mesh: Mesh, **uniforms):
        positions, outputs = self.vertex_shader(mesh.vertices, mesh.vertex_normals, uniforms)
        screen = get_screen(to_clip(positions), resolution(target))
        z_buffer.fill(np.inf)

        for face in mesh.faces:
            varying = {k: v[face] for k, v in outputs.items()}
            draw_triangle(
                target,
                z_buffer,
                screen[face],
                self.fragment_shader,
                varying)
