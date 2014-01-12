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


def sgn (x):
    return 1 if x >= 0 else -1


def pt_dist (a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** .5


def lines_intersect (a, b, x, y):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, x, y

    a1 = y2 - y1
    b1 = x1 - x2
    c1 = x2 * y1 - x1 * y2
    r3 = a1 * x3 + b1 * y3 + c1
    r4 = a1 * x4 + b1 * y4 + c1
    if r3 and r4 and sgn(r3) == sgn(r4):
        return False

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = x4 * y3 - x3 * y4
    r1 = a2 * x1 + b2 * y1 + c2
    r2 = a2 * x2 + b2 * y2 + c2
    if r1 and r2 and sgn(r1) == sgn(r2):
        return False

    denom = a1 * b2 - a2 * b1
    if denom == 0:
        return False

    offset = abs(denom) / 2
    return [(num + sgn(num) * offset) / denom
            for num in (b1 * c2 - b2 * c1, a2 * c1 - a1 * c2)]


def rect_lines (r):
    a = r.topleft
    for b in (r.topright, r.bottomright, r.bottomleft, r.topleft):
        yield (a, b)
        a = b


def line_intersects_rect (a, b, r, every=False):
    if every:
        pts = []
    for x, y in rect_lines(r):
        i = lines_intersect(a, b, x, y)
        if i:
            if every:
                pts.append(i)
            else:
                return i
    return pts if every else False


def line_intersects_rects (a, b, rects, every=False):
    if every:
        pts = []
    for r in rects:
        i = line_intersects_rect(a, b, r, every)
        if i:
            if every:
                pts += i
            else:
                return i
    return pts if every else False


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
