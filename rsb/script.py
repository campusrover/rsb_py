from rsb.redisutil import RedisUtil
from rsb.world import World
from rsb.graphics import Graphics
from rsb.robot import Robot
from rsb.panel import Panel

import pygame
import json
import sys
import random
from time import time
import math


class Script(object):
    def __init__(self, ns, worldsize, origin):
        self.namespace = ns
        self.worldsize = worldsize
        self.origin = origin
        self.frames = 0
        self.start_time = time()

    def run(self):
        self.setup()
        self.post_setup()
        while True:
            self.rutil.bulk_update()
            self.frames += 1
            self.gr.draw_background()
            self.gr.grid.draw()
            self.step()
            self.draw_map()
            self.draw_robot()
            self.draw_lidar()
            self.panel.handle_click()
            self.gr.draw_panel(self.panel)
            self.update_graphics()
            self.gr.fpsClock.tick(15)

    def setup(self):
        pass

    def step(self):
        pass

    def post_setup(self):
        self.rutil = RedisUtil(self.namespace)
        self.panel = Panel(self.namespace)
        self.gr = Graphics()
        self.gr.setup(self.worldsize, self.origin)
        self.gr.recompute_gridlines()
        self.robot = Robot(0, 0, 0, None, "robot.png")

    def update_graphics(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.on_exit()
                sys.exit()
        pygame.display.flip()

    def on_exit(self):
        print(f"Frame Rate {self.frames/(time()-self.start_time)} per second")


    def draw_map(self):
        # todo: Handle case of no maps because no walls
        #raw_map = self.rutil.get_next_map()
        raw_map = self.rutil.map
        world = World()
        world.rebuild(raw_map)
        i = 0
        for wall in world.walls:
            i += 1
            self.gr.sc_draw_line(wall)

    def draw_robot(self):
        #ri = self.rutil.get_robot_info()
        odom = self.rutil.odom
        if odom:
            self.robot.recompute(
                (odom["location"][0], odom["location"][1]), odom["orientation"][2]
            )
        self.gr.sprite_location(0, self.robot.location, self.robot.orientation)
        self.gr.draw_all_sprites()
        self.gr.draw_robot(self.robot.location, self.robot.orientation, 0.5)

    def draw_lidar(self, guidelines=False):
        lidar = self.rutil.lidar
        if lidar:
            angle_step = lidar["fov"] / lidar["slices"]
            rays = []
            for i, dist in enumerate(lidar["data"]):
                x = self.robot.location[0] + math.cos(i * angle_step + self.robot.orientation) * dist
                y = self.robot.location[1] + math.sin(i * angle_step + self.robot.orientation) * dist
                rays.append([self.robot.location[0], self.robot.location[1], x, y])

            for r in rays:
                self.gr.sc_draw_line(r, color="purple")

            # For debugging only - draw ines that show the partitions of the slices 
            if guidelines:
                slices = []
                d = max(lidar["data"])
                for i, dist in enumerate(lidar["data"]):
                    x = self.robot.location[0] + math.cos(i * angle_step + self.robot.orientation - angle_step/2) * d
                    y = self.robot.location[1] + math.sin(i * angle_step + self.robot.orientation - angle_step/2) * d
                    slices.append([self.robot.location[0], self.robot.location[1], x, y])
                for r in slices:
                    self.gr.sc_draw_line(r, color="blue")
