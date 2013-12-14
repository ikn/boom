import random

import pygame as pg
from pygame import Rect
from .engine import conf, gfx
from .engine.game import World

from .player import Player


class Level (World):
    def init (self, name='main', num_players=2):
        self.name = name
        self.players = []
        self.mines = [{'real': [], 'dummy': []} for i in xrange(num_players)]
        self.rects = []
        gm = self.graphics
        self.border = Rect((0, 0), gm.orig_size)

        self.evthandler.load('level')
        self.has_real = random.randrange(num_players)
        for i in xrange(num_players):
            self.add_player(i, self.has_real == i)

        layers = conf.LAYERS
        gm.add(gfx.Colour(conf.BG_COLOUR, gm.orig_size, layers['bg']))
        for r in conf.LEVELS[name]['rects']:
            self.rects.append(Rect(r))
            gm.add(gfx.Colour(conf.RECT_COLOUR, r, layers['rect']))

    def add_player (self, n, has_real):
        x, y = (50 * n, 50)
        p = Player(n, has_real, x, y)
        self.players.append(p)
        self.add(p)

        n = str(n)
        eh = self.evthandler
        for action in (
            'aim', 'move', 'jump', 'throw_real', 'throw_dummy', 'detonate'
        ):
            eh[action + n].cb(p.action(action))

    def add_mine (self, m):
        self.mines[m.player]['real' if m.real else 'dummy'].append(m)
        self.add(m)

    def detonate_mines (self, player):
        for group in self.mines[player.id].itervalues():
            for m in group:
                m.explode()
        self.mines[player.id] = {'real': [], 'dummy': []}

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
        self.scheduler.add_timeout(conf.GAME.quit_world, 2)
