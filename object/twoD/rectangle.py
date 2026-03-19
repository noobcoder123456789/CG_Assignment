import glfw
import numpy as np
import OpenGL.GL as GL
from libs.buffer import *
from . import Object2D


class RectangleObject(Object2D):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [-2.0, 0.5,  1.0],
            [ 2.0, 0.5,  1.0],
            [-2.0, 0.5, -1.0],
            [ 2.0, 0.5, -1.0],
        ], dtype=np.float32)

        self.colors = np.array([
            [1.0, 0.0, 0.0],  # A
            [1.0, 0.0, 1.0],  # B
            [0.0, 0.0, 1.0],  # C
            [0.0, 1.0, 0.0],  # D
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 3
        ], dtype=np.int32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )
    
    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)