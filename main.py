import pygame
from pygame.locals import *
import sys
import math
import numpy as np
from collections import defaultdict
import cProfile, pstats, io

# settings
width = 1280
height = int(width * 0.5625)
mouse_sensitivity = 0.15
fov = 90
v_fov = 60
wall_h = 100

pygame.init()
fpsClock = pygame.time.Clock()
pygame.mouse.set_visible(False)
shoot = 0


def profile(fnc):
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


def load_sprites():
    gun_sprite = []
    gun_sprite.append(pygame.image.load("Sprites\\Gun_idle.png"))
    gun_sprite.append(pygame.image.load("Sprites\\Gun_shooting.png"))

    gun_sprite[0] = pygame.transform.scale(gun_sprite[0], (width, height))
    gun_sprite[1] = pygame.transform.scale(gun_sprite[1], (width, height))

    gunshot_sprite = pygame.image.load("Sprites\\Gunshot.png")

    gunshot_sprite = pygame.transform.scale(gunshot_sprite, (int(width/3), int(width/3)))

    return gun_sprite, gunshot_sprite


def read_map():
    print("Loading map")

    map_file = open("Maps\\test_map_3.txt", "r")
    contents = map_file.read()

    walls = []

    lines = contents.split('\n')

    sp = False
    for l in lines:
        if not sp:
            start_position = l.split(',')
            start_position = list(map(int, start_position))
            sp = True
        else:
            coordinates = l.split('-')

            cord1 = coordinates[0].split(',')
            cord1 = list(map(int, cord1))

            cord2 = coordinates[1].split(',')
            cord2 = list(map(int, cord2))

            walls.append([cord1, cord2])

    return walls, start_position


def game_init():
    print("Game view")

    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.display.set_caption('Game')

    gun_sprite, gunshot_sprite = load_sprites()

    return screen, gun_sprite, gunshot_sprite


def map_init():
    print("Map view")

    screen = pygame.display.set_mode((500, 500), pygame.FULLSCREEN)
    pygame.display.set_caption('Map')

    return screen, 1000, 1000


# @profile
def map_render():
    screen.fill((0, 0, 0))
    view = (player.angle-(fov/2), player.angle+(fov/2))

    # player
    pygame.draw.circle(screen, (0, 175, 255), (int(player.x/10), int(player.y/10)), 3)

    def draw_ray(angle):
        angle -= 90

        rad = math.radians(angle)
        pos = int((player.x + 1000 * math.cos(rad))/10), int((player.y + 1000 * math.sin(rad))/10)

        pygame.draw.line(screen, (255, 0, 0), (player.x/10, player.y/10), pos, 2)

    def vector_from_angle(angle):
        angle -= 90

        rad = math.radians(angle)
        pos = int(player.x + 50 * math.cos(rad)), int(player.y + 50 * math.sin(rad))

        return pos[0] - player.x, pos[1] - player.y

    # cone of view
    draw_ray(view[0])
    draw_ray(view[1])
    cov_vector = vector_from_angle(view[0]+(fov/2))
    left_vector = vector_from_angle(view[0]+(fov/2)-90)

    # walls
    walls_dict = defaultdict(list)
    for wall in walls:
        def calculate_distance(p1, p2):
            def points_distance(p):
                arm_distance = math.sqrt(((player.x - p[0]) ** 2) + ((player.y - p[1]) ** 2))
                return arm_distance

            dist1 = points_distance(p1)
            dist2 = points_distance(p2)

            d = (dist1 + dist2)/2

            walls_dict[d].append(wall)

        pygame.draw.line(screen, (255, 255, 255), (wall[0][0]/10, wall[0][1]/10), (wall[1][0]/10, wall[1][1]/10), 2)

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
                pygame.draw.line(screen, (255, 255, 0), (wall[0][0]/10, wall[0][1]/10), (wall[1][0]/10, wall[1][1]/10), 2)
                p_found = True

                p1 = wall[0][0], wall[0][1]
                p2 = wall[1][0], wall[1][1]
                calculate_distance(p1, p2)
                break
            if not p_found:
                angles.append(angle)

        if not p_found:
            abs_angle = abs(angles[0]-angles[1])
            if abs_angle > abs(angles[0]+angles[1]):
                if 90 < abs_angle < 180:
                    pygame.draw.line(screen, (255, 0, 255), (wall[0][0]/10, wall[0][1]/10), (wall[1][0]/10, wall[1][1]/10), 2)

                    p1 = wall[0][0], wall[0][1]
                    p2 = wall[1][0], wall[1][1]
                    calculate_distance(p1, p2)

    for k in sorted(walls_dict.keys(), reverse=True):
        v = walls_dict[k]

        for wall in v:
            # visualization
            value = (k/10)
            if value > 255:
                value = 255

            pygame.draw.line(screen, (value, value, 255), (wall[0][0]/10, wall[0][1]/10), (wall[1][0]/10, wall[1][1]/10), 2)


