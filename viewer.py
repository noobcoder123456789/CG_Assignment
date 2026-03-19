import numpy as np
import glfw, sys, os
import OpenGL.GL as GL
from itertools import cycle
from libs.transform import Trackball


class Viewer:
    def __init__(self, width=800, height=800):
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.DEPTH_BITS, 16)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)

        self.win = glfw.create_window(width=width, height=height, title='Viewer', monitor=None, share=None)

        glfw.make_context_current(self.win)

        self.trackball = Trackball()
        self.mouse = (0, 0)

        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        print(f"OpenGL {GL.glGetString(GL.GL_VERSION).decode()}, GLSL {GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode()}, Renderer {GL.glGetString(GL.GL_RENDERER).decode()}")

        GL.glClearColor(0.5, 0.5, 0.5, 0.1)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)

        self.drawables = []

    def on_key(self, _win, key, _scancode, action, _mods):
        if not (action == glfw.PRESS or action == glfw.REPEAT):
            return
        
        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(self.win, True)

        if key == glfw.KEY_W:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))

        for drawable in self.drawables:
            if hasattr(drawable, 'key_handler'):
                drawable.key_handler(key)

    def on_mouse_move(self, win, x_pos, y_pos):
        old = self.mouse
        self.mouse = (x_pos, glfw.get_window_size(win)[1] - y_pos)

        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.trackball.drag(old, self.mouse, glfw.get_window_size(win))

        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, delta_x, delta_y):
        self.trackball.zoom(delta_y, glfw.get_window_size(win)[1])

    def add(self, *drawables):
        self.drawables.extend(drawables)

    def run(self):
        while not glfw.window_should_close(self.win):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            win_size = glfw.get_window_size(self.win)
            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            for drawable in self.drawables:
                drawable.draw(projection, view, None)

            glfw.swap_buffers(self.win)
            glfw.poll_events()