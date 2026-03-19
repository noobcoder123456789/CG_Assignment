import glfw
import OpenGL.GL as GL
from libs.buffer import *
from libs.shader import *
from libs.transform import *
from abc import ABC, abstractmethod
from libs.lighting import LightingManager


class Object2D(ABC):
    def __init__(self, vert_shader, frag_shader):
        self.vert_shader = vert_shader
        self.frag_shader = frag_shader

        self.vao = VAO()
        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)
        self.lighting = LightingManager(self.uma)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, stride=0, offset=None)

        if 'gouraud' in self.vert_shader.lower() or 'phong' in self.vert_shader.lower():
            self.vao.add_vbo(2, self.normals, ncomponents=3, stride=0, offset=None)

        self.vao.add_ebo(self.indices)
        return self
    
    def draw_preprocess(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)

        modelview = view
        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma.upload_uniform_matrix4fv(modelview, 'modelview', True)

        if 'phong' in self.frag_shader.lower():
            self.lighting.setup_phong()
        elif 'gouraud' in self.frag_shader.lower():
            self.lighting.setup_gouraud()

        self.vao.activate()

    @abstractmethod
    def draw(self, projection, view, model, draw_mode):
        pass

    def key_handler(self, key):
        if key == glfw.KEY_1:
            self.selected_texture = 1

        if key == glfw.KEY_2:
            self.selected_texture = 2