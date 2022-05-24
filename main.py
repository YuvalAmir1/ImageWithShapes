import copy
import pygame
import math
import random
import logging
import sys
import PIL
import pygame
from PIL import Image
import types
from pygame.pixelarray import PixelArray
import numpy

pygame.init()
clock = pygame.time.Clock()
wn_width = 1920
wn_height = 1080
wn = pygame.display.set_mode((wn_width, wn_height))
wn.fill((0, 0, 0, 0))
shapes = list()
steps_count = 0

im = Image.open('image1.png')
image_pixels = im.load()


class Shape:
    def __init__(self, max_size, evaluate):
        self.y = None
        self.x = None
        self.width = None
        self.height = None
        self.surface = None
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
        self.evaluation = 0
        self.removed = False
        self.max_size = max_size
        num = random.randint(0, 2)

        if num == 0:
            self.create_rectangle()
            self.shape_type = "rectangle"
        elif num == 1:
            self.create_ellipse()
            self.shape_type = "ellipse"
        else:
            self.create_triangle()
            self.shape_type = "triangle"

        if evaluate:
            test_surface = wn.copy()
            test_surface.blit(self.surface, (self.x, self.y))
            min_x = self.x
            if min_x < 0:
                min_x = 0

            min_y = self.y
            if min_y < 0:
                min_y = 0

            max_x = min_x + self.width
            if max_x > wn_width:
                max_x = wn_width

            max_y = min_y + self.height
            if max_y > wn_height:
                max_y = wn_height

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    if wn.get_at((x, y)) != test_surface.get_at((x, y)):
                        self.evaluation -= get_distance_difference(self.color, wn.get_at((x, y)), image_pixels[x, y])

            del test_surface

    def create_rectangle(self):
        self.width = random.randint(5, self.max_size)
        self.height = random.randint(5, self.max_size)

        if int(wn_width - 0.75 * self.width) >= 0:
            self.x = random.randint(int(-0.25 * self.width), int(wn_width - 0.75 * self.max_size))
        else:
            self.x = random.randint(int(-0.25 * self.width), 0)

        if int(wn_height - 0.75 * self.height) >= 0:
            self.y = random.randint(int(-0.25 * self.height), int(wn_height - 0.75 * self.max_size))
        else:
            self.y = random.randint(int(-0.25 * self.height), 0)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill(self.color)
        self.surface = pygame.transform.rotate(self.surface, random.randint(0, 90))

    def create_ellipse(self):
        self.width = random.randint(5, self.max_size)
        self.height = random.randint(5, self.max_size)

        if int(wn_width - 0.75 * self.width) >= 0:
            self.x = random.randint(int(-0.25 * self.width), int(wn_width - 0.75 * self.width))
        else:
            self.x = random.randint(int(-0.25 * self.width), 0)

        if int(wn_height - 0.75 * self.height) >= 0:
            self.y = random.randint(int(-0.25 * self.height), int(wn_height - 0.75 * self.height))
        else:
            self.y = random.randint(int(-0.25 * self.height), 0)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.surface, self.color, (0, 0, self.width, self.height))

    def create_triangle(self):
        x1 = random.randint(0, wn_width)
        y1 = random.randint(0, wn_height)

        x2 = random.randint(x1 - self.max_size, x1 + self.max_size)
        y2 = random.randint(y1 - self.max_size, y1 + self.max_size)

        x3 = random.randint(x1 - self.max_size, x1 + self.max_size)
        y3 = random.randint(y1 - self.max_size, y1 + self.max_size)

        min_x, min_y = min(x1, x2, x3), min(y1, y2, y3)
        max_x, max_y = max(x1, x2, x3), max(y1, y2, y3)

        self.width = max_x - min_x
        self.height = max_y - min_y

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        points = [(x1 - min_x, y1 - min_y), (x2 - min_x, y2 - min_y), (x3 - min_x, y3 - min_y)]
        pygame.draw.polygon(self.surface, self.color, points)

        self.x = min_x
        self.y = min_y

    def blit(self):
        wn.blit(self.surface, (self.x, self.y))


def RGB_to_YUV(color):
    Y = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    U = 0.492 * (color[2] - Y)
    V = 0.877 * (color[0] - Y)
    return Y, U, V


def get_distance(color1, color2):
    YUV_color1 = RGB_to_YUV(color1)
    YUV_color2 = RGB_to_YUV(color2)
    return math.sqrt((YUV_color2[0] - YUV_color1[0]) ** 2 + (YUV_color2[1] - YUV_color1[1]) ** 2 + (YUV_color2[2] - YUV_color1[2]) ** 2)


def get_distance_difference(new_color, original_color, image_color):
    return get_distance(new_color, image_color) - get_distance(original_color, image_color)


def step():
    global shapes
    global steps_count

    # https://www.desmos.com/calculator/lazpl4kkqq
    def get_max_size(a, b, c, d):
        output = a * (1 - (steps_count + c) / (b + steps_count + c))
        if output < d:
            output = d
        return int(output)

    # https://www.desmos.com/calculator/jl51l71r2z
    def get_shapes_count(a, b, c, d):
        return int(a - b * (1 - (steps_count + d) / (c + steps_count + d)))

    steps_count += 1
    print(steps_count)
    current_shapes = list()

    max_size = get_max_size(200, 500, 1000, 2)
    shape_count = get_shapes_count(15000, 45000, 1400, 3000)
    print(max_size)
    print(shape_count)

    for i in range(0, shape_count):
        current_shapes.append(Shape(max_size, True))

    current_shapes = sorted(current_shapes, key=lambda l: l.evaluation)
    print(current_shapes[len(current_shapes) - 1].evaluation)
    under_minimum_count = 0
    for last_shape in current_shapes:
        if last_shape.evaluation <= 0:
            under_minimum_count += 1
        else:
            break

    del current_shapes[0:under_minimum_count]
    shapes += current_shapes


def draw():
    wn.fill((0, 0, 0))
    for shape in shapes:
        shape.blit()


for i in range(0, 10000):
    shapes.append(Shape(200, False))
    shapes[i].blit()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    step()
    draw()
    pygame.display.update()
    clock.tick(60)