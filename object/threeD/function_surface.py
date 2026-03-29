import numpy as np
import OpenGL.GL as GL
from .. import Object

class FunctionSurface(Object):
    def __init__(self, vert_shader, frag_shader, func, x_range=(-10, 10), y_range=(-10, 10), resolution=100):
        super().__init__(vert_shader, frag_shader)

        self.x_range = x_range
        self.y_range = y_range
        
        self.vertices = []
        self.colors = []
        self.indices = []
        
        x_min, x_max = x_range[0], x_range[1]
        y_min, y_max = y_range[0], y_range[1]
        delta_x = (x_max - x_min) / (resolution - 1)
        delta_y = (y_max - y_min) / (resolution - 1)

        temp_verts = []
        z_min = float('inf')
        z_max = float('-inf')

        for i in range(resolution):
            for j in range(resolution):
                x = x_min + delta_x * i
                y = y_min + delta_y * j
                try:
                    z = func(x, y)
                except:
                    z = 0.0
                
                if z < z_min: z_min = z
                if z > z_max: z_max = z
                
                temp_verts.append([x, z, y])

        self.func = func
        self.target_height = 4.0
        self.z_min = z_min
        self.z_range_val = z_max - z_min
        if self.z_range_val == 0: self.z_range_val = 1.0 

        for v in temp_verts:
            x, z, y = v
            normalized_z = ((z - z_min) / self.z_range_val) * self.target_height
            self.vertices.append([x, normalized_z, y])
            self.colors.append([0.8, 0.8, 0.8]) 

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
        norms = np.zeros((len(self.vertices), 3), dtype=np.float32)
        for i in range(0, len(self.indices), 3):
            i1, i2, i3 = self.indices[i], self.indices[i+1], self.indices[i+2]
            v1, v2, v3 = self.vertices[i1], self.vertices[i2], self.vertices[i3]
            face_norm = np.cross(v2 - v1, v3 - v1) 
            norms[i1] += face_norm
            norms[i2] += face_norm
            norms[i3] += face_norm
            
        lengths = np.linalg.norm(norms, axis=1, keepdims=True)
        lengths[lengths == 0] = 1.0
        self.normals = norms / lengths
        self.normals = -np.array(self.normals, dtype=np.float32)

    def get_real_z(self, x, y):
        try: return self.func(x, y)
        except: return 0.0

    def get_visual_z(self, x, y):
        real_z = self.get_real_z(x, y)
        return ((real_z - self.z_min) / self.z_range_val) * self.target_height

    def get_gradient(self, x, y):
        h = 1e-4 
        df_dx = (self.get_real_z(x + h, y) - self.get_real_z(x - h, y)) / (2 * h)
        df_dy = (self.get_real_z(x, y + h) - self.get_real_z(x, y - h)) / (2 * h)
        return df_dx, df_dy

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)