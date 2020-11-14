from pathlib import Path

import numpy as np

from mesh import Mesh


def is_comment(line: str) -> bool:
    return line.startswith('#')


def load_obj(path: Path) -> Mesh:
    vertices = []
    faces = []
    with open(path) as f:
        for line in f:
            if is_comment(line):
                continue
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                vertices.append([float(x.split('/')[0]) for x in parts[1:]])
            if parts[0] == 'f':
                faces.append([int(x.split('/')[0]) - 1 for x in parts[1:]])

    mesh = Mesh(np.array(vertices), faces)
    return mesh
