import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from .. import Object


class TetrahedronObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.942809, -0.33333],
            [-0.816497, -0.471405, -0.33333],
            [0.816497, -0.471405, -0.33333]
        ], dtype=np.float32)

        self.colors = np.array([
            [1.0, 0.0, 0.0],  # A
            [0.0, 1.0, 0.0],  # B
            [0.0, 0.0, 1.0],  # C
            [1.0, 1.0, 1.0],  # D
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 3, 0, 1
        ], dtype=np.int32)

        self.normals = self.vertices / np.linalg.norm(
            self.vertices, axis=1, keepdims=True
        )

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)