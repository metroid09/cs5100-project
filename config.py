import math

BLACK     = (  0,   0,   0)

FPSCLOCK=None
DISPLAYSURF=None
BASICFONT=None

SIM_NAME = 'Predator Prey'
SIM_SECONDS = 50
DIRT_CHANCE = 50
NUM_MOVERS = 4
FPS = 200
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
CELLSIZE = 40
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

BGCOLOR = BLACK

BATTERY_MAX = 1000

RUUMBA_REPEAT_VACUUM = False
NO_BATTERY = False
STAY_BY_WALL = True