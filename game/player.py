from math import atan2, degrees

from pygame import Rect
from .engine import conf, gfx, util, entity
from .engine.evt import bmode

from .entity import Entity
from .mine import Mine


class Lasers (entity.Entity):
    def __init__ (self, player, mines):
        entity.Entity.__init__(self, *player.rect.center)
        self.player = player
        self.mines = mines

    def added (self):
        self.world.scheduler.add_timeout(self.finished, conf.LASER['time'])

    def update (self):
        w = conf.LASER['width']
        c = conf.LASER['colour']
        l = conf.LAYERS['laser']
        G = gfx.Graphic
        x, y = self.player.rect.center
        pad = 5

        self.graphics.rm(*self.graphics._graphics)
        self.graphics.pos = (x, y)
        add = self.graphics.add
        for m in self.mines:
            mx, my = m.rect.center
            dist = ((mx - x) ** 2 + (my - y) ** 2) ** .5
            sfc = util.blank_sfc((dist + 2 * pad, w + 2 * pad))
            sfc.fill(c, (pad, pad, dist, w))

            g = G(sfc, layer=l)
            dy = pad + w / 2
            g.rot_anchor = (pad, dy)
            g.rotate(atan2(y - my, mx - x))
            add(g, -pad, -dy)

    def finished (self):
        self.world.detonate_mines(self.mines, True)
        self.world.rm(self)


class Player (Entity):
    def __init__ (self, n, have_real, *args, **kwargs):
        Entity.__init__(self, (0, 0), *args, **kwargs)

        self.id = n
        self.size = conf.PLAYER['size']
        self.have_real = have_real
        self.thrown_real = False
        self.dirn = [0, 0]
        self.dead = False
        self.lasers_left = conf.PLAYER['num_lasers']

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
        self.dirn = pos

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

    def throw (self, real):
        vel = list(self.vel)
        dx, dy = dirn = self.dirn
        adirn = (dx * dx + dy * dy) ** .5
        if adirn:
            s = conf.PLAYER['throw_speed']
            vel[0] += s * dx / adirn
            vel[1] += s * dy / adirn

        pos = dirn
        dirns = []
        for d in xrange(4):
            axis = d % 2
            this_sgn = 1 if d >= 2 else -1
            x = pos[axis]
            sgn = 1 if x > 0 else -1
            if sgn != this_sgn:
                x = 0
            dirns.append((sgn * x, conf.THROW_DIRN_PRIO[d], d))
        dirn = max(dirns)[2]

        side = ('left', 'top', 'right', 'bottom')[dirn]
        r = self.rect
        pos = getattr(r, 'mid' + side)
        self.world.add_mine(Mine(real, r, self.id, vel, dirn, pos))

    def throw_real (self):
        if not self.thrown_real:
            self.throw(self.have_real)
            self.thrown_real = True

    def throw_dummy (self):
        self.throw(False)

    def detonate (self):
        self.world.detonate_mines(self, False)

    def destroy (self):
        if self.lasers_left:
            if self.world.add_lasers(self):
                self.lasers_left -= 1

    def die (self):
        # TODO: graphics
        self.dead = True
        self.world.rm(self)
