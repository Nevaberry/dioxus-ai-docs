# Manipulation, teleoperation, and robots

Use this reference for Isaac for Manipulation workflows, control dependencies,
cuMotion, XR teleoperation, robot integrations, and Unitree G1. Runtime failure
modes are collected in [Troubleshooting](troubleshooting.md).

## Isaac for Manipulation naming and workflows (4.0.0)

Isaac Manipulator is now named Isaac for Manipulation. The package remains
`isaac_manipulator`; do not rename package references merely because the
product and workflow label changed.

The reference workflows include:

- Gear assembly using a contact-rich insertion policy.
- Multi-object pick-and-place orchestrated by behavior trees.

The bundled control dependencies are not identical to their upstream package
lines. `topic_based_ros2_control` is based on a forked pull request. The `ur`
package is forked from Universal Robots ROS 2 Driver and Universal Robots
Client Library. Compare against those forks before applying upstream API
assumptions or patches.

## UR10e gear-assembly tutorial (4.1.0)

`isaac_manipulator` adds a sim-to-real gear-assembly reach-policy tutorial for
UR10e. Validate both the simulation policy path and physical robot setup; the
workflow crosses simulator, controller, perception, and robot boundaries.

## cuMotion 1.1 and controller ordering (4.5.0)

`isaac_ros_cumotion` updates to cuMotion 1.1.0 and adds or improves:

- Self-consistent ESDF planning.
- AABB clearing for drop-pose planning.
- Controller `PoseArray` hand order aligned with Isaac ROS Teleop.

Update custom publishers, recorded messages, and consumers to the revised hand
order. Treat the teleop and cuMotion change as one interface migration.

## Docker-free XR teleoperation (4.5.0)

`isaac_ros_teleop` can run CloudXR without Docker and adds:

- Meta Quest 3 support.
- Raw controller-data publication.
- Configurable XR pose transforms.
- RViz visualization.
- Revised `PoseArray` hand order shared with the cuMotion controller.

Check frame transforms and hand ordering together when controller motion is
mirrored, swapped, or offset.

## Robot and workflow integrations (4.5.0)

`isaac_ros_manipulation` adds Flexiv Rizon support and a Bring Your Own Robot
integration guide. The release also updates Flexiv, Universal Robots,
static-planning-scene, and cloud pick-and-place workflows.

When carrying forward a local robot integration, rebase the robot adapter,
planning scene, and orchestration together rather than copying only the new
launch entry point.

## Unitree G1 physical-AI workflows (4.5.0)

`isaac_ros_physical_ai` adds:

- Unitree G1 data-recording workflows.
- GR00T deployment workflows.
- G1 teleoperation for simulation and hardware.
- Firmware 1.5.1 acknowledgement handling.

`isaac_ros_robots` changes G1 bridge and bringup defaults, topic and frame
names, controller configuration, GR00T launch behavior, and acknowledgement
checks. Audit all of these interfaces when upgrading an existing G1 workspace;
changing only the launch file can leave bridge, controller, or acknowledgement
assumptions mismatched.

## Unitree G1 cloud control (4.6.0)

`isaac_ros_physical_ai` adds G1 cloud control on hardware and in Isaac Sim.
The supported mission types are intentionally asymmetric:

- Robot hardware: `isaac_ros_cloud_control` supports navigation and GR00T
  manipulation missions.
- Isaac Sim: navigation-only cloud control.
- Isaac Sim 6.0: `isaac_ros_deploy` can deploy G1 AGILE locomotion policies.

Keep cloud task handling distinct from robot bridge and policy deployment.
The VDA5050 and scene-recorder package roles are described in
[NITROS, data, compression, and cloud control](nitros-data-and-compression.md).

## Integration checklist

1. Map the product name to the actual package names in the workspace.
2. Identify fork-specific control APIs before replacing dependencies.
3. Validate controller, teleop, and recorded `PoseArray` hand ordering.
4. Recheck XR pose transforms and frames with raw controller publication.
5. Update robot bridge defaults, topics, frames, controller configuration,
   launch behavior, and acknowledgements as one migration.
6. Test action cancellation and shutdown before running unattended missions.
7. Monitor hand temperatures during sustained hardware teleoperation.
8. Test hardware and simulation cloud missions separately because their
   supported action surfaces differ.
