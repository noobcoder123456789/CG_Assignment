import numpy as np
import OpenGL.GL as GL
from .. import Object

class TrajectoryObject(Object):
    def __init__(self, vert_shader, frag_shader, color):
        super().__init__(vert_shader, frag_shader)
        self.vertices = []
        self.indices = []
        self.render_mode = 0
        self.flat_color = np.array(color, dtype=np.float32)

    def add_point(self, x, y, z):
        if isinstance(self.vertices, np.ndarray):
            self.vertices = self.vertices.tolist()
        if isinstance(self.indices, np.ndarray):
            self.indices = self.indices.tolist()

        self.vertices.append([x, y, z])
        self.indices.append(len(self.vertices) - 1)
        
        if len(self.vertices) > 1:
            v_np = np.array(self.vertices, dtype=np.float32)
            i_np = np.array(self.indices, dtype=np.uint32)
            self.vao.add_vbo(0, v_np, ncomponents=3, stride=0, offset=None)
            self.vao.add_ebo(i_np)

    def draw(self, projection, view, model):
        if len(self.vertices) < 2: return
        super().draw_preprocess(projection, view, model)
        GL.glLineWidth(3.0)
        GL.glDrawElements(GL.GL_LINE_STRIP, len(self.indices), GL.GL_UNSIGNED_INT, None)
        GL.glLineWidth(1.0)