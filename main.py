from pathlib import Path
import sys

import numpy as np

from mesh import Mesh
from mesh_io import load_obj
from pygl import Program
import numgl

def vec4(v3, scalar):
    return np.hstack([v3, scalar * np.ones(shape=(len(v3), 1))])

# Only called _once_ per render, should compute all vertices
def vertex_shader(positions_in, normals_in, uniforms):
    projection = uniforms['projection']
    model_view = uniforms['model_view']
    mvp = projection @ model_view
    light = uniforms['light1']
    positions = mvp @ vec4(positions_in, 1).T
    normals = np.linalg.inv(model_view).T @ vec4(normals_in, 0).T
    return positions.T, {'intensity': np.sum(normals.T * light, axis=1)}

def fragment_shader(inputs):
    intensity = inputs['intensity']
    return np.vstack([intensity, intensity, intensity]).T
    #return (255, 255, 255)


def main():
    mesh = load_obj(Path('meshes/cube.obj'))
    mesh.compute_vertex_normals()
    print(mesh.vertex_normals, file=sys.stderr)
    w, h = 320, 200
    buffer = np.zeros((h, w, 3), dtype=np.uint8)
    program = Program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    projection = numgl.perspective(90, w/h, 0.1, 5)
    wy = 0.01
    wx = 0.03
    for a in range(1024):
        camera = numgl.translate((0, 0, -10)) @ numgl.roty(a * wy) @ numgl.rotx(a * wx)
        buffer.fill(0)
        program.render(buffer, mesh, projection=projection, model_view=camera, light1=np.array([0, 0, -1, 0]))
        sys.stdout.buffer.write(buffer.tobytes())


main()
