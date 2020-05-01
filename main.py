import pygame
from pygame.locals import *
import sys
import math
import numpy as np

# settings
width = 1280
height = int(width * 0.5625)
mouse_sensitivity = 1
fov = 90

pygame.init()
fpsClock = pygame.time.Clock()
pygame.mouse.set_visible(False)
mouse_sensitivity /= 4


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
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Game')

    return screen


def map_init():
    print("Map view")

    screen = pygame.display.set_mode((1000, 1000), 0, 32)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Map')

    return screen, 1000, 1000


def map_render():
    screen.fill((0, 0, 0))
    view = (player.angle-(fov/2), player.angle+(fov/2))

    # player
    pygame.draw.circle(screen, (0, 175, 255), (player.x, player.y), 5)

    def draw_ray(angle):
        angle -= 90

        rad = math.radians(angle)
        pos = int(player.x + 750 * math.cos(rad)), int(player.y + 750 * math.sin(rad))

        pygame.draw.line(screen, (255, 0, 0), (player.x, player.y), pos, 2)

    def center_angle(angle):
        angle -= 90

        rad = math.radians(angle)
        pos = int(player.x + 50 * math.cos(rad)), int(player.y + 50 * math.sin(rad))

        pygame.draw.line(screen, (255, 0, 0), (player.x, player.y), pos, 2)

        return pos[0] - player.x, pos[1] - player.y

    # cone of view
    draw_ray(view[0])
    draw_ray(view[1])
    cov_vector = center_angle(view[0]+(fov/2))
    left_vector = center_angle(view[0]+(fov/2)-90)

    # walls
    walls_dict = {}
    for wall in walls:
        pygame.draw.line(screen, (255, 255, 255), wall[0], wall[1], 2)

        p_found = False
        angles = []
        for point in wall:
            wall_vector = point[0] - player.x, point[1] - player.y

            def get_angle(v1, v2):
                f1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
                f2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

                uv1 = np.array([v1[0] / f1, v1[1] / f1])
                uv2 = np.array([v2[0] / f2, v2[1] / f2])

                dot_product = np.dot(uv1, uv2)

                angle = math.degrees(np.arccos(dot_product))

                return angle

            angle = get_angle(cov_vector, wall_vector)
            left_angle = get_angle(left_vector, wall_vector)

            if left_angle <= 90:
                angle = -angle

            if -fov/2 < angle < fov/2:
                def distance(lp_1, lp_2):
                    return int(abs((lp_2[0]-lp_1[0])*(lp_1[1]-player.y) - (lp_1[0]-player.x)*(lp_2[1]-lp_1[1])) / np.sqrt(np.square(lp_2[0]-lp_1[0]) + np.square(lp_2[1]-lp_1[1])))
                    # p1 = np.array([lp_1[0], lp_1[1]])
                    # p2 = np.array([lp_2[0], lp_2[1]])
                    # p3 = np.array([player.x, player.y])
                    # return int(abs(np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1)))

                pygame.draw.line(screen, (255, 255, 0), wall[0], wall[1], 2)

                p1 = wall[0][0], wall[0][1]
                p2 = wall[1][0], wall[1][1]
                d = distance(p1, p2)

                walls_dict[d] = wall
                p_found = True
                break
            if not p_found:
                angles.append(angle)
        if not p_found:
            abs_angle = abs(angles[0]-angles[1])
            if abs_angle > abs(angles[0]+angles[1]):
                if 90 < abs_angle < 180:
                    pygame.draw.line(screen, (255, 255, 0), wall[0], wall[1], 2)

    # i = len(walls_dict)
    # for k, v in walls_dict.items():
    #     i -= 1
    #     if i == 0:
    #         pygame.draw.line(screen, (255, 0, 0), v[0], v[1], 2)


class Player:
    def __init__(self, start_position):
        self.x = start_position[0]
        self.y = start_position[1]
        self.angle = 0


walls, start_position = read_map()
screen, width, height = map_init()

player = Player(start_position)

while True:
    def controls():
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                mouse_X, _ = event.pos
                movement = mouse_X - (width/2)

                player.angle = player.angle + (movement*(360/width)*mouse_sensitivity)

                pygame.mouse.set_pos(width/2, height/2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        rad_1 = math.radians(player.angle - 90)
        vector_1 = round(2 * math.cos(rad_1)), round(2* math.sin(rad_1))

        rad_2 = math.radians(player.angle)
        vector_2 = round(2 * math.cos(rad_2)), round(2 * math.sin(rad_2))

        if keys[pygame.K_w]:
            player.x += vector_1[0]
            player.y += vector_1[1]
        if keys[pygame.K_s]:
            player.x += -vector_1[0]
            player.y += -vector_1[1]
        if keys[pygame.K_a]:
            player.x += -vector_2[0]
            player.y += -vector_2[1]
        if keys[pygame.K_d]:
            player.x += vector_2[0]
            player.y += vector_2[1]

    controls()
    map_render()

    pygame.display.update()
    fpsClock.tick(60)