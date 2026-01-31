# game
from frggj.api.level import GLevel
from frggj.api.scene import GScene
from frggj.api.entity import GPlayer, GEnemyGuard, GItemActionable
from frggj.api.asset import GAsset
from frggj.api.transform import GTransform
from frggj.api.camera import GCamera
from frggj.api.constants import GControl
import numpy as np

class GGame(object):
    def __init__(self, end_callback = None):
        self._current_level = 0
        self._levels = None
        self._player = None
        self._initialized = False
        self._assets = {}
        self._camera = None
        self._end_callback = end_callback

    def update(self, elapsed_time, controls):
        if self._player:
            self._player.update(elapsed_time, controls)
        self._levels[self._current_level].update(elapsed_time, self._player)
    
    def add_level(self, level : GLevel) -> None:
        if self._levels is None:
            self._levels = []
        self._levels.append(level)

    def set_current_level(self, level_index : int) -> None:
        if self._levels == None or level_index < len(self._levels):
            raise ValueError("The provided level index is greater than the number of available levels.")
        else:
            self._levels = level_index
    
    def get_current_level(self) -> GLevel:
        if self._levels is None:
            raise RuntimeError("The game has no levels.")
        else:
            return self._levels[self._current_level]
    
    def render(self, canvas, time):
        canvas.fill(50, 127, 200)
        canvas.z_reset()
        self.get_current_level().get_current_scene().render(canvas, self._player, self._camera, time)
    
    def initialize(self, execution_path):
        if self._initialized == False:
            assets_path = "{0}/../../assets".format(execution_path)
            player_asset = GAsset("player")
            player_asset.load("{0}/merchant/asset.json".format(assets_path))
            player_spawn = GTransform()
            self._player = GPlayer("player", 5, player_asset, player_spawn)
            self._camera = GCamera()
            self._camera.set_translation([-40.0, 3.0, 4.0])
            self._camera.set_eulers([0.0, 90, 0.0])
            self._camera.set_parent_constraint(player_spawn)

            dummy_level = GLevel()
            dummy_scene = GScene()
            
            enemy1_spawn = GTransform()
            enemy1_spawn.set_translation([0.0, 0.0, 0.0])
            enemy1 = GEnemyGuard("enemy1", 5, player_asset, enemy1_spawn)
            enemy1.set_max_patrol_distance(20, GControl.kRight)
            enemy1.set_max_patrol_distance(5, GControl.kLeft)
            dummy_scene.add_entity(enemy1)
            
            enemy2_spawn = GTransform()
            enemy2_spawn.set_translation([0.0, 0.0, -10.0])
            enemy2 = GEnemyGuard("enemy2", 5, player_asset, enemy2_spawn)
            enemy2.set_max_patrol_distance(5, GControl.kRight)
            enemy2.set_max_patrol_distance(-20, GControl.kLeft)
            dummy_scene.add_entity(enemy2)
            
            end_item_spawn = GTransform()
            end_item_spawn.set_translation([0.0, 0.0, 100.0])
            end_item = GItemActionable("end_item", player_asset, end_item_spawn)
            end_item.set_action_callback(self._end_callback)
            dummy_scene.add_entity(end_item)

            dummy_level.add_scene(dummy_scene)
            self.add_level(dummy_level)
            self._initialized = True
