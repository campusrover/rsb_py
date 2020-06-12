from rsb.redisutil import RedisUtil
from rsb.world import World
from rsb.graphics import Graphics
from rsb.robot import Robot

import pygame
import json
import sys
import random

class Script(object):
    def __init__(self, ns, worldsize, origin):
        self.namespace(ns)
        self.worldsize(worldsize)
        self.origin(origin)

    def run(self):
        self.setup()
        self.post_setup()
        while True:
            self.gr.draw_background()
            self.gr.draw_grid()
            self.step()
            self.draw_map()
            self.draw_robot()
            self.gr.draw_robot()
            self.gr.update_graphics()
            self.gr.fpsClock.tick(5)
  
    def setup(self):
        pass

    def step(self):
        pass

    def namespace(self,arg):
        self.ns = arg

    def worldsize(self, arg):
        self.worldsize = arg

    def origin(self, arg):
        self.origin = arg

    def post_setup(self):
        self.rutil = RedisUtil(self.ns)
        self.gr = Graphics()
        self.gr.setup({"width": self.worldsize[0], "height": self.worldsize[1]})
        self.gr.origin(self.origin)
        self.gr.recompute_gridlines()

    def update_graphics(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        
    def draw_map(self):
        raw_map = self.rutil.get_next_map()
        world = World()
        world.rebuild(raw_map)
        i = 0
        for wall in world.walls:
            i += 1
            self.gr.scaled_draw_line(wall)

    def draw_robot(self):
        robot = Robot(self.rutil.get_robot_info())
        self.gr.sprite_location(0, robot.location, robot.orientation)
        self.gr.draw_all_sprites()

