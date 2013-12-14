from .engine import conf, gfx
from .engine.evt import bmode

from .entity import Entity
from .mine import Mine


class Player (Entity):
    def __init__ (self, n, *args, **kwargs):
        Entity.__init__(self, (0, 0), *args, **kwargs)

        self.id = n
        self.size = conf.PLAYER['size']
        self.thrown_real = False

        self.graphics.add(gfx.Colour(
            conf.PLAYER_COLOURS[n], self.size, conf.LAYERS['player']
        ), *conf.PLAYER['offset'])

    def added (self):
        Entity.added(self)
        self.done_jumping = \
            self.world.scheduler.counter(conf.PLAYER['jump_time'])

    def move (self, dirn):
        speed = conf.PLAYER['move_ground' if self.on_sfc[1] else 'move_air']
        self.vel[0] += dirn * speed

    def jump (self, evt):
        if evt[bmode.DOWN] and self.on_sfc[1]:
            self.vel[1] -= conf.PLAYER['jump_initial']
            self.done_jumping.reset()
        elif evt[bmode.HELD] and not self.done_jumping:
            self.vel[1] -= conf.PLAYER['jump_continue']

    def throw (self, real):
        axis, dirn = max((abs(vx), i, vx > 0)
                         for i, vx in enumerate(self.vel))[1:]
        dirn = axis + dirn * 2
        side = ('left', 'top', 'right', 'bottom')[dirn]
        pos = getattr(self.rect, 'mid' + side)
        self.world.add_mine(real, Mine(self.vel, dirn, *pos))

    def throw_real (self):
        if not self.thrown_real:
            self.throw(True)
            self.thrown_real = True

    def throw_dummy (self):
        self.throw(False)
