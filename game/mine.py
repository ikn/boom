from .engine import conf, gfx
from .engine.evt import bmode

from .entity import Entity


class Mine (Entity):
    def __init__ (self, vel, dirn, *args, **kwargs):
        Entity.__init__(self, vel, *args, **kwargs)

        self.size = conf.MINE['size']

        self.graphics.add(gfx.Colour(
            conf.MINE_COLOUR, self.size, conf.LAYERS['mine']
        ), *conf.MINE['offset'])

    def collide (self, rect, dirn):
        return True
