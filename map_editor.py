import pygame
from pygame.locals import *
import sys
import math
import numpy as np


def screen_init():
    print("Map editor")
    print("LMB - create wall, RMB - set player starting position")
    print("Z - undo, S - save map")

    screen = pygame.display.set_mode((800, 800), 0, 32)
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Map')

    return screen


def save_map():
    print("Saving map")
    map_file = open("Maps\\saved_map.txt", "w")

    map_file.write("{},{}".format(int(player_pos[0]*6.25), int(player_pos[1]*6.25)))

    for w in walls:
        map_file.write("\n{},{}-{},{}".format(int(w[0][0]*6.25), int(w[0][1]*6.25), int(w[1][0]*6.25), int(w[1][1]*6.25)))


pygame.init()
fpsClock = pygame.time.Clock()
screen = screen_init()

click = 0
starting_node = ()
walls = []
player_pos = [400, 400]

while True:
    def controls(click, starting_node, player_pos):
        m_pos = pygame.mouse.get_pos()
        closest_pos = (round(m_pos[0]/16)*16, round(m_pos[1]/16)*16)

        # # 6.25 = 5 000(map width and height) / 800(screen width and height)
        # map_pos = (int(closest_pos[0]*6.25), int(closest_pos[1]*6.25))

        pygame.draw.circle(screen, (255, 100, 0), closest_pos, 3)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click += 1

                    if click == 1:
                        starting_node = closest_pos

                    if click == 2:
                        walls.append([starting_node, closest_pos])
                        click = 0

                if event.button == 3:
                    player_pos = closest_pos

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    del walls[-1]

                if event.key == pygame.K_s:
                    save_map()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        return click, starting_node, player_pos

    screen.fill((0, 0, 0))

    for w in walls:
        pygame.draw.line(screen, (255, 255, 255), w[0], w[1], 2)

        pygame.draw.circle(screen, (255, 255, 255), w[0], 2)
        pygame.draw.circle(screen, (255, 255, 255), w[1], 2)

    click, starting_node, player_pos = controls(click, starting_node, player_pos)

    if click == 1:
        pygame.draw.circle(screen, (255, 0, 0), starting_node, 2)

    pygame.draw.circle(screen, (100, 100, 255), player_pos, 3)

    pygame.display.update()
    fpsClock.tick(60)