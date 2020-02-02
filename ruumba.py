# (Originally) Ruumbay (a Nibbles clone)
# Now a roomba simulator!
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
# Modified by Chris Merkley for CS 5110

import copy
import math
import random
import sys

import pygame
from pygame.locals import *

from .classes import CELL_COLORS, Cell, CellType, Ruumba
from .render import (drawBullets, drawGrid, drawPressKeyMsg, drawRuumba,
                     drawScore, showGameOverScreen, showStartScreen)

SIM_NAME = 'ruumba'
FPS = 5
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
CELLSIZE = 40
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 255,   0)
BLUE      = ( 47,  41,  99)
LIGHTBLUE = ( 72,  63, 155)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the ruumba's head

NUM_RUUMBAS = 2

DEBUG = True

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption(SIM_NAME)

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point.
    ruumbas = []
    walls = []
    direction = []
    for n in range(NUM_RUUMBAS):
        ruumba = Ruumba()
        startx, starty = get_rand_coords()
        ruumbas.append(ruumbaCoords)
        direction.append(RIGHT)

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            direction = get_direction(event, direction)

        for ruumba_iter in range(len(ruumbas)):
            ruumbaCoords = ruumbas[ruumba_iter]
            if hits_snek(ruumbaCoords[HEAD], ruumba_iter, ruumbas):
                delete_ruumbas.append(ruumba_iter)
                continue

            # check if ruumba has eaten an apple
            eaten = None
            for i, apple in enumerate(apples):
                if ruumbaCoords[HEAD]['x'] == apple['x'] and ruumbaCoords[HEAD]['y'] == apple['y']:
                    eaten = i

            # move the ruumba by adding a segment in the direction it is moving
            is_safe = True
            if ruumba_iter == 0 or not DEBUG:
                newHead = get_new_head(direction[ruumba_iter], ruumbaCoords)
            if DEBUG:
                is_safe, newHead = next_move_safe(ruumbaCoords)

            if is_safe:
                ruumbaCoords.insert(0, newHead)   #have already removed the last segment
            else:
                ruumbaCoords.insert(-1, del_coords)

        # Render
        DISPLAYSURF.fill(BGCOLOR)
        for ruumbaCoords in ruumbas:
            drawRuumba(ruumbaCoords)
        draw_walls(walls)
        for i, ruumbaCoords in enumerate(ruumbas):
            drawScore(len(ruumbaCoords) - 3, i)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def get_direction(event, direction):
    if event.type == QUIT:
        terminate()
    elif event.type == KEYDOWN:
        if event.key == K_LEFT and direction[0] != RIGHT:
            direction[0] = LEFT
        elif event.key == K_RIGHT and direction[0] != LEFT:
            direction[0] = RIGHT
        elif event.key == K_UP and direction[0] != DOWN:
            direction[0] = UP
        elif event.key == K_DOWN and direction[0] != UP:
            direction[0] = DOWN
        if event.key == K_a and direction[1] != RIGHT:
            direction[1] = LEFT
        elif event.key == K_d and direction[1] != LEFT:
            direction[1] = RIGHT
        elif event.key == K_w and direction[1] != DOWN:
            direction[1] = UP
        elif event.key == K_s and direction[0] != UP:
            direction[1] = DOWN
        if event.key == K_KP4 and direction[0] != RIGHT:
            for i in range(len(direction)):
                direction[i] = LEFT
        elif event.key == K_KP6 and direction[0] != LEFT:
            for i in range(len(direction)):
                direction[i] = RIGHT
        elif event.key == K_KP8 and direction[0] != DOWN:
            for i in range(len(direction)):
                direction[i] = UP
        elif event.key == K_KP2 and direction[0] != UP:
            for i in range(len(direction)):
                direction[i] = DOWN
        if event.key == K_ESCAPE:
            terminate()
    return direction


def get_rand_coords():
    return random.randint(5, CELLWIDTH - 6), random.randint(5, CELLHEIGHT - 6)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


if __name__ == '__main__':
    main()
