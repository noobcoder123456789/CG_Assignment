import OpenGL.GL as GL
import numpy as np
from .. import Object


VERTEX_GLSL = "./shader/axis.vert"
FRAGMENT_GLSL = "./shader/axis.frag"


class AxisObject(Object):
    def __init__(self, size=10.0):
        super().__init__(VERTEX_GLSL, FRAGMENT_GLSL)
        self.size = size

        self.vertices = np.array([
            0.0, 0.0, 0.0,  self.size, 0.0, 0.0,
            0.0, 0.0, 0.0,  0.0, self.size, 0.0,
            0.0, 0.0, 0.0,  0.0, 0.0, self.size 
        ], dtype=np.float32)

        self.colors = np.array([
            1.0, 0.0, 0.0,  1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,  0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,  0.0, 0.0, 1.0 
        ], dtype=np.float32)

        self.indices = np.array([0, 1, 2, 3, 4, 5], dtype=np.uint32)

    def draw(self, projection, view, model=None):
        GL.glLineWidth(3.0)
        self.draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_LINES, len(self.indices), GL.GL_UNSIGNED_INT, None)
        GL.glLineWidth(1.0)