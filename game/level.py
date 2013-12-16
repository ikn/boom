from math import ceil
import random

import pygame as pg
from pygame import Rect
from .engine import conf, gfx
from .engine.game import World

from .player import Player, Lasers
from .util import Particles


class Intro (World):
    def init (self):
        n_pads = pg.joystick.get_count()
        if n_pads == 0:
            img = 'nopads'
        elif n_pads == 1:
            img = '1pad'
        else:
            img = '2pads'
        self.graphics.add(
            gfx.Colour('fff', self.graphics.orig_size, layer=1),
            gfx.Graphic('intro-{0}.png'.format(img))
        )

        for i in xrange(n_pads):
            pg.joystick.Joystick(i).init()
        self.evthandler.add((pg.KEYDOWN, pg.JOYBUTTONDOWN,
                             lambda: conf.GAME.switch_world(Level)))


class Level (World):
    def init (self, name='main', colour='000'):
        self.name = name
        self.players = []
        self.mines = [{'real': [], 'dummy': []} for i in xrange(2)]
        self.rects = []
        gm = self.graphics
        gm.fade_from(conf.FADE_IN_TIME, colour)
        self.border = Rect((0, 0), gm.orig_size)

        self.load_evts()
        self.has_real = random.randrange(2)
        for i in xrange(2):
            self.add_player(i, self.has_real == i,
                            conf.LEVELS[name]['spawn'][i])

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

    def add_player (self, n, has_real, pos):
        p = Player(n, has_real, *pos)
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

    def particles (self, name, pos):
        self.graphics.add(Particles(
            self.scheduler, conf.PARTICLES[name], pos, conf.LAYERS['particles']
        ))

    def end (self):
        alive = [p for p in self.players if not p.dead]
        if alive:
            if len(alive) == 1:
                winner = alive[0]
            else:
                winner = [p for p in alive if not p.have_real][0]
            c = conf.PLAYER['colours'][winner.id]
        else:
            c = '000'

        self.scheduler.add_timeout(lambda: self.real_end(c),
                                   conf.START_END_TIME)

    def real_end (self, c):
        self.graphics.fade_to(conf.FADE_OUT_TIME, c)
        self.scheduler.add_timeout(
            lambda: conf.GAME.switch_world(Level, colour=c), conf.END_TIME
        )
