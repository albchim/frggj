# entity
from copy import deepcopy
import numpy as np
from frggj.api.state_manager import BASE_STATES, GStateManager
from frggj.api.constants import GControl, GEvent
from frggj.api.transform import GTransform


class GEntityType(object):
    kPlayer = 0
    kEnemy = 1
    kSet = 2
    kItem = 3
    kPlatform = 4
    kBackground = 5


class GEntity(object):
    def __init__(self, name, asset=None, transform=None):
        self._name = name
        self._asset = asset
        self._transform = transform
        self._direction = np.asarray([0, 0, 1])
        self._velocity = 0
        self._active = True
        self._active_animation = 0
        self._action_callback = None
        self._animation_start_time = 0.0
    
    def set_action_callback(self, callback):
        self._action_callback = callback
        
    def action_callback(self, args=[]):
        if self._action_callback:
            self._action_callback(*args)
    
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
        anim_index = self._asset._anim_map.get(anim_label, 0)
        if anim_index != self._active_animation:
            self._active_animation = anim_index
            self._animation_start_time = 0
        
    def animation_step(self, time):
        if self._animation_start_time == 0:
            self._animation_start_time = time
        asset = self.get_asset()
        asset_animation = asset.get_animation(self.get_active_animation())
        if asset_animation:
            frame = int(0.024 * (time - self._animation_start_time))%asset_animation.get_length()
            animation_frame = asset_animation.get_frame(frame)
        else:
            animation_frame = None
        return animation_frame
        
    def _init_state_manager(self, states: dict, init_state: str):
        self._state_manager = GStateManager(states, init_state)
        self._state_manager.start()
        
    def _init_anim_state_frames(self, states: dict):
        for key in states:
            states[key].set_animation_frames(self.get_asset().get_takes().get_animation(self.get_asset()._anim_map.get(states[key].name, 0)).get_length())
        return states


class GCollideableMixin(object):
    
    _collideable = True
    
    def is_collideable(self):
        return self._collideable
    
    def solve_collision(self, player):
        if np.abs(self.get_transform().get_translation()[2] - player.get_transform().get_translation()[2]) < 1.0:
            player._velocity = 0
            increment = -0.5 if player._direction[2] > 0 else +0.5
            player.get_transform().set_translation([player.get_transform().get_translation()[0], player.get_transform().get_translation()[1], player.get_transform().get_translation()[2] + increment])
            player._state_manager.handle_event({GEvent.kStop: True, 
                                                player._state_manager.get_current_state().direction: False})
            return True
        else:
            return False


class GPlayer(GEntity):
    def __init__(self, name, health, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._init_state_manager(self._init_anim_state_frames(deepcopy(BASE_STATES)), "idle_right")
        self._health = health
        self._state = None
        self._in_air_counter = 1000
    
    def update(self, elapsed_time, controls):
        if self._in_air_counter < 100:
            self._in_air_counter += 1
            controls[GEvent.kOnGround] = False
        else:   
            controls[GEvent.kOnGround] = True
        controls[GEvent.kStop] = self._velocity < 1.0
        if controls[GControl.kJump]:
            self._in_air_counter = 0
        self._state_manager.handle_event(controls)
        self.set_active_animation(self._state_manager.get_animation_name())
        if self._state_manager.get_current_state().direction == "right":
            self._direction[2] = 1
        elif self._state_manager.get_current_state().direction == "left":
            self._direction[2] = -1
        if self._state_manager.get_current_state().moving:
            if self._state_manager.get_current_state().name in ["walk", "jump"]:
                self._velocity = 30
            elif self._state_manager.get_current_state().name == "run":
                self._velocity = 50
        super().update(elapsed_time)
    
    def get_type(self):
        return GEntityType.kPlayer


class GEnemy(GEntity):
    def __init__(self, name, health, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._init_state_manager(self._init_anim_state_frames(deepcopy(BASE_STATES)), "idle_left")
        self._health = health
        self._state = None
        self._velocity = 0.0
        self._active_animation = 1
        self._max_patrol_distance = {GControl.kRight: 10.0, GControl.kLeft: 10.0}
        
    def brain(self, player = None) -> dict:
        return {}
    
    def update(self, elapsed_time, player):
        self._state_manager.handle_event(self.brain(player))
        self.set_active_animation(self._state_manager.get_animation_name())
        if self._state_manager.get_current_state().direction == "right":
            self._direction[2] = 1
        elif self._state_manager.get_current_state().direction == "left":
            self._direction[2] = -1
        self._velocity = 0
        if self._state_manager.get_current_state().name in ["walk", "jump"]:
            self._velocity = 10
        elif self._state_manager.get_current_state().name == "run":
            self._velocity = 15
        super().update(elapsed_time)
    
    def get_type(self):
        return GEntityType.kEnemy


class GEnemyGuard(GEnemy):
    
    def set_max_patrol_distance(self, distance: float, side: str):
        if side not in [GControl.kRight, GControl.kLeft]:
            raise ValueError("Invalid max patrol distance side provided.")
        self._max_patrol_distance[side] = distance
    
    def brain(self, player):
        events = {}
        
        if not player:
            return events
        
        if np.abs(self.get_transform().get_translation()[2] - player.get_transform().get_translation()[2]) < 3.0:
            for control in [GControl.kRight, GControl.kLeft]:
                events[control] = False
            events[GControl.kAttack] = True
            return events
        
        # Patrol cycle
        if (self._direction[2] == 1 and self.get_transform().get_translation()[2] > self._max_patrol_distance[GControl.kRight]) or \
            (self._direction[2] == -1 and self.get_transform().get_translation()[2] < self._max_patrol_distance[GControl.kLeft]):
            for control in [GControl.kRight, GControl.kLeft]:
                events[control] = not (self._state_manager.get_current_state().direction == control)
        else:
            for control in [GControl.kRight, GControl.kLeft]:
                events[control] = self._state_manager.get_current_state().direction == control
                
        return events


class GPlatform(GEntity):
    def __init__(self, name, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._state = None
        self._active_animation = 1

    def update(self, elapsed_time, player):
        pass
        
    def get_type(self):
        return GEntityType.kPlatform


class GSet(GEntity):
    def __init__(self, name, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._state = None
        self._active_animation = 1

    def update(self, elapsed_time, player):
        pass
        
    def get_type(self):
        return GEntityType.kSet


class GItem(GEntity):
    def __init__(self, name, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._state = None
        self._active_animation = 1

    def update(self, elapsed_time, player):
        pass
        
    def get_type(self):
        return GEntityType.kItem


class GBackground(GEntity):
    def __init__(self, name, asset=None, transform=None):
        super().__init__(name, asset, transform)
        self._state = None
        self._active_animation = 1

    def update(self, elapsed_time, player):
        pass
        
    def get_type(self):
        return GEntityType.kBackground


class GItemActionable(GItem, GCollideableMixin):
    def update(self, elapsed_time, player):
        if player:
            if np.abs(self.get_transform().get_translation()[2] - player.get_transform().get_translation()[2]) < 1.0:
                if player._state_manager.get_current_state().name == GControl.kAttack:
                    self._actioned = True
                    if self._action_callback:
                        self._action_callback()
                self.solve_collision(player)
        super().update(elapsed_time, player)