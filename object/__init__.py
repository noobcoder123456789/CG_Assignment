import glfw
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs import transform as T
from abc import ABC, abstractmethod
from libs.lighting import LightingManager


class Object(ABC):
    def __init__(self, vert_shader, frag_shader):
        self.main_shaders = (vert_shader, frag_shader)

        self.shaders = {
            "flat": Shader("./shader/vertex.vert", "./shader/fragment.frag"),
            "phong": Shader("./shader/phong.vert", "./shader/phong.frag"),
            "gouraud": Shader("./shader/gouraud.vert", "./shader/gouraud.frag")
        }
        
        self.translation = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        self.model_matrix = np.eye(4, dtype=np.float32)
        
        self.render_mode = 2 
        self.flat_color = np.array([0.2, 0.3, 0.2], dtype=np.float32)
        self.is_wireframe = False
        self.texture_file = "./assets/chair.jpg"

        self.vao = VAO()
        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)
        self.lighting = LightingManager(self.uma)

    def update_model_matrix(self):
        tx, ty, tz = self.translation
        rx, ry, rz = self.rotation
        sx, sy, sz = self.scale

        mat_t = T.translate(tx, ty, tz)
        
        mat_rx = T.rotate(axis=(1, 0, 0), angle=rx)
        mat_ry = T.rotate(axis=(0, 1, 0), angle=ry)
        mat_rz = T.rotate(axis=(0, 0, 1), angle=rz)
        mat_r = mat_rz @ mat_ry @ mat_rx
        
        mat_s = T.scale(sx, sy, sz)
        self.model_matrix = (mat_t @ mat_r @ mat_s)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, stride=0, offset=None)

        if 'gouraud' in self.main_shaders[0].lower() or 'phong' in self.main_shaders[0].lower():
            self.vao.add_vbo(2, self.normals, ncomponents=3, stride=0, offset=None)

        if hasattr(self, 'uvs') and self.uvs is not None:
            self.vao.add_vbo(3, self.uvs, ncomponents=2, stride=0, offset=None)

        self.vao.add_ebo(self.indices)

        if self.texture_file is not None:
            self.uma.setup_texture("u_Texture", self.texture_file)

        return self
    
    def draw_preprocess(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)

        modelview = view @ self.model_matrix

        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma.upload_uniform_matrix4fv(modelview, 'modelview', True)
        self.uma.upload_uniform_scalar1i(self.render_mode, "u_RenderMode")
        self.uma.upload_uniform_vector3fv(self.flat_color, "u_FlatColor")

        if 'gouraud' in self.main_shaders[0].lower():
            self.lighting.setup_gouraud()
        elif 'phong' in self.main_shaders[0].lower():
            self.lighting.setup_phong()

        if self.is_wireframe:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        self.vao.activate()
    
    @abstractmethod
    def draw(self, projection, view, model):
        pass

    def key_handler(self, key):
        if key == glfw.KEY_1:
            self.selected_texture = 1
        
        if key == glfw.KEY_2:
            self.selected_texture = 2