import numpy as np
import OpenGL.GL as GL
from PySide6.QtCore import Qt
from object.threeD.axis import AxisObject
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from libs.transform import Trackball


class OpenGLCanvas(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cameras = [
            Trackball(distance=4.0),
            Trackball(distance=6.0, pitch=45.0, yaw=45.0, roll=0.0),
            Trackball(distance=5.0, pitch=89.0, yaw=0.0, roll=0.0)
        ]
        self.current_cam_idx = 0
        self.last_mouse_pos = None

        self.axis = None
        self.objects = [] 
        self.selected_idx = -1

        self.light_positions = [
            [10.0, 10.0, 10.0],
            [-10.0, 5.0, 5.0],
            [0.0, -10.0, 0.0]
        ]
        self.sun_idx = -1
        self.sun_pos = [0.0, 0.0, 0.0]
        self.has_sun = 0
        self.light_intensity = 500.0
        
        self.is_dragging_object = False 
        self.current_tool = 0 

    def initializeGL(self):
        GL.glClearColor(0.15, 0.15, 0.15, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.axis = AxisObject().setup()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        win_size = (self.width(), self.height())
        view = self.cameras[self.current_cam_idx].view_matrix()
        projection = self.cameras[self.current_cam_idx].projection_matrix(win_size)

        self.light_positions = []
        self.light_colors = []
        self.light_states = []
        self.light_intensities = []
        for obj in self.objects:
            if type(obj).__name__ == 'SunObject':
                self.light_positions.append(obj.translation.copy())
                self.light_colors.append(obj.flat_color.copy())
                self.light_states.append(1)
                self.light_intensities.append(getattr(obj, 'intensity', 50.0))

        if self.axis:
            self.axis.draw(projection, view, self.axis.model_matrix)

        for obj in self.objects:
            obj.draw(projection, view, obj.model_matrix)

    def mousePressEvent(self, event):
        self.last_mouse_pos = (event.position().x(), self.height() - event.position().y())

        if event.button() == Qt.LeftButton:
            self.makeCurrent()
            
            GL.glClearColor(1.0, 1.0, 1.0, 1.0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            
            win_size = (self.width(), self.height())
            view = self.cameras[self.current_cam_idx].view_matrix()
            projection = self.cameras[self.current_cam_idx].projection_matrix(win_size)
            
            for i, obj in enumerate(self.objects):
                old_mode = obj.render_mode
                old_color = obj.flat_color.copy()
                
                obj.render_mode = 0
                obj.flat_color = np.array([(i + 1) / 255.0, 0.0, 0.0], dtype=np.float32)
                obj.draw(projection, view, obj.model_matrix)
                
                obj.render_mode = old_mode
                obj.flat_color = old_color

            ratio = self.devicePixelRatio()
            px = int(event.position().x() * ratio)
            py = int((self.height() - event.position().y()) * ratio)
            pixel = GL.glReadPixels(px, py, 1, 1, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)
            r = pixel[0] 
            
            if r == 255:
                self.selected_idx = -1
                self.window().lst_objects.setCurrentRow(-1) 
                self.is_dragging_object = False 
            else:
                selected_idx = r - 1
                if 0 <= selected_idx < len(self.objects):
                    self.selected_idx = selected_idx
                    self.window().lst_objects.setCurrentRow(selected_idx)
                    self.is_dragging_object = True 
            
            GL.glClearColor(0.15, 0.15, 0.15, 1.0)
            self.doneCurrent()
            self.update()

    def mouseMoveEvent(self, event):
        if not self.last_mouse_pos: return
        current_pos = (event.position().x(), self.height() - event.position().y())
        
        dx = current_pos[0] - self.last_mouse_pos[0]
        dy = current_pos[1] - self.last_mouse_pos[1]
        active_cam = self.cameras[self.current_cam_idx]

        if event.buttons() & Qt.LeftButton:
            if self.current_tool == 0 or (self.current_tool in [2, 3, 4] and not self.is_dragging_object):
                active_cam.drag(self.last_mouse_pos, current_pos, (self.width(), self.height()))
            
            elif self.current_tool == 1:
                active_cam.pan(self.last_mouse_pos, current_pos)
            
            elif self.current_tool == 2 and self.is_dragging_object:
                obj = self.objects[self.selected_idx]
                
                view = active_cam.view_matrix()
                proj = active_cam.projection_matrix((self.width(), self.height()))
                
                obj_pos_world = np.array([obj.translation[0], obj.translation[1], obj.translation[2], 1.0])
                obj_pos_view = view @ obj_pos_world
                
                cam_right = view[0, :3]
                cam_up = view[1, :3]
                
                z_depth = obj_pos_view[2] 
                dx_view = (2.0 * dx / self.width()) * (-z_depth) / proj[0, 0]
                dy_view = (2.0 * dy / self.height()) * (-z_depth) / proj[1, 1]
                delta_world = cam_right * dx_view + cam_up * dy_view
                
                obj.translation[0] += delta_world[0]
                obj.translation[1] += delta_world[1]
                obj.translation[2] += delta_world[2]
                
                if hasattr(obj, 'update_model_matrix'): 
                    obj.update_model_matrix()
                
            elif self.current_tool == 3 and self.is_dragging_object:
                obj = self.objects[self.selected_idx]
                obj.rotation[0] += dy 
                obj.rotation[1] += dx
                if hasattr(obj, 'update_model_matrix'): obj.update_model_matrix()
                
            elif self.current_tool == 4 and self.is_dragging_object:
                obj = self.objects[self.selected_idx]
                scale_factor = 1.0 + (dy / 100.0)
                obj.scale[0] *= scale_factor
                obj.scale[1] *= scale_factor
                obj.scale[2] *= scale_factor
                if hasattr(obj, 'update_model_matrix'): obj.update_model_matrix()
                
        elif event.buttons() & Qt.RightButton:
            active_cam.pan(self.last_mouse_pos, current_pos)
            
        self.last_mouse_pos = current_pos
        self.update()

    def wheelEvent(self, event):
        self.cameras[self.current_cam_idx].zoom(event.angleDelta().y() / 120.0, self.height())
        self.update()