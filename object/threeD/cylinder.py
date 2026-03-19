import colorsys
import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from libs.transform import sincos
from object.threeD.truncated_cone import TruncatedConeObject


class CylinderObject(TruncatedConeObject):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader, 2.0, 2.0)