import glfw
import numpy as np
from viewer import Viewer
from object.threeD.mesh_object import MeshObject as Object


def main():
    viewer = Viewer()
    model = Object("./shader/phong.vert", "./shader/phong.frag", "./assets/temp.obj", color=[1.0, 0.5, 0.0]).setup()
    viewer.add(model)
    viewer.run()

if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()