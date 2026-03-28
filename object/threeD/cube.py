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
            [-1,-1, 1], [ 1,-1, 1], [ 1, 1, 1], [-1, 1, 1],
            [ 1,-1,-1], [-1,-1,-1], [-1, 1,-1], [ 1, 1,-1],
            [-1,-1,-1], [-1,-1, 1], [-1, 1, 1], [-1, 1,-1],
            [ 1,-1, 1], [ 1,-1,-1], [ 1, 1,-1], [ 1, 1, 1],
            [-1, 1, 1], [ 1, 1, 1], [ 1, 1,-1], [-1, 1,-1],
            [-1,-1,-1], [ 1,-1,-1], [ 1,-1, 1], [-1,-1, 1] 
        ], dtype=np.float32)

        self.normals = np.array([
            [ 0, 0, 1], [ 0, 0, 1], [ 0, 0, 1], [ 0, 0, 1],
            [ 0, 0,-1], [ 0, 0,-1], [ 0, 0,-1], [ 0, 0,-1],
            [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0],
            [ 1, 0, 0], [ 1, 0, 0], [ 1, 0, 0], [ 1, 0, 0],
            [ 0, 1, 0], [ 0, 1, 0], [ 0, 1, 0], [ 0, 1, 0],
            [ 0,-1, 0], [ 0,-1, 0], [ 0,-1, 0], [ 0,-1, 0]
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7,
            8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15,
            16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23
        ], dtype=np.uint32)

        self.colors = np.ones((24, 3), dtype=np.float32)

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)