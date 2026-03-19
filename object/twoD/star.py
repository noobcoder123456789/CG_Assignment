import numpy as np
import glfw, colorsys
import OpenGL.GL as GL
from libs.buffer import *
from libs.shader import *
from libs.transform import *
from . import Object2D


class StarObject(Object2D):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        r_in, r_out = 0.4, 1.0
        self.vertices = [[0.0, 0.5, 0.0]]
        self.colors = [[1.0, 1.0, 1.0]]
        points_num = 10

        for k in range(points_num): 
            r = r_out if k % 2 == 0 else r_in
            sin, cos = sincos(radians=np.pi * k / 5) 
            
            x = r * cos
            z = r * sin
            self.vertices.append([x, 0.5, z])
            rgb = colorsys.hsv_to_rgb(k / points_num, 1.0, 1.0)
            self.colors.append(list(rgb))

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1
        ], dtype=np.int32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )
    
    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)