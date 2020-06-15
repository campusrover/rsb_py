from math import degrees

class Robot(object):
    # def __init__(self, locx, locy, oriention, lidar):
    #     self.odom = robot_info["odom"]
    #     self.lidar = robot_info["lidar"]
    #     self.location = (self.odom["location"][0], self.odom["location"][1])
    #     self.orientation = degrees(self.odom["orientation"][2])
    #     self.lidar_beams = self.lidar["data"]

    def __init__(self, locx, locy, orientation, lidar, image):
        self.lidar = lidar
        self.location = (locx, locy)
        self.orientation = orientation
        self.lidar_beams = lidar
        self.image = image