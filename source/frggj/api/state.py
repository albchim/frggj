from typing import Optional
import logging

from frggj.api.constants import GEvent, GControl


class GState(object):
    
    name = None
    animation_name = None
    
    def __init__(self, direction, animation_frames: int = 0):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
        self._elapsed_time = 0.0
        self.current_frame = 0.0
        self.orig_direction = direction
        self.animation_frames = animation_frames
        self.moving = False
    
    def on_enter(self, previous_state: Optional[str]) -> None:
        self._elapsed_time = 0.0
        self.current_frame = 0.0
        pass
    
    def on_exit(self, next_state: Optional[str]) -> None:
        pass
    
    def get_frame(self):
        return self.current_frame
    
    def set_animation_frames(self, n_frames: int):
        self.animation_frames = n_frames
    
    def handle_event(self, event: dict, elapsed_time: float = None) -> str:
        """Return next state name"""
        return None
    
    def tick(self, elapsed_time: float) -> bool:
        self._elapsed_time += elapsed_time
        if self.animation_frames < 1:
            return True
        elif self._elapsed_time >= self.animation_frames/24:
            return True
        self.current_frame += 1
        return False
        

class IdleState(GState):
    
    name = "idle"
    animation_name = "idle"
    
    def handle_event(self, event: int, elapsed_time: float) -> str:
        """Handles events """
        if event.get(GControl.kAttack):
            return "attack_{0}".format(self.direction)
        elif event.get(GControl.kRight):
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event.get(GControl.kRun) else "walk_right"
        elif event.get(GControl.kLeft):
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event.get(GControl.kRun) else "walk_left"
        elif event.get(GEvent.kOnGround) and event.get(GControl.kJump):
            return "jump_{0}".format(self.direction)
        return None


class WalkState(GState):
    
    name = "walk"
    animation_name = "walk"
    
    def handle_event(self, event: int, elapsed_time: float) -> str:
        self.moving = event.get(GControl.kRight) or event.get(GControl.kLeft)
        if event.get(GControl.kAttack):
            return "attack_{0}".format(self.direction)
        elif event.get(GEvent.kOnGround) and event.get(GControl.kJump):
            return "jump_{0}".format(self.direction)
        elif event.get(GControl.kRight):
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event.get(GControl.kRun) else None
        elif event.get(GControl.kLeft):
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event.get(GControl.kRun) else None
        elif event.get(GEvent.kStop):
            return "idle_{0}".format(self.direction)
        return None
            
            
class TurnState(GState):
    
    name = "turn"
    animation_name = "turn"
        
    def handle_event(self, event: int, elapsed_time: float) -> str:
        if event.get(GControl.kAttack):
            return "attack_{0}".format(self.direction)
        elif event.get(GEvent.kOnGround) and event.get(GControl.kJump):
            return "jump_{0}".format(self.direction)
        elif event.get(GControl.kRight):
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event.get(GControl.kRun) else "walk_right"
        elif event.get(GControl.kLeft):
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event.get(GControl.kRun) else "walk_left"
        return "idle_{0}".format(self.direction)
        
        
class RunState(GState):
    
    name = "run"
    animation_name = "run"
            
    def handle_event(self, event: int, elapsed_time: float) -> str:
        self.moving = event.get(GControl.kRight) or event.get(GControl.kLeft)
        if event.get(GControl.kAttack):
            return "attack_{0}".format(self.direction)
        elif event.get(GEvent.kOnGround) and event.get(GControl.kJump):
            return "jump_{0}".format(self.direction)
        elif event.get(GControl.kRight):
            if self.direction == "left":
                return "turn_right"
            return None if event.get(GControl.kRun) else "walk_right"
        elif event.get(GControl.kLeft):
            if self.direction == "right":
                return "turn_left"
            return None if event.get(GControl.kRun) else "walk_left"
        elif event.get(GEvent.kStop):
            return "idle_{0}".format(self.direction)
        return None


class JumpState(GState):
    
    name = "jump"
    animation_name = "jump"
            
    def handle_event(self, event: int, elapsed_time: float) -> str:
        self.moving = event.get(GControl.kRight) or event.get(GControl.kLeft)
        if self.tick(elapsed_time):
            if event.get(GControl.kAttack):
                return "attack_{0}".format(self.direction)
            if event.get(GEvent.kOnGround):
                if event.get(GControl.kRight):
                    if self.direction == "left":
                        return "turn_right"
                    return "run_right" if event.get(GControl.kRun) else "walk_right"
                elif event.get(GControl.kLeft):
                    if self.direction == "right":
                        return "turn_left"
                    return "run_left" if event.get(GControl.kRun) else "walk_left"
                return "idle_{0}".format(self.direction)
        if event.get(GControl.kRight):
            self.direction = GControl.kRight
        elif event.get(GControl.kLeft):
            self.direction = GControl.kLeft
        return None
    
    
class AttackState(GState):
    
    name = "attack"
    animation_name = "attack"
            
    def handle_event(self, event: int, elapsed_time: float) -> str:
        if self.tick(elapsed_time):
            if event.get(GControl.kRight):
                if self.direction == "left":
                    return "turn_right"
                return "run_right" if event.get(GControl.kRun) else "walk_right"
            elif event.get(GControl.kLeft):
                if self.direction == "right":
                    return "turn_left"
                return "run_left" if event.get(GControl.kRun) else "walk_left"
            return "idle_{0}".format(self.direction)
        if event.get(GControl.kRight):
            self.direction = GControl.kRight
        elif event.get(GControl.kLeft):
            self.direction = GControl.kLeft
        return None
    
    def on_exit(self, next_state: Optional[str]) -> None:
        self.direction = self.orig_direction

