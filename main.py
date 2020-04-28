import pygame
from pygame.locals import *
import sys

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

    start_position = (500, 500)

    return walls, start_position


def game_init():
    print("Game view")

    screen = pygame.display.set_mode((width, height), 0, 32)
    pygame.display.set_caption('Game')

    return screen


def map_init():
    print("Map view")

    scale = 0.5

    screen = pygame.display.set_mode((int(1000 * scale), int(1000 * scale)), 0, 32)
    pygame.display.set_caption('Map')

    return screen, scale, 500, 500


def map_render():
    screen.fill((0, 0, 0))

    for wall in walls:
        pygame.draw.line(screen, (255, 255, 255), [i * scale for i in wall[0]], [i * scale for i in wall[1]], 2)

    pygame.draw.circle(screen, (0, 175, 255), (player.x, player.y), 5)


class Player:
    def __init__(self, start_position):
        self.x = start_position[0]
        self.y = start_position[1]


walls, start_position = read_map()
screen, scale, width, height = map_init()

player = Player(start_position)

# divide for map view
player.x = (int(player.x/2))
player.y = (int(player.y/2))

while True:
    def controls():
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if player.y > 0:
                player.y -= 1
        if keys[pygame.K_s]:
            if player.y < height:
                player.y += 1
        if keys[pygame.K_a]:
            if player.x > 0:
                player.x -= 1
        if keys[pygame.K_d]:
            if player.x < width:
                player.x += 1

    controls()
    map_render()

    pygame.display.update()
    fpsClock.tick(60)