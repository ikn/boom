from pygame import Rect
from .engine import conf, gfx, entity
from .engine.evt import bmode


class Entity (entity.Entity):
    # subclasses must implement size as hitbox size
    # top-left is at (0, 0) in graphics

    def added (self):
        self.vel = [0, 0]
        self.rem = [0, 0]
        self.on_sfc = [0, 0]

    @property
    def rect (self):
        return Rect(self.graphics.pos, self.size)

    def update (self):
        v = self.vel
        rem = self.rem
        g = self.graphics
        on_sfc = self.on_sfc
        rects = self.world.rects

        v[1] += conf.GRAVITY
        pr = self.rect
        dp = [0, 0]
        for i in (0, 1):
            if on_sfc[not i]:
                v[i] *= conf.FRICTION[i]
            v[i] *= conf.AIR_RESISTANCE[i]
            dxf = v[i] + rem[i]
            dx = int(dxf)
            rem[i] = dxf - dx
            sgn = 1 if dx > 0 else -1

            if dx and sgn != on_sfc[i]:
                on_sfc[i] = 0
            for j in xrange(sgn * dx):
                dp[i] += sgn
                temp_pr = pr.move(dp)
                if (not self.world.border.contains(temp_pr) or
                    temp_pr.collidelist(rects) != -1):
                    on_sfc[i] = sgn
                    dp[i] -= sgn
                    v[i] = 0
                    break

        g.move_by(*dp)


class Player (Entity):
    def __init__ (self, n, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)

        self.id = n
        self.size = conf.PLAYER['size']

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
