import colorsys
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs.transform import sincos
from . import Object3D


class TruncatedConeObject(Object3D):
    def __init__(self, vert_shader, frag_shader, radius_small=2.0, radius_big=4.0):
        super().__init__(vert_shader, frag_shader)

        self.radius_small = radius_small
        self.radius_big = radius_big
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
            self.vertices.append([self.radius_small * cos, -2.0 + self.height, self.radius_small * sin])
            self.vertices.append([self.radius_big * cos, -2.0, self.radius_big * sin])
            rgb = colorsys.hsv_to_rgb(k / segments, 1.0, 1.0)
            self.colors.append(list(rgb))
            self.colors.append(list(rgb))

            curr_top = 2 * k + 2
            curr_bot = 2 * k + 3
            
            next_k = (k + 1) % segments
            next_top = 2 * next_k + 2
            next_bot = 2 * next_k + 3

            self.indices.extend([0, curr_top, next_top])
            self.indices.extend([1, next_bot, curr_bot])
            self.indices.extend([curr_top, curr_bot, next_top])
            self.indices.extend([curr_bot, next_bot, next_top])

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