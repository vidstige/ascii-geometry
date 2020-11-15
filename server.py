from itertools import count
from pathlib import Path
import sys
import time

from flask import Flask, request, Response
import numpy as np

import ascii
from mesh import Mesh
from mesh_io import load_obj
from pygl import Program, vec4, Resolution
import numgl
from torus import torus


app = Flask(__name__)


def parse_resolution(s: str) -> Resolution:
    return tuple(int(d) for d in s.split('x'))


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
    return intensity.T


def scroller(line: bytes, text: str, t, w=1) -> bytes:
    work = list(line)
    data = text.encode()
    start = int(t * w) - len(data)
    n = len(work) + len(data)
    for i, char in enumerate(data):
        j = (start + i) % n
        if j >= 0 and j < len(work):
            work[j] = char
    return bytes(work)


@app.route('/torus')
def stream():
    mesh = torus(1, 0.4, 6, 16)

    w, h = parse_resolution(request.args.get('resolution', '80x50'))
    aspect = float(request.args.get('aspect', '0.5'))
    fps = float(request.args.get('fps', 25))
    buffer = np.zeros((h, w), dtype=np.float)
    
    light1 = numgl.normalized(np.array([0, -1, -1, 0]))

    z_buffer = np.empty(buffer.shape[:2])
    program = Program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    projection = numgl.perspective(90, aspect * w / h, 0.1, 5)
    wx, wy, wz = 1.7, 2, 0
    dt = 1 / fps
    beginning = time.time()
    def frames():
        for _ in count():
            t = time.time() - beginning
            camera = numgl.translate((0, 0, -10)) @ numgl.rotz(t * wz) @ numgl.roty(t * wy) @ numgl.rotx(t * wx)
            buffer.fill(0)
            program.render(buffer, z_buffer, mesh, projection=projection, model_view=camera, light1=light1, ambient=0.1)
            lines = ascii.shade(buffer)
            lines[2] = scroller(lines[0], 'vidstige 2020', t, w=10)
            yield b"\033[2J\033[1;1H" + b'\n'.join(lines) + b"\n"
            duration = (time.time() - beginning) - t
            #yield "\n\n{} - {} = {}".format(dt, duration, dt - duration)
            if dt - duration > 0:
                time.sleep(dt - duration)

    return Response(frames(), mimetype='text/plain;charset=UTF-8')
