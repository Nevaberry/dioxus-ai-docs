---
name: nvidia-isaac-sim-knowledge-patch
description: NVIDIA Isaac Sim
version: 6.0.0
license: MIT
metadata:
  author: Nevaberry
---


# NVIDIA Isaac Sim Knowledge Patch

Load this skill when upgrading, extending, scripting, deploying, or debugging
NVIDIA Isaac Sim. Check the application's manifest, Kit build, enabled
extensions, authored USD schemas, and runtime behavior before applying
version-sensitive guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [extensions-and-core.md](references/extensions-and-core.md) | Extension namespace changes, removals, Kit boundaries, Core API and project templates |
| [physics-and-simulation.md](references/physics-and-simulation.md) | Articulation dynamics, colliders, PhysX schemas, corrected results, Newton and multitick rendering |
| [sensors-and-rendering.md](references/sensors-and-rendering.md) | Camera, lidar, radar, acoustic, RTX outputs, annotators, materials and sensor migration |
| [ros-and-deployment.md](references/ros-and-deployment.md) | ROS 2 graphs, bridge libraries, Simulation Control, containers, workspaces, artifacts and Nucleus |
| [synthetic-data-and-assets.md](references/synthetic-data-and-assets.md) | Replicator, Actor SDG, Replicator Agent, robot assets and data collection |

## Start with breaking changes

### Treat 6.0 as an API migration

- Replace deprecated Core imports with `isaacsim.core.experimental.*` and
  `isaacsim.core.simulation_manager`.
- Replace legacy camera and RTX sensor APIs with
  `isaacsim.sensors.experimental.rtx`; author a sensor prim separately from
  the runtime acquisition wrapper.
- Move ROS 2 transform and joint-state USD lookup into dedicated source nodes,
  then wire typed outputs into publisher nodes.
- Port Replicator Agent 0.x configuration as a new 1.x configuration. The old
  Python API, dependency set, JSON transitions, and internal imports are not
  compatible.
- Remove dependencies on extensions that were merely deprecated in earlier
  releases; they were scheduled for removal at the 6.0 boundary.
- Revalidate application extensions against Kit `110.1.1`.

### Do not mechanically rename 4.x extensions

The 4.5 namespace migration includes one-to-many replacements and removals.
Update dependency declarations, imports, settings paths, and code from the
mapping in
[extensions-and-core.md](references/extensions-and-core.md). In particular:

- `omni.isaac.wheeled_robots` split into implementation and examples
  extensions.
- `omni.replicator.isaac` split into domain-randomization, examples, and
  writers extensions.
- `omni.isaac.unit_converter` moved to the differently named
  `omni.usd.metrics_assembler`.
- Dynamic control, examples nodes, and the REPL had no direct 4.5 rename and
  were scheduled for removal.

### Track the RTX point-cloud node transition

The supported node changed in consecutive releases:

| Stage | Action |
| --- | --- |
| Moving to 5.0 | Replace legacy RTX point-cloud and scan-buffer nodes with `OgnIsaacExtractRTXSensorPointCloud`. |
| Moving to 5.1 | Replace `OgnIsaacExtractRTXSensorPointCloud` with per-frame output from `OgnIsaacCreateRTXLidarScanBuffer`. |
| Moving to 6.0 sensor APIs | Request explicit short-named annotators and acquire data with `get_data(...)`. |

Do not preserve a 5.0-only graph when targeting 5.1 or later.

## Migrate experimental RTX sensors

### Camera pattern

Author with `RtxCamera`, acquire with `CameraSensor`,
`TiledCameraSensor`, or `SingleViewDepthCameraSensor`, and request every output
explicitly:

```python
from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera

camera = CameraSensor(
    RtxCamera(
        "/World/Camera",
        tick_rate=30.0,
        translations=[[0.0, 0.0, 1.0]],
    ),
    resolution=(640, 480),
    annotators=["rgb"],
)
rgb, info = camera.get_data("rgb")
```

Apply these conversions:

- Use `tick_rate`, not `frequency` or `dt`.
- Pass translations and orientations as plural N×3 and N×4 arrays.
- Enumerate tiled-camera paths; a `prim_paths_expr` regular expression is no
  longer the input contract.
