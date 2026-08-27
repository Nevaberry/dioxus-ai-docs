# ROS 2 integration

## Configure bridge libraries and distributions

The ROS 2 bridge supports Jazzy in 5.0. Enabling the bridge loads its internal
ROS 2 libraries automatically (`5.0.0`).

In 5.1, internal Humble and Jazzy distributions include common interfaces,
`tf2_ros`, `sensor_msgs_py`, and Simulation Interfaces 1.1.0. The bridge
library setting defaults to `system_default`: Ubuntu 22.04 selects internal
Humble and Ubuntu 24.04 selects internal Jazzy (`5.1.0`).

For 6.0 workspaces, Jazzy defaults `use_internal_libs` to false, while Humble
retains true. `run_isaacsim.py` no longer forces a DDS implementation. Set
`dds_type` explicitly for Fast DDS, Cyclone DDS, or Zenoh; leave it empty to
preserve `RMW_IMPLEMENTATION` (`6.0.0`).

## Build scalable namespaces and correct message consumers

ROS 2 assets can generate namespaces automatically for scalable multi-robot
setups as of 4.5; account for the `NameOverride` attribute when defining
names (`4.5.0`).

In 5.1 `CameraInfo.fy` is no longer forced to equal `fx`, and timestamps are
no longer duplicated or omitted. Remove consumer and test workarounds for
those old semantics (`5.1.0`).

## Migrate transform publishers to typed source data

`ROS2 Publish Transform Tree` no longer owns direct USD lookup in the 6.0
migration. Existing graphs still load during the deprecation window, but
forward-compatible graphs add `Isaac Compute Transform Tree` from
`isaacsim.core.nodes` (`6.0.0-migration`).

Set `targetPrims` and optionally `parentPrim`, then connect:

| Source output | Publisher input |
| --- | --- |
| `execOut` | Corresponding execution input |
| `parentFrames` | `parentFrames` |
| `childFrames` | `childFrames` |
| `translations` | `translations` |
| `orientations` | `orientations` |

An articulation-root target automatically expands to its full link tree.
Topic, namespace, queue, frame, and other unaffected inputs retain their
existing wiring.

In the 6.0 ROS 2 integration, Publish TF and Odometry likewise consume
precomputed transforms from `IsaacComputeTransformTree`; their direct
`targetPrims` input is deprecated (`6.0.0`).

## Migrate joint-state publishers to typed source data

`ROS2 Publish Joint State` also relinquishes direct USD lookup
(`6.0.0-migration`). Add `Isaac Read Joint State` from
`isaacsim.sensors.physics.nodes`, and set its `prim` to the articulation root.

Connect:

| Source output | Publisher input |
| --- | --- |
| `execOut` | `execIn` |
| `jointNames` | `jointNames` |
| `jointPositions` | `jointPositions` |
| `jointVelocities` | `jointVelocities` |
| `jointEfforts` | `jointEfforts` |
| `jointDofTypes` | `jointDofTypes` |
| `stageMetersPerUnit` | `stageMetersPerUnit` |
| `sensorTime` | `sensorTime` |

Topic, namespace, queue, frame, and other unaffected publisher inputs retain
their existing wiring.

## Use Simulation Control

`isaacsim.ros2.sim_control` implements automated simulation control through
the ROS 2 Simulation Interfaces standard as of 5.0 (`5.0.0`).

In 5.1 it supports world operations through `GetAvailableWorlds`,
`GetCurrentWorld`, `LoadWorld`, and `UnloadWorld`. Enable Simulation Control
at startup with (`5.1.0`):

```text
--isaac/startup/ros_sim_control_extension=True
```

In 6.0, Simulation Control adds services for entity bounds, entity spawning,
and discovering spawnable entities (`6.0.0`).

## Update ROS-facing extensions and workflows

The 6.0 bridge uses `isaacsim.core.experimental.*` and
`isaacsim.sensors.experimental.{rtx,physics}` (`6.0.0`).

Replace deprecated `URDFImportFromROS2Node` with `RobotDefinitionReader` and
`URDFImporter`. ROS 2 can also publish RTX radar as `PointCloud2`
(`6.0.0`).

ROS 2 workflows support Windows through Pixi and Isaac Sim ROS Workspaces.
The workspace package `isaacsim` is renamed to `isaacsim_bringup`.
`isaacsim`, `cmdvel_to_ackermann`, `h1_fullbody_controller`, and
`isaac_moveit` move from `ament_cmake` to `ament_python` (`6.0.0`).
