from rsb.redisutil import RedisUtil
from rsb.world import World
from rsb.graphics import Graphics
import pygame
import json

class Script(object):
    def __init__(self):
        pass

    def run(self):
        self.setup()
        self.post_setup()
        while True:
            self.gr.draw_background()
            self.gr.draw_grid()

            raw_map = self.rutil.get_next_map()
            world = World()
            world.rebuild(raw_map)
            i = 0
            for wall in world.walls:
                i += 1
                self.gr.scaled_draw_line(wall)
            self.gr.draw_robot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.gr.fpsClock.tick(2)
  
    def setup(self):
        pass

    def step(self):
        pass

    def namespace(self,arg):
        self.ns = arg

    def worldsize(self, arg):
        self.worldsize = arg

    def post_setup(self):
        self.rutil = RedisUtil(self.ns)
        self.gr = Graphics()
        self.gr.setup({"width": self.worldsize[0], "height": self.worldsize[1]})

