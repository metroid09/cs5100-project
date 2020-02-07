import random
from enum import Enum

import pygame
from pygame.locals import *

import config
from colors import BROWN_LEVEL

SIM_NAME = config.SIM_NAME
FPS = config.FPS
WINDOWWIDTH = config.WINDOWWIDTH
WINDOWHEIGHT = config.WINDOWHEIGHT
CELLSIZE = config.CELLSIZE
RADIUS = config.RADIUS
CELLWIDTH = config.CELLWIDTH
CELLHEIGHT = config.CELLHEIGHT
BGCOLOR = config.BGCOLOR
BATTERY_MAX = config.BATTERY_MAX
DIRT_CHANCE = config.DIRT_CHANCE
RUUMBA_REPEAT_VACUUM = config.RUUMBA_REPEAT_VACUUM
NO_BATTERY = config.NO_BATTERY
STAY_BY_WALL = config.STAY_BY_WALL

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
    IMPASSABLE = 'IMPASSABLE'


CELL_COLORS = {
    CellType.STAIRS: RED,
    CellType.WALL: WHITE,
    CellType.DOG: YELLOW,
    CellType.FURNITURE: DARKGRAY,
    CellType.CHARGER: GREEN,
    CellType.RUUMBA: LIGHTBLUE,
    CellType.FLOOR: BLACK,
    CellType.IMPASSABLE: YELLOW,
}


class Direction(Enum):
    UP = 'UP',
    DOWN = 'DOWN',
    LEFT = 'LEFT',
    RIGHT = 'RIGHT',

    @classmethod
    def opposite_direction(cls, direction):
        if direction == cls.UP:
            return cls.DOWN
        if direction == cls.DOWN:
            return cls.UP
        if direction == cls.LEFT:
            return cls.RIGHT
        if direction == cls.RIGHT:
            return cls.LEFT

    @classmethod
    def other_directions(cls, direction):
        directions = []
        for d in list(cls):
            if d == direction:
                continue
            directions.append(d)
        return directions


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
        pygame.draw.rect(config.DISPLAYSURF, self.color, cellRect)

    def __str__(self):
        return "<Cell {}: (x:{},y:{}) >".format(self.cell_type, self.pos_x, self.pos_y)


class TerrainCell(Cell):
    # A number between 0-5 where 5 is a lot of dirt and 1 is very little
    dirt = 0
    is_terrain = True

    def __init__(self, x, y, cell_type=None, color=None, dirt=0, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color)
        if cell_type == CellType.FLOOR:
            if random.randint(0, 100) > DIRT_CHANCE:
                self.dirt = random.randint(0, 5)
            else:
                self.dirt = 0
            self.color = BROWN_LEVEL[self.dirt]

    @property
    def is_dirty(self):
        if self.cell_type == CellType.FLOOR:
            return self.dirt > 0
        return False

    def vacuum(self):
        if self.is_dirty:
            self.dirt -= 1
            self.color = BROWN_LEVEL[self.dirt]

    def render(self):
        if self.cell_type == CellType.IMPASSABLE:
            X = pygame.font.Font('freesansbold.ttf', 45)
            X = X.render('X', True, WHITE)
            X_rect = X.get_rect()
            X_rect.midtop = ((self.pos_x * CELLSIZE)+(CELLSIZE/2), self.pos_y * CELLSIZE)
            config.DISPLAYSURF.blit(X, X_rect)
            return
        super().render()


# These are moveable cells which ride "over" the background cells
class MoveableCell(Cell):
    is_terrain = False
    id = None
    facing_direction = None
    # Speed is measured in frames / cell (number of cells moved in x frames)
    speed = 4
    frame = 1
    hit_bottom = True

    def __init__(self, x, y, id, facing_direction, cell_type=None, color=None, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color, **kwargs)
        self.id = id
        if type(facing_direction) is Direction:
            self.facing_direction = facing_direction
        else:
            self.facing_direction = random.choice(list(Direction))
        self.next_direction = facing_direction

    def random_move(self):
        if self.frame % self.speed == 0:
            self.frame = 1
            if random.randint(0, 6) == 5:
                self.facing_direction = random.choice(list(Direction))
            self.move()
        if self.hits_edge():
            self.undo_move()
        self.frame += 1

    def move(self):
        if self.facing_direction == Direction.UP:
            self.move_up()
        if self.facing_direction == Direction.DOWN:
            self.move_down()
        if self.facing_direction == Direction.LEFT:
            self.move_left()
        if self.facing_direction == Direction.RIGHT:
            self.move_right()

    def move_up(self):
        self.pos_y = self.pos_y - 1

    def move_down(self):
        self.pos_y = self.pos_y + 1

    def move_left(self):
        self.pos_x = self.pos_x - 1

    def move_right(self):
        self.pos_x = self.pos_x + 1

    def turn_90(self, clockwise=True):
        if self.facing_direction == Direction.UP:
            if clockwise:
                self.facing_direction = Direction.RIGHT
            else:
                self.facing_direction = Direction.LEFT
        elif self.facing_direction == Direction.DOWN:
            if clockwise:
                self.facing_direction = Direction.LEFT
            else:
                self.facing_direction = Direction.RIGHT
        elif self.facing_direction == Direction.LEFT:
            if clockwise:
                self.facing_direction = Direction.UP
            else:
                self.facing_direction = Direction.DOWN
        elif self.facing_direction == Direction.RIGHT:
            if clockwise:
                self.facing_direction = Direction.DOWN
            else:
                self.facing_direction = Direction.UP

    def get_side_directions(self):
        if self.facing_direction in [Direction.UP, Direction.DOWN]:
            return Direction.RIGHT, Direction.LEFT
        elif self.facing_direction in [Direction.RIGHT, Direction.LEFT]:
            return Direction.UP, Direction.DOWN

    def undo_move(self):
        new_direction = random.choice(Direction.other_directions(self.facing_direction))
        self.facing_direction = Direction.opposite_direction(self.facing_direction)
        self.move()
        self.facing_direction = new_direction

    def interact_with(self, cell=None):
        # This will have the cell passed in that we are "interacting with" so we can do things based on it
        if cell is None:
            import ipdb; ipdb.set_trace()
            return
        if cell.cell_type not in [CellType.FLOOR, CellType.CHARGER]:
            self.undo_move()

    def hits_edge(self):
        global CELLWIDTH, CELLHEIGHT
        return self.pos_x == -1 or self.pos_x == CELLWIDTH or self.pos_y == -1 or self.pos_y == CELLHEIGHT

    def hits_object(self, obj):
        return self.pos_x == obj.pos_x and self.pos_y == obj.pos_y

    def update_internal_state(self):
        pass



