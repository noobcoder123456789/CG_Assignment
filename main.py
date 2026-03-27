import glfw
import numpy as np
from viewer import Viewer
from object.threeD.mesh_object import MeshObject as Objec
from object.threeD.axis import *
from object.threeD.function_surface import *


VERTEX_GLSL = "./shader/vertex.vert"
FRAGMENT_GLSL = "./shader/fragment.frag"
OBJ_PATH = "./assets/temp.obj"

def main():
    viewer = Viewer(800, 800)
    model = Objec(VERTEX_GLSL, FRAGMENT_GLSL, OBJ_PATH, color=[1.0, 0.5, 0.0]).setup()
    viewer.add(model)
    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()