import pygame
import os
import sys
from pygame.locals import *
import random as rd

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Graphics(object):
    def __init__(self):
        pygame.init()
        self.fpsClock = pygame.time.Clock()

    # size: {"width": 5, "height": 5} - in meters
    def setup(self, size):
        self.scale = 100
        self.dimensions = (size["width"] * self.scale, size["height"] * self.scale)
        print(self.dimensions)
        self.surface = pygame.display.set_mode(self.dimensions)
        self.background = pygame.Color(100, 149, 237) 

    def draw_grid(self):
        pass

    def draw_background(self):
        self.surface.fill(self.background)
    
    def draw_robot(self):
        pass

    def draw_walls(self, cb, arg):
        print(f"draw_walls-{rd.randrange(10)}")
        walls = cb(arg).copy()
        i = 0
        for wall in walls:
            print(f"w{i}")
            i += 1
            self.scaled_draw_line(wall)
        
    def main_loop(self, wall_callback, arg):
        while True:
            self.draw_background()
            self.draw_grid()
            self.draw_walls(wall_callback, arg)
            self.draw_robot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.fpsClock.tick(1)

    def scaled_draw_line(self,wall):
        ends = self.scale_line(wall)
        pygame.draw.line(self.surface, BLACK, ends[0], ends[1], 5)
        #pygame.draw.line(self.surface, BLACK, [50,50], [100,100], 5)

    def scale_line(self, points):
        return [self.sc_coord(points[0]), self.sc_coord(points[1])],[self.sc_coord(points[2]), self.sc_coord(points[3])]

    def sc_coord(self, c):
        return self.scale * (c + 5)
