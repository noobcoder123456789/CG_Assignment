import glfw
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs import transform as T
from abc import ABC, abstractmethod
from libs.lighting import LightingManager


class Object3D(ABC):
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

        if 'gouraud' in self.vert_shader.lower():
            self.lighting.setup_gouraud()
        elif 'phong' in self.vert_shader.lower():
            self.lighting.setup_phong()

        self.vao.activate()
    
    @abstractmethod
    def draw(self, projection, view, model):
        pass

    def key_handler(self, key):
        if key == glfw.KEY_1:
            self.selected_texture = 1
        
        if key == glfw.KEY_2:
            self.selected_texture = 2