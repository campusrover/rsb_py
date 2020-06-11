from rsb.script import Script

class MyScript(Script):
    def setup(self):
        pass

    def step(self):
        print("step")

r = MyScript("pito", (10,10), (5,5))
r.run()