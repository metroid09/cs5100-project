import math
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
MESSAGE_LENGTH = config.MESSAGE_LENGTH
N_RANGE = config.N_RANGE
BEARINGS = config.BEARINGS
N_BEARING = config.N_BEARING
CHROMOSOME_LEN = config.CHROMOSOME_LEN
INPUT_MAP = config.INPUT_MAP

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
    PREY = 'PREY'
    FURNITURE = 'FURNITURE'
    FLOOR = 'FLOOR'
    CHARGER = 'CHARGER'
    PREDATOR = 'PREDATOR'
    IMPASSABLE = 'IMPASSABLE'


CELL_COLORS = {
    CellType.PREDATOR: RED,
    CellType.FLOOR: BLACK,
    CellType.PREY: DARKGREEN,
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


def degree_to_bearing(x):
    if x >= 337.5 and x < 22.5:
        return "N"
    elif x >= 22.5 and x < 67.5:
        return "NE"
    elif x >= 67.5 and x < 112.5:
        return "E"
    elif x >= 112.5 and x < 157.5:
        return "SE"
    elif x >= 157.5 and x < 202.5:
        return "S"
    elif x >= 202.5 and x < 247.5:
        return "SW"
    elif x >= 247.5 and x < 292.5:
        return "W"
    else:
        return "NW"


def manhattan_to_string(dist):
    if dist < 1:
        return "00"
    elif dist < 2:
        return "01"
    elif dist < 3:
        return "10"
    else:
        return "11"


def direction_to_string(dir: Direction):
    if dir == Direction.UP:
        return "00"
    elif dir == Direction.LEFT:
        return "01"
    elif dir == Direction.DOWN:
        return "10"
    else:
        return "11"


message_board = ["0" for i in range(4)]
last_message_board = ["0" for i in range(4)]

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

    def render(self):
        x = self.pos_x * CELLSIZE
        y = self.pos_y * CELLSIZE
        cellRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(config.DISPLAYSURF, self.color, cellRect)

    def __str__(self):
        return "<Cell {}: (x:{},y:{}) >".format(self.cell_type, self.pos_x, self.pos_y)


class TerrainCell(Cell):
    is_terrain = True

    def __init__(self, x, y, cell_type=None, color=None, dirt=0, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color)


# These are moveable cells which ride "over" the background cells
class MoveableCell(Cell):
    is_terrain = False
    id = None
    facing_direction = None
    # Speed is measured in frames / cell (number of cells moved in x frames)
    speed = 1
    frame = 1
    last_x = 0
    last_y = 0
    move_back = False

    def __init__(self, x, y, id, facing_direction, cell_type=None, color=None, **kwargs):
        super().__init__(x, y, cell_type=cell_type, color=color, **kwargs)
        self.id = id
        self.last_x = x
        self.last_y = y
        if type(facing_direction) is Direction:
            self.facing_direction = facing_direction
        else:
            self.facing_direction = random.choice(list(Direction))
        self.next_direction = facing_direction

    def random_move(self):
        self.facing_direction = random.choice(list(Direction))
        self.move()

    def needs_move_back(self):
        self.move_back = True

    def try_revert_move(self):
        if self.move_back:
            self.pos_x = self.last_x
            self.pos_y = self.last_y
            self.move_back = False

    def move(self):
        self.last_x = self.pos_x
        self.last_y = self.pos_y
        if self.facing_direction == Direction.UP:
            self.move_up()
        if self.facing_direction == Direction.DOWN:
            self.move_down()
        if self.facing_direction == Direction.LEFT:
            self.move_left()
        if self.facing_direction == Direction.RIGHT:
            self.move_right()

    def move_up(self):
        self.pos_y = (self.pos_y - 1) % CELLHEIGHT

    def move_down(self):
        self.pos_y = (self.pos_y + 1) % CELLHEIGHT

    def move_left(self):
        self.pos_x = (self.pos_x - 1) % CELLWIDTH

    def move_right(self):
        self.pos_x = (self.pos_x + 1) % CELLWIDTH

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

    def surrounded(self, predators):
        num_sides_surrounded = 0
        for predator in predators:
            if predator.pos_x == self.pos_x + 1 and predator.pos_y == self.pos_y:
                num_sides_surrounded += 1
            if predator.pos_x == self.pos_x - 1 and predator.pos_y == self.pos_y:
                num_sides_surrounded += 1
            if predator.pos_x == self.pos_x and predator.pos_y == self.pos_y + 1:
                num_sides_surrounded += 1
            if predator.pos_x == self.pos_x and predator.pos_y == self.pos_y - 1:
                num_sides_surrounded += 1
        return num_sides_surrounded == 4

class Predator(MoveableCell):
    start_x = 0
    start_y = 0
    move_queue = []
    manhattan_str = ''
    bearing_str = ''
    last_msg = '0'

    """
    The length c of the chromosome string is a function of the
    number of possible states N observable by the predator based
    on its sensory information, and the number of actions b.

    The paper isn't very helpful, think of it this way instead. It's a direct map from input -> output,
    where any input state + moves that can be made are mapped to a random output. That way we can use the
    genetic algorithm on the output and evolve better outputs.

    For instance, if we have 4 inputs and our message length is 1
    input -> message sent
    0000 -> 1 NORTH
    0001 -> 1 WEST
    0010 -> 0 WEST
    0011 -> 1 SOUTH
    0100 -> 0 NORTH
    0101 -> 1 EAST
    0110 -> 1 NORT
    0111 -> 1 WEST
    1000 -> 0 EAST
    1001 -> 1 EAST
    1010 -> 1 SOUTH
    1011 -> 1 WEST
    1100 -> 0 NORTH
    1101 -> 1 SOUTH
    1110 -> 0 WEST
    1111 -> 1 EAST

    then we do that with 10 random predators, the best predators are used with crossover to breed the next set of predators with the genetic algorithm and 2 crossover breeding
    """
    chromosome = [0 for x in range(CHROMOSOME_LEN)]
    dir_chromosome = []

    def __init__(self, x, y, id, facing_direction, chromosome="", **kwargs):
        if not kwargs.get('chromosome'):
            self.chromosome = [random.choice(["0", "1"]) for x in range(CHROMOSOME_LEN)]
        else:
            self.chromosome = [i for i in kwargs.get('chromosome')]
        random.seed(CHROMOSOME_LEN) # Make random deterministic
        self.dir_chromosome = [random.choice(list(Direction)) for i in range(CHROMOSOME_LEN)] # List of directions is always the same, only the messages change
        random.seed(None, version=2)
        if kwargs.get("cell_type"):
            kwargs.pop("cell_type")
        super().__init__(x, y, id, facing_direction, cell_type=CellType.PREDATOR, **kwargs)
        self.start_x = x
        self.start_y = y

    def random_move(self):
        # self.facing_direction = random.choice(list(Direction))
        self.move()

    def update_internal_state(self):
        global message_board
        # DIRECTION_STRS, MSG_STRS, DIST_STRS, BEARING_STRS, MESSAGE_BOARD_STR
        state_str = (
            direction_to_string(self.facing_direction)
            + self.last_msg
            + self.manhattan_str
            + self.bearing_str
            + "".join(last_message_board)
        )
        msg_i = INPUT_MAP[state_str]
        msg = self.chromosome[msg_i]
        self.facing_direction = self.dir_chromosome[msg_i]
        self.last_msg = msg
        message_board[self.id] = msg

    def get_chromosome_str(self):
        return "".join(self.chromosome)

    def get_distance(self, mover):
        return abs(self.pos_x - mover.pos_x) + abs(self.pos_y - mover.pos_y)

    def sense(self, mover: MoveableCell):
        manhattan_dist = abs(self.pos_x - mover.pos_x) + abs(self.pos_y - mover.pos_y)
        self.manhattan_str = manhattan_to_string(manhattan_dist)
        y = mover.pos_y - self.pos_y
        x = mover.pos_x - self.pos_x
        b = math.degrees(math.atan2(y, x))
        if b < 0:
            b += 360
        bearing = degree_to_bearing(b)
        self.bearing_str = BEARINGS[bearing]
        self.update_internal_state()
