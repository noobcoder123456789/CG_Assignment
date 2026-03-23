import glfw
from viewer import Viewer
from object.threeD.mesh_object import MeshObject as Object
from object.threeD.axis import *


def main():
    viewer = Viewer(800, 800)
    model = Object("./shader/phong.vert", "./shader/phong.frag", "./assets/temp.obj", color=[1.0, 0.5, 0.0]).setup()
    axis = AxisObject().setup()
    viewer.add(axis, model)
    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()