# Manipulation and teleoperation

## Isaac for Manipulation naming and workflows

Isaac Manipulator is named Isaac for Manipulation as of 4.0.0. The
`isaac_manipulator` references include gear assembly with a contact-rich
insertion policy and multi-object pick-and-place orchestrated by behavior trees.

The bundled `topic_based_ros2_control` is based on a forked pull request. The
`ur` package is forked from Universal Robots ROS 2 Driver and Universal Robots
Client Library instead of directly using the upstream packages. Account for
those forks when debugging behavior or comparing dependency versions.

## UR10e gear-assembly policy

`isaac_manipulator` adds a sim-to-real gear-assembly reach-policy tutorial for
UR10e (4.1.0).

## cuMotion 1.1 and hand ordering

In 4.5.0, `isaac_ros_cumotion` updates to cuMotion 1.1.0, improves
self-consistent ESDF planning, and adds AABB clearing for drop-pose planning.
The controller's `PoseArray` hand order changes to match Isaac ROS Teleop.
Update all producers and consumers together.

## Docker-free XR teleoperation

`isaac_ros_teleop` can run CloudXR without Docker and supports Meta Quest 3,
raw controller-data publication, configurable XR pose transforms, and RViz
visualization (4.5.0). Its `PoseArray` hand order is revised together with the
cuMotion controller.

## Robot integrations

`isaac_ros_manipulation` adds Flexiv Rizon support and a Bring Your Own Robot
guide in 4.5.0. Its Flexiv, Universal Robots, static-planning-scene, and cloud
pick-and-place workflows are updated.

## Unitree G1 workflows and migration

In 4.5.0, `isaac_ros_physical_ai` adds Unitree G1 data-recording, GR00T
deployment, and simulation and hardware teleoperation workflows, including
firmware 1.5.1 acknowledgement handling.

`isaac_ros_robots` changes G1 bridge and bringup defaults, topic and frame
names, controller configuration, GR00T launch behavior, and acknowledgement
checks. Migrate older launch and consumer assumptions explicitly.

For real-hardware teleoperation, G1 hands can lower after several minutes due
to motor temperature limits.

## Unitree G1 cloud control

Isaac ROS 4.6.0 adds G1 cloud control for hardware and Isaac Sim. On hardware,
`isaac_ros_cloud_control` supports navigation and GR00T manipulation missions;
simulation supports navigation-only cloud control. `isaac_ros_deploy` can
deploy G1 AGILE locomotion policies to Isaac Sim 6.0.

