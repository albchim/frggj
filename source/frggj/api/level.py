# level
from frggj.api.scene import GScene


class GLevel(object):
    def __init__(self):
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
