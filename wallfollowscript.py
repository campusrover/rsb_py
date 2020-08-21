"""
Demo of a wall follower using robot_servies and rsb
"""
from rsb.script import Script, Conditional_Brain, Frequency_Brain, Else_Brain, Brain
from rsb.redisutil import RedisUtil
import json, math

wallfollow_ru = RedisUtil("Nate", keys={"Cmd": "list", "Lidar": "string", "Cmd_Feedback": "list"})
Brain.state_tree = {
    "stopped_no_wall": ["find_wall", "front_wall"], 
    "stopped_with_wall": ["follow_wall", "front_wall"],
    "follow_wall": ["follow_adjust", "wall_dropoff"], 
    "find_wall": ["follow_wall"]}  # all states can go to stopped, no need to enumerate
# add new shared properties to Brain that are used only in this script
Brain.angle_to_wall = 0
Brain.state = "stopped_no_wall"
Brain.used_adjust = False
# oher values accessed but not updated throughout
IDEAL_DIST = 0.25
DIST_GIVE = 0.1
FRONT = (1, 0, 7)
LEFT = (3, 2, 1)

# @@---- Status brain: updates RU, resets brain.state, updates angle to left wall ---- @@ #

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

class StatBrain(Frequency_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru, 500)

    def fire(self):  # updates state of the wall_follower
        self.ru.bulk_update()
        Brain.angle_to_wall = wall_angle(self.ru, LEFT)
        Brain.used_adjust = False
        if self.ru.cmd_feedback:
            if self.ru.cmd_feedback["code"] != "APPROVED":
                if self.ru.lidar['data'][2] < IDEAL_DIST + DIST_GIVE:
                    Brain.state = "stopped_with_wall"
                else:
                    Brain.state = "stopped_no_wall"
                print("stopped")

stat_brain = StatBrain()

def wall_angle_test(lray, cray, rray):
    langle = math.radians(113)
    rangle = math.radians(67)
    cangle = math.radians(90)
    runs = [rray * math.cos(rangle) - lray * math.cos(langle), rray * math.cos(rangle) - cray * math.cos(cangle), cray * math.cos(cangle) - lray * math.cos(langle)]
    rises = [rray * math.sin(rangle) - lray * math.sin(langle), rray * math.sin(rangle) - cray * math.sin(cangle), cray * math.sin(cangle) - lray * math.sin(langle)]
    return [math.atan2(rise, run) * 180 / math.pi for rise, run in zip(rises, runs)]

# @@---- find wall ---- @@ #

class FindWallBrain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)
        self.active_state = "find_wall"


    def condition(self):
        try: 
            return self.ru.lidar['data'][0] > IDEAL_DIST
        except:
            return False

    def fire(self):
        cmd = {"cmd": "move", "duration": 10, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))

find_wall_brain = FindWallBrain()

# @@---- Front wall - turn to align with wall on left side ----@@ #

class FrontWallBrain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)
        self.active_state = "front_wall"

    def condition(self):
        try:
            return min([self.ru.lidar['data'][i] for i in [0, 1, 7]]) <= IDEAL_DIST
        except:
            return False

    def fire(self):  # back off the wall just a bit, then turn
        cmd = {"cmd": "move", "duration": 1, "speed": -0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        turn_amt = -90 + wall_angle(self.ru, FRONT)
        cmd = {"cmd": "rotate", "duration": 5, "speed": turn_amt/5}
        self.ru.change_key_value("Cmd", json.dumps(cmd))

front_wall_brain = FrontWallBrain()

# @@---- Follow wall ----@@ #

class FollowWallBrain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)
        self.active_state = "follow_wall"

    def condition(self):
        try:
            return self.ru.lidar['data'][2] <= IDEAL_DIST + DIST_GIVE and self.ru.lidar['data'][0] > IDEAL_DIST
        except:
            return False

    def fire(self):
        if Brain.state == "find_wall":
            cmd = {"cmd": "stop"}
            self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "move", "duration": 10, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))


follow_wall_brain = FollowWallBrain()
# @@---- Distance from wall adjustment ----@@ #

class WallAdjustBrain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)
        self.active_state = "follow_adjust"

    def condition(self):
        dist_to_wall = min(self.ru.lidar['data'][1:4])
        return (abs(Brain.angle_to_wall) > 20 or dist_to_wall < IDEAL_DIST - DIST_GIVE or dist_to_wall > IDEAL_DIST + DIST_GIVE) and not Brain.used_adjust

    def fire(self):
        Brain.used_adjust = True
        # stop wall follow
        cmd = {"cmd": "stop"}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        # calculate angle to drive to ideal dist
        dist_to_wall = min(self.ru.lidar['data'][1:4])
        dist_error = -IDEAL_DIST + dist_to_wall  # the max value of this is about DIST_GIVE
        dist_comp = math.asin(dist_error/0.15) * 180 / math.pi 
        cmd = {"cmd": "rotate", "duration": 5, "speed": (Brain.angle_to_wall + dist_comp)/5} # don't go parrallel to the wall, over/under compensate based on dist_error to get closer to IDEAL_DIST
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        # drive to idealdist from wall
        cmd = {"cmd": "move", "duration": 1.5, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        # re-center @ ideal dist
        cmd = {"cmd": "rotate", "duration": 5, "speed": -dist_comp/5}
        self.ru.change_key_value("Cmd", json.dumps(cmd))

follow_adjust_brain = WallAdjustBrain()

# @@---- Left wall lost/ dropped off ---@@ #

class LostWallBrain(Conditional_Brain):
    def __init__(self):
        super().__init__(wallfollow_ru)
        self.active_state = "wall_dropoff"

    def condition(self):
        try:
            return self.ru.lidar['data'][1] > IDEAL_DIST + DIST_GIVE * 2 and self.ru.lidar['data'][2] < IDEAL_DIST + DIST_GIVE
        except:
            return False

    def fire(self):  # go forward a little, turn left, fo forward a little, repeat - try to right turn around a corner, u-turn or 90 degrees
        cmd = {"cmd": "stop"}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "move", "duration": 2.5, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "rotate", "duration": 5, "speed": 18}  # 90 degree left turn
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "move", "duration": 5, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "rotate", "duration": 5, "speed": 18}  # 90 degree left turn
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        cmd = {"cmd": "move", "duration": 2.5, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))

wall_dropoff_brain = LostWallBrain()

# @@---- else brain ----@@ #

def nothing(self):
    print("Nothing worked")

else_brain = Else_Brain(wallfollow_ru, nothing)

# priority of brains is dictated by order they are passed into the script
r = Script("Nate", (10,10), (5,5), brains=[wall_dropoff_brain, follow_adjust_brain, front_wall_brain, follow_wall_brain, find_wall_brain, stat_brain, else_brain])
r.run()

"""
print(wall_angle_test(7, 10))
print(wall_angle_test(10, 7))
print(wall_angle_test(10, 10))
print(wall_angle_test(8.9, 2.2))
"""