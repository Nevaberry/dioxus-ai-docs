---
name: nvidia-isaac-sim-knowledge-patch
description: NVIDIA Isaac Sim
version: "6.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# NVIDIA Isaac Sim

Use this skill when upgrading Isaac Sim applications, extensions, USD stages,
OmniGraph graphs, sensors, Replicator workflows, or ROS 2 integrations. Start
with the breaking-change checks below, then open the topic reference that
matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/extensions-and-core-apis.md](references/extensions-and-core-apis.md) | Extension renames and removals, Kit compatibility, Core APIs, templates |
| [references/rtx-sensors-and-rendering.md](references/rtx-sensors-and-rendering.md) | Camera, lidar, radar, acoustic, annotators, render timing, sensor corrections |
| [references/ros2-integration.md](references/ros2-integration.md) | Bridge libraries, Simulation Control, publisher graphs, workspaces, DDS |
| [references/physics-and-robotics.md](references/physics-and-robotics.md) | PhysX and Newton, articulations, joints, deformables, robot assets and tools |
| [references/replicator-and-deployment.md](references/replicator-and-deployment.md) | Replicator Agent, synthetic data, containers, artifacts, offline and Nucleus |

## Upgrade triage

Before changing code:

1. Identify the installed Isaac Sim and Kit versions.
2. Inventory extension dependencies, Python imports, settings paths, USD prim
   types, asset paths, OmniGraph node types, and ROS 2 graph connections.
3. Treat an extension rename as a deliberate migration. Some old extensions
   split into several replacements, while others have no direct replacement.
4. Remove deprecated dependencies before crossing a major-version boundary.
5. Rebaseline tests around corrected physics, sensor transforms, timestamps,
   camera intrinsics, and ROS 2 message behavior.
6. Validate packaged artifacts and platform defaults separately from API
   migrations.

## Highest-priority API migrations

### Core and project scaffolding

For 6.0 work, move from `isaacsim.core.api`, `isaacsim.core.prims`, and
`isaacsim.core.utils` to `isaacsim.core.experimental.*` and
`isaacsim.core.simulation_manager`.

Replace `isaacsim.examples.extension` scaffolding with:

```bash
./repo.sh template new
```

The experimental Core interfaces are also the engine-neutral route for
physics data when selecting PhysX or Newton.

### RTX camera construction and acquisition

The 6.0 experimental camera API separates USD authoring from acquisition:

```python
from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera

sensor = CameraSensor(
    RtxCamera(
        "/World/Camera",
        tick_rate=30.0,
        translations=[[0.0, 0.0, 1.0]],
    ),
    resolution=(640, 480),
    annotators=["rgb"],
)
data, info = sensor.get_data("rgb")
```

Use `tick_rate`, plural N×3/N×4 transform arrays, explicit annotators, and
`get_data()`. Do not preserve command-based camera construction,
`frequency`/`dt`, or the unused `name` argument.

Replace:

- `CameraView(prim_paths_expr=..., output_annotators=...)` with
  `TiledCameraSensor(paths=[...], annotators=[...])`.
- Regex prim selection with an enumerated `paths` list.
- Tiled implicit output with `get_data("rgb", tiled=True)`.
- `SingleViewDepthSensor` with
  `SingleViewDepthCameraSensor(RtxCamera.create(...), annotators=[...])`.
- Polynomial distortion setters with native OpenCV fisheye or pinhole USD
  schemas.

### RTX lidar, radar, and acoustic construction

Author prims with `Lidar.create()`, `Radar.create()`, or `Acoustic.create()`,
then wrap them in `LidarSensor`, `RadarSensor`, or `AcousticSensor`:

```python
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor

sensor = LidarSensor(
    Lidar.create(
        "/World/Lidar",
        config="Example_Rotary",
        orientations=[[1.0, 0.0, 0.0, 0.0]],
    ),
    annotators=["generic-model-output"],
)
data, info = sensor.get_data("generic-model-output")
```

Use explicit annotator acquisition and parse generic model output with
`parse_generic_model_output_data`. Use `parse_stable_id_map_data` and
`parse_object_ids` for stable IDs. Timeline control replaces per-sensor
initialize, pause, and resume methods.

Keep these exceptions in view:

- IDS has no experimental create-command replacement; use the deprecated
  command or author USD directly.
- The active point-cloud annotator remains in
  `isaacsim.sensors.rtx.nodes`.
- Radar Doppler requires Motion BVH.
- Auxiliary levels use
  `_replicator:rendervar:GenericModelOutput:channels`.
