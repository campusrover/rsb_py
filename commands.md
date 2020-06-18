* Idea: two keys, /cmd and /prog which take the same commands, but one is a queue that "executes" commands in order, while /cmd does them instantatuously. 

### Commands

* forward [cm] [sec] [m/sec]
* turn [angle] [sec] [deg/sec]
* circle [degrees] [radius/cm]

### movement

* Class: Robot
* .forward(cm, sec, m/sec) => robot
* .turn(angle, sec, deg/sec) => robot
* .circle(deg, radius) => robot
* .state() => {"location": [x,y], "direction": [deg]}

### Sensors

* Class: Robot
* .lidar(bearing) => None or distance to obstacle in meters


