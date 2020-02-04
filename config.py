import math

BLACK     = (  0,   0,   0)

FPSCLOCK=None
DISPLAYSURF=None
BASICFONT=None

SIM_NAME = 'ruumba'
FPS = 10
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
CELLSIZE = 40
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

BGCOLOR = BLACK

HEAD = 0 # syntactic sugar: index of the ruumba's head

NUM_RUUMBAS = 2

DEBUG = True