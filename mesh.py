import numpy as np


def normalized(a, axis=-1, order=2):
    n = np.atleast_1d(np.linalg.norm(a, order, axis))
    return a / n


class Mesh:
    def __init__(self,
            vertices, faces,
            attributes=None):
        assert attributes is None or len(vertices) == len(attributes)
        self.vertices = vertices
        self.faces = faces
        self.face_normals = None
        self.vertex_normals = None
        self.attributes = attributes

    def _face_normal(self, face) -> np.array:
        p0, p1, p2 = [self.vertices[i] for i in face]
        return normalized(np.cross(p2 - p0, p1 - p0))

    def compute_face_normals(self) -> None:
        self.face_normals = [self._face_normal(f) for f in self.faces]
