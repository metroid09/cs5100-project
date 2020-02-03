import random
from enum import Enum

import pygame
from pygame.locals import *

import config

SIM_NAME = config.SIM_NAME
FPS = config.FPS
WINDOWWIDTH = config.WINDOWWIDTH
WINDOWHEIGHT = config.WINDOWHEIGHT
CELLSIZE = config.CELLSIZE
RADIUS = config.RADIUS
CELLWIDTH = config.CELLWIDTH
CELLHEIGHT = config.CELLHEIGHT
BGCOLOR = config.BGCOLOR
HEAD = config.HEAD
NUM_RUUMBAS = config.NUM_RUUMBAS
DEBUG = config.DEBUG

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
    STAIRS = 'STAIRS'
    WALL = 'WALL'
    DOG = 'DOG'
    FURNITURE = 'FURNITURE'
    FLOOR = 'FLOOR'
    CHARGER = 'CHARGER'
    RUUMBA = 'RUUMBA'


CELL_COLORS = {
    CellType.STAIRS: RED,
    CellType.WALL: WHITE,
    CellType.DOG: BROWN,
    CellType.FURNITURE: DARKGRAY,
    CellType.CHARGER: GREEN,
    CellType.RUUMBA: LIGHTBLUE,
    CellType.FLOOR: BLACK,
}


class Direction(Enum):
    UP = 'UP',
    DOWN = 'DOWN',
    LEFT = 'LEFT',
    RIGHT = 'RIGHT',

    @classmethod
    def opposite_direction(cls, direction):
        if direction == UP:
            return DOWN
        if direction == DOWN:
            return UP
        if direction == LEFT:
            return RIGHT
        if direction == RIGHT:
            return LEFT


class Cell(object):
    pos_x = 0
    pos_y = 0
    cell_type = None
    color = None
    is_terrain = None
    
    def __init__(self, x, y, cell_type=None, color=None):
        self.color = color
        if type(cell_type) is CellType:
            self.cell_type = cell_type
            self.color = CELL_COLORS[cell_type]
        self.pos_x = x
        self.pos_y = y

    @property
    def is_obstacle(self):
        return self.cell_type in [CellType.STAIRS, CellType.FURNITURE, CellType.WALL, CellType.DOG]

    def render(self):
        x = self.pos_x * CELLSIZE
        y = self.pos_y * CELLSIZE
        cellRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        try:
            pygame.draw.rect(config.DISPLAYSURF, self.color, cellRect)
        except TypeError:
            import ipdb; ipdb.set_trace()

    def __str__(self):
        return "<Cell {}: (x:{},y:{}) >".format(self.cell_type, self.pos_x, self.pos_y)


class TerrainCell(Cell):
    # A number between 0-5 where 5 is a lot of dirt and 1 is very little
    dirt = 0
    is_terrain = True

    def __init__(self, x, y, cell_type=None, color=None, dirt=0, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color)
        if cell_type == CellType.FLOOR:
            self.dirt = random.randint(0, 5)

    @property
    def is_dirty(self):
        if self.cell_type == CellType.FLOOR:
            return self.dirt > 0
        return False


# These are moveable cells which ride "over" the background cells
class MoveableCell(Cell):
    is_terrain = False
    id = None
    facing_direction = None
    # Speed is measured in frames / cell (number of cells moved in x frames)
    speed = 0
    frame = 1

    def __init__(self, x, y, id, facing_direction, cell_type=None, color=None, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color, **kwargs)
        self.id = id
        if type(facing_direction) is Direction:
            self.facing_direction = facing_direction
        else:
            self.facing_direction = random.choice(list(Direction))
        self.next_direction = facing_direction
        self.speed = 1 # Measured in frames/cell

    def random_move(self):
        if self.frame % self.speed == 0:
            self.frame = 1
            if random.randint(0, 6) == 5:
                self.facing_direction = random.choice(list(Direction))
            if self.facing_direction == Direction.UP:
                self.move_up()
            if self.facing_direction == Direction.DOWN:
                self.move_down()
            if self.facing_direction == Direction.LEFT:
                self.move_left()
            if self.facing_direction == Direction.RIGHT:
                self.move_right()
        self.frame += 1

    def move_up(self):
        self.pos_x = self.pos_x + 1

    def move_down(self):
        self.pos_x = self.pos_x - 1

    def move_left(self):
        self.pos_y = self.pos_y + 1

    def move_right(self):
        self.pos_y = self.pos_y - 1

    def interact_with(self, cell=None):
        # This will have the cell passed in that we are "interacting with" so we can do things based on it
        pass

    def hits_edge(self):
        global CELLWIDTH, CELLHEIGHT
        self.facing_direction = Direction.opposite_direction(self.facing_direction)
        return self.pos_x == -1 or self.pos_x == CELLWIDTH or self.pos_y == -1 or self.pos_y == CELLHEIGHT

    def hits_object(self, obj):
        return self.pos_x == obj.pos_x and self.pos_y == obj.pos_y



class Ruumba(MoveableCell):

    def __init__(self, x, y, id, facing_direction, **kwargs):
        if 'cell_type' in kwargs:
            kwargs.pop('cell_type')
        self.cell_type = CellType.RUUMBA
        super().__init__(x, y, id, facing_direction, cell_type=CellType.RUUMBA, **kwargs)

    def interact_with(self, cell=None):
        super().interact_with(cell)
        self.set_speed(dirt=cell.dirt)

    def set_speed(self, dirt=0):
        if dirt > 0:
            self.speed = 4 # Set speed to 4 frames/cell
            return 
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
