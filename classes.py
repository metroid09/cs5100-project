import random

from enum import Enum, auto


#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
BROWN     = (160,  82,  45)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 255,   0)
BLUE      = ( 47,  41,  99)
LIGHTBLUE = ( 72,  63, 155)
BGCOLOR = BLACK


class CellType(Enum):
    STAIRS = auto()
    WALL = auto()
    DOG = auto()
    FURNITURE = auto()


CELL_COLORS = {
    CellType.STAIRS: BLACK,
    CellType.WALL: WHITE,
    CellType.DOG: BROWN,
    CellType.FURNITURE: DARKGRAY,
}


class Ruumba(object):
    id = 0
    pos_x = 0
    pos_y = 0

    def __init__(self, x, y, id):
        self.pos_x = x
        self.pox_y = y
        self.id = id

    def move_up(self):
        pos_x = pos_x + 1

    def move_down(self):
        pos_x = pos_x - 1

    def move_left(self):
        pos_x = pos_y + 1

    def move_right(self):
        pos_x = pos_y - 1

    def hits_bullet(self, bullets=[]):
        for bullet in bullets:
            if self.pos_x == bullet[0] and self.pos_x == bullet[1]:
                return True, i
        return False, None

    def hits_wall(self):
        if self.pos_x == -1 or self.pos_x == CELLWIDTH or self.pos_y == -1 or self.pos_y == CELLHEIGHT:
            return True
        return False

    def hits_ruumba(self, ruumbas):
        ruumbas = ruumbas[:id] + ruumbas[id+1:]
        for ruumba in ruumbas:
            if self.pos_x == ruumba.pos_x and self.pos_y == ruumba.pos_y:
                return True
        return False

    # Might need this for AI?
    # def next_move_safe(ruumbaCoords, depth=0, max_depth=30):
    #     is_hit = True
    #     loops = 0
    #     choices = [UP, DOWN, LEFT, RIGHT]
    #     while is_hit:
    #         direction = random.choice(choices)
    #         choices.remove(direction)
    #         newHead = get_new_head(direction, ruumbaCoords)
    #         is_hit = hits_self(newHead, ruumbaCoords) or hits_wall(newHead)
    #         if not is_hit and depth < max_depth + 3:
    #             newCoords = copy.deepcopy(ruumbaCoords)
    #             newCoords.insert(0, newHead)
    #             del newCoords[-1] # remove ruumba's tail segment
    #             safe, _ = next_move_safe(newCoords, depth=depth+1, max_depth=max_depth)
    #             # if not safe and depth == 0 and len(choices) == 0:
    #             #     import ipdb; ipdb.set_trace()
    #             is_hit = not safe
    #         if len(choices) == 0:
    #             return False, newHead
    #     return True, newHead


class Cell(object):
    cell_type = None
    color = None
    # A number between 0-5 where 5 is a lot of dirt and 1 is very little
    dirt = 0
    is_obstacle = None
    
    def __init__(self, cell_type=None, color=None, dirt=0):
        self.color = color
        self.dirt = dirt
        if type(cell_type) is CellType:
            self.cell_type = cell_type
            self.color = CELL_COLORS[cell_type]

    @property
    def is_dirty(self):
        return self.dirt > 0
