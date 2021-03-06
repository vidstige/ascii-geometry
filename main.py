from pathlib import Path
import sys

import numpy as np

import ascii
from mesh import Mesh
from mesh_io import load_obj
from pygl import Program, vec4
import numgl
from torus import torus


# Only called _once_ per render, should compute all vertices
def vertex_shader(positions_in, normals_in, uniforms):
    projection = uniforms['projection']
    model_view = uniforms['model_view']
    ambient = uniforms['ambient']
    mvp = projection @ model_view
    light = uniforms['light1']
    positions = mvp @ vec4(positions_in, 1).T
    normals = np.linalg.inv(model_view).T @ vec4(normals_in, 0).T
    return positions.T, {'intensity': np.clip(np.sum(normals.T * light, axis=1), 0, 1) + ambient}


def fragment_shader(inputs):
    intensity = inputs['intensity']
    #return np.vstack([intensity, intensity, intensity]).T
    return intensity.T


def draw(resolution, mesh, aspect=1):
    w, h = resolution
    buffer = np.zeros((h, w), dtype=np.float)
    
    light1 = numgl.normalized(np.array([0, -1, -1, 0]))

    z_buffer = np.empty(buffer.shape[:2])
    program = Program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    projection = numgl.perspective(90, aspect * w / h, 0.1, 5)
    wx, wy = 0.03, 0.01
    for a in range(1024):
        camera = numgl.translate((0, 0, -10)) @ numgl.roty(a * wy) @ numgl.rotx(a * wx)
        buffer.fill(0)
        program.render(buffer, z_buffer, mesh, projection=projection, model_view=camera, light1=light1, ambient=0.3)
        final = ascii.shade(buffer)
        print("\033[2J\033[1;1H")  # clear and move to top left
        sys.stdout.buffer.write(final)

def raw(buffer: np.array) -> bytes:
    return buffer.tobytes()

def main():
    mesh = torus(1, 0.4, 8, 8)
    draw((80, 24), mesh, aspect=0.5)
    #draw((320, 200), mesh, raw)

main()
