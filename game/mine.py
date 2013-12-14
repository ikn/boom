from pygame import Rect
from .engine import conf, gfx, entity
from .engine.evt import bmode

from .entity import Entity


class Mine (Entity):
    def __init__ (self, real, within, player, vel, dirn, pos):
        self.size = conf.MINE['size']
        r = Rect((0, 0), self.size)
        r.center = pos

        Entity.__init__(self, vel, *r.clamp(within).topleft)

        self.real = real
        self.player = player
        self.placed = None

        self.graphics.add(gfx.Colour(
            conf.MINE_COLOUR, self.size, conf.LAYERS['mine']
        ), *conf.MINE['offset'])

    def collide (self, axis, sgn):
        # TODO: fix angle/pos
        self.placed = (axis, sgn)

    def update (self):
        if self.placed is None:
            Entity.update(self)

    def explode (self, destroy):
        pos = self.rect.center
        if not destroy and self.real:
            self.world.damage(pos, conf.MINE['explosion_radius'])

        axis, sgn = self.placed or (None, None)
        mode = 'crumble' if destroy else ('explode' if self.real else 'dud')
        self.world.add(DeadMine(mode, self.vel, axis, sgn, *pos))
        self.world.rm(self)


class DeadMine (entity.Entity):
    def __init__ (self, mode, vel, axis, sgn, *args, **kwargs):
        entity.Entity.__init__(self, *args, **kwargs)
        self.vel = list(vel)
        # mode: explode, dud, crumble

    def added (self):
        # TODO: use animation callback (has one?)
        self.world.scheduler.counter(1).reset().cb(self.finished)

    def update (self):
        self.graphics.move_by(*self.vel)

    def finished (self):
        self.world.rm(self)
