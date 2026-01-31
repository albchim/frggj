# engine
import pygame as pg
import numpy as np
from frggj.api.constants import GControl
from frggj.api.game import GGame
from frggj.api.canvas import GCanvas

# from groucho.canvas import GCanvas

class GEngineState(object):
    kIntro = 1
    kMenu = 2
    kEnd = 3
    kGame = 4


class GEngine(object):
    def __init__(self, execution_path, fullscreen=False):
        self._execution_path = execution_path
        self._state = GEngineState.kMenu
        self._game = GGame()

        self._width = 426
        self._height = 240
        self._scale_factor = 4
        self._elapsed_time = 0
        self._pg = pg
        self._pg.init()
        self._controls = None
        self._font = self._pg.font.SysFont("Arial" , 18 , bold = True)
        self._clock = self._pg.time.Clock()
        if fullscreen:
            self._screen = self._pg.display.set_mode((self._width * self._scale_factor, self._height * self._scale_factor), self._pg.FULLSCREEN)
        else:
            self._screen = self._pg.display.set_mode((self._width * self._scale_factor, self._height * self._scale_factor))
        self._clock = self._pg.time.Clock()
        self._canvas = GCanvas(self._width, self._height, self)
        self._run()

    def _run(self):
        running = True
        while running:
            self._elapsed_time = self._clock.tick(60)*0.001
            for event in self._pg.event.get():
                if event.type == self._pg.QUIT:
                    running = False
                if event.type == self._pg.KEYDOWN and event.key == self._pg.K_ESCAPE:
                    running = False
            pressed_keys = self._pg.key.get_pressed()
            if self._state == GEngineState.kMenu:
                if pressed_keys[self._pg.K_RETURN]:
                    self._state = GEngineState.kGame
            if self._state == GEngineState.kGame:
                self._controls = {GControl.kUp: False, GControl.kDown: False, GControl.kLeft: False, 
                                  GControl.kRight: False, GControl.kJump: False, GControl.kRun: False, 
                                  GControl.kAttack: False, GControl.kAction: False}
                self._controls[GControl.kUp] = pressed_keys[ord('w')] or pressed_keys[self._pg.K_UP]
                self._controls[GControl.kDown] = pressed_keys[ord('s')] or pressed_keys[self._pg.K_DOWN]
                self._controls[GControl.kLeft] = pressed_keys[ord('a')] or pressed_keys[self._pg.K_LEFT]
                self._controls[GControl.kRight] = pressed_keys[ord('d')] or pressed_keys[self._pg.K_RIGHT]
                self._controls[GControl.kJump] = pressed_keys[self._pg.K_SPACE]
                self._controls[GControl.kRun] = pressed_keys[self._pg.K_LSHIFT]
                self._controls[GControl.kAction] = pressed_keys[self._pg.K_LCTRL]
                self._controls[GControl.kAttack] = pressed_keys[self._pg.K_x]
                    
            if self._state == GEngineState.kMenu:
                self._run_menu()
            elif self._state == GEngineState.kGame:
                self._run_game()
            elif self._state == GEngineState.kEnd:
                running = False

            surf = pg.surfarray.make_surface(self._canvas.get_pixels())
            surf = self._pg.transform.scale(surf, (self._width * self._scale_factor, self._height * self._scale_factor))
            self._screen.blit(surf, (0,0))
            fps = str(int(self._clock.get_fps()))
            fps_t = self._font.render(fps , 1, self._pg.Color("RED"))
            self._screen.blit(fps_t,(0,0))
            self._pg.display.update()

    def run_intro(self):
        self._canvas.fill(0, 255, 0)
        a = 0

    def _run_menu(self):
        self._canvas.fill(255, 0, 0)
        a = 0

    def _run_game(self):
        self._game.initialize(self._execution_path)
        self._game.update(self._elapsed_time, self._controls)
        self._game.render(self._canvas, self._pg.time.get_ticks())
        
    def _run_end(self):
        a = 0

if __name__ == '__main__':
    engine = GEngine()
