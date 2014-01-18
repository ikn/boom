import random

import pygame as pg
from pygame import Rect
from .engine import conf, sched
from .engine.gfx import Graphic, Colour, GraphicsManager
from .engine.game import World
from .engine.util import randsgn

from .player import Player, Lasers
from . import util


def setup_bg (gm, layer, scheduler):
    g = Graphic('background.png').resize(*gm.orig_size)
    w = g.w
    s = pg.Surface((w * 2, g.h))
    s.blit(g.surface, (0, 0))
    s.blit(g.flip(True).surface, (w, 0))
    g = Graphic(s, layer=layer)
    gm.add(g)

    speed = util.rand(conf.BG_SPEED)
    if speed != 0:
        start = -w
        end = 0
        if randsgn() == -1:
            start, end = end, start
        t = float(g.w) / speed
        scheduler.interp(
            sched.interp_repeat(sched.interp_linear(start, (end, t)), t),
            (g, 'x'), round_val=True
        )

    return g


class Intro (World):
    def init (self):
        n_pads = pg.joystick.get_count()
        if n_pads == 0:
            img = 'nopads'
        elif n_pads == 1:
            img = '1pad'
        else:
            img = '2pads'

        gm_r = Rect((0, 0), self.graphics.size)
        frame = gm_r.inflate(*(-2 * w for w in conf.INTRO_FRAME_WIDTH))
        viewport = GraphicsManager(self.scheduler, frame.size)
        setup_bg(viewport, 1, self.scheduler)
        text = Graphic('intro-{0}.png'.format(img))
        viewport.add(text)
        text.align()
        self.graphics.add(
            util.tile_graphic(Graphic('solid.png'), gm_r, 1),
            viewport
        )
        viewport.align()

        for i in xrange(n_pads):
            pg.joystick.Joystick(i).init()
        self.evthandler.add((pg.KEYDOWN, pg.JOYBUTTONDOWN,
                             lambda: conf.GAME.switch_world(Level)))


class Level (World):
    def init (self, colour='000'):
        self.players = []
        self.mines = [{'real': [], 'dummy': []} for i in xrange(2)]
        self.rects = []
        gm = self.graphics
        gm.fade_from(conf.FADE_IN_TIME, colour)
        self.border = Rect((0, 0), gm.orig_size).inflate(0, 1000).move(0, -500)
        lvl = random.choice(conf.LEVELS)

        self.load_evts()
        self.has_real = random.randrange(2)
        for i in xrange(2):
            self.add_player(i, self.has_real == i, lvl['spawn'][i])

        layers = conf.LAYERS
        setup_bg(gm, layers['bg'], self.scheduler)
        g = Graphic('solid.png')
        for r in lvl['rects']:
            r = Rect(r)
            self.rects.append(r)
            gm.add(util.tile_graphic(g, r, layers['rect']))

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
        p = Player(n, has_real, pos)
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
        for p in self.players:
            ppos = p.rect.center
            dist = util.pt_dist(pos, ppos)
            if dist > radius:
                continue
            i = util.line_intersects_rects(pos, ppos, self.rects)
            if i and util.pt_dist(pos, i) <= radius:
                break
            else:
                p.die()

    def particles (self, name, pos):
        self.graphics.add(util.Particles(
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
