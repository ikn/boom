import pygame as pg
from pygame import Rect
from .engine import conf, gfx
from .engine.game import World

from .player import Player


class Level (World):
    def init (self, name='main', num_players=2):
        self.name = name
        self.players = []
        self.mines = {'real': [], 'dummy': []}
        self.rects = []
        gm = self.graphics
        self.border = Rect((0, 0), gm.orig_size)

        self.evthandler.load('level')
        for i in xrange(num_players):
            self.add_player(i)

        layers = conf.LAYERS
        gm.add(gfx.Colour(conf.BG_COLOUR, gm.orig_size, layers['bg']))
        for r in conf.LEVELS[name]['rects']:
            self.rects.append(Rect(r))
            gm.add(gfx.Colour(conf.RECT_COLOUR, r, layers['rect']))

    def add_player (self, n):
        x, y = (50 * n, 50)
        p = Player(n, x, y)
        self.players.append(p)
        self.add(p)

        n = str(n)
        eh = self.evthandler
        for action in ('move', 'jump', 'throw_real', 'throw_dummy'):
            eh[action + n].cb(getattr(p, action))

    def add_mine (self, real, m):
        self.mines['real' if real else 'dummy'].append(m)
        self.add(m)