class Ruumba(MoveableCell):
    battery = BATTERY_MAX
    start_x = 0
    start_y = 0
    charged = True
    next_to_wall = False
    move_queue = []

    def __init__(self, x, y, id, facing_direction, **kwargs):
        if 'cell_type' in kwargs:
            kwargs.pop('cell_type')
        self.cell_type = CellType.RUUMBA
        super().__init__(x, y, id, facing_direction, cell_type=CellType.RUUMBA, **kwargs)
        self.start_x = x
        self.start_y = y

    def interact_with(self, cell=None):
        super().interact_with(cell)
        if cell is None:
            return
        if self.frame % self.speed == 0 and type(cell) is TerrainCell:
            self.set_speed(dirt=cell.dirt)
            if RUUMBA_REPEAT_VACUUM:
                if cell.dirt > 3 and len(self.move_queue) < 1:
                    for i in range(cell.dirt - 1):
                        self.move_queue.append(Direction.opposite_direction(self.facing_direction))
                        self.move_queue.append(self.facing_direction)
            cell.vacuum()

    def set_speed(self, dirt=0):
        if dirt > 0:
            self.speed = 8 # Set speed to n frames/cell
            return 
        self.speed = 4 # Set speed to n frame/cell

    def super_random_move(self):
        if self.frame % self.speed == 0:
            self.frame = 1
            if len(self.move_queue) < 1:
                if self.next_to_wall and STAY_BY_WALL: #  Try to stay next to wall if possible
                    if random.randint(0, 15) == 15:
                        self.facing_direction = random.choice(list(Direction))
                else:
                    if random.randint(0, 6) == 6:
                        self.facing_direction = random.choice(list(Direction))
            else:
                self.facing_direction = self.move_queue.pop()
            self.move()
        if self.hits_edge():
            self.undo_move()
        self.frame += 1

    def random_move(self):
        if self.charged or NO_BATTERY:
            self.super_random_move()
        else:
            if self.start_x != self.pos_x or self.start_y != self.pos_y:
                if random.randint(0,1) > 0:
                    if self.start_x < self.pos_x:
                        self.facing_direction = Direction.LEFT
                    elif self.start_x > self.pos_x:
                        self.facing_direction = Direction.RIGHT
                else:
                    if self.start_y < self.pos_y:
                        self.facing_direction = Direction.UP
                    elif self.start_y > self.pos_y:
                        self.facing_direction = Direction.DOWN
                self.move()
            return

    def update_internal_state(self):
        if not NO_BATTERY:
            if self.battery < (0.05 * BATTERY_MAX):
                self.charged = False
            if self.charged and self.start_x != self.pos_x and self.start_y != self.pos_y and self.battery > 0:
                    self.battery -= 1
            if not self.charged and self.start_x == self.pos_x and self.start_y == self.pos_y:
                if self.battery < BATTERY_MAX:
                    self.battery += 5
                    if self.battery >= BATTERY_MAX:
                        self.charged = True

    # +++++++++++++++++++ BEGIN SENSE FUNCTIONS +++++++++++++++++++
    def sense(self, **kwargs):
        self.interact_with(kwargs["on_cell"])
        facing_cell = self.sense_facing_cell(**kwargs)
        if facing_cell is not None and (facing_cell.cell_type == CellType.FURNITURE or facing_cell.cell_type == CellType.WALL):
            self.turn_90(clockwise=(random.randint(0, 1) > 0))
        self.next_to_wall = False
        side1, side2 = self.get_side_directions()
        try:
            if side1 in [Direction.UP, Direction.DOWN]:
                if self.cell_is_wall('up_cell', kwargs) or self.cell_is_wall('down_cell', kwargs):
                    self.next_to_wall = True
            if side1 in [Direction.LEFT, Direction.RIGHT]:
                if self.cell_is_wall('left_cell', kwargs) or self.cell_is_wall('right_cell', kwargs):
                    self.next_to_wall = True
        except AttributeError:
            import ipdb; ipdb.set_trace()

    def cell_is_wall(self, cell, kwargs):
        if cell in kwargs and kwargs[cell] is not None and kwargs[cell].cell_type == CellType.WALL:
            return True
        return False

    def sense_facing_cell(self, **kwargs):
        if self.facing_direction == Direction.UP:
            return kwargs["up_cell"]
        elif self.facing_direction == Direction.DOWN:
            return kwargs["down_cell"]
        elif self.facing_direction == Direction.RIGHT:
            return kwargs["right_cell"]
        elif self.facing_direction == Direction.UP:
            return kwargs["left_cell"]
    # +++++++++++++++++++ END SENSE FUNCTIONS +++++++++++++++++++++
