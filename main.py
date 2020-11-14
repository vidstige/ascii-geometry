from pathlib import Path
import sys

import numpy as np

from mesh import Mesh
from mesh_io import load_obj
from pygl import render
import numgl

def main():
    mesh = load_obj(Path('meshes/cube.obj'))
    w, h = 320, 200
    buffer = np.zeros((h, w, 3), dtype=np.uint8)
    projection = numgl.perspective(90, w/h, 0.1, 5)
    camera = numgl.lookat(np.array([0, 0, -10]), np.array([0, 0, 0]), np.array([0, 1, 0]))
    render(buffer, mesh, mvp=projection @ camera)

    for _ in range(1024):
        sys.stdout.buffer.write(buffer.tobytes())
    

main()
