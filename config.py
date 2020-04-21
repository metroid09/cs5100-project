import math

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
MESSAGE_LENGTH = 16 # Known as l in the paper


BGCOLOR = BLACK