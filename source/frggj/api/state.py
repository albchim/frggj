from typing import Optional

from frggj.api.constants import GEvent, GControl


class GState(object):
    
    name = None
    current_frame = 0
    direction = None
    animation_name = None
    
    def __init__(self, direction, animation_frames: int = 0):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
        self.animation_frames = animation_frames
    
    def on_enter(self, previous_state: Optional[str]) -> None:
        self.current_frame = 0.0
        pass
    
    def on_exit(self, next_state: Optional[str]) -> None:
        pass
    
    def handle_event(self, event: dict) -> str:
        """Return next state name"""
        return None
    
    def tick(self) -> bool:
        if self.animation_frames < 1:
            return True
        elif self.current_frame >= self.animation_frames:
            return True
        self.current_frame += 1
        return False
        
        
    
class IdleState(GState):
    
    name = "idle"
    animation_name = "idle"
    
    def handle_event(self, event: int) -> str:
        """Handles events """
        # if event.get(GEvent.kHit]:
        #     return "hit"
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
        elif event == GEvent.kOnGround and event == GControl.kJump:
            return "jump"
        return "{0}_{1}".format(self.name, self.direction)


class WalkState(GState):
    
    name = "walk"
    animation_name = "walk"
    
    def handle_event(self, event: int) -> str:
        # if event.get(GEvent.kHit]:
        #     return "hit"
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
        elif event == GEvent.kOnGround and event == GControl.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
            
            
class TurnState(GState):
    
    name = "turn"
    animation_name = "turn"
        
    def handle_event(self, event: int) -> str:
        # if event.get(GEvent.kHit]:
        #     return "hit"
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
        elif event == GEvent.kOnGround and event == GControl.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
        
        
class RunState(GState):
    
    name = "run"
    animation_name = "run"
            
    def handle_event(self, event: int) -> str:
        # if event.get(GEvent.kHit]:
        #     return "hit"
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
        elif event == GEvent.kOnGround and event == GControl.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)


class JumpState(GState):
    
    name = "jump"
    animation_name = "jump"
            
    def handle_event(self, event: int) -> str:
        # if event.get(GEvent.kHit]:
        #     return "hit"
        if not self.tick():
            return "{0}_{1}".format(self.name, self.direction)
        if event.get(GControl.kAttack):
            return "attack_{0}".format(self.direction)
        if not event.get(GEvent.kOnGround):
            if event.get(GControl.kRight):
                if self.direction == "left":
                    return "jump_right"
            elif event.get(GControl.kLeft):
                if self.direction == "right":
                    return "jump_left"
        else:
            if event.get(GControl.kRight):
                if self.direction == "left":
                    return "turn_right"
                return "run_right" if event.get(GControl.kRun) else "walk_right"
            elif event.get(GControl.kLeft):
                if self.direction == "right":
                    return "turn_left"
                return "run_left" if event.get(GControl.kRun) else "walk_left"
            return "idle_{0}".format(self.direction)
        return "{0}_{1}".format(self.name, self.direction)
    
    
class AttackState(GState):
    
    name = "attack"
    animation_name = "attack"
            
    def handle_event(self, event: int) -> str:
        # if event.get(GEvent.kHit]:
        #     return "hit"
        if event.get(GControl.kRight):
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event.get(GControl.kRun) else "walk_right"
        elif event.get(GControl.kLeft):
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event.get(GControl.kRun) else "walk_left"
        elif event == GEvent.kOnGround and event == GControl.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
    
    
# class HitState(GState):
    
#     name = "hit"
#     animation_name = "hit"
            
#     def handle_event(self, event: int) -> str:
#         if event.get(GControl.kAttack]:
#             return "attack_{0}".format(self.direction)
#         elif event.get(GControl.kRight]:
#             if self.direction == "left":
#                 return "turn_right"
#             return "run_right" if event.get(GControl.kRun] else "walk_right"
#         elif event.get(GControl.kLeft]:
#             if self.direction == "right":
#                 return "turn_left"
#             return "run_left" if event.get(GControl.kRun] else "walk_left"
#         elif event == GEvent.kOnGround and event == GControl.kJump:
#             return "jump"
#         return "idle_{0}".format(self.direction)
