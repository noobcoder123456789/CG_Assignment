import glfw
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from .. import Object


class CubeObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [-1, -1, +1],  # A <= Bottom: ABCD
            [+1, -1, +1],  # B
            [+1, -1, -1],  # C
            [-1, -1, -1],  # D
            [-1, +1, +1],  # E <= Top: EFGH
            [+1, +1, +1],  # F
            [+1, +1, -1],  # G
            [-1, +1, -1],  # H
        ], dtype=np.float32)

        self.indices = np.array([
            0, 4, 1, 5, 2, 6, 3, 7, 0, 4, 4, 0, 0, 3, 1, 2, 2, 4, 4, 7, 5, 6
        ], dtype=np.int32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )

        self.colors = np.array([
            [1.0, 0.0, 0.0],  # A <= Bottom: ABCD
            [1.0, 0.0, 1.0],  # B
            [0.0, 0.0, 1.0],  # C
            [0.0, 0.0, 0.0],  # D
            [1.0, 1.0, 0.0],  # E <= Top: EFGH
            [1.0, 1.0, 1.0],  # F
            [0.0, 1.0, 1.0],  # G
            [0.0, 1.0, 0.0],  # H
        ], dtype=np.float32)

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)