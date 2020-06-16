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
        self.namespace = ns
        self.worldsize = worldsize
        self.origin = origin

    def run(self):
        self.setup()
        self.post_setup()
        while True:
            self.gr.draw_background()
            self.gr.grid.draw()
            self.step()
            self.draw_map()
            self.draw_robot()
            self.gr.update_graphics()
            self.gr.fpsClock.tick(5)

    def setup(self):
        pass

    def step(self):
        pass

    def post_setup(self):
        self.rutil = RedisUtil(self.namespace)
        self.gr = Graphics()
        self.gr.setup(self.worldsize, self.origin)
        self.gr.recompute_gridlines()
        self.robot = Robot(0, 0, 0, None, "robot.png")

    def update_graphics(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    def draw_map(self):
    # todo: Handle case of no maps because no walls
        raw_map = self.rutil.get_next_map()
        world = World()
        world.rebuild(raw_map)
        i = 0
        for wall in world.walls:
            i += 1
            self.gr.sc_draw_line(wall)

    def draw_robot(self):
        ri = self.rutil.get_robot_info()
        self.robot.recompute((ri["odom"]["location"][0],
            ri["odom"]["location"][1]), ri["odom"]["orientation"][2] )
        self.gr.sprite_location(0, self.robot.location, self.robot.orientation)
        self.gr.draw_all_sprites()
        self.gr.draw_robot(self.robot.location, self.robot.orientation, 0.5)

