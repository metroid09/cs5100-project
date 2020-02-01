import random, pygame, sys,math, copy
from pygame.locals import *

def drawScore(score, i):
    i = i+1
    scoreSurf = BASICFONT.render('Score {}: {}'.format(i, score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 20 * i)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawRuumba(ruumbaCoords):
    for coord in ruumbaCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        ruumbaSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, ruumbaSegmentRect)
        ruumbaInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, ruumbaInnerSegmentRect)


def drawBullets(bullets):
    for bullet in bullets:
        x = bullet[0] * CELLSIZE
        y = bullet[1] * CELLSIZE
        bulletRect = pygame.Rect(x + 8, y + 8, CELLSIZE - 16, CELLSIZE - 16)
        pygame.draw.rect(DISPLAYSURF, WHITE, bulletRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    xcenter = coord['x'] * CELLSIZE + math.floor(CELLSIZE/2)
    ycenter = coord['y'] * CELLSIZE+ math.floor(CELLSIZE/2)
    #appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    #pygame.draw.rect(DISPLAYSURF, RED, appleRect)
    pygame.draw.circle(DISPLAYSURF, RED,(xcenter,ycenter),RADIUS)


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
    titleSurf1 = titleFont.render('SNEK', True, DARKGRAY, WHITE)
    titleSurf2 = titleFont.render('SNEK', True, YELLOW)

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


def draw_walls(walls):
    for coord in walls:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        ruumbaSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, BLUE, ruumbaSegmentRect)
        ruumbaInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, LIGHTBLUE, ruumbaInnerSegmentRect)



