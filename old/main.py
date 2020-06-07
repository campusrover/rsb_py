from rsb.redisutil import RedisUtil
from rsb.world import World
from rsb.graphics import Graphics
import pygame
import json


def wall_callback(rutil):
    raw_map = rutil.get_next_map()
    world = World()
    world.rebuild(raw_map)
    print(f"callback {raw_map['id']}")
    return world.walls


# rutil = RedisUtil("pito")
# gr = Graphics()
# gr.setup({"width": 10, "height": 10})
# gr.main_loop(wall_callback, rutil)

class RsbScript(object):
    def __init__(self):
        pass

    def run(self):
        self.setup()
        self.post_setup()
        for x in range(100):
            self.gr.draw_background()
            self.gr.draw_grid()

            raw_map = self.rutil.get_next_map()
            world = World()
            world.rebuild(raw_map)
            print(f"callback {raw_map['id']}")
            i = 0
            for wall in world.walls:
                print(f"w{i}")
                i += 1
                self.gr.scaled_draw_line(wall)
                self.gr.draw_robot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.gr.fpsClock.tick(1)
  
            # self.step()
            # self.raw_map = self.rutil.get_next_map()
            # self.world = World()
            # self.walls = self.world.rebuild(self.raw_map)
            # self.gr.draw_walls_once(self.walls)
            # self.gr.main_loop_once()

    def setup(self):
        print(self.ns)

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

