import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from .. import Object


class PrismObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [ 1.0,  2.0, 0.0], # A
            [-1.0,  2.0, 0.0], # B
            [ 0.0,  2.0, 2.0], # C
            [ 1.0, -2.0, 0.0], # D
            [-1.0, -2.0, 0.0], # E
            [ 0.0, -2.0, 2.0], # F
        ], dtype=np.float32)

        self.colors = np.array([
            [1.0, 0.0, 0.0],  # A
            [0.0, 1.0, 0.0],  # B
            [0.0, 0.0, 1.0],  # C
            [1.0, 1.0, 1.0],  # D
            [0.0, 1.0, 1.0],  # E
            [0.2, 0.3, 0.5],  # F
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 5, 3, 4, 1, 5, 5, 1, 1, 3, 0, 2
        ], dtype=np.int32)

        self.normals = self.vertices / np.linalg.norm(
            self.vertices, axis=1, keepdims=True
        )

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)