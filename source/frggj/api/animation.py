# animation
import numpy as np
from frggj.api.io import import_animation, import_takes


class GAnimationTakes(object):
    def __init__(self, parent):
        self._parent = parent
        self._takes = []
        self._active_take = 0

    def set_active(self, index):
        self._active_take = index

    def get_active(self):
        return self._active_take

    def get_active_animation(self):
        return self._takes[self._active_take]

    def add_animation(self, animation):
        self._takes.append(animation)
    
    def get_animation(self, index):
        return self._takes[index]

    def load(self, filepath):
        takes_data = import_takes(filepath)

        fps = takes_data["fps"]
        for take in takes_data["takes"]:
            new_animation = GAnimation()
            new_animation.set_fps(fps)
            new_animation.set_length(take["length"])
            new_animation.set_frames(np.asarray(take["frames"]).astype(float))
            self.add_animation(new_animation)


class GAnimation(object):
    def __init__(self):
        self._fps = None
        self._length = None
        self._frames = None

    def set_frames(self, frames):
        self._frames = frames

    def set_length(self, length):
        self._length = length

    def get_frames(self):
        return self._frames

    def get_frame(self, index):
        return self._frames[index]

    def get_length(self):
        return self._length

    def set_fps(self, fps):
        self._fps = fps

    def get_fps(self):
        return self._fps

    def load(self, filepath):
        self._fps, self._length, self._frames = import_animation(filepath)

    def interpolate(self, from_index, to_index):
        from_matrix = self._frames[from_index]
        to_matrix = self._frames[to_index]
