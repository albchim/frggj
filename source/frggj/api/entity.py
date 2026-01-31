# entity
import numpy as np


class GEntityType(object):
    kPlayer = 0
    kEnemy = 1
    kScenery = 2
    kItem = 3
    kPlatform = 4


class GEntity(object):
    def __init__(self, name, asset=None, transform=None):
        self._name = name
        self._asset = asset
        self._transform = transform
        self._direction = np.asarray([0, 0, 1])
        self._velocity = 0
        self._active = True
        self._active_animation = 0
    
    def update(self, elapsed_time):
        if self._velocity > 0:
            translation = self._transform.get_translation()
            translation += self._direction * self._velocity * elapsed_time
            self._transform.set_translation(translation)
            self._velocity = max(self._velocity - elapsed_time * 20.0, 0)
            if self._direction[2] > 0:
                self._transform.set_eulers([0.0, 0.0, 0.0])
            if self._direction[2] < 0:
                self._transform.set_eulers([0.0, 180.0, 0.0])
    
    def set_name(self, name):
        self._name = name
    
    def get_name(self):
        return self._name
    
    def set_asset(self, asset):
        self._asset = asset
    
    def get_asset(self):
        return self._asset
    
    def set_transform(self, transform):
        self._transform = transform
    
    def get_transform(self):
        return self._transform
    
    def set_active(self, status):
        self._active = status
    
    def get_active(self):
        return self._active
    
    def get_asset(self):
        return self._asset
    
    def get_active_animation(self):
        return self._active_animation
    
    def set_active_animation(self, index):
        self._active_animation = index


class GPlayer(GEntity):
    def __init__(self, name, health, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._health = health
        self._state = None
    
    def update(self, elapsed_time, controls):
        if controls["right"]:
            self._direction = np.asarray([0, 0, 1])
            self._velocity = 10.0
            self._active_animation = 1
        if controls["left"]:
            self._direction = np.asarray([0, 0, -1])
            self._velocity = 10.0
            self._active_animation = 1
        if True not in controls.values() and self._velocity == 0.0:
            self._active_animation = 0
        super().update(elapsed_time)
    
    def get_type(self):
        return GEntityType.kPlayer


class GEnemy(GEntity):
    def __init__(self, name, health, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._health = health
        self._state = None
        self._velocity = 0.0
        self._active_animation = 1
    
    def update(self, elapsed_time):
        self._velocity = 10.0
        if self._direction[2] == 1 and self.get_transform().get_translation()[2] > 20:
            self._direction[2] = -1
        if self._direction[2] == -1 and self.get_transform().get_translation()[2] < 5:
            self._direction[2] = 1
        super().update(elapsed_time)
    
    def get_type(self):
        return GEntityType.kEnemy
