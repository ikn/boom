from pygame import Rect
from .engine import conf, entity


class Entity (entity.Entity):
    # subclasses must implement:
    #   size: hitbox size (top-left is at (0, 0) in `graphics`)
    #   collide(axis, sgn, vel)
    def __init__ (self, vel, *args, **kwargs):
        entity.Entity.__init__(self, *args, **kwargs)
        self.vel = list(vel) or [0, 0]

    def added (self):
        self.rem = [0, 0]
        self.on_sfc = [0, 0]

    @property
    def rect (self):
        # hitbox
        return Rect(self.graphics.pos, self.size)

    def collides (self, rect):
        return (not self.world.border.contains(rect) or
                rect.collidelist(self.world.rects) != -1)

    def update (self):
        v = self.vel
        rem = self.rem
        g = self.graphics
        on_sfc = self.on_sfc

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

            for j in xrange(sgn * dx):
                dp[i] += sgn
                if self.collides(pr.move(dp)):
                    # collision
                    self.collide(i, sgn, v[i])
                    dp[i] -= sgn
                    v[i] = 0
                    break

        g.move_by(*dp)

        on_sfc[0] = on_sfc[1] = 0
        pr = self.rect
        for i in xrange(4):
            dp = [0, 0]
            axis = i % 2
            sgn = 1 if i >= 2 else -1
            dp[axis] += sgn
            if self.collides(pr.move(dp)):
                on_sfc[axis] = sgn
