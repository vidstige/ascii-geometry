import numpy as np


def normalized(a, axis=-1, order=2):
    n = np.atleast_1d(np.linalg.norm(a, order, axis))
    return a / n


class Mesh:
    def __init__(self, vertices, faces, vertex_normals=None):
        self.vertices = vertices
        self.faces = faces
        self.face_normals = None
        self.vertex_normals = vertex_normals

    def _face_normal(self, face) -> np.array:
        p0, p1, p2 = [self.vertices[i] for i in face]
        return normalized(np.cross(p2 - p0, p1 - p0))

    def compute_face_normals(self) -> None:
        self.face_normals = [self._face_normal(f) for f in self.faces]

    def compute_vertex_normals(self) -> None:
        self.compute_face_normals()
        normals = np.zeros(self.vertices.shape)
        for face, face_normal in zip(self.faces, self.face_normals):
            normals[face] += face_normal

        self.vertex_normals = normalized(normals, axis=0)