import numpy as np
from typing import Callable, Optional, Tuple

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


class RenderTarget(object):
    def __init__(self, img: np.array):
        self.img = img

    def pixel(self, x, y, color):
        self.img[int(x), int(y)] = color

    def triangle(self, t, color):
        p0, p1, p2 = [np.array(x).ravel().astype(int) for x in t]
        width, height = self.img.shape[1], self.img.shape[0]
        # First calculate a bounding box for this triangle so we don't have to iterate over the entire image
        # Clamped to the bounds of the image
        xmin = max(min(p0[0], p1[0], p2[0]), 0)
        xmax = min(max(p0[0], p1[0], p2[0]), width)
        ymin = max(min(p0[1], p1[1], p2[1]), 0)
        ymax = min(max(p0[1], p1[1], p2[1]), height)

        # Iterate over all pixels in the bounding box, test if they lie inside in the triangle
        # If they do, set that pixel with the barycentric color of that point
        for x in range(xmin, xmax):
            for y in range(ymin, ymax):
                if contains_point(p0, p1, p2, (x, y, 1, 1)):
                    self.img[y, x] = color


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
        triangle: Tuple[int, int, int],
        attributes: np.array):
    # drop z coordinate
    p0, p1, p2 = [p[:2] for p in triangle]

    # compute area 
    area = edge(p0, p1, p2)

    if area == 0:
        return

    width, height = resolution(target)
    xmin = int(max(min(p0[0], p1[0], p2[0]), 0))
    xmax = int(min(max(p0[0], p1[0], p2[0]), width))
    ymin = int(max(min(p0[1], p1[1], p2[1]), 0))
    ymax = int(min(max(p0[1], p1[1], p2[1]), height))

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

    # Compute indices of all points inside triangle
    #stride = np.array([4, target.get_stride()])
    #indices = np.dot(p[is_inside], stride)

    # Interpolate vertex attributes
    if attributes:
        attrs = np.dot(barycentric[is_inside], attributes)

    # Fill pixels
    sx, sy = np.hsplit(p[is_inside], 2)
    target[sy, sx, :] = (255, 255, 255)
    #for index, a in zip(indices, attrs):
    #    r, g, b = 1, 1, 1
    #    data[index + 0] = r
    #   data[index + 1] = g
    #    data[index + 2] = b


def render(target: np.array, model: Mesh, mvp: np.array):
    # transform points to camera space and divide into clip space
    clip_vertices = transform(mvp, model.vertices)
    # scale and transform into screen space
    screen = get_screen(clip_vertices, resolution(target))

    for face in model.faces:
        draw_triangle(
            target,
            screen[face],
            model.attributes[face] if model.attributes else None)

    #for s in screen:
    #    x, y, z, w = s[0,0], s[0,1], s[0,2], s[0,3]
    #    target.pixel(x, y, color=(255, 0, 255, 255))
    
