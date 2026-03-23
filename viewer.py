import imgui
from imgui.integrations.glfw import GlfwRenderer
import numpy as np
import glfw, sys, os
import OpenGL.GL as GL
from itertools import cycle
from libs.transform import Trackball

from object.twoD.arrow import *
from object.twoD.circle import *
from object.twoD.ellipse import *
from object.twoD.hexagon import *
from object.twoD.pentagon import *
from object.twoD.rectangle import *
from object.twoD.star import *
from object.twoD.trapezium import *
from object.twoD.triangle import *

from object.threeD.cone import *
from object.threeD.cube import *
from object.threeD.cylinder import *
from object.threeD.function_surface import *
from object.threeD.mesh_object import *
from object.threeD.prism import *
from object.threeD.sphere import *
from object.threeD.tetrahedron import *
from object.threeD.torus import *
from object.threeD.truncated_cone import *


VERTEX_GLSL = "./shader/phong.vert"
FRAGMENT_GLSL = "./shader/phong.frag"


class Viewer:
    def __init__(self, width=800, height=800):
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, True)
        glfw.window_hint(glfw.DEPTH_BITS, 16)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)

        self.win = glfw.create_window(width=width, height=height, title='Viewer BTL1', monitor=None, share=None)

        glfw.make_context_current(self.win)

        self.trackball = Trackball()
        self.mouse = (0, 0)

        print(f"OpenGL {GL.glGetString(GL.GL_VERSION).decode()}, GLSL {GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode()}, Renderer {GL.glGetString(GL.GL_RENDERER).decode()}")

        GL.glClearColor(0.5, 0.5, 0.5, 0.1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)

        imgui.create_context()
        self.gui_renderer = GlfwRenderer(self.win)
        self.drawables = []
        self.selected_shape = "None"
        self.current_tool = "orbit"
        self.selected_obj_idx = -1

        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)
        glfw.set_mouse_button_callback(self.win, self.on_mouse_button)
        glfw.set_char_callback(self.win, self.on_char)

    def on_mouse_button(self, win, button, action, mods):
        self.gui_renderer.mouse_callback(win, button, action, mods)

    def on_char(self, win, char):
        self.gui_renderer.char_callback(win, char)

    def on_key(self, win, key, scancode, action, mods):
        self.gui_renderer.keyboard_callback(win, key, scancode, action, mods)
        
        if imgui.get_io().want_capture_keyboard:
            return

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
        dx = x_pos - self.mouse[0]
        dy = (glfw.get_window_size(win)[1] - y_pos) - self.mouse[1]
        
        old = self.mouse
        self.mouse = (x_pos, glfw.get_window_size(win)[1] - y_pos)

        if imgui.get_io().want_capture_mouse:
            return

        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            if self.current_tool == "orbit":
                self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
            
            elif self.current_tool == "pan":
                self.trackball.pan(old, self.mouse)
                
            elif self.current_tool == "move" and self.selected_obj_idx != -1:
                obj = self.drawables[self.selected_obj_idx]
                obj.translation[0] += dx / 100.0
                obj.translation[1] += dy / 100.0
                obj.update_model_matrix()
                
            elif self.current_tool == "rotate" and self.selected_obj_idx != -1:
                obj = self.drawables[self.selected_obj_idx]
                obj.rotation[0] += dy 
                obj.rotation[1] += dx
                obj.update_model_matrix()

        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, x_offset, y_offset):
        self.gui_renderer.scroll_callback(win, x_offset, y_offset)
        
        if imgui.get_io().want_capture_mouse:
            return
            
        self.trackball.zoom(y_offset, glfw.get_window_size(win)[1])

    def add(self, *drawables):
        self.drawables.extend(drawables)

    def render_ui(self):
        _get_object_id = 0

        def get_object_id():
            nonlocal _get_object_id
            _get_object_id += 1
            return _get_object_id

        imgui.new_frame()
        
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(180, glfw.get_window_size(self.win)[1])
        
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.0)
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (8, 10))
        
        imgui.begin("Dashboard", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE)

        if imgui.collapsing_header("TOOLS", imgui.TREE_NODE_DEFAULT_OPEN):
            imgui.text("--- View ---")
            
            if imgui.radio_button("Orbit", self.current_tool == "orbit"):
                self.current_tool = "orbit"
            
            if imgui.is_item_hovered():
                imgui.set_tooltip("Navigate by reorienting the camera view")
            
            if imgui.radio_button("Pan", self.current_tool == "pan"):
                self.current_tool = "pan"

            if imgui.is_item_hovered():
                imgui.set_tooltip("Move your view horizontally or vertically")
                
            imgui.spacing()
            imgui.text("--- Transform ---")
            
            if imgui.radio_button("Move", self.current_tool == "move"):
                self.current_tool = "move"

            if imgui.is_item_hovered():
                imgui.set_tooltip("Move object")
            
            if imgui.radio_button("Rotate", self.current_tool == "rotate"):
                self.current_tool = "rotate"

            if imgui.is_item_hovered():
                imgui.set_tooltip("Rotate object")
                
        imgui.spacing()
        imgui.separator()

        if imgui.collapsing_header("3D OBJECTS", imgui.TREE_NODE_DEFAULT_OPEN):
            if imgui.selectable(f"{get_object_id()}. Cone")[0]:
                self.add(ConeObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Cube")[0]:
                cube = CubeObject(VERTEX_GLSL, FRAGMENT_GLSL).setup()
                translation_matrix = np.array([
                    [1.0, 0.0, 0.0, 3.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0]
                ], dtype=np.float32)
                
                cube.model_matrix = translation_matrix.T
                self.add(cube)

            if imgui.selectable(f"{get_object_id()}. Cylinder")[0]:
                self.add(CylinderObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Prism")[0]:
                self.add(PrismObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())
            
            if imgui.tree_node("Sphere Methods"):
                methods = ["Lat-Long", "Subdivision", "Grid Project"]
                for label in methods:
                    opened, selected = imgui.selectable(label)
                    if opened:
                        if label == "Lat-Long":
                            self.add(CubeSphereObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())
                        elif label == "Subdivision":
                            self.add(TetrahedronSphereObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())
                        else:
                            self.add(CoordinatesSphereObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

                    if imgui.is_item_hovered():
                        imgui.set_tooltip(f"Create Sphere using {label} method")
                imgui.tree_pop()

            if imgui.selectable(f"{get_object_id()}. Tetrahedrone")[0]:
                self.add(TetrahedronObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Torus")[0]:
                self.add(TorusObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Truncated Cone")[0]:
                self.add(TruncatedConeObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

        imgui.spacing()
        if imgui.collapsing_header("2D OBJECTS"):
            if imgui.selectable(f"{get_object_id()}. Arrow")[0]:
                self.add(ArrowObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Circle")[0]:
                self.add(CircleObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Ellipse")[0]:
                self.add(EllipseObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Hexagon")[0]:
                self.add(HexagonObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Pentagon")[0]:
                self.add(PentagonObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Rectangle")[0]:
                self.add(RectangleObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Star")[0]:
                self.add(StarObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Trapezium")[0]:
                self.add(TrapeziumObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

            if imgui.selectable(f"{get_object_id()}. Triangle")[0]:
                self.add(TriangleObject(VERTEX_GLSL, FRAGMENT_GLSL).setup())

        imgui.set_cursor_pos_y(glfw.get_window_size(self.win)[1] - 50)
        imgui.separator()
        if imgui.button("CLEAR SCENE", width=160):
            self.drawables = []

        imgui.end()
        imgui.pop_style_var(2)

        imgui.set_next_window_position(180, 0)
        imgui.set_next_window_size(160, glfw.get_window_size(self.win)[1])
        imgui.begin("Inspector", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE)
        
        imgui.text("OBJECT LIST:")
        imgui.separator()
        
        for i, obj in enumerate(self.drawables):
            opened, selected = imgui.selectable(f"Vat the {i}: {obj.__class__.__name__}", self.selected_obj_idx == i)
            if opened:
                self.selected_obj_idx = i
                
        imgui.end()
        
        imgui.render()
        self.gui_renderer.render(imgui.get_draw_data())

    def run(self):
        while not glfw.window_should_close(self.win):
            self.gui_renderer.process_inputs()
            win_size = glfw.get_window_size(self.win)
            GL.glViewport(0, 0, win_size[0], win_size[1])
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.render_ui()
            view = self.trackball.view_matrix()
            projection = self.trackball.projection_matrix(win_size)

            for drawable in self.drawables:
                drawable.draw(projection, view, drawable.model_matrix)

            glfw.swap_buffers(self.win)
            glfw.poll_events()