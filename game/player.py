from .engine import conf, gfx, util
from .engine.evt import bmode

from .entity import Entity
from .mine import Mine


throw_dirn_prio = [1, 0, 1, 2]


class Player (Entity):
    def __init__ (self, n, have_real, *args, **kwargs):
        Entity.__init__(self, (0, 0), *args, **kwargs)

        self.id = n
        self.size = conf.PLAYER['size']
        self.have_real = have_real
        self.thrown_real = False
        self.dirn = 3
        self.dead = False

        self.graphics.add(gfx.Colour(
            conf.PLAYER_COLOURS[n], self.size, conf.LAYERS['player']
        ), *conf.PLAYER['offset'])

    def added (self):
        Entity.added(self)
        self.done_jumping = \
            self.world.scheduler.counter(conf.PLAYER['jump_time'])

    def collide (self, axis, sgn):
        pass

    def action (self, action):
        action = util.wrap_fn(getattr(self, action))

        def f (*args):
            if not self.dead:
                action(*args)

        return f

    def aim (self, pos):
        dirns = []
        for d in xrange(4):
            axis = d % 2
            this_sgn = 1 if d >= 2 else -1
            x = pos[axis]
            sgn = 1 if x > 0 else -1
            if sgn != this_sgn:
                x = 0
            dirns.append((sgn * x, throw_dirn_prio[d], d))

        self.dirn = max(dirns)[2]

    def move (self, dirn):
        speed = conf.PLAYER['move_ground' if self.on_sfc[1] else 'move_air']
        self.vel[0] += dirn * speed

    def jump (self, evt):
        if evt[bmode.DOWN] and self.on_sfc[1]:
            self.vel[1] -= conf.PLAYER['jump_initial']
            self.done_jumping.reset()
        elif evt[bmode.HELD] and not self.done_jumping:
            self.vel[1] -= conf.PLAYER['jump_continue']
        else:
            return
        self.dirn = 1

    def throw (self, real):
        dirn = self.dirn
        vel = list(self.vel)
        vel[dirn % 2] += (1 if dirn >= 2 else -1) * conf.PLAYER['throw_speed']

        side = ('left', 'top', 'right', 'bottom')[dirn]
        pos = getattr(self.rect, 'mid' + side)
        self.world.add_mine(Mine(real, self.id, vel, dirn, *pos))

    def throw_real (self):
        if not self.thrown_real:
            self.throw(self.have_real)
            self.thrown_real = True

    def throw_dummy (self):
        self.throw(False)

    def detonate (self):
        self.world.detonate_mines(self)

    def die (self):
        # TODO: graphics
        self.dead = True
        self.world.rm(self)
