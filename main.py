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

    wy = 0.01
    wx = 0.03
    for a in range(1024):
        camera = numgl.translate((0,0, -10)) @ numgl.roty(a * wy) @ numgl.rotx(a * wx)
        buffer.fill(0)
        render(buffer, mesh, mvp=projection @ camera)
        sys.stdout.buffer.write(buffer.tobytes())
    

main()
