import pygame as pg
import os
import sys
from pygame.locals import *
import random as rd
import math

class Graphics(object):
    def __init__(self):
        pg.init()
        self.fpsClock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()

    # size: {"width": 10, "height": 10} - in meters
    def setup(self, size):
        self.scale = 100
        self.dimensions = (size["width"] * self.scale, size["height"] * self.scale)
        self.surface = pg.display.set_mode(self.dimensions)
        self.background = pg.Color("azure3")
        self.gridlines = []

    def origin(self, origin):
        self.origin = (origin[0] * self.scale, origin[1] * self.scale)

    def draw_grid(self):
        for line in self.gridlines:
            pg.draw.aaline(self.surface, pg.Color("azure"), (line[0], line[1]), (line[2], line[3]))

    def recompute_gridlines(self):
        self.gridlines = []
        self.calc_vertical_gridlines()
        self.calc_horizontal_gridlines()

    def calc_vertical_gridlines(self):
        # verical grid lines go from y=0 to y=self.dimensions[1]
        # .. and from x=self.origin[0] +/- scale until they are either below zero or above self.dimensions[0]
        xloops = math.ceil(self.dimensions[0] / self.scale)
        for x in range(xloops):
            inc = x * self.scale
            self.gridlines.append(
                [inc + self.origin[0], 0, inc + self.origin[0], self.dimensions[0]]
            )
            self.gridlines.append(
                [-inc + self.origin[0], 0, -inc + self.origin[0], self.dimensions[0]]
            )

    def calc_horizontal_gridlines(self):
        # horizontal grid lines go from x=0 to x=self.dimesnions[0]
        # .. and from y=self.origin[1] +/- scale until they are either below zero or above self.dimensions[1]
        xloops = math.ceil(self.dimensions[1] / self.scale)
        for x in range(xloops):
            inc = x * self.scale
            self.gridlines.append(
                [0, inc + self.origin[1], self.dimensions[0], inc + self.origin[1]]
            )
            self.gridlines.append(
                [0, -inc + self.origin[1], self.dimensions[1], -inc + self.origin[1]]
            )

    def update_graphics(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        pg.display.update()

    def draw_background(self):
        self.surface.fill(self.background)

    def draw_robot(self):
        self.all_sprites.update()

    def draw_walls(self, cb, arg):
        walls = cb(arg).copy()
        i = 0
        for wall in walls:
            i += 1
            self.scaled_draw_line(wall)

    def main_loop(self, wall_callback, arg):
        while True:
            self.draw_background()
            self.draw_grid()
            self.draw_walls(wall_callback, arg)
            self.draw_robot()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            pg.display.update()
            self.fpsClock.tick(1)

    def main_loop_once(self):
        self.draw_background()
        self.draw_grid()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        pg.display.update()
        self.fpsClock.tick(1.0)

    def draw_walls_once(self, walls):
        i = 0
        for wall in walls:
            i += 1
            self.scaled_draw_line(wall)

    def scaled_draw_line(self, wall):
        ends = self.scale_line((wall[0], wall[1]), (wall[2], wall[3]))
        pg.draw.line(self.surface, pg.Color("black"), ends[0], ends[1], 5)

    def scale_line(self, beg, end):
        return [self.sc_point(beg), (self.sc_point(end))]

    def sc_point(self, c):
        return (c[0] * self.scale + self.origin[0], c[1] * self.scale + self.origin[1])

    def sc_rect(self, r):
        return Rect(self.sc_point((r[0], self.sc_point(r[1])), (r[1], r[2])))

    def sc_draw_rect(self, rect, color):
        pg.draw.rect(self.surface, color, self.sc_rect(rect))

    def draw_all_sprites(self):
        self.all_sprites.draw(self.surface)


# For now just recreate the sprite each time and see if performance is bad
    def sprite_location(self, idx, location, orientation):
        location = self.sc_point(location)
        if len(self.all_sprites) == 0:
            self.all_sprites.add(Sprite(location))
        else:
            self.all_sprites.sprites()[0].pos = location
            self.all_sprites.sprites()[0].angle = orientation

# Rotatable image and movable image
class Sprite(pg.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        # self.image = pg.Surface((20, 40), pg.SRCALPHA)
        self.image = pg.image.load("robot1.png")
        # pg.draw.polygon(self.image, pg.Color('red'),
        #                 ((10, 0), (0, 40), (20, 40)))
        # A reference to the original image to preserve the quality.
        self.orig_image = self.image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.angle = 0

    def update(self):
        self.rotate()
        self.move()

    def move(self):
        self.rect = self.image.get_rect(center=self.pos)

    def rotate(self):
        """Rotate the image of the sprite around its center."""
        # `rotozoom` usually looks nicer than `rotate`. Pygame's rotation
        # functions return new images and don't modify the originals.
        self.image = pg.transform.rotozoom(self.orig_image, self.angle, 1)
        # Create a new rect with the center of the old rect.
        self.rect = self.image.get_rect(center=self.rect.center)
