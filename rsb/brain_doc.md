# rsb_script and Brains

this document serves as a quick start guide to anyone who picks up this project

## RSB Script

an rsb script is an instance that creates a gui to visualize robot movement, sensors and surroundings that are provided over redis from robot_services. It is programmable by passing in a set of brains, specialized objects that each do a specific task or part fo a task. 

## the Brain Manager

At a high level, the brain manager works very simply. Each loop, the brain manager:

1. pops all frequency brains off the frequency brain queue that have waited long enough since their last fire. these brains get a chance to fire, then have their next fire time adjusted and are reinserted into the frequency brain queue
2. gives each of the conditiona brains a chance to fire
3. if none of the conditional brains fire and an else brain is present, then the else brain gets a chance to fire

## types of brains

### the brain parent class

Brain classes must be initialized with a Redis_util object. optionally, they can be initiallized with a function fn passed as the second arguement, and this will set that instance's fire() method to fn

Upon initialization, brains are assigned a random uuid int (univeral unique identifier). This is useful for subsumption control mapping. 

the Brain class has a number of static attributes:

1. `move_state`: should be set to `redis_util.cmd_feedback['code']`. move state is used to determine whether additional movement commands should be accepted based on whether the robot is currently moving based on the reporting of the robot_services cmd_feedback channel from movement_bridge. 
2. `control_map`: this is a dict that should brain uuid's to lists/arrays of othr brain uuids. this structure is meant to create a subsumption control structure, where if brain `b` has it's uuid under the key of brain `a`'s uuid, then brain `b` can subsume control from brain `a` if brain `a` is in control. 
3. `controller`: the uuid of the brain that currently has control. -1 if no brain is in control. 
4. `command_queue`: a list of commands to be sent to the `Cmd` redis key
5. `curr_cmd_timeout`: the time, in seconds, when the most recent command sent to redis is expected to complete. this attribute and `move_state` both are used to gatekeep the command queue from commands being spammed from the brain in control

the brain class also includes a number of methods to handle control acquisition and move command handling. 

**fire() is not defined in the Brain class! it is assumed that is is either defined in a subclass or passed to the constructor!**

### Frequency Brains

Frequency brains accept an additional constructor parameter `ms`, which represents the number of milliseconds between each time the brain should fire. there is also an option kwarg `requires_control`, which should indicate whether the instance of the brain requires to be the brain in control (e.g. `Brain.controller`) in order to fire

`fire()` is encapsulated with `ffire()`, which returns a boolean whether the the internal `fire()` was actually able to get called

### Conditional brains

Conditional brains will only fire if their condition is met **AND** they are in control (unlike frequency brains which only require control is specified)

like `ffire()`, conditional brains wrap their `fire()` method in `cfire()` with the same boolean output.

### Conditional and Frequency brain similarities:

* both `cfire()` and `ffire()` will try to seize control at the beginning of their call
* seize control will check both Brain.control_map **AND** the `Brain.control_cond()` method, which returns true unless it is overridden in a subclass
* at the end of each ffire and cfire, the brain.command_queue is emptied into redis

## Next Steps

1. the current brain/control strucutre works fine for simple applications such as roomba, but fails at more complex applications like wall following. I see three depths that could be delved to to possible ammend this 9going deeper is better)
    1. Depth 1: the logic of the wall follower script (wallfollow2.py) is bad and could be fixed
    2. Depth 2: the brain control structure is not robust enough and should be flushed out mroe
    3. Depth 3: the movement_bridge of robot services is not robust enough, and should provide more movement options
2. one notable issue is if two brains are able to subsume each other, then they will constantly loop and subsume each other if one takes control and both have simialr conditions. 
3. the command queue gatekeeping logic could be refactored to better allow for multiple commands to be passed, and for overriding commaneds to be more refined. 
4. perhaps other types of brains could be derived
5. in theory, brains are modular and they can be plugged + played in any application - e.g. write a 'wall following" brain that just does the action if a wall is present to the side and nothing else
