import colorsys
import numpy as np
import OpenGL.GL as GL
from . import Object3D

class TorusObject(Object3D):
    def __init__(self, vert_shader, frag_shader, R=3.0, r=1.0):
        super().__init__(vert_shader, frag_shader)

        self.R = R
        self.r = r
        main_segments = 64
        tube_segments = 32

        verts = []
        clrs = []
        indices = []

        for i in range(main_segments):
            theta = (2.0 * np.pi * i) / main_segments
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            for j in range(tube_segments):
                phi = (2.0 * np.pi * j) / tube_segments
                cos_phi = np.cos(phi)
                sin_phi = np.sin(phi)

                x = (self.R + self.r * cos_phi) * cos_theta
                y = self.r * sin_phi
                z = (self.R + self.r * cos_phi) * sin_theta

                verts.append([x, y, z])
                rgb = colorsys.hsv_to_rgb((i / main_segments), 1.0, 1.0)
                clrs.append(list(rgb))

        for i in range(main_segments):
            for j in range(tube_segments):
                curr = i * tube_segments + j
                next_main = ((i + 1) % main_segments) * tube_segments + j
                curr_next_tube = i * tube_segments + ((j + 1) % tube_segments)
                next_main_next_tube = ((i + 1) % main_segments) * tube_segments + ((j + 1) % tube_segments)

                indices.extend([curr, next_main, next_main_next_tube])
                indices.extend([curr, next_main_next_tube, curr_next_tube])

        self.vertices = np.array(verts, dtype=np.float32)
        self.colors = np.array(clrs, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.int32)
        self.setup_normals(main_segments, tube_segments)

    def setup_normals(self, main_segments, tube_segments):
        norms = []
        for i in range(main_segments):
            theta = (2.0 * np.pi * i) / main_segments
            center_x = self.R * np.cos(theta)
            center_z = self.R * np.sin(theta)
            center = np.array([center_x, 0, center_z])

            for j in range(tube_segments):
                idx = i * tube_segments + j
                pos = self.vertices[idx]
                normal = pos - center
                norms.append(normal / np.linalg.norm(normal))
        
        self.normals = np.array(norms, dtype=np.float32)

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)