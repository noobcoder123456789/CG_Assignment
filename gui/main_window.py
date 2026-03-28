import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QCheckBox, QLabel, QGroupBox, QFormLayout, QDockWidget,
    QListWidget, QTabWidget, QLineEdit, QFileDialog, QColorDialog, QSlider
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

from object.twoD.arrow import ArrowObject
from object.twoD.circle import CircleObject
from object.twoD.ellipse import EllipseObject
from object.twoD.hexagon import HexagonObject
from object.twoD.pentagon import PentagonObject
from object.twoD.rectangle import RectangleObject
from object.twoD.star import StarObject
from object.twoD.trapezium import TrapeziumObject
from object.twoD.triangle import TriangleObject

from object.threeD.cone import ConeObject
from object.threeD.cube import CubeObject
from object.threeD.cylinder import CylinderObject
from object.threeD.prism import PrismObject
from object.threeD.tetrahedron import TetrahedronObject
from object.threeD.torus import TorusObject
from object.threeD.truncated_cone import TruncatedConeObject
from object.threeD.sun import SunObject

from object.threeD.sphere import CoordinatesSphereObject, CubeSphereObject, TetrahedronSphereObject 
from object.threeD.function_surface import FunctionSurface
from object.threeD.mesh_object import MeshObject
from gui.canvas import *


