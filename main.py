# (Originally) wormy (a Nibbles clone)
# Then a roomba simulator!
# Now a predator prey simulation!
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
# Modified by Chris Merkley - Zac Johnson for CS 5110

import math
import random
import sys
from datetime import datetime

import pygame
import config
from classes import CELL_COLORS, Cell, CellType, Direction, Predator, TerrainCell, MoveableCell
from pygame.locals import *
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
SIM_TURNS = config.SIM_TURNS


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
    start_time = datetime.now()

    terrain = []
    for i in range(CELLWIDTH):
        add = []
        for j in range(CELLHEIGHT):
            if j == 0 or j == CELLHEIGHT-1 or i == 0 or i == CELLWIDTH-1:
                if random.randint(0, 1000) > 970:
                    try:
                        predators[0].pos_x = i
                        predators[0].pos_y = j
                    except UnboundLocalError:
                        continue
            if random.randint(0, 1000) > 970:
                add.append(TerrainCell(i, j, CellType.FLOOR))
                continue
            add.append(TerrainCell(i, j, CellType.FLOOR))
        terrain.append(add)

    terrain = load_room()

    #generate predators
    predators = gen_predators(terrain, CellType.PREDATOR, number=4)

    movers = gen_movers(terrain, CellType.PREY)

    sim_turn = 0
    while sim_turn < SIM_TURNS: # main game loop
        for event in pygame.event.get(): # event handling loop
            get_keyboard(event)

        for mover in movers:
            mover.random_move()
            for predator in predators:
                if predator.pos_x == mover.pos_x and predator.pos_y == mover.pos_y:
                    mover.needs_move_back()
                    mover.try_revert_move()

        for predator in predators:
            predator.random_move()
            predator.sense(movers[0])
            for p in predators:
                if predator != p and predator.pos_x == p.pos_x and predator.pos_y == p.pos_y:
                    predator.needs_move_back()
                    predator.try_revert_move()
                    continue
            for mover in movers:
                if predator.pos_x == mover.pos_x and predator.pos_y == mover.pos_y:
                    predator.needs_move_back()
                    predator.try_revert_move()
                    continue

        # Render
        DISPLAYSURF.fill(BGCOLOR)
        for l in terrain:
            for cell in l:
                cell.render()
        for mover in movers:
            mover.render()
        for predator in predators:
            predator.render()
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        sim_turn += 1


def gen_movers(terrain, cell_type, number=1):
    global CELLWIDTH, CELLHEIGHT
    movers = []
    for i in range(number):
        cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        while cell.cell_type != CellType.FLOOR:
            cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        movers.append(MoveableCell(cell.pos_x, cell.pos_y, i, random.choice(list(Direction)), cell_type=cell_type))
    return movers


def gen_predators(terrain, cell_type, number=1):
    global CELLWIDTH, CELLHEIGHT
    movers = []
    for i in range(number):
        cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        while cell.cell_type != CellType.FLOOR:
            cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        movers.append(Predator(cell.pos_x, cell.pos_y, i, random.choice(list(Direction)), cell_type=cell_type))
    return movers


def get_keyboard(event):
    if event.type == QUIT:
        terminate()


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
