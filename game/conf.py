import os

from .engine import conf
from .engine.util import dd


class Conf (object):
    IDENT = 'boom'
    WINDOW_TITLE = 'boom'
    WINDOW_ICON = os.path.join(conf.IMG_DIR, 'icon.png')
    RES_W = (960, 540)

    # remove fullscreen keys since they disable KEYDOWN on enter without alt
    GAME_EVENTS = '''
button _game_quit DOWN
    [ALT] kbd F4

button _game_minimise DOWN
    kbd F10

button _game_fullscreen DOWN
'''

    SOUND_VOLUME = dd(1)
    SOUND_VOLUMES = dd(1, {
        'collide': 1,
        'jump': .6,
        'walljump': .6,
        'walk': .5,
        'throw': .6,
        'place': .4,
        'explode': .8,
        'dud': .5,
        'laser': .4,
        'crumble': .4
    })
    MAX_SOUNDS = dd(5)
    SOUND_ALIASES = {
        'jump': 'clang',
        'walljump': 'clang',
        'collide': 'clang',
        'walk': 'miniclang'
    }
    WALK_SOUND_DELAY = .2
    WALK_SOUND_DELAY_VARIANCE = .02

    PAD_DEADZONE = .2

    LEVELS = {
        'main': {
            'spawn': [
                (20, 340),
                (800, 360)
            ],
            'rects': [
                (0, 480, 960, 60), # ground
                (0, 380, 80, 100), # left bottom
                (220, 380, 150, 40), # centre bottom
                (370, 330, 200, 150),
                (570, 450, 170, 30), # right bottom
                (740, 400, 130, 80),
                (130, 230, 350, 40), # left top
                (130, 80, 40, 150),
                (440, 190, 40, 40),
                (620, 130, 340, 100), # right top
            ]
        }
    }

    GRAVITY = 1
    FRICTION = (.8, .8)
    AIR_RESISTANCE = (.95, .95)
    DEAD_MINE_DAMPING = .9
    THROW_DIRN_PRIO = [1, 0, 1, 2]
    MINE = {
        'offset': (-13, -4), # of graphics from hitbox
        'size': (8, 8),
        'explosion_radius': 150,
        'animation_frame_time': .4,
        'rotate_speed': 4, # rad/s
        'rotate_speed_variance': 2
    }
    PLAYER = {
        'offset': (0, 0), # of graphics from hitbox
        'size': (40, 40),
        'move_ground': 2.5,
        'move_air': .3,
        'jump': {
            'time': .11,
            'initial': 10,
            'continue': 2
        },
        'walljump': {
            'vert': .6,
            'horiz': .6
        },
        'throw_speed': 50,
        'max_throw_speed': .5,
        'num_lasers': 3,
        'legs': {
            'num': 4,
            'x_offset_base': -8,
            'x_offset_multiple': 10,
            'y_offset': 8,
            'frame_time': .1
        },
        'colours': ['5c4a2c', '2a5853']
    }
    LASER = {
        'time': .3,
        'width': 4,
        'colour': (180, 20, 20, 255)
    }
    LAYERS = {
        'bg': 1,
        'rect': 0,
        'player1': -1,
        'legs1': -2,
        'player0': -3,
        'legs0': -4,
        'mine': -5,
        'deadmine': -6,
        'laser': -7,
        'particles': -8
    }
    # offset: of graphics from mine's centre
    DEAD_MINE_GRAPHICS = {
        'dud': {
            'offset': (-22, -59),
            'ncols': 5,
            'frame_time': .1
        }
    }

    PARTICLES = {
        # colour
        # amount: total area
        # size <rand>
        # speed <rand>: per frame
        # life <rand>: frames
        'explode': {
            'size': {'mean': 2, 'dev': 1},
            'speed': 3,
            'life': {'mean': 60, 'dev': 20},
            'colours': [
                {'colour': 'c22', 'amount': 1700}, # red
                {'colour': 'd51', 'amount': 1700}, # orange
                {'colour': 'fb2', 'amount': 1000}, # yellow
                {'colour': 'a68e69', 'amount': 200 }, # mine colour
                {'colour': '000', 'amount': 200}
            ]
        },

        'crumble': {
            'size': {'mean': 1.5, 'dev': .5},
            'speed': .5,
            'life': {'mean': 30, 'dev': 10},
            'colours': [
                {'colour': '620d0d', 'amount': 20}, # main
                {'colour': '816e51', 'amount': 5}, # shadow
                {'colour': 'ccae81', 'amount': 5}, # highlight
                {'colour': 'a68e69', 'amount': 10}, # red
                {'colour': '1c1812', 'amount': 80}, # charred
                {'colour': '1c1812', 'amount': 30} # charred
            ]
        },

        'die0': {
            'size': {'mean': 3, 'dev': 2},
            'speed': 2,
            'life': {'mean': 40, 'dev': 15},
            'colours': [
                {'colour': '312a19', 'amount': 500}, # dark
                {'colour': '5c4a2c', 'amount': 500}, # ...
                {'colour': '695a31', 'amount': 500}, # ...
                {'colour': '9a8758', 'amount': 500}, # light
                {'colour': '000', 'amount': 500}
            ]
        },

        'die1': {
            'size': {'mean': 3, 'dev': 2},
            'speed': 2,
            'life': {'mean': 40, 'dev': 15},
            'colours': [
                {'colour': '182e2e', 'amount': 500}, # dark
                {'colour': '2a5853', 'amount': 500}, # ...
                {'colour': '2e6463', 'amount': 500}, # ...
                {'colour': '539390', 'amount': 500}, # light
                {'colour': '000', 'amount': 500}
            ]
        }
    }
    PARTICLE_DAMPING = .95

    START_END_TIME = .5
    FADE_IN_TIME = 1
    FADE_OUT_TIME = 1
    END_TIME = 2