# @profile
def game_render():
    screen.fill((0, 0, 0))
    view = (player.angle-(fov/2), player.angle+(fov/2))

    # # player
    # pygame.draw.circle(screen, (0, 175, 255), (player.x, player.y), 5)

    def vector_from_angle(angle):
        angle -= 90

        rad = math.radians(angle)
        pos = player.x + 50 * math.cos(rad), player.y + 50 * math.sin(rad)

        return pos[0] - player.x, pos[1] - player.y

    # cone of view
    # draw_ray(view[0])
    # draw_ray(view[1])
    cov_vector = vector_from_angle(view[0]+(fov/2))
    left_vector = vector_from_angle(view[0]+(fov/2)-90)

    # walls
    walls_dict = defaultdict(list)
    for wall in walls:
        def calculate_distance(p1, p2):
            def points_distance(p):
                arm_distance = math.sqrt(((player.x - p[0]) ** 2) + ((player.y - p[1]) ** 2))
                return arm_distance

            dist1 = points_distance(p1)
            dist2 = points_distance(p2)

            vector_1 = [wall[0][0] - player.x, wall[0][1] - player.y]
            vector_2 = [wall[1][0] - player.x, wall[1][1] - player.y]
            ang1 = get_angle(cov_vector, vector_1)
            ang2 = get_angle(cov_vector, vector_2)

            l_angle = get_angle(left_vector, vector_1)
            if l_angle <= 90:
                ang1 = -ang1

            l_angle = get_angle(left_vector, vector_2)
            if l_angle <= 90:
                ang2 = -ang2

            d = (dist1 + dist2)/2

            walls_dict[d].append([[ang1, dist1], [ang2, dist2]])

        # pygame.draw.line(screen, (255, 255, 255), wall[0], wall[1], 2)

        p_found = False
        angles = []
        for point in wall:
            wall_vector = point[0] - player.x, point[1] - player.y

            def get_angle(v1, v2):
                f1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
                f2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

                if f2 == 0:
                    f2 = 0.01
                    print("f2 == 0")

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
                # pygame.draw.line(screen, (255, 255, 0), wall[0], wall[1], 2)
                p_found = True

                p1 = wall[0][0], wall[0][1]
                p2 = wall[1][0], wall[1][1]
                calculate_distance(p1, p2)
                break
            if not p_found:
                angles.append(angle)

        if not p_found:
            abs_angle = abs(angles[0]-angles[1])
            if abs_angle > abs(angles[0]+angles[1]):
                if 90 < abs_angle < 180:
                    # pygame.draw.line(screen, (255, 0, 255), wall[0], wall[1], 2)

                    p1 = wall[0][0], wall[0][1]
                    p2 = wall[1][0], wall[1][1]
                    calculate_distance(p1, p2)

    def render(walls_dict):
        # background
        pygame.draw.rect(screen, (245, 245, 255), (0, 0, width, height / 2))
        pygame.draw.rect(screen, (70, 70, 80), (0, height / 2, width, height / 2))

        # walls
        for k in sorted(walls_dict.keys(), reverse=True):
            v = walls_dict[k]

            for wall in v:
                value = (k / 10)
                if value > 255:
                    value = 255

                x1 = ((wall[0][0] + fov / 2) / fov) * width
                x2 = ((wall[1][0] + fov / 2) / fov) * width

                # # fish eye
                # a1 = math.degrees(math.atan((wall_h/2) / wall[0][1]))
                # a2 = math.degrees(math.atan((wall_h/2) / wall[1][1]))

                # getting rid of fish eye
                dist1 = abs(wall[0][1] * math.cos(math.radians(abs(wall[0][0]))))
                dist2 = abs(wall[1][1] * math.cos(math.radians(abs(wall[1][0]))))

                if dist1 == 0:
                    dist1 = 0.01
                if dist2 == 0:
                    dist2 = 0.01

                a1 = math.degrees(math.atan((wall_h / 2) / dist1))
                a2 = math.degrees(math.atan((wall_h / 2) / dist2))

                y1 = (height / 2) * (a1 / (v_fov / 2))
                y2 = (height / 2) * (a2 / (v_fov / 2))

                B = 255 - value + 10
                if B > 255:
                    B = 255

                pygame.draw.polygon(screen, (255 - value, 255 - value, B),
                                    [(x1, height / 2 - y1), (x2, height / 2 - y2),
                                     (x2, height / 2 + y2), (x1, height / 2 + y1)], 0)

        # crosshair
        pygame.draw.circle(screen, (255, 25, 25), (int(width / 2), int(height / 2)), 2)

        # gun
        if shoot == 0:
            screen.blit(gun_sprite[0], (0, 0))
        else:
            screen.blit(gunshot_sprite, (width/2, height/3))

            screen.blit(gun_sprite[1], (0, 0))

    render(walls_dict)


class Player:
    def __init__(self, start_position):
        self.x = start_position[0]
        self.y = start_position[1]
        self.angle = 0


walls, start_position = read_map()

screen, gun_sprite, gunshot_sprite = game_init()
# screen, width, height = map_init()

player = Player(start_position)

while True:
    def controls(shoot):
        shoot -= 1
        if shoot < 0:
            shoot = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEMOTION:
                movement = pygame.mouse.get_rel()

                player.angle = player.angle + (movement[0]*(360/width)*mouse_sensitivity)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if shoot == 0:
                        shoot = 6

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        rad_1 = math.radians(player.angle - 90)
        vector_1 = round(2 * math.cos(rad_1)), round(2 * math.sin(rad_1))

        rad_2 = math.radians(player.angle)
        vector_2 = round(2 * math.cos(rad_2)), round(2 * math.sin(rad_2))

        if keys[pygame.K_w]:
            if keys[pygame.K_LSHIFT]:
                vector_1 = vector_1[0] * 2, vector_1[1] * 2

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

        return shoot

    shoot = controls(shoot)
    game_render()
    # map_render()

    pygame.display.update()
    fpsClock.tick(60)