VERTEX_GLSL = "./shader/vertex.vert"
FRAGMENT_GLSL = "./shader/fragment.frag"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_sgd_running = False
        self.sgd_ball_idx = -1
        self.target_surface_idx = -1

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
        self.timer.timeout.connect(self.sgd_step)
        self.timer.start(16) 

    def add_sun(self):
        self.gl_canvas.makeCurrent()
        try:
            sun = SunObject(VERTEX_GLSL, FRAGMENT_GLSL).setup()
            sun.canvas = self.gl_canvas
            sun.render_mode = 0 
            sun.flat_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
            sun.intensity = 50.0
            sun.scale = [0.3, 0.3, 0.3]
            sun.translation = [2.0, 3.0, 2.0]
            if hasattr(sun, 'update_model_matrix'):
                sun.update_model_matrix()
            
            self.gl_canvas.objects.append(sun)
            self.gl_canvas.sun_idx = len(self.gl_canvas.objects) - 1
            self.lst_objects.addItem("Light source")
            self.lst_objects.setCurrentRow(self.gl_canvas.sun_idx)
            self.cb_tool.setCurrentIndex(2)
            
            self.gl_canvas.has_sun = 1
            self.gl_canvas.update()
            
        finally:
            self.gl_canvas.doneCurrent()

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
            file_name, _ = QFileDialog.getOpenFileName(self, "Choose Texture Image", "", "Images (*.png *.jpg *.jpeg)")
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
        self.cb_mode.addItems(["Flat Color", "Vertex Color", "Phong Shading", "Texture", "Phong+Tex", "Depth Map", "Phong + Contour"])
        self.cb_mode.setCurrentIndex(2)
        self.cb_mode.currentIndexChanged.connect(self.update_object_props)
        form_render.addRow("Shading:", self.cb_mode)

        self.chk_wireframe = QCheckBox("Wireframe")
        self.chk_wireframe.stateChanged.connect(self.update_object_props)
        form_render.addRow("", self.chk_wireframe)

        self.btn_color = QPushButton("Change Flat Color")
        self.btn_color.clicked.connect(self.pick_color)
        form_render.addRow("Color:", self.btn_color)

        self.btn_tex = QPushButton("Load Texture Image")
        self.btn_tex.clicked.connect(self.load_texture)
        form_render.addRow("Texture:", self.btn_tex)

        layout_render.addLayout(form_render)
        layout_render.addStretch()
        tabs.addTab(tab_render, "Material")

        tab_math = QWidget()
        layout_math = QVBoxLayout(tab_math)
        
        layout_math.addWidget(QLabel("Predefined Loss Functions:"))
        self.cb_loss_funcs = QComboBox()
        self.cb_loss_funcs.addItems([
            "Himmelblau Function", 
            "Rosenbrock Function (a=1, b=100)", 
            "Booth Function",
            "quadratic 2D",
            "Custom",
        ])
        self.cb_loss_funcs.currentIndexChanged.connect(self.on_loss_func_changed)
        layout_math.addWidget(self.cb_loss_funcs)

        layout_math.addWidget(QLabel("Mathematical function z = f(x, y):"))
        self.txt_func = QLineEdit("(x**2 + y - 11)**2 + (x + y**2 - 7)**2")
        
        btn_draw_func = QPushButton("Draw Surface")
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

        btn_add_sun = QPushButton("Spawn Sun (White Light)")
        btn_add_sun.setStyleSheet("background-color: #f57f17; color: white; font-weight: bold;")
        btn_add_sun.clicked.connect(self.add_sun)
        layout_env.addWidget(btn_add_sun)

        self.btn_light_color = QPushButton("Change light color")
        self.btn_light_color.setStyleSheet("background-color: #0277bd; color: white; font-weight: bold;")
        self.btn_light_color.clicked.connect(self.pick_light_color)
        layout_env.addWidget(self.btn_light_color)

        self.lbl_intensity = QLabel("Intensity:")
        layout_env.addWidget(self.lbl_intensity)
        
        self.slider_intensity = QSlider(Qt.Horizontal)
        self.slider_intensity.setMinimum(1)
        self.slider_intensity.setMaximum(500)
        self.slider_intensity.setValue(50)
        self.slider_intensity.valueChanged.connect(self.change_intensity)
        layout_env.addWidget(self.slider_intensity)
        
        layout_env.addStretch()
        tabs.addTab(tab_env, "Environment")

        tab_sgd = QWidget()
        layout_sgd = QVBoxLayout(tab_sgd)
        form_sgd = QFormLayout()

        self.txt_lr = QLineEdit("0.01")
        form_sgd.addRow("Learning Rate (η):", self.txt_lr)

        self.btn_spawn_ball = QPushButton("Spawn Agent")
        self.btn_spawn_ball.setStyleSheet("background-color: #c62828; color: white; font-weight: bold;")
        self.btn_spawn_ball.clicked.connect(self.spawn_sgd_ball)
        form_sgd.addRow("", self.btn_spawn_ball)

        self.btn_run_sgd = QPushButton("Run / Pause SGD")
        self.btn_run_sgd.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        self.btn_run_sgd.clicked.connect(self.toggle_sgd)
        form_sgd.addRow("", self.btn_run_sgd)

        self.lbl_sgd_pos = QLabel("Current Position:\nX (w1): --\nY (w2): --\nLoss: --")
        self.lbl_sgd_pos.setStyleSheet(
            "color: #ffca28; "
            "font-family: 'Consolas', monospace; "
            "font-size: 14px; "
            "font-weight: bold; "
            "background-color: #222; "
            "padding: 10px; "
            "border-radius: 5px;"
        )

        form_sgd.addRow(self.lbl_sgd_pos)
        layout_sgd.addLayout(form_sgd)
        layout_sgd.addStretch()
        tabs.addTab(tab_sgd, "SGD Sim")

        dock.setWidget(tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.update_inspector_ui()

    def pick_light_color(self, *args):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            obj = self.gl_canvas.objects[idx]
            
            if type(obj).__name__ == 'SunObject':
                color = QColorDialog.getColor()
                if color.isValid():
                    obj.flat_color = np.array(
                        [color.red()/255, color.green()/255, color.blue()/255],
                        dtype=np.float32
                    )
                    self.lst_objects.item(idx).setText(f"Light Source (RGB: {color.red()}, {color.green()}, {color.blue()})")
                    self.gl_canvas.update()
            else:
                print("Please select a 'Light Source' in the Scene Graph before changing the color!")

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
            new_obj.canvas = self.gl_canvas
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
                try:
                    return eval(expr.replace('^', '**'), {"__builtins__": None}, {"sin": np.sin, "cos": np.cos, "x": x, "y": y})
                except:
                    return 0
            
            surface = FunctionSurface(VERTEX_GLSL, FRAGMENT_GLSL, func=temp_func).setup()
            surface.render_mode = 6
            surface.canvas = self.gl_canvas
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
                mesh.canvas = self.gl_canvas
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
            self.update_inspector_ui()

    def clear_scene(self):
        self.gl_canvas.objects.clear()
        self.lst_objects.clear()
        self.gl_canvas.selected_idx = -1
        self.update_inspector_ui()

    def on_object_selected(self, index):
        self.gl_canvas.selected_idx = index
        if 0 <= index < len(self.gl_canvas.objects):
            obj = self.gl_canvas.objects[index]
            self.cb_mode.setCurrentIndex(obj.render_mode)
            self.chk_wireframe.setChecked(obj.is_wireframe)
            
            if type(obj).__name__ == 'SunObject' and hasattr(obj, 'intensity'):
                self.slider_intensity.blockSignals(True)
                self.slider_intensity.setValue(int(obj.intensity))
                self.slider_intensity.blockSignals(False)

        self.update_inspector_ui()

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

    def change_intensity(self, value):
        idx = self.gl_canvas.selected_idx
        if 0 <= idx < len(self.gl_canvas.objects):
            obj = self.gl_canvas.objects[idx]
            if type(obj).__name__ == 'SunObject':
                obj.intensity = float(value)
                self.gl_canvas.update()

    def change_camera(self, index):
        self.gl_canvas.current_cam_idx = index

    def update_inspector_ui(self):
        idx = self.gl_canvas.selected_idx
        has_selection = (0 <= idx < len(self.gl_canvas.objects))
        
        self.cb_mode.setEnabled(has_selection)
        self.chk_wireframe.setEnabled(has_selection)
        self.btn_color.setEnabled(has_selection)
        self.btn_tex.setEnabled(has_selection)
        
        is_sun = False
        if has_selection:
            obj = self.gl_canvas.objects[idx]
            if type(obj).__name__ == 'SunObject':
                is_sun = True
                self.btn_tex.setEnabled(False)
                
        self.btn_light_color.setVisible(is_sun)
        self.lbl_intensity.setVisible(is_sun)
        self.slider_intensity.setVisible(is_sun)

    def spawn_sgd_ball(self):
        surface_idx = -1
        for i, obj in enumerate(self.gl_canvas.objects):
            if type(obj).__name__ == 'FunctionSurface':
                surface_idx = i
                break

        if surface_idx == -1:
            print("Draw a Math Surface before dropping the ball!")
            return

        self.target_surface_idx = surface_idx
        surface = self.gl_canvas.objects[surface_idx]

        self.gl_canvas.makeCurrent()
        ball = CubeSphereObject(VERTEX_GLSL, FRAGMENT_GLSL).setup()
        ball.canvas = self.gl_canvas
        ball.render_mode = 1
        ball.flat_color = np.array([1.0, 0.2, 0.2], dtype=np.float32)
        ball.scale = [0.15, 0.15, 0.15] 

        start_x, start_y = 3.0, 3.0
        start_z = surface.get_visual_z(start_x, start_y)

        ball.translation = [start_x, start_z + 0.15, start_y]
        ball.update_model_matrix()

        self.gl_canvas.objects.append(ball)
        self.sgd_ball_idx = len(self.gl_canvas.objects) - 1
        self.lst_objects.addItem("SGD Agent")
        self.lst_objects.setCurrentRow(self.sgd_ball_idx)
        
        loss_val = surface.get_real_z(start_x, start_y)
        self.lbl_sgd_pos.setText(f"Current Position:\nX (w1): {start_x:.5f}\nY (w2): {start_y:.5f}\nLoss:   {loss_val:.5f}")
        
        self.gl_canvas.doneCurrent()
        self.gl_canvas.update()

    def toggle_sgd(self):
        self.is_sgd_running = not self.is_sgd_running

    def sgd_step(self):
        if not self.is_sgd_running or self.sgd_ball_idx == -1 or self.target_surface_idx == -1:
            return

        try:
            ball = self.gl_canvas.objects[self.sgd_ball_idx]
            surface = self.gl_canvas.objects[self.target_surface_idx]
            x = ball.translation[0]
            y = ball.translation[2] 
            grad_x, grad_y = surface.get_gradient(x, y)
            lr = float(self.txt_lr.text())
            new_x = x - lr * grad_x
            new_y = y - lr * grad_y
            new_x = max(-5.0, min(5.0, new_x))
            new_y = max(-5.0, min(5.0, new_y))
            new_z = surface.get_visual_z(new_x, new_y)
            ball.translation = [new_x, new_z + 0.15, new_y]
            loss_val = surface.get_real_z(new_x, new_y)
            self.lbl_sgd_pos.setText(f"Current Position:\nX (w1): {new_x:.5f}\nY (w2): {new_y:.5f}\nLoss:   {loss_val:.5f}")
            ball.update_model_matrix()
            
        except Exception as e:
            print("Error calculate SGD:", e)
            self.is_sgd_running = False

    def on_loss_func_changed(self, index):
        if index == 0:
            self.txt_func.setText("(x**2 + y - 11)**2 + (x + y**2 - 7)**2")
        elif index == 1:
            # Rosenbrock (Banana): a=1, b=100. Đáy thung lũng hẹp.
            self.txt_func.setText("(1 - x)**2 + 100 * (y - x**2)**2")
        elif index == 2:
            self.txt_func.setText("(x + 2*y - 7)**2 + (2*x + y - 5)**2")
        elif index == 3:
            self.txt_func.setText("x**2 + y**2")
        else:
            self.txt_func.setText("")