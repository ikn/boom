from math import atan2, degrees
from random import gauss

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
        self.world.play_snd('laser')

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
        self.throwing = False

        self.graphics.add(gfx.Colour(
            conf.PLAYER_COLOURS[n], self.size, conf.LAYERS['player']
        ), *conf.PLAYER['offset'])

    def walk_sound (self):
        self.world.play_snd('walk')
        self.walk_counter.t = gauss(conf.WALK_SOUND_DELAY,
                                    conf.WALK_SOUND_DELAY_VARIANCE)
        self.walk_counter.pause()

    def added (self):
        Entity.added(self)
        C = self.world.scheduler.counter
        self.done_jumping = C(conf.PLAYER['jump']['time'])
        self.walk_counter = C(0, True).reset().cb(self.walk_sound)
        self.walk_counter.pause()
        self.walked = False

    def update (self):
        Entity.update(self)
        if self.throwing:
            self.throw_time += self.world.scheduler.frame
        if self.walked:
            self.walked = False
            self.walk_counter.unpause()
        else:
            self.walk_counter.pause()

    def collide (self, axis, sgn, v):
        v = abs(v)
        if v > 5:
            self.world.play_snd('collide', min(v / 20., 1))

    def action (self, action):
        action = util.wrap_fn(getattr(self, action))

        def f (*args):
            if not self.dead:
                action(*args)

        return f

    def aim (self, pos):
        self.dirn = pos

    def move (self, dirn):
        if dirn:
            on_ground = self.on_sfc[1] == 1
            self.walked = self.walked or on_ground
            speed = conf.PLAYER['move_ground' if on_ground else 'move_air']
            self.vel[0] += dirn * speed

    def jump (self, evt):
        if evt[bmode.DOWN]:
            s = conf.PLAYER['jump']['initial']
            if self.on_sfc[1] == 1:
                self.world.play_snd('jump')
                self.vel[1] -= s
                self.done_jumping.reset()
            elif self.on_sfc[0]:
                # wall jump
                self.world.play_snd('walljump')
                wj = conf.PLAYER['walljump']
                self.vel[0] -= self.on_sfc[0] * s * wj['horiz']
                self.vel[1] -= s * wj['vert']
                self.done_jumping.reset()
        elif evt[bmode.HELD] and not self.done_jumping:
            self.vel[1] -= conf.PLAYER['jump']['continue']

    def throw (self, real, evt):
        down = evt[bmode.DOWN]
        up = evt[bmode.UP]
        while True:
            if self.throwing:
                if up:
                    up -= 1
                    self.release(real, self.throw_time)
                    self.throwing = False
                    yield None
                else:
                    break
            # now self.throwing is False
            if down:
                down -= 1
                self.throwing = True
                self.throw_time = 0
            else:
                break

    def release (self, real, force):
        self.world.play_snd('throw')

        vel = list(self.vel)
        dx, dy = dirn = self.dirn
        adirn = (dx * dx + dy * dy) ** .5
        if adirn:
            s = (min(force, conf.PLAYER['max_throw_speed']) *
                 conf.PLAYER['throw_speed'])
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

    def throw_real (self, evt):
        if not self.thrown_real:
            for x in self.throw(self.have_real, evt):
                self.thrown_real = True
                break

    def throw_dummy (self, evt):
        list(self.throw(False, evt))

    def detonate (self):
        self.world.detonate_mines(self, False)

    def destroy (self):
        if self.lasers_left:
            if self.world.add_lasers(self):
                self.lasers_left -= 1

    def die (self):
        # TODO: graphics
        self.dead = True
        self.walk_counter.cancel()
        self.world.rm(self)
