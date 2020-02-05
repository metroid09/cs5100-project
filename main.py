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
import config
from classes import CELL_COLORS, Cell, CellType, Direction, Ruumba, TerrainCell
from pygame.locals import *
# from render import (drawGrid, drawPressKeyMsg, drawScore, showGameOverScreen,
#                     showStartScreen)
from colors import *
from utils import dump_room, load_room

DISPLAYSURF = config.DISPLAYSURF

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

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    config.FPSCLOCK = FPSCLOCK
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    config.DISPLAYSURF = DISPLAYSURF
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    config.BASICFONT = BASICFONT
    pygame.display.set_caption(SIM_NAME)

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():

    terrain = []
    for i in range(CELLWIDTH):
        add = []
        for j in range(CELLHEIGHT):
            if j == 0 or j == CELLHEIGHT-1 or i == 0 or i == CELLWIDTH-1:
                if random.randint(0, 1000) > 970:
                    add.append(TerrainCell(i, j, CellType.CHARGER))
                    try:
                        ruumbas[0].pos_x = i
                        ruumbas[0].pos_y = j
                    except UnboundLocalError:
                        continue
            if random.randint(0, 1000) > 970:
                add.append(TerrainCell(i, j, random.choice([CellType.FLOOR, CellType.FURNITURE, CellType.STAIRS])))
                continue
            add.append(TerrainCell(i, j, CellType.FLOOR))
        terrain.append(add)

    terrain = load_room()

    # Set a random start point.
    ruumbas = []
    for i in range(len(terrain)):
        for j in range(len(terrain[i])):
            if terrain[i][j].cell_type == CellType.CHARGER:
                ruumba = Ruumba(i, j, len(ruumbas), random.choice(list(Direction)))
                ruumbas.append(ruumba)

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            get_direction(event)

        for ruumba in ruumbas:
            ruumba.random_move()
            ruumba.interact_with(terrain[ruumba.pos_x][ruumba.pos_y])
            ruumba.update_internal_state()

        # Render
        DISPLAYSURF.fill(BGCOLOR)
        for l in terrain:
            for cell in l:
                cell.render()
        for ruumba in ruumbas:
            ruumba.render()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def get_direction(event):
    if event.type == QUIT:
        terminate()
    # elif event.type == KEYDOWN:
    #     if event.key == K_LEFT and direction[0] != RIGHT:
    #         direction[0] = LEFT
    #     elif event.key == K_RIGHT and direction[0] != LEFT:
    #         direction[0] = RIGHT
    #     elif event.key == K_UP and direction[0] != DOWN:
    #         direction[0] = UP
    #     elif event.key == K_DOWN and direction[0] != UP:
    #         direction[0] = DOWN
    #     if event.key == K_a and direction[1] != RIGHT:
    #         direction[1] = LEFT
    #     elif event.key == K_d and direction[1] != LEFT:
    #         direction[1] = RIGHT
    #     elif event.key == K_w and direction[1] != DOWN:
    #         direction[1] = UP
    #     elif event.key == K_s and direction[0] != UP:
    #         direction[1] = DOWN
    #     if event.key == K_KP4 and direction[0] != RIGHT:
    #         for i in range(len(direction)):
    #             direction[i] = LEFT
    #     elif event.key == K_KP6 and direction[0] != LEFT:
    #         for i in range(len(direction)):
    #             direction[i] = RIGHT
    #     elif event.key == K_KP8 and direction[0] != DOWN:
    #         for i in range(len(direction)):
    #             direction[i] = UP
    #     elif event.key == K_KP2 and direction[0] != UP:
    #         for i in range(len(direction)):
    #             direction[i] = DOWN
    #     if event.key == K_ESCAPE:
    #         terminate()
    # return direction


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

def drawScore(score, i):
    i = i+1
    scoreSurf = BASICFONT.render('Score {}: {}'.format(i, score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 20 * i)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (math.floor(WINDOWWIDTH / 2), 10)
    overRect.midtop = (math.floor(WINDOWWIDTH / 2), gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render(SIM_NAME, True, DARKGRAY, WHITE)
    titleSurf2 = titleFont.render(SIM_NAME, True, YELLOW)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, YELLOW)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


if __name__ == '__main__':
    main()
