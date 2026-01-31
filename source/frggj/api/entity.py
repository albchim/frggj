# entity
import numpy as np
from frggj.api.state_manager import BASE_STATES, GStateManager


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
    
    def set_active_animation(self, anim_label):
        self._active_animation = self._asset._anim_map.get(anim_label, 0)


class GPlayer(GEntity):
    def __init__(self, name, health, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._init_state_manager(self._init_anim_state_frames(BASE_STATES))
        self._health = health
        self._state = None
    
    def _init_state_manager(self, states):
        self._state_manager = GStateManager(BASE_STATES, "idle_right")
        self._state_manager.start()
        
    def _init_anim_state_frames(self, states):
        for key in states:
            states[key].set_animation_frames(self.get_asset().get_takes().get_animation(self.get_asset()._anim_map.get(states[key].name, 0)).get_length())
        return states
    
    def update(self, elapsed_time, controls):
        self._state_manager.handle_event(controls)
        self.set_active_animation(self._state_manager.get_animation_name())
        self._velocity = 0
        if self._state_manager.get_current_state().direction == "right":
            self._direction = np.asarray([0, 0, 1])
        elif self._state_manager.get_current_state().direction == "left":
            self._direction = np.asarray([0, 0, -1])
        if self._state_manager.get_current_state().name == "walk":
            self._velocity = 10
        elif self._state_manager.get_current_state().name == "run":
            self._velocity = 15
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
