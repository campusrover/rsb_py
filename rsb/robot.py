from math import degrees

class Robot(object):
    def __init__(self, locx, locy, orientation, lidar, image):
        self.lidar = lidar
        self.location = (locx, locy)
        self.orientation = orientation
        self.lidar_beams = lidar
        self.image = image

    def recompute(self, location, orientation):
        self.location = location
        self.orientation = orientation

    def draw(self):
        pass
