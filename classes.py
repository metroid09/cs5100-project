import random
from enum import Enum, auto

import pygame
from pygame.locals import *

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


CELL_COLORS = {
    CellType.STAIRS: BLACK,
    CellType.WALL: WHITE,
    CellType.DOG: BROWN,
    CellType.FURNITURE: DARKGRAY,
    CellType.CHARGER: GREEN,
}


class CellType(Enum):
    STAIRS = auto()
    WALL = auto()
    DOG = auto()
    FURNITURE = auto()
    FLOOR = auto()
    CHARGER = auto()


class Cell(object):
    cell_type = None
    color = None
    is_terrain = None
    
    def __init__(self, cell_type=None, color=None):
        self.color = color
        if type(cell_type) is CellType:
            self.cell_type = cell_type
            self.color = CELL_COLORS[cell_type]

    @property
    def is_obstacle(self):
        return self.cell_type in [CellType.STAIRS, CellType.FURNITURE, CellType.WALL, CellType.DOG]

    def render(self):
        global CELLSIZE
        x = self.pos_x * CELLSIZE
        y = self.pos_y * CELLSIZE
        cellRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.color, cellRect)


class TerrainCell(Cell):
    # A number between 0-5 where 5 is a lot of dirt and 1 is very little
    dirt = 0
    is_terrain = True

    def __init__(self, cell_type=None, color=None, dirt=0):
        super().__init__(cell_type=cell_type, color=color)
        if cell_type == CellType.FLOOR:
            self.dirt = random.randint(0, 5)

    @property
    def is_dirty(self):
        if not self.is_obstacle:
            return self.dirt > 0
        return False


# These are moveable cells which ride "over" the background cells
class MoveableCell(Cell):
    is_terrain = False
    id = None
    pos_x = 0
    pos_y = 0
    # Speed is measured in frames / cell (number of cells moved in x frames)
    speed = 0

    def __init__(self, x, y, id, **kwargs):
        super().__init__(**kwargs)
        self.pos_x = x
        self.pox_y = y
        self.id = id
        self.speed = 1 # Measured in frames/cell

    def move_up(self):
        self.pos_x = self.pos_x + 1

    def move_down(self):
        self.pos_x = self.pos_x - 1

    def move_left(self):
        self.pos_y = self.pos_y + 1

    def move_right(self):
        self.pos_y = self.pos_y - 1

    def interact_with(self, cell=None):
        # This will be passed in the cell that we are "interacting with" so we can do things with it

    def hits_edge(self):
        global CELLWIDTH, CELLHEIGHT
        return self.pos_x == -1 or self.pos_x == CELLWIDTH or self.pos_y == -1 or self.pos_y == CELLHEIGHT

    def hits_object(self, obj):
        return self.pos_x == obj.pos_x and self.pos_y == obj.pos_y:


class Ruumba(MoveableCell):

    def set_speed(self, dirt=0):
        if dirt > 0:
            self.speed = 4 # Set speed to 4 frames/cell
        self.speed = 1 # Set speed to 1 frame/cell

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
