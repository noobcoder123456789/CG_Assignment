import numpy as np
from object.threeD.sphere import CubeSphereObject

class SunObject(CubeSphereObject):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)
        
        self.render_mode = 0
        self.flat_color = np.array([1.0, 0.9, 0.0], dtype=np.float32)
        self.scale = [0.4, 0.4, 0.4]
        self.translation = [10.0, 10.0, 10.0]