- Request tiled output with `get_data("rgb", tiled=True)`.
- Use native OpenCV fisheye or pinhole USD schemas instead of polynomial
  distortion setters.
- Drop the unused `name` argument.

### Lidar, radar, and acoustic pattern

Use `Lidar.create()`, `Radar.create()`, or `Acoustic.create()` to author the
prim and wrap it with the corresponding sensor object. Acquire
`generic-model-output` explicitly and parse it with
`parse_generic_model_output_data`. Use module-level
`parse_stable_id_map_data` and `parse_object_ids` for stable IDs.

Remember the exceptions:

- IDS has no experimental create-command replacement; use its deprecated
  command or author USD directly.
- The active point-cloud annotator remains in
  `isaacsim.sensors.rtx.nodes`.
- Radar Doppler requires Motion BVH.
- Mixed auxiliary-output levels are currently last-attach-wins across render
  products.

## Rewire ROS 2 publishers

For transform publishing, configure `Isaac Compute Transform Tree` with
`targetPrims` and optional `parentPrim`, then connect:

```text
execOut       -> execIn
parentFrames  -> parentFrames
childFrames   -> childFrames
translations  -> translations
orientations  -> orientations
```

An articulation-root target expands to its full link tree.

For joint states, configure `Isaac Read Joint State` at the articulation root
and wire `execOut`, names, positions, velocities, efforts, DOF types, stage
units, and sensor time to the matching publisher inputs. Keep topic,
namespace, queue, frame, and other unaffected publisher inputs.

In 6.0, Publish TF and Odometry likewise consume precomputed transforms from
`IsaacComputeTransformTree`; direct `targetPrims` publisher input is
deprecated.

## Check ROS library selection

- In 5.1, `system_default` chooses bundled Humble on Ubuntu 22.04 and bundled
  Jazzy on Ubuntu 24.04.
- In 6.0 workspaces, Jazzy defaults `use_internal_libs` to false while Humble
  retains true.
- `run_isaacsim.py` no longer forces a DDS implementation. Set `dds_type` for
  Fast DDS, Cyclone DDS, or Zenoh; leave it empty to preserve
  `RMW_IMPLEMENTATION`.
- Delete workarounds for duplicated or missing ROS timestamps and for
  `CameraInfo.fy` being forced to `fx`; those outputs were corrected.

## Port Replicator Agent configuration

Treat a 0.x-to-1.x move as a rewrite:

| Old surface | New surface |
| --- | --- |
| `scene.asset_path` | Required `environment.base_stage_asset_path` |
| `simulation_length` in 30-FPS frames | `simulation_duration` in seconds |
| `sdg_scheduler.py` | `actor_sdg.py` |
| `omni.anim.people` | `omni.anim.behavior.core` |
| Text commands and JSON transitions | Inline YAML `routines` and `triggers` |
| Top-level response/event/incident sections | Actor-group triggers |
| Character `filters` | Removed |

Validate the new Pydantic v2 configuration before a long generation job.
Select robot onboard cameras with `camera_prim_paths`. The environment accepts
an Isaac asset-relative path, URL, or absolute path.

## Validate behavior after an upgrade

1. Confirm the exact Kit build and run the integrated Compatibility Checker
   where available.
2. Resolve enabled extension IDs and scan manifests, imports, settings, and
   OmniGraph node types for deprecated names.
3. Inspect sensor prim types, USD schemas, annotator attachment, auxiliary
   levels, Motion BVH, and render timing.
4. Rebuild ROS graphs around typed source nodes and verify bridge-library and
   DDS selection on the deployment platform.
5. Recheck tests that asserted old physics, lidar timestamp, transform,
   distortion, depth-transform, or ROS message values; several releases
   intentionally corrected those results.
6. Validate Replicator configuration models and synthetic-data outputs before
   launching expensive jobs.
7. For containers, verify rootless permissions, architecture, streaming
   support, asset-pack completeness, and cache or Nucleus dependencies.

## Use the detailed references

The quick reference prioritizes migrations and common failure points. Consult
all relevant topic files before changing an existing project: they preserve
the complete API additions, corrected behaviors, platform constraints, asset
changes, and migration exceptions.
