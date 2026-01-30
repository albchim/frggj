from typing import Optional

from utils.constants import GEvent


class GState(object):
    
    name = None
    direction = None
    animation_name = None
    
    def on_enter(self, previous_state: Optional[str]) -> None:
        pass
    
    def on_exit(self, next_state: Optional[str]) -> None:
        pass
    
    def handle_event(self, event: dict) -> str:
        """Return next state name"""
        return None
        
    
class IdleState(GState):
    
    name = "idle"
    animation_name = "idle"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
    
    def handle_event(self, event: int) -> str:
        """Handles events """
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kAttack]:
            return "attack_{0}".format(self.direction)
        elif event[GEvent.kMoveRight]:
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event[GEvent.kRun] else "walk_right"
        elif event[GEvent.kMoveLeft]:
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event[GEvent.kRun] else "walk_left"
        elif event == GEvent.kOnGround and event == GEvent.kJump:
            return "jump"
        return self.name


class WalkState(GState):
    
    name = "walk"
    animation_name = "walk"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
    
    def handle_event(self, event: int) -> str:
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kAttack]:
            return "attack_{0}".format(self.direction)
        elif event[GEvent.kMoveRight]:
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event[GEvent.kRun] else "walk_right"
        elif event[GEvent.kMoveLeft]:
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event[GEvent.kRun] else "walk_left"
        elif event == GEvent.kOnGround and event == GEvent.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
            
            
class TurnState(GState):
    
    name = "turn"
    animation_name = "turn"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
        
    def handle_event(self, event: int) -> str:
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kAttack]:
            return "attack_{0}".format(self.direction)
        elif event[GEvent.kMoveRight]:
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event[GEvent.kRun] else "walk_right"
        elif event[GEvent.kMoveLeft]:
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event[GEvent.kRun] else "walk_left"
        elif event == GEvent.kOnGround and event == GEvent.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
        
        
class RunState(GState):
    
    name = "run"
    animation_name = "run"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
            
    def handle_event(self, event: int) -> str:
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kAttack]:
            return "attack_{0}".format(self.direction)
        elif event[GEvent.kMoveRight]:
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event[GEvent.kRun] else "walk_right"
        elif event[GEvent.kMoveLeft]:
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event[GEvent.kRun] else "walk_left"
        elif event == GEvent.kOnGround and event == GEvent.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)


class JumpState(GState):
    
    name = "jump"
    animation_name = "jump"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
            
    def handle_event(self, event: int) -> str:
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kAttack]:
            return "attack_{0}".format(self.direction)
        if not event[GEvent.kOnGround]:
            if event[GEvent.kMoveRight]:
                if self.direction == "left":
                    return "jump_right"
            elif event[GEvent.kMoveLeft]:
                if self.direction == "right":
                    return "jump_left"
        else:
            if event[GEvent.kMoveRight]:
                if self.direction == "left":
                    return "turn_right"
                return "run_right" if event[GEvent.kRun] else "walk_right"
            elif event[GEvent.kMoveLeft]:
                if self.direction == "right":
                    return "turn_left"
                return "run_left" if event[GEvent.kRun] else "walk_left"
            return "idle_{0}".format(self.direction)
        return "{0}_{1}".format(self.name, self.direction)
    
    
class AttackState(GState):
    
    name = "attack"
    animation_name = "attack"
    
    def __init__(self, direction):
        if direction not in ["left", "right"]:
            raise ValueError("Wrong initialization for direction")
        self.direction = direction
            
    def handle_event(self, event: int) -> str:
        # if event[GEvent.kHit]:
        #     return "hit"
        if event[GEvent.kMoveRight]:
            if self.direction == "left":
                return "turn_right"
            return "run_right" if event[GEvent.kRun] else "walk_right"
        elif event[GEvent.kMoveLeft]:
            if self.direction == "right":
                return "turn_left"
            return "run_left" if event[GEvent.kRun] else "walk_left"
        elif event == GEvent.kOnGround and event == GEvent.kJump:
            return "jump"
        return "idle_{0}".format(self.direction)
    
    
# class HitState(GState):
    
#     name = "hit"
#     animation_name = "hit"
            
#     def handle_event(self, event: int) -> str:
#         if event[GEvent.kAttack]:
#             return "attack_{0}".format(self.direction)
#         elif event[GEvent.kMoveRight]:
#             if self.direction == "left":
#                 return "turn_right"
#             return "run_right" if event[GEvent.kRun] else "walk_right"
#         elif event[GEvent.kMoveLeft]:
#             if self.direction == "right":
#                 return "turn_left"
#             return "run_left" if event[GEvent.kRun] else "walk_left"
#         elif event == GEvent.kOnGround and event == GEvent.kJump:
#             return "jump"
#         return "idle_{0}".format(self.direction)
