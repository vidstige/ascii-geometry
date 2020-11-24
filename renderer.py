import io
import json
from pathlib import Path
from typing import BinaryIO, Dict, List, Tuple

import numpy as np
import moderngl

from mesh import Mesh


Size = Tuple[int, int]


def to_vaocontent(ctx: moderngl.Context, pos_data, normal_data, uv_data) -> List[moderngl.Buffer]:
    del normal_data
    return [
        (ctx.buffer(pos_data.astype('f4').tobytes()), '3f', 'in_position'),
        (ctx.buffer(uv_data.astype('f4').tobytes()), '2f', 'in_texcoord_0'),
    ]

def get_aspect(size: Size) -> float:
    width, height = size
    return width / height


def create_fbo(ctx: moderngl.Context, size: Size, components: int = 4) -> moderngl.Framebuffer:
    """Create a Frame Buffer Object (fbo) with the given size and
    color components"""
    return ctx.framebuffer(
        color_attachments=[ctx.renderbuffer(size, components)],
        depth_attachment=ctx.depth_renderbuffer(size))


def from_mesh(ctx: moderngl.Context, program: moderngl.Program, mesh: Mesh):
    buffer = mesh.vertices.astype('f4').copy('C')
    vbo = ctx.buffer(buffer)
    vao = ctx.simple_vertex_array(
        program, vbo, 'in_position', 'in_normal')
    return vao
    #vbo = ctx.buffer(np.hstack([mesh.vertices, mesh.vertex_normals]).astype('f4').copy(order='C'))
    #return ctx.vertex_array(
    #    program,
    #    [
    #        (vbo, '3f', 'in_position'),
    #        (vbo, '3f', 'in_normal')
    #    ]
    #)

def pack(mesh: Mesh) -> np.array:
    rows = []
    for i0, i1, i2 in mesh.faces:
        rows.append(np.hstack([mesh.vertices[i0], mesh.vertex_normals[i0]]))
        rows.append(np.hstack([mesh.vertices[i1], mesh.vertex_normals[i1]]))
        rows.append(np.hstack([mesh.vertices[i2], mesh.vertex_normals[i2]]))

    return np.vstack(rows).copy('C')


class Renderer:
    def __init__(
            self, ctx: moderngl.Context, size: Size, mesh: Mesh, projection: np.array, components=4):
        self.size = size
        self.projection = projection

        self.prog = ctx.program(
            vertex_shader=Path('shaders/simple.vert').read_text(),
            fragment_shader=Path('shaders/simple.frag').read_text())

        #from ModernGL.ext.obj import Obj
        #mesh = Obj.open('meshes/cube.obj')
        #vertex_data = mesh.pack('vx vy vz nx ny nz')
        #self.vao = from_mesh(ctx, self.prog, mesh)
        vertex_data = pack(mesh).astype('f4').tobytes()
        self.vbo = ctx.buffer(vertex_data)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_normal')
        self.fbo = create_fbo(ctx, self.size, components)
        self.fbo.use()

        self.ctx = ctx

    def render(self, camera: np.array, light1: np.array):
        self.ctx.clear()

        self.prog['u_light1'].write(light1.astype('f4'))
        self.prog['u_ambient'].write(np.array(0.01).astype('f4'))
        self.prog['u_projection'].write(self.projection.astype('f4'))
        self.prog['u_modelView'].write(camera.astype('f4'))
        self.vao.render()

    def snapshot(self, components=4):
        """Returns current fbo as an image"""
        fbo = self.fbo
        data = fbo.read(components=3)
        from PIL import Image
        return Image.frombytes('RGB', fbo.size, data).transpose(Image.FLIP_TOP_BOTTOM)

    def snapshot2(self) -> np.array:
        """Returns current fbo as an ndarray"""
        fbo = self.fbo
        data = fbo.read(components=3, dtype='f4')
        w, h = self.size
        return np.flipud(np.frombuffer(data, dtype='f4').reshape((h, w, 3)))
