import numpy as np
import OpenGL.GL as GL
from libs.shader import *
from libs.buffer import *
from .. import Object


class TetrahedronSphereObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.vertices = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.942809, -0.33333],
            [-0.816497, -0.471405, -0.33333],
            [0.816497, -0.471405, -0.33333]
        ], dtype=np.float32)

        self.colors = np.array([
            [1.0, 0.0, 0.0],  # A
            [0.0, 1.0, 0.0],  # B
            [0.0, 0.0, 1.0],  # C
            [1.0, 1.0, 1.0],  # D
        ], dtype=np.float32)

        self.radius = 1
        self.next_id = 0
        self.lookup_table = {}
        self.all_vertices = []
        self.all_colors = []

        v = self.vertices
        c = self.colors

        final_indices = []
        faces = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
        
        for f in faces:
            ids = self.method1(v[f[0]], v[f[1]], v[f[2]], c[f[0]], c[f[1]], c[f[2]], step=4)
            final_indices.extend(ids)

        self.vertices = np.array(self.all_vertices, dtype=np.float32)
        self.colors = np.array(self.all_colors, dtype=np.float32)
        self.indices = np.array(final_indices, dtype=np.int32)

        self.normals = self.vertices / np.linalg.norm(self.vertices, axis=1, keepdims=True)

    def get_id(self, vertex, color):
        v_sphere = self.normal_radius(vertex)
        hashable = tuple(np.round(v_sphere, 6))
        
        if hashable not in self.lookup_table:
            self.lookup_table[hashable] = self.next_id
            self.all_vertices.append(v_sphere)
            self.all_colors.append(color)
            self.next_id += 1
        
        return self.lookup_table[hashable]

    def normal_radius(self, vertex):
        new_vertex = np.array(vertex, dtype=np.float32)
        norm_vertex = np.linalg.norm(new_vertex)

        if norm_vertex == 0:
            return vertex
        
        new_vertex = (new_vertex / norm_vertex) * self.radius
        return new_vertex

    def method1(self, A, B, C, cA, cB, cC, step):
        if step == 0:
            return [
                self.get_id(A, cA),
                self.get_id(B, cB),
                self.get_id(C, cC),
            ]

        mAB = (A + B) / 2; cAB = (cA + cB) / 2
        mAC = (A + C) / 2; cAC = (cA + cC) / 2
        mBC = (B + C) / 2; cBC = (cB + cC) / 2

        res = []
        res.extend(self.method1(A, mAB, mAC, cA, cAB, cAC, step - 1))
        res.extend(self.method1(B, mAB, mBC, cB, cAB, cBC, step - 1))
        res.extend(self.method1(C, mBC, mAC, cC, cBC, cAC, step - 1))
        res.extend(self.method1(mAB, mAC, mBC, cAB, cAC, cBC, step - 1))
        return res

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)


class CubeSphereObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.radius = 1.0
        self.vertices = []
        self.indices = []
        self.colors = []

        self.directions = [
            [0, 1, 0], [0, -1, 0],
            [1, 0, 0], [-1, 0, 0],
            [0, 0, 1], [0, 0, -1],
        ]

        subdivisions = 20
        self.method2(subdivisions)

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.int32)

        self.normals = self.vertices / np.linalg.norm(self.vertices, axis=1, keepdims=True)

    def method2(self, subdivisions):
        for i, direction in enumerate(self.directions):
            v, c, idx = self.generate_face(np.array(direction, dtype=np.float32), subdivisions)
            offset = i * (subdivisions ** 2)
            self.vertices.extend(v)
            self.colors.extend(c)
            self.indices.extend([j + offset for j in idx])

    def generate_face(self, local_up, subdivisions):
        axis_a = np.array([local_up[1], local_up[2], local_up[0]], dtype=np.float32)
        axis_b = np.cross(local_up, axis_a)

        face_vertices = []
        face_colors = []
        face_indices = []

        for y in range(subdivisions):
            for x in range(subdivisions):
                percent = np.array([x, y], dtype=np.float32) / (subdivisions - 1)
                point_on_cube = local_up + (percent[0] - 0.5) * 2 * axis_a + (percent[1] - 0.5) * 2 * axis_b
                point_on_sphere = (point_on_cube / np.linalg.norm(point_on_cube)) * self.radius
                face_vertices.append(point_on_sphere)
                color = (point_on_sphere / self.radius + 1.0) / 2.0
                face_colors.append(color)

                if x < subdivisions - 1 and y < subdivisions - 1:
                    i = x + y * subdivisions
                    face_indices.extend([i, i + subdivisions, i + subdivisions + 1])
                    face_indices.extend([i, i + subdivisions + 1, i + 1])

        return face_vertices, face_colors, face_indices

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)


class CoordinatesSphereObject(Object):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

        self.radius = 1.0
        self.vertices = []
        self.indices = []
        self.colors = []

        self.directions = [
            [0, 1, 0], [0, -1, 0],
            [1, 0, 0], [-1, 0, 0],
            [0, 0, 1], [0, 0, -1],
        ]

        v, c, idx = self.method3(lat_bands=40, long_bands=40)

        self.vertices = np.array(v, dtype=np.float32)
        self.colors = np.array(c, dtype=np.float32)
        self.indices = np.array(idx, dtype=np.int32)

        self.normals = self.vertices / np.linalg.norm(self.vertices, axis=1, keepdims=True)

    def method3(self, lat_bands=30, long_bands=30):
        vertices = []
        colors = []
        indices = []

        for lat in range(lat_bands + 1):
            theta = lat * np.pi / lat_bands
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            for lon in range(long_bands + 1):
                phi = lon * 2 * np.pi / long_bands
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = self.radius * sin_theta * cos_phi
                y = self.radius * cos_theta
                z = self.radius * sin_theta * sin_phi
                
                vertices.append([x, y, z])
                r = (x / self.radius + 1.0) / 2.0
                g = (y / self.radius + 1.0) / 2.0
                b = (z / self.radius + 1.0) / 2.0
                colors.append([r, g, b])

        for lat in range(lat_bands):
            for lon in range(long_bands):
                first = (lat * (long_bands + 1)) + lon
                second = first + long_bands + 1

                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])

        return vertices, colors, indices

    def draw(self, projection, view, model):
        super().draw_preprocess(projection, view, model)
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)