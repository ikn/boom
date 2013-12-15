from math import ceil
import random

import pygame as pg
from pygame import Rect
from .engine import conf, gfx
from .engine.game import World

from .player import Player, Lasers


class Level (World):
    def init (self, name='main'):
        self.name = name
        self.players = []
        self.mines = [{'real': [], 'dummy': []} for i in xrange(2)]
        self.rects = []
        gm = self.graphics
        self.border = Rect((0, 0), gm.orig_size)

        self.load_evts()
        self.has_real = random.randrange(2)
        for i in xrange(2):
            self.add_player(i, self.has_real == i)

        layers = conf.LAYERS
        gm.add(gfx.Graphic('background.png', layer=layers['bg']))
        g = gfx.Graphic('solid.png')
        for r in conf.LEVELS[name]['rects']:
            r = Rect(r)
            self.rects.append(r)
            w = int(ceil(float(r.w) / g.w))
            h = int(ceil(float(r.h) / g.h))
            gm.add(gfx.Tilemap(
                g.size, (lambda x, y: 0, w, h), {0: g}, r.topleft,
                layers['rect']
            ).crop(((0, 0), r.size)))

    def load_evts (self):
        eh = self.evthandler
        eh.load('ui')
        eh['quit'].cb(lambda: conf.GAME.quit_world())

        n_pads = pg.joystick.get_count()
        if n_pads == 0:
            eh.load('kbshared')
        else:
            if n_pads == 1:
                eh.load('kb')
                eh.load('x360-1')
                eh.assign_devices(y=0)
            else:
                eh.load('x360-0')
                eh.load('x360-1')
                eh.assign_devices(x=0, y=1)
            eh.set_deadzones(('pad', conf.PAD_DEADZONE))

    def add_player (self, n, has_real):
        x, y = (50 * n, 50)
        p = Player(n, has_real, x, y)
        self.players.append(p)
        self.add(p)

        n = str(n)
        eh = self.evthandler
        for action in (
            'aim', 'move', 'jump', 'throw_real', 'throw_dummy', 'detonate',
            'destroy'
        ):
            eh[action + n].cb(p.action(action))

    def add_mine (self, m):
        self.mines[m.player]['real' if m.real else 'dummy'].append(m)
        self.add(m)

    def add_lasers (self, player):
        mines = sum((sum(mines.itervalues(), []) for mines in self.mines), [])
        if mines:
            self.add(Lasers(player, mines))
        return bool(mines)

    def detonate_mines (self, mines, destroy):
        # mines is player or list of mines
        if not isinstance(mines, list):
            mines = sum(self.mines[mines.id].itervalues(), [])
        for m in mines:
            ms = self.mines[m.player]['real' if m.real else 'dummy']
            if m in ms:
                m.explode(destroy)
                ms.remove(m)
            # else it already got removed

    def damage (self, pos, radius):
        x, y = pos
        for p in self.players:
            px, py = p.rect.center
            if ((x - px) ** 2 + (y - py) ** 2) ** .5 <= radius:
                p.die()

        alive = [p.id for p in self.players if not p.dead]

        from .engine.util import normalise_colour
        cs = [normalise_colour(conf.PLAYER_COLOURS[i]) for i in alive]
        cs.append((0, 0, 0))
        c = [sum(l[:3]) for l in zip(*cs)]
        self.graphics.fade_to(2, c)
        #self.scheduler.add_timeout(conf.GAME.quit_world, 2)
