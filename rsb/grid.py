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
        self.calc_vertical_gridlines()
        self.calc_horizontal_gridlines()

    def draw(self):
        for line in self.gridlines:
            pg.draw.aaline(self.surface, pg.Color("azure"), (line[0], line[1]), (line[2], line[3]))

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
