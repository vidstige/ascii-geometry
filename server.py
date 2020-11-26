from itertools import count
from pathlib import Path
import sys
import time

from flask import Flask, request, Response
import moderngl
import numpy as np
from pyrr import Matrix44

import ascii
from mesh import Mesh
from mesh_io import load_obj
from renderer import Renderer  # opengl
import numgl
from torus import torus


app = Flask(__name__)


def parse_resolution(s: str):
    return tuple(int(d) for d in s.split('x'))


def create_context():
    # Re-use context objects as a workaround for this issue
    # https://github.com/moderngl/moderngl/issues/226
    if create_context.cache:
        return create_context.cache

    ctx = moderngl.create_standalone_context(
        libgl='libGL.so.1',
        libx11='libX11.so.6')
    ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
    create_context.cache = ctx
    return ctx
create_context.cache = None  # type: ignore[attr-defined]


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


@app.route('/torus.png')
def torus_image():
    mesh = torus(1, 0.5, 12, 32)
    w, h = parse_resolution(request.args.get('resolution', '80x50'))
    aspect = float(request.args.get('aspect', '1'))
    t = float(request.args.get('t', 0))
    
    light1 = numgl.normalized(np.array([0, 1, 1]))
    angular_velocity = np.array([1.7, 2, 0])
    projection = Matrix44.perspective_projection(60.0, aspect * w / h, 0.1, 10.0)
    camera = Matrix44.from_translation(np.array([0, 0, -3])) * Matrix44.from_eulers(t * angular_velocity)

    with create_context() as ctx:
        renderer = Renderer(ctx, (w, h), mesh, projection=projection)
        renderer.render(camera, light1)
        image = renderer.snapshot()        
        from io import BytesIO
        with BytesIO() as f:
            image.save(f, 'png')
            return Response(f.getvalue(), mimetype='image/png')


@app.route('/torus')
def stream_torus():
    if 'curl' not in request.headers.get('User-Agent', 'unknown') and 'curl' not in request.args.get('user-agent', 'unknown'):
        return app.send_static_file('ubuntu.html')

    mesh = torus(1, 0.5, 12, 32)
    w, h = parse_resolution(request.args.get('resolution', '80x50'))
    aspect = float(request.args.get('aspect', '0.5'))
    fps = float(request.args.get('fps', 25))
    fov = float(request.args.get('fov', 60))
    d = float(request.args.get('d', 3.2))

    light1 = numgl.normalized(np.array([0, 1, 1]))
    angular_velocity = np.array([1.7, 2, 0])
    projection = Matrix44.perspective_projection(fov, aspect * w / h, 0.1, 10.0)

    dt = 1 / fps
    beginning = time.time()
    def frames():
        with create_context() as ctx:
            renderer = Renderer(ctx, (w, h), mesh, projection=projection)

            for _ in count():
                t = time.time() - beginning
                theta = t * angular_velocity
                rotation = Matrix44.from_z_rotation(theta[2]) * Matrix44.from_y_rotation(theta[1]) * Matrix44.from_x_rotation(theta[0])
                camera = Matrix44.from_translation(np.array([0, 0, -d])) * rotation
                renderer.render(camera, light1)
                buffer = np.mean(renderer.snapshot2(), axis=-1)
                lines = ascii.shade(buffer)
                text = 'vidstige 2020'
                lines[-2] = scroller(lines[-2], text, t, w=9)
                yield b"\033[2J\033[1;1H" + b'\n'.join(lines) + b"\n"
                duration = (time.time() - beginning) - t
                if dt - duration > 0:
                    time.sleep(dt - duration)

    return Response(frames(), mimetype='text/plain;charset=UTF-8')
