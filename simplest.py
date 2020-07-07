# This is the simplest possible script using the first model of rsbscript. It should work and we will be building on it.

from rsb.script import Script
class MyScript(Script):
    def setup(self):
        pass

    def step(self):
        pass
    
r = MyScript("pito2", (10,10), (5,5))
r.run()