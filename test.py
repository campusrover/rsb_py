from rsb.script import Script
class MyScript(Script):
    def setup(self):
        pass

    def step(self):
        pass
    
r = MyScript("pito", (8,8), (4,4))
r.run()