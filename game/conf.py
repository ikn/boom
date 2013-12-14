class Conf (object):
    IDENT = 'game'
    WINDOW_TITLE = ''
    #WINDOW_ICON = 'icon.png'
    RES_W = (960, 540)

    PAD_DEADZONE = .2

    LEVELS = {
        'main': {
            'rects': [
                (0, 450, 960, 90)
            ]
        }
    }

    # physics/gameplay
    GRAVITY = 1
    FRICTION = (.8, .8)
    AIR_RESISTANCE = (.95, .95)
    THROW_DIRN_PRIO = [1, 0, 1, 2]
    MINE = {
        'offset': (0, 0),
        'size': (10, 10),
        'explosion_radius': 125
    }
    PLAYER = {
        'offset': (0, 0), # of graphics from hitbox
        'size': (20, 50),
        'move_ground': 2.5,
        'move_air': .3,
        'jump_time': .11,
        'jump_initial': 9,
        'jump_continue': 1.9,
        'throw_speed': 50,
        'max_throw_speed': .5,
        'num_lasers': 3
    }
    LASER = {
        'time': .2,
        'width': 3,
        'colour': (255, 0, 0, 255)
    }

    # graphics
    BG_COLOUR = 'aaa'
    RECT_COLOUR = '333'
    PLAYER_COLOURS = ['d33', '151']
    MINE_COLOUR = '000'
    LAYERS = {
        'bg': 1,
        'rect': 0,
        'laser': -1,
        'player': -2,
        'mine': -3
    }
