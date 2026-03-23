import numpy as np
import glfw, colorsys
import OpenGL.GL as GL
from libs.buffer import *
from libs.shader import *
from libs.transform import *
from .. import Object


class ArrowObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [ 0.0, 0.5,  1.0],
            [-0.5, 0.5,  0.5],
            [-0.2, 0.5,  0.5],
            [-0.2, 0.5, -0.5],
            [ 0.2, 0.5, -0.5],
            [ 0.2, 0.5,  0.5],
            [ 0.5, 0.5,  0.5],
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 6, 2, 3, 4, 2, 4, 5 
        ], dtype=np.int32)

        self.colors = np.array([
            [1.0, 0.0, 0.0],
            [0.8, 0.4, 0.0],
            [0.6, 0.0, 0.6],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.6, 0.0, 0.6],
            [0.8, 0.4, 0.0],
        ], dtype=np.float32)

        self.normals = self.vertices.copy()
        self.normals = self.normals / np.linalg.norm(
            self.normals, axis=1, keepdims=True
        )

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)