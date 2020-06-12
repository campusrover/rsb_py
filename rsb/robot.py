from math import degrees

class Robot(object):
    def __init__(self, robot_info):
        self.robot_info = robot_info
        self.location = (robot_info["location"][0], robot_info["location"][1])
        self.orientation = degrees(robot_info["orientation"][2])