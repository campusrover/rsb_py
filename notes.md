# RBX1 Github Repo

## Basic Test (already done in tb3-docker)
* install Arbotix Simulator
`rosdep update`
`sudo apt-get -y install ros-melodic-arbotix-*`
`sudo apt-get -y install ros-melodic-turtlebot*`
`rospack profile`

* Test the Simulator (one of these two, for different simulated robots)

`roslaunch rbx1_bringup fake_turtlebot.launch`
`roslaunch rbx1_bringup fake_pi_robot.launch`
fake
* Run rviz to see
`rosrun rviz rviz -d `rospack find rbx1_nav`/sim.rviz`

## Navigation

* Launch the simulator first
`roslaunch rbx1_bringup fake_turtlebot.launch`

* Now move base with a blank map
`roslaunch rbx1_nav fake_move_base_blank_map.launch`

* Launch rviz
`rosrun rviz rviz -d `rospack find rbx1_nav`/nav.rviz`

* Manually give it a goal
`rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
'{ header: { frame_id: "map" }, pose: { position: { x: 1.0, y: 0, z:
0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } } }`
* Also can give it a goal through rviz!

## Navigation with an obstacle

* Start over. Kill Everything and then:

* Run the robot simulator
`roslaunch rbx1_bringup fake_turtlebot.launch`

* Run the map server with obstacles:
`roslaunch rbx1_nav fake_move_base_map_with_obstacles.launch`

* Run Rviz to visualize
`rosrun rviz rviz -d `rospack find rbx1_nav`/nav_obstacles.rviz`

