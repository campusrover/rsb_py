# This doesn't work. It's a sketch of a different programming model.

from rsb.script import Script

class MyScript(Script):
    def setup(self):
        self.robot1 = Robot("The Best")
        flip = 1
        count = 0
        robot1.motion(flip * 0.2, 0)
        pass

    def step(self, seconds, minutes):
       if second % 5 is 0:
            flip = flip * -1
            robot1.motion(flip * 0.2, 0)
        

r = MyScript("pitox", (8,8), (4,4))
r.run()