from math import pi, cos, sin, ceil
import random

from .engine import conf
from .engine.gfx import Graphic, Tilemap
from .engine.util import randsgn, ir, blank_sfc, normalise_colour


def tile_graphic (g, r, layer):
    w = int(ceil(float(r.w) / g.w))
    h = int(ceil(float(r.h) / g.h))
    return Tilemap(
        g.size, (lambda x, y: 0, w, h), {0: g}, r.topleft, layer
    ).crop(((0, 0), r.size))


def rand (arg):
    if isinstance(arg, dict):
        return random.gauss(arg['mean'], arg['dev'])
    else:
        return random.expovariate(1. / arg) * randsgn()


class Particles (Graphic):
    def __init__ (self, scheduler, data, pos=(0, 0), layer=0):
        self.ptcls = ptcls = []
        for g in data['colours']:
            left = g['amount']
            while left > 0:
                sz = max(ir(rand(data['size'])), 1)
                left -= sz * sz
                speed = rand(data['speed'])
                angle = random.uniform(0, 2 * pi)
                vel = [speed * cos(angle), speed * sin(angle)]
                life = max(ir(rand(data['life'])), 0)
                c = normalise_colour(g['colour'])
                # life, pos, vel, size
                ptcls.append([life, [0, 0], vel, sz, c])

        Graphic.__init__(self, blank_sfc((0, 0)), pos, layer)
        self.anchor = 'center'

        scheduler.add_timeout(self.update, frames=1)

    def update (self):
        damp = conf.PARTICLE_DAMPING
        ptcls = []
        xs = []
        ys = []
        for p in self.ptcls:
            p[0] -= 1
            if p[0]:
                life, pos, vel, sz, c = p
                vel[0] *= damp
                vel[1] *= damp
                pos[0] += vel[0]
                pos[1] += vel[1]
                x, y = pos
                xs.append(x)
                xs.append(x + sz)
                ys.append(y)
                ys.append(y + sz)
                ptcls.append(p)


        if not ptcls:
            self.manager.rm(self)
            return False

        max_x = max(abs(min(xs)), abs(max(xs)))
        max_y = max(abs(min(ys)), abs(max(ys)))
        sfc = blank_sfc((2 * max_x, 2 * max_y))
        for p in ptcls:
            x, y = p[1]
            sz = p[3]
            sfc.fill(p[4], (x + max_x, y + max_y, sz, sz))

        self.ptcls = ptcls
        self.orig_sfc = sfc
        return True
