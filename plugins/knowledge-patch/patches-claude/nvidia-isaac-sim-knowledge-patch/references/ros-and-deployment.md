# ROS 2 and Deployment

## Namespaces and bridge changes

Batch `4.5.0` lets ROS 2 assets generate namespaces automatically for
scalable multi-robot setups and adds guidance for the `NameOverride`
attribute.

Batch `5.0.0` adds ROS 2 Jazzy support. Enabling the bridge now loads its
internal ROS 2 libraries automatically. The new
`isaacsim.ros2.sim_control` extension automates simulation through the ROS 2
Simulation Interfaces standard. ROS 1 support is removed, and 4.5
compatibility aliases must be replaced with supported APIs and namespaces.

## Simulation Control and bundled libraries

Batch `5.1.0` adds world operations to Simulation Interfaces:

- `GetAvailableWorlds`
- `GetCurrentWorld`
- `LoadWorld`
- `UnloadWorld`

Enable Simulation Control at startup with:

```text
--isaac/startup/ros_sim_control_extension=True
```

The bundled Humble and Jazzy distributions include common interfaces,
`tf2_ros`, `sensor_msgs_py`, and Simulation Interfaces 1.1.0.

The bridge-library setting defaults to `system_default`. On Ubuntu 22.04 it
automatically selects internal Humble; on Ubuntu 24.04 it selects internal
Jazzy.

The release corrects ROS message semantics: `CameraInfo.fy` is no longer
forced to equal `fx`, and timestamps are no longer duplicated or omitted.
Remove consumer and test workarounds for the old output.

## Publisher source-node migration

Batch `6.0.0-migration` deprecates direct USD lookup in `ROS2 Publish
Transform Tree` and `ROS2 Publish Joint State`. Existing graphs still load
during the deprecation window, but new graphs should pass typed data from
source nodes.

For transforms:

1. Add `Isaac Compute Transform Tree` from `isaacsim.core.nodes`.
2. Set `targetPrims` and optionally `parentPrim`.
3. Wire the outputs to the corresponding publisher inputs.

| Source output | Publisher input |
| --- | --- |
| `execOut` | `execIn` |
| `parentFrames` | `parentFrames` |
| `childFrames` | `childFrames` |
| `translations` | `translations` |
| `orientations` | `orientations` |

An articulation-root target automatically expands to its full link tree.

For joint states:

1. Add `Isaac Read Joint State` from
   `isaacsim.sensors.physics.nodes`.
2. Set `prim` to the articulation root.
3. Connect every typed output to its corresponding publisher input.

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

Topic, namespace, queue, frame, and other unaffected inputs keep their
existing wiring.

## ROS 2 APIs in 6.0

Batch `6.0.0` moves the bridge to
`isaacsim.core.experimental.*` and
`isaacsim.sensors.experimental.{rtx,physics}`.

ROS 2 Publish TF and Odometry must consume transforms precomputed by
`IsaacComputeTransformTree`; their direct `targetPrims` input is deprecated.

Other ROS changes:

- `URDFImportFromROS2Node` is deprecated; use
  `RobotDefinitionReader` and `URDFImporter`.
- RTX radar can be published as `PointCloud2`.
- Simulation Control adds services for entity bounds, entity spawning, and
  discovery of spawnable entities.

## Workspace packages, libraries, and DDS

ROS 2 workflows support Windows through Pixi and Isaac Sim ROS Workspaces.
The workspace package `isaacsim` is renamed to `isaacsim_bringup`.

These packages change from `ament_cmake` to `ament_python`:

- `isaacsim`
- `cmdvel_to_ackermann`
- `h1_fullbody_controller`
- `isaac_moveit`

Jazzy workspaces default `use_internal_libs` to false; Humble retains true.
`run_isaacsim.py` no longer forces a DDS implementation. Set `dds_type` to
select Fast DDS, Cyclone DDS, or Zenoh. An empty value preserves
`RMW_IMPLEMENTATION`.

## Architecture and container behavior

Batch `5.1.0` adds DGX Spark support and multi-architecture Docker packaging.
Containers run as a rootless user by default. Live streaming remains
unsupported on `aarch64` in this release.

Check mounted-volume ownership and paths that previously assumed root. On
Arm, distinguish general application support from the live-streaming
restriction.

## Packaged artifacts and offline use

The 6.0 documentation line is distributed at patch level 6.0.1, while package
families version independently:

| Artifact | Version | Platforms or packaging |
| --- | --- | --- |
| Isaac Sim | 6.0.1 | Linux x86_64, Linux aarch64, Windows |
| Isaac Sim Assets | 6.0.1 | Complete pack split into five parts |
| WebRTC Streaming Client | 2.0.0 | Linux x86_64, Linux aarch64, Windows, macOS x86_64, macOS aarch64 |

For an offline complete asset pack, download, verify, combine, and extract all
five parts. For a headless deployment using the Docker Compose web viewer,
the WebRTC desktop client is optional.

## Launcher and Nucleus transition

Removal of Omniverse Launcher, Nucleus Workstation, and Nucleus Cache began
October 1, 2025. Use Enterprise Nucleus Server when Nucleus and Live Sync are
required. Replace Nucleus Cache with Hub Workstation Cache.
