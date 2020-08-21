# This file presents two ways to acheive roomba functionality using rsb script
# first is lines 10-51
# second is lines 55-104

from rsb.script import Script, Conditional_Brain, Frequency_Brain, Brain
from rsb.redisutil import RedisUtil
import json, random
"""
# Method #1: externally define functions, bind with constructors
roomba_ru = RedisUtil("Nate", keys={"Cmd": "list", "Lidar": "string", "Cmd_Feedback": "list"})
has_task = False

def gocond(self):
    try:
        return self.ru.lidar["data"][0] > 0.4 and not has_task
    except:
        return False

def go(self):
    global has_task
    cmd = {"cmd": "move", "duration": 10, "speed": 0.1}
    self.ru.change_key_value("Cmd", json.dumps(cmd))
    has_task = True

def turncond(self):
    try:
        return self.ru.lidar["data"][0] <= 0.4 and not has_task
    except:
        return False

def turn(self):
    global has_task
    cmd = {"cmd": "rotate", "duration": 10, "speed": 12}  # need to remember that rotate speed takes deg/s #* (random.sample([1,-1], 1)[0])
    self.ru.change_key_value("Cmd", json.dumps(cmd))
    has_task = True

def status(self):
    global has_task
    self.ru.bulk_update()
    #print(self.ru.__dict__)
    print(self.next_fire_time)
    if self.ru.cmd_feedback:
        if self.ru.cmd_feedback["code"] != "APPROVED":
            has_task = False

gobrain = Conditional_Brain(roomba_ru, go, gocond)  # this brain sends a move forward command if there is open space ahead (lidar[0])
turnbrain = Conditional_Brain(roomba_ru, turn, turncond)  # this brain turns if gobrain can't go
statbrain = Frequency_Brain(roomba_ru, 1000, status)  # this brain manages the other two, updates the shared redisUtil @1hz, and cleans the has_task global var

r = Script("Nate", (10,10), (5,5), brains=[gobrain, turnbrain, statbrain])
r.run()
"""
"""
# Method #2: Use subclasses
roomba_ru = RedisUtil("Nate", keys={"Cmd": "list", "Lidar": "string", "Cmd_Feedback": "list"})
has_task = False

class GoBrain(Conditional_Brain):
    def __init__(self, ru):
        super().__init__(ru)
    
    def condition(self):  # same as gocond()
        try:
            return self.ru.lidar["data"][0] > 0.4 and not has_task
        except:
            return False

    def fire(self):  # same as go()
        global has_task
        cmd = {"cmd": "move", "duration": 10, "speed": 0.1}
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        has_task = True

class TurnBrain(Conditional_Brain):
    def __init__(self, ru):
        super().__init__(ru)

    def condition(self):  # same as turncond()
        try:
            return self.ru.lidar["data"][0] <= 0.4 and not has_task
        except:
            return False

    def fire(self):  # same as turn()
        global has_task
        cmd = {"cmd": "rotate", "duration": 10, "speed": 12}  # need to remember that rotate speed takes deg/s #* (random.sample([1,-1], 1)[0])
        self.ru.change_key_value("Cmd", json.dumps(cmd))
        has_task = True

class StatusBrain(Frequency_Brain):
    def __init__(self, ru, ms):
        super().__init__(ru, ms)

    def fire(self):  # Same as status()
        global has_task
        self.ru.bulk_update()
        #print(self.ru.__dict__)
        print(self.next_fire_time)
        if self.ru.cmd_feedback:
            if self.ru.cmd_feedback["code"] != "APPROVED":
                has_task = False

r = Script("Nate", (10,10), (5,5), brains=[GoBrain(roomba_ru), TurnBrain(roomba_ru), StatusBrain(roomba_ru, 1000)])
r.run()
"""

# Method #3: using new state tools
# with new state tools, conditional brains don't have to worry about state outside of defining their active_state in the constructor
roomba_ru = RedisUtil("Nate", keys={"Cmd": "list", "Lidar": "string", "Cmd_Feedback": "list"})
Brain.state_tree = {"going": ["stopped"], "stopped": ["going", "turning"], "turning": ["stopped"]}

def gocond(self):
    try:
        return self.ru.lidar["data"][0] > 0.4
    except:
        return False

def go(self):
    cmd = {"cmd": "move", "duration": 10, "speed": 0.1}
    self.ru.change_key_value("Cmd", json.dumps(cmd))
    print("going")

def turncond(self):
    try:
        return self.ru.lidar["data"][0] <= 0.4
    except:
        return False

def turn(self):
    cmd = {"cmd": "rotate", "duration": 10, "speed": 12}  # need to remember that rotate speed takes deg/s #* (random.sample([1,-1], 1)[0])
    self.ru.change_key_value("Cmd", json.dumps(cmd))
    print("turning")

def status(self):
    self.ru.bulk_update()
    #print(self.ru.__dict__)
    print(self.next_fire_time)
    if self.ru.cmd_feedback:
        if self.ru.cmd_feedback["code"] != "APPROVED":
            Brain.state = "stopped"

gobrain = Conditional_Brain(roomba_ru, go, gocond, "going")  # this brain sends a move forward command if there is open space ahead (lidar[0])
turnbrain = Conditional_Brain(roomba_ru, turn, turncond, "turning")  # this brain turns if gobrain can't go
statbrain = Frequency_Brain(roomba_ru, 1000, status)  # this brain manages the other two, updates the shared redisUtil @1hz, and cleans the has_task global var

r = Script("Nate", (10,10), (5,5), brains=[gobrain, turnbrain, statbrain])
r.run()