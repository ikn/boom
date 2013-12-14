from pygame import Rect
from .engine import conf, entity


class Entity (entity.Entity):
    # subclasses must implement:
    #   size: hitbox size (top-left is at (0, 0) in `graphics`)
    #   collide(axis, sgn)
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
                    # collision
                    self.collide(i, sgn)
                    on_sfc[i] = sgn
                    dp[i] -= sgn
                    v[i] = 0
                    break

        g.move_by(*dp)
