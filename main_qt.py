import sys, os
import numpy as np
import OpenGL.GL as GL
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QCheckBox, QLabel, QGroupBox, QFormLayout,
    QDockWidget, QListWidget, QTabWidget, QLineEdit, QFileDialog, QColorDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from object.twoD.arrow import ArrowObject
from object.twoD.circle import CircleObject
from object.twoD.ellipse import EllipseObject
from object.twoD.hexagon import HexagonObject
from object.twoD.pentagon import PentagonObject
from object.twoD.rectangle import RectangleObject
from object.twoD.star import StarObject
from object.twoD.trapezium import TrapeziumObject
from object.twoD.triangle import TriangleObject

from object.threeD.axis import AxisObject
from object.threeD.cone import ConeObject
from object.threeD.cube import CubeObject
from object.threeD.cylinder import CylinderObject
from object.threeD.prism import PrismObject
from object.threeD.tetrahedron import TetrahedronObject
from object.threeD.torus import TorusObject
from object.threeD.truncated_cone import TruncatedConeObject

from object.threeD.sphere import CoordinatesSphereObject, CubeSphereObject, TetrahedronSphereObject 
from object.threeD.function_surface import FunctionSurface
from object.threeD.mesh_object import MeshObject

from libs.transform import Trackball

VERTEX_GLSL = "./shader/vertex.vert"
FRAGMENT_GLSL = "./shader/fragment.frag"

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
        self.light_states = [1, 0, 0] 
        
        # --- THÊM 2 BIẾN NÀY ĐỂ QUẢN LÝ TƯƠNG TÁC ---
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
                # Click ra ngoài Vũ trụ -> Hủy chọn, không kéo vật thể
                self.selected_idx = -1
                self.window().lst_objects.clearSelection()
                self.is_dragging_object = False 
            else:
                # Click trúng vật thể -> Bắt đầu quá trình thao tác
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
                obj.translation[0] += dx / 100.0
                obj.translation[1] += dy / 100.0
                if hasattr(obj, 'update_model_matrix'): obj.update_model_matrix()
                
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CG Assignment - Advanced 3D Viewer")
        self.resize(1280, 800)
        self.apply_dark_theme()

        self.gl_canvas = OpenGLCanvas()
        self.setCentralWidget(self.gl_canvas)

        self.shape_catalog = {
            "2D Shapes": {
                "Arrow": ArrowObject, "Circle": CircleObject, "Ellipse": EllipseObject,
                "Hexagon": HexagonObject, "Pentagon": PentagonObject, "Rectangle": RectangleObject,
                "Star": StarObject, "Trapezium": TrapeziumObject, "Triangle": TriangleObject
            },
            "3D Primitives": {
                "Cube": CubeObject, "Cone": ConeObject, "Cylinder": CylinderObject,
                "Prism": PrismObject, "Tetrahedron": TetrahedronObject, "Torus": TorusObject,
                "Truncated Cone": TruncatedConeObject
            },
            "Spheres & Advanced": {
                "Sphere (Lat-Long)": CubeSphereObject,
                "Sphere (Subdiv)": TetrahedronSphereObject,
                "Sphere (Coordinates)": CoordinatesSphereObject
            }
        }

        self.create_left_dock()
        self.create_right_dock()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.gl_canvas.update)
        self.timer.start(16) 

    def apply_dark_theme(self):
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)
    
    def load_texture(self):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            file_name, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh Texture", "", "Images (*.png *.jpg *.jpeg)")
            if file_name:
                obj = self.gl_canvas.objects[idx]
                obj.texture_file = file_name
                self.gl_canvas.makeCurrent()
                
                try:
                    if hasattr(obj, 'uma'):
                        obj.uma.setup_texture("u_Texture", file_name)
                except Exception as e:
                    print("Lỗi load texture:", e)
                finally:
                    self.gl_canvas.doneCurrent()
                
                if self.cb_mode.currentIndex() not in [3, 4]:
                    self.cb_mode.setCurrentIndex(4)
                self.gl_canvas.update()

    def create_left_dock(self):
        dock = QDockWidget("Scene Manager", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group_tool = QGroupBox("Interactive Tools (Left Mouse Button)")
        layout_tool = QVBoxLayout()
        self.cb_tool = QComboBox()
        self.cb_tool.addItems([
            "Orbit",
            "Pan",
            "Translate", 
            "Rotate", 
            "Scale"
        ])
        self.cb_tool.currentIndexChanged.connect(self.change_tool)
        layout_tool.addWidget(self.cb_tool)
        group_tool.setLayout(layout_tool)
        layout.addWidget(group_tool)

        group_create = QGroupBox("Create")
        form_create = QFormLayout()
        
        self.cb_category = QComboBox()
        self.cb_category.addItems(self.shape_catalog.keys())
        self.cb_category.currentTextChanged.connect(self.update_shape_list)
        
        self.cb_shape = QComboBox()
        self.update_shape_list(self.cb_category.currentText())

        btn_add = QPushButton("Add Object")
        btn_add.clicked.connect(self.add_shape)
        btn_add.setStyleSheet("background-color: #2e7d32; font-weight: bold;")

        form_create.addRow("Loại:", self.cb_category)
        form_create.addRow("Hình:", self.cb_shape)
        form_create.addRow("", btn_add)
        group_create.setLayout(form_create)
        layout.addWidget(group_create)

        group_import = QGroupBox("Import External")
        btn_load_obj = QPushButton("Load .OBJ / .PLY")
        btn_load_obj.clicked.connect(self.load_mesh)
        layout_import = QVBoxLayout()
        layout_import.addWidget(btn_load_obj)
        group_import.setLayout(layout_import)
        layout.addWidget(group_import)

        layout.addWidget(QLabel("--- Scene Graph ---"))
        self.lst_objects = QListWidget()
        self.lst_objects.currentRowChanged.connect(self.on_object_selected)
        layout.addWidget(self.lst_objects)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self.delete_selected)
        btn_clear = QPushButton("Clear Scene")
        btn_clear.clicked.connect(self.clear_scene)
        
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(btn_delete)
        layout_buttons.addWidget(btn_clear)
        layout.addLayout(layout_buttons)

        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def create_right_dock(self):
        dock = QDockWidget("Inspector", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        tabs = QTabWidget()

        tab_render = QWidget()
        layout_render = QVBoxLayout(tab_render)
        form_render = QFormLayout()
        
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["Flat Color", "Vertex Color", "Phong Shading", "Texture", "Phong+Tex", "Depth Map"])
        self.cb_mode.setCurrentIndex(2)
        self.cb_mode.currentIndexChanged.connect(self.update_object_props)
        form_render.addRow("Shading:", self.cb_mode)

        self.chk_wireframe = QCheckBox("Wireframe")
        self.chk_wireframe.stateChanged.connect(self.update_object_props)
        form_render.addRow("", self.chk_wireframe)

        btn_color = QPushButton("Change Flat Color")
        btn_color.clicked.connect(self.pick_color)
        form_render.addRow("Color:", btn_color)

        btn_tex = QPushButton("🖼️ Load Texture Image")
        btn_tex.clicked.connect(self.load_texture)
        form_render.addRow("Texture:", btn_tex)

        layout_render.addLayout(form_render)
        layout_render.addStretch()
        tabs.addTab(tab_render, "Material")

        tab_math = QWidget()
        layout_math = QVBoxLayout(tab_math)
        layout_math.addWidget(QLabel("Enter mathematical functions z = f(x, y):"))
        self.txt_func = QLineEdit("sin(x) + cos(y)")
        btn_draw_func = QPushButton("Drawing the Jaw Surface")
        btn_draw_func.clicked.connect(self.draw_function)
        
        layout_math.addWidget(self.txt_func)
        layout_math.addWidget(btn_draw_func)
        layout_math.addStretch()
        tabs.addTab(tab_math, "Math Surface")

        tab_env = QWidget()
        layout_env = QVBoxLayout(tab_env)
        form_env = QFormLayout()
        self.cb_cam = QComboBox()
        self.cb_cam.addItems(["Cam 1 (Default)", "Cam 2 (Side)", "Cam 3 (Top-down)"])
        self.cb_cam.currentIndexChanged.connect(self.change_camera)
        form_env.addRow("Camera:", self.cb_cam)
        layout_env.addLayout(form_env)
        
        layout_env.addWidget(QLabel("--- Lighting ---"))
        self.chk_l1 = QCheckBox("💡 Light 1 (White - Right)")
        self.chk_l1.setChecked(True)
        self.chk_l2 = QCheckBox("💡 Light 2 (Đỏ - Left)")
        self.chk_l3 = QCheckBox("💡 Light 3 (Blue - Bottom)")
        
        self.chk_l1.stateChanged.connect(self.update_lights)
        self.chk_l2.stateChanged.connect(self.update_lights)
        self.chk_l3.stateChanged.connect(self.update_lights)
        
        layout_env.addWidget(self.chk_l1)
        layout_env.addWidget(self.chk_l2)
        layout_env.addWidget(self.chk_l3)
        layout_env.addStretch()
        tabs.addTab(tab_env, "Environment")

        dock.setWidget(tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def update_shape_list(self, category):
        self.cb_shape.clear()
        self.cb_shape.addItems(self.shape_catalog[category].keys())

    def change_tool(self, index):
        self.gl_canvas.current_tool = index

    def add_shape(self):
        category = self.cb_category.currentText()
        shape_name = self.cb_shape.currentText()
        ShapeClass = self.shape_catalog[category][shape_name]
        self.gl_canvas.makeCurrent()

        try:
            new_obj = ShapeClass(VERTEX_GLSL, FRAGMENT_GLSL).setup()
            self.gl_canvas.objects.append(new_obj)
            self.lst_objects.addItem(f"[{category[:2]}] {shape_name}")
            self.lst_objects.setCurrentRow(len(self.gl_canvas.objects) - 1)
        except Exception as e:
            print(f"Lỗi khi khởi tạo {shape_name}: {e}")
        finally:
            self.gl_canvas.doneCurrent()

    def draw_function(self):
        expr = self.txt_func.text()
        self.gl_canvas.makeCurrent()
        try:
            def temp_func(x, y):
                try: return eval(expr.replace('^', '**'), {"__builtins__": None}, {"sin": np.sin, "cos": np.cos, "x": x, "y": y})
                except: return 0
            
            surface = FunctionSurface(VERTEX_GLSL, FRAGMENT_GLSL, func=temp_func).setup()
            self.gl_canvas.objects.append(surface)
            self.lst_objects.addItem(f"f(x,y): {expr}")
            self.lst_objects.setCurrentRow(len(self.gl_canvas.objects) - 1)
        except Exception as e:
            print("Lỗi vẽ hàm:", e)
        finally:
            self.gl_canvas.doneCurrent()

    def load_mesh(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open 3D file", "./assets", "3D Files (*.obj *.ply)")
        if file_name:
            self.gl_canvas.makeCurrent()
            try:
                mesh = MeshObject(VERTEX_GLSL, FRAGMENT_GLSL, file_name).setup()
                self.gl_canvas.objects.append(mesh)
                self.lst_objects.addItem(file_name.split("/")[-1])
                self.lst_objects.setCurrentRow(len(self.gl_canvas.objects) - 1)
            except Exception as e:
                print(f"Lỗi khi load mesh: {e}")
            finally:
                self.gl_canvas.doneCurrent()

    def delete_selected(self):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            self.gl_canvas.objects.pop(idx)
            self.lst_objects.takeItem(idx)
            self.gl_canvas.selected_idx = -1

    def clear_scene(self):
        self.gl_canvas.objects.clear()
        self.lst_objects.clear()
        self.gl_canvas.selected_idx = -1

    def on_object_selected(self, index):
        self.gl_canvas.selected_idx = index
        if 0 <= index < len(self.gl_canvas.objects):
            obj = self.gl_canvas.objects[index]
            self.cb_mode.setCurrentIndex(obj.render_mode)
            self.chk_wireframe.setChecked(obj.is_wireframe)

    def update_object_props(self, *args):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            obj = self.gl_canvas.objects[idx]
            obj.render_mode = self.cb_mode.currentIndex()
            obj.is_wireframe = self.chk_wireframe.isChecked()
            self.gl_canvas.update()

    def pick_color(self, *args):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            color = QColorDialog.getColor()
            if color.isValid():
                self.gl_canvas.objects[idx].flat_color = np.array(
                    [color.red()/255, color.green()/255, color.blue()/255],
                    dtype=np.float32
                )
                self.gl_canvas.update()

    def update_lights(self, *args):
        self.gl_canvas.light_states = [
            1 if self.chk_l1.isChecked() else 0,
            1 if self.chk_l2.isChecked() else 0,
            1 if self.chk_l3.isChecked() else 0
        ]
        self.gl_canvas.update()

    def change_camera(self, index):
        self.gl_canvas.current_cam_idx = index

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())