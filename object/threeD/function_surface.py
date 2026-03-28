import numpy as np
import OpenGL.GL as GL
from .. import Object

class FunctionSurface(Object):
    def __init__(self, vert_shader, frag_shader, func, x_range=(-5, 5), y_range=(-5, 5), resolution=50):
        super().__init__(vert_shader, frag_shader)
        
        self.vertices = []
        self.colors = []
        self.indices = []
        
        x_min, x_max = x_range[0], x_range[1]
        y_min, y_max = y_range[0], y_range[1]
        delta_x = (x_max - x_min) / (resolution - 1)
        delta_y = (y_max - y_min) / (resolution - 1)

        for i in range(resolution):
            for j in range(resolution):
                x = x_min + delta_x * i
                y = y_min + delta_y * j

                z = func(x, y)
                self.vertices.append([x, z, y])
                color_val = (z - (-2)) / (2 - (-2))
                self.colors.append([0.0, 0.5, 1.0 - 0.0])

        for i in range(resolution - 1):
            for j in range(resolution - 1):
                topleft = i * resolution + j
                topright = topleft + 1
                botleft = (i + 1) * resolution + j
                botright = botleft + 1
                
                self.indices.extend([topleft, botleft, topright])
                self.indices.extend([topright, botleft, botright])

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.int32)
        self.setup_normals()

    def setup_normals(self):
        norms = np.zeros_like(self.vertices)
        norms[:, 1] = 1.0 
        self.normals = norms
        self.normals = -np.array(self.normals, dtype=np.float32)

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)