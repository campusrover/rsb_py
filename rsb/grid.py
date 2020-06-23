import math
import pygame as pg

X0_CLR = pg.Color("red")
X_CLR = pg.Color("thistle1")
Y0_CLR = pg.Color("green")
Y_CLR = pg.Color("springgreen3")

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
            pg.draw.aaline(self.surface, line[4], (line[0], line[1]), (line[2], line[3]))

    def calc_y_gridlines(self):
        # verical grid lines go from y=0 to y=self.dimensions[1]
        # .. and from x=self.origin[0] +/- scale until they are either below zero or above self.dimensions[0]
        xloops = math.ceil(self.dimensions[0] / self.scale)
        for x in range(xloops):
            inc = x * self.scale
            color = Y0_CLR if x == 0 else Y_CLR
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
        for x in range(xloops):
            ddd = X0_CLR if x == 0 else X_CLR
            inc = x * self.scale
            self.gridlines.append(
                [0, inc + self.origin[1], self.dimensions[0], inc + self.origin[1], ddd]
            )
            self.gridlines.append(
                [0, -inc + self.origin[1], self.dimensions[1], -inc + self.origin[1], ddd]
            )
