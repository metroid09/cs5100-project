import math
from itertools import product

BLACK     = (  0,   0,   0)

FPSCLOCK=None
DISPLAYSURF=None
BASICFONT=None

SIM_NAME = 'Predator Prey'
SIM_TURNS=5000
FPS = 1000
WINDOWWIDTH = 900
WINDOWHEIGHT = 900
CELLSIZE = 30
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
MESSAGE_LENGTH = 1 # Known as l in the paper
N_RANGE = 4
BEARINGS = {
    'N':    "000",
    'NE':   "001",
    'E':    "010",
    'SE':   "011",
    'S':    "100",
    'SW':   "101",
    'W':    "110",
    'NW':   "111",
}
N_BEARING = len(BEARINGS)

DIRECTION_STRS = [
    "00",
    "01",
    "10",
    "11",
]

MSG_STRS = [
    "0",
    "1",
]

DIST_STRS = [
    "00",
    "01",
    "10",
    "11",
]

BEARING_STRS = [
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
]

MESSAGE_BOARD_STR = [
    "0000",
    "0001",
    "0010",
    "0011",
    "0100",
    "0101",
    "0110",
    "0111",
    "1000",
    "1001",
    "1010",
    "1011",
    "1100",
    "1101",
    "1110",
    "1111",
]

ALL_POSSIBLE_STRINGS = set()

for a, b, c, d, e in product(DIRECTION_STRS, MSG_STRS, DIST_STRS, BEARING_STRS, MESSAGE_BOARD_STR):
    ALL_POSSIBLE_STRINGS.add(a+b+c+d+e)

print(len(ALL_POSSIBLE_STRINGS))
print((2 + MESSAGE_LENGTH) * N_RANGE * N_BEARING * 2**(MESSAGE_LENGTH * 4))


BGCOLOR = BLACK