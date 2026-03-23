import numpy as np
import glfw, colorsys
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs.transform import *
from .. import Object


class CircleObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = [[0.0, 0.5, 0.0]]
        self.colors = [[1.0, 1.0, 1.0]]

        self.radius = 2
        points_num = 100
        for k in range(points_num):
            sin, cos = sincos(radians=(2.0 * np.pi / points_num) * k)
            self.vertices.append([self.radius * cos, 0.5, self.radius * sin])
            rgb = colorsys.hsv_to_rgb(k / points_num, 1.0, 1.0)
            self.colors.append(list(rgb))

        self.vertices.append(self.vertices[1])
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )
        
        self.indices = np.array([
            *[_ for _ in range(len(self.vertices) - 1)], 1
        ], dtype=np.int32)

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)