from typing import Dict, Optional
import logging

from frggj.api.state import GState, IdleState, WalkState, TurnState, RunState, JumpState, AttackState

BASE_STATES = {'idle_left': IdleState("left"), 'idle_right': IdleState("right"),
               'walk_left': WalkState("left"), 'walk_right': WalkState("right"),
               'turn_left': TurnState("left"), 'turn_right': TurnState("right"),
               'run_left': RunState("left"), 'run_right': RunState("right"),
               'jump_left': JumpState("left"), 'jump_right': JumpState("right"),
               'attack_left': AttackState("left"), 'attack_right': AttackState("right")}


class GStateManager(object):
    """A small finite state machine."""

    def __init__(self, states: Dict[str, GState], initial: str) -> None:
        self._states = states
        self._current_state = initial

    def start(self) -> None:
        if self._current_state not in self._states:
            raise KeyError(f"Unknown initial state: {self._current_state}")
        self._states[self._current_state].on_enter(None)

    def get_current_state(self) -> GState:
        return self._states[self._current_state]

    def get_animation_name(self) -> str:
        return getattr(self.get_current_state(), "animation_name", self._current_state)

    def transition(self, new_state: str) -> None:
        if new_state == self._current_state:
            return
        if new_state not in self._states:
            raise KeyError(f"Unknown state: {new_state}")
        prev = self._current_state
        self._states[prev].on_exit(new_state)
        self._current_state = new_state
        self._states[new_state].on_enter(prev)
        logging.info("Changing from state {0} to {1} ".format(prev, new_state))

    def handle_event(self, event: dict, elapsed_time: float) -> None:
        nxt = self.get_current_state().handle_event(event, elapsed_time)
        if nxt:
            self.transition(nxt)
