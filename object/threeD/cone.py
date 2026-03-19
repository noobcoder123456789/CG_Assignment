import colorsys
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs.transform import sincos
from . import Object3D


class ConeObject(Object3D):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.radius = 2.0
        self.height = 6.0
        segments = 64

        self.vertices = [
            [0.0,  4.0, 0.0],
            [0.0, -2.0, 0.0],
        ]

        self.colors = [
            [1.0, 1.0, 1.0],
            [0.5, 0.5, 0.5],
        ]

        self.indices = []

        for k in range(segments):
            sin, cos = sincos(radians=(2.0 * np.pi / segments) * k)
            self.vertices.append([self.radius * cos, -2.0, self.radius * sin])
            rgb = colorsys.hsv_to_rgb(k / segments, 1.0, 1.0)
            self.colors.append(list(rgb))

            curr = k + 2
            next_p = ((k + 1) % segments) + 2
            self.indices.extend([0, curr, next_p, 1, curr, next_p])

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.int32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)