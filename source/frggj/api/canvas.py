# canvas
import numpy as np


class GCanvas(object):
    def __init__(self, width, height, game):
        self._game = game
        self._width = width
        self._height = height
        self._surface = game._pg.surface.Surface((width, height))
        self._pixels = np.ones((width, height, 3)).astype('uint8')
        self._z = np.ones((width, height))
        
    def get_pixels(self):
        return self._pixels

    def fill(self, r, g, b):
        self._pixels[:,:,:] = np.asarray([r, g, b]).astype('uint8')

    def z_reset(self):
        self._z[:,:] = 1e32

    @property
    def size(self):
        return (self._width, self._height)
