class Conf (object):
    IDENT = 'game'
    WINDOW_TITLE = ''
    #WINDOW_ICON = 'icon.png'
    RES_W = (960, 540)

    LEVELS = {
        'main': {
            'rects': [
                (0, 450, 960, 90)
            ]
        }
    }

    # physics
    GRAVITY = 1
    FRICTION = (.8, .8)
    AIR_RESISTANCE = (.95, .95)
    PLAYER = {
        'offset': (0, 0), # of graphics from hitbox
        'size': (20, 50),
        'move_ground': 2.5,
        'move_air': .3,
        'jump_time': .11,
        'jump_initial': 9,
        'jump_continue': 1.9
    }

    # graphics
    BG_COLOUR = 'aaa'
    RECT_COLOUR = '333'
    PLAYER_COLOURS = ['d33', '151']
    LAYERS = {
        'bg': 1,
        'rect': 0,
        'player': -1
    }
