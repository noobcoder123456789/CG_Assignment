import trimesh
import numpy as np
import OpenGL.GL as GL
from . import Object3D

class MeshObject(Object3D):
    def __init__(self, vert_shader, frag_shader, file_path, color=[0.7, 0.7, 0.7]):
        super().__init__(vert_shader, frag_shader)
        
        self.file_path = file_path
        self.default_color = color
        
        loaded = trimesh.load(file_path)
        if isinstance(loaded, trimesh.Scene):
            mesh = loaded.dump(concatenate=True)
        else:
            mesh = loaded

        self.vertices = np.array(mesh.vertices, dtype=np.float32)
        self.indices = np.array(mesh.faces, dtype=np.int32).flatten()
        
        if hasattr(mesh, 'vertex_normals') and len(mesh.vertex_normals) > 0:
            self.normals = np.array(mesh.vertex_normals, dtype=np.float32)
        else:
            self.setup_normals()
            
        self.colors = np.full((len(self.vertices), 3), self.default_color, dtype=np.float32)
        self.normalize_mesh()

    def normalize_mesh(self):
        v_arr = self.vertices
        center = (v_arr.max(axis=0) + v_arr.min(axis=0)) / 2.0
        size = (v_arr.max(axis=0) - v_arr.min(axis=0)).max()
        if size > 0:
            self.vertices = (v_arr - center) * (2.0 / size)

    def setup_normals(self):
        self.normals = np.zeros_like(self.vertices)
        self.normals[:, 1] = 1.0 

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)