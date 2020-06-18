import math
import os
import sys
import pygame as pg
import random as rd
from pygame.locals import *
from rsb.grid import Grid
from rsb.robot import Robot

class Graphics(object):
    def __init__(self):
        pg.init()
        self.fpsClock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()

    def setup(self, size, origin):
        """
        scale: convert from input points to pixels
        rotation: rotate the overall coordinate system
        """
        self.scale = 100
        self.rotation = 0
        self.origin = (origin[0] * self.scale, origin[1] * self.scale)
        self.dimensions = (size[0] * self.scale, size[1] * self.scale)
        self.surface = pg.display.set_mode(self.dimensions, DOUBLEBUF)
        self.background = pg.Color("grey10")
        self.grid = Grid(self.dimensions, self.scale, self.origin, self.surface)

    def recompute_gridlines(self):
        self.grid.recompute()

    def update_graphics(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        pg.display.update()

    def draw_background(self):
        self.surface.fill(self.background)

    def draw_robot(self, robot_origin, angle, length):
        angle = math.degrees(angle)
        self.all_sprites.update()
        angle += 90             # 0 degrees is up for us.
        self.draw_angle_line(self.sc_point(robot_origin), length * self.scale, angle)

    def sc_draw_line(self, wall):
        ends = self.scale_line((wall[0], wall[1]), (wall[2], wall[3]))
        pg.draw.line(self.surface, pg.Color("white"), ends[0], ends[1], 5)

    def sc_draw_rect(self, rect, color):
        pg.draw.rect(self.surface, color, self.sc_rect(rect))

    def scale_line(self, beg, end):
        return [self.sc_point(beg), (self.sc_point(end))]

    def sc_point(self, c):
        return (self.origin[0] - c[0] * self.scale, self.origin[1] - c[1] * self.scale)

    def sc_rect(self, r):
        return Rect(self.sc_point((r[0], self.sc_point(r[1])), (r[1], r[2])))

    def sc_rotate_point(self, point_origin, angle, length):
        x = point_origin[0] + math.cos(math.radians(-angle)) * length
        y = point_origin[1] + math.sin(math.radians(-angle)) * length
        return (x,y)

    def draw_angle_line(self, line_origin, length, angle):

        rotated = self.sc_rotate_point(line_origin, angle, length)
        # then render the line origin->(x,y)
        pg.draw.line(self.surface, Color("red"), line_origin, rotated, 2)       

    def draw_all_sprites(self):
        self.all_sprites.draw(self.surface)

# For now just recreate the sprite each time and see if performance is bad
    def sprite_location(self, idx, location, orientation):
        """
        input angles are always in radians, inside this module we work with degrees
        """
        orientation = math.degrees(orientation)
        location = self.sc_point(location)
        if len(self.all_sprites) == 0:
            self.all_sprites.add(Sprite(location))
        else:
            print(location, orientation)
            self.all_sprites.sprites()[0].pos = location
            self.all_sprites.sprites()[0].angle = orientation

# Rotatable image and movable image
class Sprite(pg.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load("rsb/robot.png")
        self.image = pg.transform.scale(self.image, (30, 60))

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

# Demo and test code

if __name__ == "__main__":
    g = Graphics()
    r = Robot(0, 0, 0, None, "robot.png")
    g.setup((10, 10), (5,5))
    g.recompute_gridlines()
    angle = 0.0
    i = 0.0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
#        loc = (loc[0] + rd.uniform(-0.01, 0.01), loc[1] + rd.uniform(-0.01, 0.01))
#        loc = (loc[0] + 0.05, loc[1])
        loc = (0,i)
        g.sprite_location(0, loc, angle)
        g.draw_background()
        g.grid.draw()
        g.draw_robot(loc, angle, 1)
        g.draw_all_sprites()
        pg.display.flip()
        g.fpsClock.tick(50)
        i += 0.1
        angle += 0.05




