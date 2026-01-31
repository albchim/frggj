# level
from frggj.api.scene import GScene
import os


class GLevel(object):
    def __init__(self, name):
        self._name = name
        self._scenes = None
        self._current_scene = 0
    
    def update(self, elapsed_time, player):
        self._scenes[self._current_scene].update(elapsed_time, player)

    def add_scene(self, scene : GScene) -> None:
        if self._scenes is None:
            self._scenes = []
        self._scenes.append(scene)
    
    def set_current_scene(self, scene_index : int) -> None:
        if self._scenes == None or scene_index < len(self._scenes):
            raise ValueError("The provided scene index is greater than the number of available scenes.")
        else:
            self._current_scene = scene_index
    
    def get_current_scene(self) -> GScene:
        if self._scenes is None:
            raise RuntimeError("The game has no scenes.")
        else:
            return self._scenes[self._current_scene]
    
    def load(self, levels_path, assets_lib):
        scenes = os.listdir(os.path.join(levels_path, self._name))
        self._scenes = [None] * len(scenes)
        for scene_name in scenes:
            scene_index = int(scene_name[6:]) - 1
            new_scene = GScene()
            scene_description_filepath = os.path.join(levels_path, self._name, scene_name, "description.json")
            new_scene.load(scene_description_filepath, assets_lib)
            self._scenes[scene_index] = new_scene
        
