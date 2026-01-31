# asset
from frggj.api.io import import_texture
from frggj.api.mesh import GMesh
from frggj.api.skeleton import GSkeleton
from frggj.api.animation import GAnimationTakes
import json
import os


class GAsset(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._mesh = None
        self._skeleton = None
        self._texture = None
        self._takes = None
        self._anim_map = {}

    def load(self, filepath):
        with open(filepath) as json_data:
            asset_data = json.load(json_data)
            json_data.close()
            self._mesh = GMesh(self)
            self._mesh.load(os.path.join(os.path.dirname(filepath), asset_data["mesh"]))
            self._texture = import_texture(os.path.join(os.path.dirname(filepath), asset_data["texture"]))
            if asset_data["skeleton"]:
                self._skeleton = GSkeleton(self)
                self._skeleton.load(os.path.join(os.path.dirname(filepath), asset_data["skeleton"]))
            if asset_data["animation"]:
                self._takes = GAnimationTakes(self)
                self._takes.load(os.path.join(os.path.dirname(filepath), asset_data["animation"]))
            if asset_data.get("animation_map"):
                with open(os.path.join(os.path.dirname(filepath), asset_data["animation_map"])) as anim_map_json:
                    self._anim_map = json.load(anim_map_json)

    def get_mesh(self):
        return self._mesh

    def get_texture(self):
        return self._texture

    def get_skeleton(self):
        return self._skeleton

    def set_takes(self, takes):
        self._takes = takes

    def get_takes(self):
        return self._takes

    def get_animation(self, index):
        if self._takes:
            return self._takes.get_animation(index)
        else:
            return None
