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
from classes import CELL_COLORS, Cell, CellType, Direction, Predator, TerrainCell, MoveableCell, message_board, last_message_board
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
CHROMOSOME_LEN = config.CHROMOSOME_LEN


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
    chromo_map = {
        # fitness -> chromo_string
    }
    for t in range(20):
        for run in range(100):
            print("+++++++++++++++++++++++++++++++++++++++")
            print("Running scenario {}".format(run))
            n_max = 5000
            num_scenarios = 100
            num_captures = 0
            num_blocks = 0
            dist_avg = 100
            time_to_capture = []
            random.seed(a=None, version=2)
            chromo_str = "".join([str(int(random.getrandbits(1))) for x in range(CHROMOSOME_LEN)])
            n_s = num_scenarios
            while n_s > 0:
                result = runGame(chromo_str)
                if result["captured"]:
                    num_captures += 1
                num_blocks += result["num_blocks"]
                dist_avg = (dist_avg + result["dist_avg"]) / 2
                time_to_capture.append(result["num_turns"])
                # showGameOverScreen()
                n_s -= 1
            fitness = calc_fitness(
                n_max=n_max,
                n_scenarios=num_scenarios,
                n_captures=num_captures,
                d_avg=dist_avg,
                n_blocks=num_blocks,
                time_to_capture=time_to_capture
            )
            print("Fitness of run {} was {}".format(run, fitness))
            print("+++++++++++++++++++++++++++++++++++++++")
            chromo_map[chromo_str] = fitness

        print("+++++++++++++++++++ FINAL ++++++++++++++++++++")
        best = ("", 0)
        for key, value in chromo_map.items():
            if value > best[1]:
                best = (key, value)
        print("Best score was string {}".format(best[0]))
        print("Final score {}".format(best[1]))
        print("+++++++++++++++++++ FINAL ++++++++++++++++++++")


def runGame(chromo_str):
    global last_message_board, message_board
    terrain = load_room()

    predators = gen_predators(terrain, CellType.PREDATOR, number=4, chromo_str=chromo_str)

    movers = gen_movers(terrain, CellType.PREY)

    sim_turn = 0
    num_blocks = 0
    dist_avg = 100
    while sim_turn < SIM_TURNS: # main game loop
        for event in pygame.event.get(): # event handling loop
            get_keyboard(event)

        for mover in movers:
            mover.random_move()
            for predator in predators:
                if predator.pos_x == mover.pos_x and predator.pos_y == mover.pos_y:
                    mover.needs_move_back()
                    mover.try_revert_move()
                    num_blocks = num_blocks + 1

        pred_dist = 0
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
            pred_dist += predator.get_distance(movers[0])
        pred_dist = pred_dist / len(predators)
        dist_avg = (dist_avg + pred_dist) / 2

        for mover in movers:
            if mover.surrounded(predators):
                return {
                    "captured": True,
                    "num_turns": sim_turn,
                    "num_blocks": num_blocks,
                    "dist_avg": dist_avg,
                    "chromo_str": chromo_str,
                }

        # # Render
        # DISPLAYSURF.fill(BGCOLOR)
        # for l in terrain:
        #     for cell in l:
        #         cell.render()
        # for mover in movers:
        #     mover.render()
        # for predator in predators:
        #     predator.render()
        # pygame.display.update()
        # FPSCLOCK.tick(FPS)
        last_message_board = message_board
        sim_turn += 1

    return {
        "captured": False,
        "num_turns": sim_turn,
        "num_blocks": num_blocks,
        "dist_avg": dist_avg,
        "chromo_str": chromo_str,
    }


def calc_fitness(n_max=5000, n_scenarios=100, n_captures=0, d_avg=0, n_blocks=0, time_to_capture=[]):
    if n_captures == 0:
        return (0.4)/(d_avg + (0.6 * (n_blocks / (n_max * n_scenarios))))
    elif n_captures < n_scenarios:
        return n_captures
    else:
        return n_scenarios + ((10000 * n_scenarios)/sum(time_to_capture))


def gen_movers(terrain, cell_type, number=1):
    global CELLWIDTH, CELLHEIGHT
    movers = []
    for i in range(number):
        cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        while cell.cell_type != CellType.FLOOR:
            cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        movers.append(MoveableCell(cell.pos_x, cell.pos_y, i, random.choice(list(Direction)), cell_type=cell_type))
    return movers


def gen_predators(terrain, cell_type, number=1, chromo_str=""):
    global CELLWIDTH, CELLHEIGHT
    movers = []
    for i in range(number):
        cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        while cell.cell_type != CellType.FLOOR:
            cell = terrain[random.randint(1, CELLWIDTH-1)][random.randint(1, CELLHEIGHT-1)]
        movers.append(Predator(cell.pos_x, cell.pos_y, i, random.choice(list(Direction)), cell_type=cell_type, chromosome=chromo_str))
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