- Mixed auxiliary levels on attached render products are last-attach-wins.

### Version-sensitive RTX point-cloud nodes

Do not choose a lidar point-cloud node from memory:

- In 5.0, legacy point-cloud and scan-buffer nodes moved to
  `OgnIsaacExtractRTXSensorPointCloud`.
- In 5.1, per-frame output from `OgnIsaacCreateRTXLidarScanBuffer` replaced
  that 5.0 path.
- In 6.0, use the experimental sensor API where applicable, while honoring
  the point-cloud annotator exception above.

Also attach every required lidar output explicitly; implicit annotator or
writer attachment is no longer a safe assumption.

## ROS 2 graph migration

Publisher nodes no longer perform direct USD lookup for forward-compatible
graphs.

For transforms, add `Isaac Compute Transform Tree` from
`isaacsim.core.nodes`, set `targetPrims` and optionally `parentPrim`, then
connect:

- `execOut`
- `parentFrames`
- `childFrames`
- `translations`
- `orientations`

to the corresponding publisher inputs. An articulation-root target expands
to its complete link tree.

For joint states, add `Isaac Read Joint State` from
`isaacsim.sensors.physics.nodes`, set `prim` to the articulation root, and
wire `execOut`, joint names, positions, velocities, efforts, DOF types,
stage meters per unit, and sensor time to the publisher.

For 6.0 Publish TF and Odometry graphs, feed precomputed transforms from
`IsaacComputeTransformTree`; direct `targetPrims` is deprecated.

## Replicator Agent migration

Treat Replicator Agent 1.x as an architectural replacement:

| 0.x surface | 1.x surface |
| --- | --- |
| `scene.asset_path` | Required `environment.base_stage_asset_path` |
| `simulation_length` in 30-FPS frames | `simulation_duration` in seconds |
| `sdg_scheduler.py` | `actor_sdg.py` |
| `omni.anim.people` | `omni.anim.behavior.core` |
| Command text and JSON transition maps | Inline YAML `routines` and `triggers` |
| Top-level response, event, incident | Actor-group triggers |
| Character `filters` | Removed |

The environment path may be asset-relative, a URL, or absolute. Select robot
onboard cameras with `camera_prim_paths`, and validate the Pydantic v2
configuration before long generation jobs.

## Physics and robotics quick choices

- Use floating-base inverse dynamics for gravity/Coriolis compensation,
  mass matrices, center of mass, and centroidal momentum calculations.
- CPU signed-distance-field triangle-mesh collision is supported for small
  scenes.
- Use compliant mimic-joint constraints when manipulation stability benefits.
- Consider solve-articulation-contacts-last to reduce gripper penetration
  when tuning is imperfect.
- Use `PhysxJointAxisAPI` for Stribeck-like friction and
  `PhysxDrivePerformanceEnvelopeAPI` for speed-dependent motor torque.
- Enable the beta deformable schema in Physics preferences and restart
  before using it.
- When Newton is active, expect importers, policies, ROS 2, and tensor-backed
  graph nodes to select registered Newton-compatible paths.

## Runtime and deployment defaults

- Multitick rendering can schedule camera and RTX lidar rates and offsets
  from physics simulation time.
- On 5.1, the ROS 2 bridge `system_default` selects internal Humble on Ubuntu
  22.04 and internal Jazzy on Ubuntu 24.04.
- On 6.0 Jazzy workspaces, `use_internal_libs` defaults to false; Humble
  retains true.
- An empty `dds_type` preserves `RMW_IMPLEMENTATION`; an explicit value
  selects Fast DDS, Cyclone DDS, or Zenoh.
- Containers run rootless by default in 5.1, and live streaming is unsupported
  on `aarch64` there.
- For the complete offline asset pack, acquire, verify, combine, and extract
  all five parts.
- The WebRTC desktop client is optional for headless Docker Compose web-viewer
  deployments.

## Verification checklist

- Run the Compatibility Checker for the installation modality.
- Confirm every extension and import resolves without a compatibility alias.
- Inspect authored prim types and moved asset paths.
- Verify annotators and writers are attached explicitly.
- Recheck lidar timestamps, transforms, motion settings, and auxiliary levels.
- Compare camera intrinsics and distortion schemas with downstream consumers.
- Exercise ROS 2 world, spawn, transform, joint-state, and time semantics.
- Rebaseline physics assertions affected by corrected simulation results.
- Validate Replicator configurations before expensive runs.
- Test container user, architecture, ROS library, DDS, streaming, and offline
  asset assumptions on the actual deployment platform.
