import math
import pygame as pg


class Grid(object):
    def __init__(self, dimensions, scale, origin, surface):
        self.gridlines = []
        self.dimensions = dimensions
        self.scale = scale
        self.origin = origin
        self.surface = surface

    def recompute(self):
        self.gridlines = []
        self.calc_y_gridlines()
        self.calc_x_gridlines()

    def draw(self):
        for line in self.gridlines:
            pg.draw.aaline(self.surface, pg.Color("azure"), (line[0], line[1]), (line[2], line[3]))

    def calc_y_gridlines(self):
        # verical grid lines go from y=0 to y=self.dimensions[1]
        # .. and from x=self.origin[0] +/- scale until they are either below zero or above self.dimensions[0]
        xloops = math.ceil(self.dimensions[0] / self.scale)
        color = "green"
        for x in range(xloops):
            inc = x * self.scale
            if x == 0: color = "bright green"
            self.gridlines.append(
                [inc + self.origin[0], 0, inc + self.origin[0], self.dimensions[0], color]
            )
            self.gridlines.append(
                [-inc + self.origin[0], 0, -inc + self.origin[0], self.dimensions[0], color]
            )

    def calc_x_gridlines(self):
        # horizontal grid lines go from x=0 to x=self.dimesnions[0]
        # .. and from y=self.origin[1] +/- scale until they are either below zero or above self.dimensions[1]
        xloops = math.ceil(self.dimensions[1] / self.scale)
        color = "red"
        for x in range(xloops):
            if x == 0: color = "bright_red"
            inc = x * self.scale
            self.gridlines.append(
                [0, inc + self.origin[1], self.dimensions[0], inc + self.origin[1], color]
            )
            self.gridlines.append(
                [0, -inc + self.origin[1], self.dimensions[1], -inc + self.origin[1], color]
            )
