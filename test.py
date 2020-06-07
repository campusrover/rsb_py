from rsb.script import Script


class MyRobot(Script):
    def setup(self):
        self.namespace("pito")
        self.worldsize((10, 10))

    def step(self):
        print("run")

r = MyRobot()
r.run()