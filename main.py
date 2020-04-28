import pygame
from pygame.locals import *
import sys
import random

# settings
width = 1280
height = int(width * 0.5625)

pygame.init()
fpsClock = pygame.time.Clock()


def read_map():
    print("Loading map")

    map_file = open("Maps\\test_map.txt", "r")
    contents = map_file.read()

    walls = []

    lines = contents.split('\n')
    for l in lines:
        coordinates = l.split('-')

        map_object = map(int, coordinates[0].split(','))
        cord1 = list(map_object)

        map_object = map(int, coordinates[1].split(','))
        cord2 = list(map_object)

        walls.append([cord1, cord2])

    return walls


def game_init():
    print("Game view")

    screen = pygame.display.set_mode((width, height), 0, 32)
    pygame.display.set_caption('Game')

    return screen


def map_init():
    print("Map view")

    map_size = 1000
    scale = 0.5

    screen = pygame.display.set_mode((int(map_size * scale), int(map_size * scale)), 0, 32)
    pygame.display.set_caption('Map')

    return screen, scale


def map_render():
    screen.fill((0, 0, 0))

    for wall in walls:
        pygame.draw.line(screen, (255, 255, 255), [i * scale for i in wall[0]], [i * scale for i in wall[1]], 2)


walls = read_map()

screen, scale = map_init()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    map_render()

    pygame.display.update()