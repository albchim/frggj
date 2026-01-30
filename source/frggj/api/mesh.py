# mesh
from frggj.api.io import import_mesh


class GMesh(object):
    def __init__(self, parent):
        self._parent = parent
        self._points = None
        self._triangles = None
        self._uvs = None

    def set_points(self, points):
        self._points = points

    def set_triangles(self, triangles):
        self._triangles = triangles

    def set_uvs(self, uvs):
        self._uvs = uvs

    def get_points(self):
        return self._points

    def get_triangles(self):
        return self._triangles

    def get_uvs(self):
        return self._uvs

    def load(self, filepath):
        self._points, self._triangles, self._uvs = import_mesh(filepath)
