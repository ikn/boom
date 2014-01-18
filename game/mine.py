from math import pi
from random import gauss

import pygame as pg
from pygame import Rect
from .engine import conf, gfx, entity, sched
from .engine.evt import bmode
from .engine.util import randsgn

from .entity import Entity


class Mine (Entity):
    def __init__ (self, real, within, player, vel, dirn, pos):
        Entity.__init__(self, vel)
        self.size = conf.MINE['size']
        r = Rect((0, 0), self.size)
        r.center = pos
        self.graphics.pos = r.clamp(within).topleft
        self.real = real
        self.player = player
        self.placed = None

    def added (self):
        Entity.added(self)

        dx, dy = conf.MINE['offset']
        g = gfx.Animation(
            gfx.util.Spritemap('mine.png', nrows=2), layer=conf.LAYERS['mine'],
            scheduler=self.world.scheduler
        ).add('run', frame_time=conf.MINE['animation_frame_time']).play('run')
        self.graphics.add(g, dx, dy)
        g.rot_origin = Rect((-dx, -dy), self.size).center

        r_speed = gauss(conf.MINE['rotate_speed'],
                        conf.MINE['rotate_speed_variance']) * randsgn()
        self.rotating = self.world.scheduler.interp(
            lambda t: r_speed * t, g.rotate
        )

    def collide (self, axis, sgn, v):
        s = self.world.scheduler
        s.rm_timeout(self.rotating)
        for g in self.graphics:
            g.angle = g.angle % (2 * pi)
            target = (pi / 2) * (2 - (axis + sgn))
            dist = abs(target - g.angle)
            dist2 = abs(target + 2 * pi - g.angle)
            if dist > dist2:
                target += 2 * pi
                dist = dist2

            def fix_final_state ():
                g.rotate_fn = (lambda sfc, angle:
                    pg.transform.rotate(sfc, angle * 180 / pi))

            s.interp_simple(g, 'angle', target,
                            float(dist) / conf.MINE_FIX_ANGLE_SPEED,
                            fix_final_state)
        self.vel = (0, 0)
        self.placed = (axis, sgn)
        self.world.play_snd('place')

    def update (self):
        if self.placed is None:
            Entity.update(self)

    def explode (self, destroy):
        pos = self.rect.center
        if self.real:
            if not destroy:
                self.world.particles('explode', pos)
                self.world.damage(pos, conf.MINE['explosion_radius'])
            self.world.end()

        axis, sgn = self.placed or (None, None)
        mode = 'crumble' if destroy else ('explode' if self.real else 'dud')
        self.world.play_snd(mode)
        if mode == 'crumble':
            self.world.particles('crumble', pos)
        else:
            self.world.add(DeadMine(mode, pos, self.vel, axis, sgn))
        self.world.rm(self)


class DeadMine (entity.Entity):
    def __init__ (self, mode, pos, vel, axis, sgn):
        # mode: explode, dud, crumble
        entity.Entity.__init__(self)
        self.graphics.pos = pos
        self.mode = mode
        self.vel = list(vel)

    def added (self):
        settings = conf.DEAD_MINE_GRAPHICS.get(self.mode)
        if settings is not None:
            g = gfx.Animation(
                gfx.util.Spritemap(self.mode + '.png',
                                   ncols=settings['ncols']),
                self.graphics.pos, conf.LAYERS['deadmine'],
                self.world.scheduler
            ) \
                .add('run', frame_time=settings['frame_time']) \
                .play('run', False, cb=self.finished)
            self.graphics.add(g, *settings['offset'])

    def update (self):
        for i in (0, 1):
            self.vel[i] *= conf.DEAD_MINE_DAMPING
        self.graphics.move_by(*self.vel)

    def finished (self):
        self.world.rm(self)
