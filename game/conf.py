import os

from .engine import conf
from .engine.util import dd


class Conf (object):
    IDENT = 'game'
    WINDOW_TITLE = ''
    WINDOW_ICON = os.path.join(conf.IMG_DIR, 'icon.png')
    RES_W = (960, 540)

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
            'rects': [
                (0, 450, 960, 90),
                (800, 0, 50, 400)
            ]
        }
    }

    # physics/gameplay
    GRAVITY = 1
    FRICTION = (.8, .8)
    AIR_RESISTANCE = (.95, .95)
    THROW_DIRN_PRIO = [1, 0, 1, 2]
    MINE = {
        'offset': (-13, -4), # of graphics from hitbox
        'size': (8, 8),
        'explosion_radius': 125,
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
        'num_lasers': 3
    }
    LASER = {
        'time': .3,
        'width': 3,
        'colour': (255, 0, 0, 255)
    }

    # graphics
    BG_COLOUR = 'fff'
    RECT_COLOUR = '333'
    PLAYER_COLOURS = ['d33', '151']
    MINE_COLOUR = '000'
    LAYERS = {
        'bg': 1,
        'rect': 0,
        'player': -1,
        'mine': -2,
        'laser': -3
    }
