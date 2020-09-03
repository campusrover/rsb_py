"""
Demo of a wall follower using robot_servies and rsb
Clean restart
"""
from rsb.script import Script, Conditional_Brain, Frequency_Brain, Else_Brain, Brain
from rsb.redisutil import RedisUtil
import json, math

wallfollow_ru = RedisUtil("Nate", keys={"Cmd": "list", "Lidar": "string", "Cmd_Feedback": "list"})
wall_dist = 0.35  # movement_bridge safe-thresh is .25
dist_wiggle = 0.05  # 0.35 +/- 0.05
angle_wiggle = 20  # degrees

def wall_angle(ru, lidar_ray_threetuple):
    lindex, cindex, rindex = lidar_ray_threetuple
    lray = ru.lidar['data'][lindex]
    rray = ru.lidar['data'][rindex]
    # some mathy assumptions are made here
    # the main one is that if you have rays a, b, and c, where b is the min and all three are reflecting off the same wall, then a and b will be coming from just outside b's width
    # so if b has a width of 90 degrees centered on 90 then a and c are probably measured from 135 and 45
    # in this case though I know I have 8 45 degree lidar slices, so a and c are placed at 113 and 67 (90+/-23). I also always put b at 90 to get nice "flat" measurements
    langle = math.radians(113)
    rangle = math.radians(67)
    run = rray * math.cos(rangle) - lray * math.cos(langle)
    rise = rray * math.sin(rangle) - lray * math.sin(langle)
    return math.atan2(rise, run) * 180 / math.pi
"""
planning space
Brains: 
    Fbrains:
        Status_brain: updates/ reports status
        State_brain: updates shared redis-util and decides which state robot should be in based on lidar data
    Cbrains:
        Find_wall
        Front_wall
        Follow_wall
        too close/ too far/ bad angle
        wall dropoff (swing around left corner)

States:
    no wall (nw)
    has wall front (hwf)
    has wall left (hwl)
    wall left drop/ left corner (wd)

state changes:

nw -> hwf, hwl
hwf -> hwl
hwl -> hwf, wd
wd -> hwf, hwl
"""

class Status_Brain(Frequency_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru, 100)  # higher frequency than roomba 

    def fire(self):
        # update redis util and refresh move state, wall angles
        self.ru.bulk_update()
        Brain.move_state = self.ru.cmd_feedback["code"]
        Brain.left_wall_angle = wall_angle(self.ru, (3, 2, 1))
        Brain.front_wall_angle = wall_angle(self.ru, (1, 0, 7))


class NoWall_Brain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)

    def condition(self):
        return self.ru.lidar['data'][0] > wall_dist and self.ru.lidar['data'][2] > wall_dist + dist_wiggle

    def fire(self):
        cmd = {"cmd": "move", "duration": 10, "speed": 0.1, "name": "no-wall-go"}
        self.add_cmd(cmd)

    def control_cond(self):
        return self.condition()

class FrontWall_Brain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)

    def condition(self):
        return self.ru.lidar['data'][0] < wall_dist + dist_wiggle

    def fire(self):
        cmd1 = {"cmd": "move", "duration": 1, "speed": -0.1, "name": "front-wall-backup"}
        turn_amt = -90 + Brain.front_wall_angle
        cmd2 = {"cmd": "rotate", "duration": 5, "speed": turn_amt/5, "name": "front-wall-turn"}
        self.add_cmds(cmd1, cmd2, override=self.seizing)

    def control_cond(self):
        return self.condition()

class LeftWall_Brain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)

    def condition(self):
        return self.ru.lidar['data'][0] > wall_dist and self.ru.lidar['data'][2] < wall_dist + dist_wiggle

    def fire(self):
        cmd = {"cmd": "move", "duration": 10, "speed": 0.1, "name": "left-wall-go"}
        self.add_cmd(cmd)

    def control_cond(self):
        return self.condition()


class WallAdjust_Brain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)

    def condition(self):
        return (wall_dist - dist_wiggle <= self.ru.lidar['data'][2] <= wall_dist + dist_wiggle) and abs(Brain.left_wall_angle) >= angle_wiggle

    def fire(self):
        print(self.ru.lidar['data'][2], abs(Brain.left_wall_angle))
        dist_to_wall = min(self.ru.lidar['data'][1:4])
        dist_error = -wall_dist + dist_to_wall  # the max value of this is about DIST_GIVE
        try:
            dist_comp = math.asin(dist_error/0.25) * 180 / math.pi
        except:
            dist_comp = angle_wiggle
        cmd1 = {"cmd": "rotate", "duration": 5, "speed": (Brain.left_wall_angle + dist_comp)/5, "name": "adjust-rotate-1"} # don't go parrallel to the wall, over/under compensate based on dist_error to get closer to IDEAL_DIST
        cmd2 = {"cmd": "move", "duration": 2.5, "speed": 0.1, "name": "adjust-move"}
        cmd3 = {"cmd": "rotate", "duration": 5, "speed": -dist_comp/5, "name": "adjust-rotate-2"}
        self.add_cmds(cmd1, cmd2, cmd3, override=self.seizing)

    def control_cond(self):
        return self.condition()


class WallLost_Brain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)

    def condition(self):
        return min(self.ru.lidar['data'][1:4]) < wall_dist + dist_wiggle and self.ru.lidar['data'][0] > wall_dist

    def fire(self):
        cmd1 = {"cmd": "rotate", "duration": 5, "speed": 18/5, "name": "part-turn-around-corner"}
        cmd2 = {"cmd": "move", "duration": 2, "speed": 0.06, "name": "part-move-around-corner"}
        self.add_cmds(cmd1, cmd2, override=self.seizing)

    def control_cond(self):
        return min(self.ru.lidar['data'][2:4]) < wall_dist + dist_wiggle and self.ru.lidar['data'][1] > wall_dist * 3

nwb = NoWall_Brain()
fwb = FrontWall_Brain()
lwb = LeftWall_Brain()
lwab = WallAdjust_Brain()
lwlb = WallLost_Brain()
sb = Status_Brain()

Brain.control_map = {
    -1: [nwb.uuid, fwb.uuid, lwb.uuid],          # no control -> no wall, front wall, left wall
    nwb.uuid: [fwb.uuid, lwb.uuid],              # no wall -> front, left wall
    fwb.uuid: [lwb.uuid],                        # front wall -> left wall
    lwb.uuid: [lwab.uuid, fwb.uuid, lwlb.uuid],  # left wall -> wall adjust, front wall, left wall lost
    lwab.uuid: [],                       # wall adjust -> left wall
    lwlb.uuid: [fwb.uuid]              # left wall lost -> front wall, left wall
} 

r = Script("Nate", (10,10), (5,5), brains=[nwb, fwb, lwb, lwab, lwlb, sb])
r.run()
