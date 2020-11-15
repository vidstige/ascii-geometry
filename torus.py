import numpy as np

from mesh import Mesh

TAU = 2 * np.pi

def tesselate(shape):
    """Tesselates the grid with faces"""
    # a b
    # c d
    n = np.prod(shape)
    indices = np.arange(n).reshape(shape)
    a = indices.ravel()
    b = np.roll(indices, 1, axis=1).ravel()
    c = np.roll(indices, 1, axis=0).ravel()
    d = np.roll(np.roll(indices, 1, axis=0), 1, axis=1).ravel()
    top = np.vstack([a, d, b])
    bottom = np.vstack([a, c, d])
    return np.hstack([top, bottom]).T


def torus(R: float, r: float, a, b) -> Mesh:
    # all points to evaluate
    theta, phi = np.meshgrid(np.linspace(0, TAU, a, endpoint=False), np.linspace(0, TAU, b, endpoint=False), indexing='ij')
    x = (R + r * np.cos(theta)) * np.cos(phi)
    y = (R + r * np.cos(theta)) * np.sin(phi)
    z = r * np.sin(theta)
    vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
    
    nx = np.cos(phi) * np.cos(theta)
    ny = np.sin(phi) * np.cos(theta)
    nz = np.sin(theta)
    normals = -np.vstack([nx.ravel(), ny.ravel(), nz.ravel()]).T
    return Mesh(vertices, tesselate(theta.shape), vertex_normals=normals)

