# engine
import pygame as pg
import numpy as np
from frggj.api.game import GGame
from frggj.api.canvas import GCanvas

# from groucho.canvas import GCanvas

class GEngineState(object):
    kIntro = 1
    kMenu = 2
    kEnd = 3
    kLevel = 4


class GEngine(object):
    def __init__(self, fullscreen=False):
        self._state = GEngineState.kMenu
        self._game = GGame()

        self._width = 426
        self._height = 240
        self._scale_factor = 4
        self._pg = pg
        self._pg.init()
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
            elapsed_time = self._clock.tick(60)*0.001
            for event in self._pg.event.get():
                if event.type == self._pg.QUIT:
                    running = False
                if event.type == self._pg.KEYDOWN and event.key == self._pg.K_ESCAPE:
                    running = False
            pressed_keys = self._pg.key.get_pressed()
            if self._state == GEngineState.kMenu:
                if pressed_keys[self._pg.K_RETURN]:
                    self._state = GEngineState.kLevel
            if self._state == GEngineState.kLevel:
                self._run_game()

                """self._init_level()
                self._scene._assets[0].set_active(0)
                asset_transform = self._scene._assets[0].get_transform()
                asset_translation = asset_transform.get_translation()
                asset_eulers = asset_transform.get_eulers()
                front_axis = asset_transform.get_front()
                side_axis = asset_transform.get_side()
                step = np.asarray([0.0, 0.0, 0.0])
                if pressed_keys[ord('w')]:
                    self._scene._assets[0].set_active(1)
                    step = step + front_axis * 1.0
                if pressed_keys[ord('s')]:
                    self._scene._assets[0].set_active(1)
                    step = step - front_axis * 1.0
                if pressed_keys[ord('q')]:
                    step = step + side_axis * 0.1
                if pressed_keys[ord('e')]:
                    step = step - side_axis * 0.1
                if pressed_keys[ord('a')]:
                    asset_eulers[1] += 3
                if pressed_keys[ord('d')]:
                    asset_eulers[1] -= 3
                asset_transform.set_translation(asset_translation + step)
                asset_transform.set_eulers(asset_eulers)
                self._scene._assets[0].set_transform(asset_transform)"""
                    
            if self._state == GEngineState.kMenu:
                self._run_menu()
            elif self._state == GEngineState.kLevel:
                self._run_game()

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

    """def _init_game(self):
        if self._scene is None:
            self._scene = GScene()
            self._scene.set_camera(np.asarray([
                [1.0, 0.0, 0.0, -3.0],
                [0.0, 0.9848077, -0.1736482, 7.5],
                [0.0, 0.1736482, 0.9848077, -15.0],
                [0.0, 0.0, 0.0, 1.0]]))
            self._scene.add_asset("merchant", "D:/projects/groucho/assets/merchant/asset.json")
            self._scene._assets[0]._transform._matrix[0] = np.asarray([1.0, 0.0, 0.0, 0])
            self._scene._assets[0]._transform._matrix[1] = np.asarray([0.0, 1.0, 0.0, 0])
            self._scene._assets[0]._transform._matrix[2] = np.asarray([0.0, 0.0, 1.0, 0])
            self._scene.add_asset("terrain", "D:/projects/groucho/assets/desert_terrain/asset.json")
            # self._scene.add_asset("merchant", "D:/projects/groucho/assets/desert_tavern/asset.json")

            self._scene.get_camera().set_parent_constraint(self._scene._assets[0].get_transform())"""

    def _run_game(self):
        self._game.initialize()
        self._game.update(self._pg.time.get_ticks())
        self._game.render(self._canvas, self._pg.time.get_ticks())
        
    def _run_end(self):
        a = 0

if __name__ == '__main__':
    engine = GEngine()
