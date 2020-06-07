from rsb.redisutil import RedisUtil
from rsb.world import World
from rsb.graphics import Graphics
import json

def wall_callback(rutil):
    raw_map = rutil.get_next_map()
    world = World()
    world.rebuild(raw_map)
    print(f"callback {raw_map['id']}")
    return world.walls


rutil = RedisUtil("pito")
gr = Graphics()
gr.setup({"width": 10, "height": 10})
gr.main_loop(wall_callback, rutil)
