# Synthetic Data, Replicator, and Assets

## Modular behaviors and robot assets

Batch `4.5.0` adds a modular Replicator behavior-scripting workflow for
reusable, persistent, configurable synthetic-data behaviors.

Robot assets add variants for animation, physics simulation, and sensor
simulation. Added or refreshed models include:

- ANYbotics ANYmal V2 and V4.
- Unitree Aliengo and Laikago.
- X-Humanoid Tien Kung.
- Yaskawa Motoman NEXT NEX 10.
- RobotEra STAR1.
- TurtleBot3 Burger, including a ROS asset.
- 1X NEO.
- Nova Carter.
- Universal Robots models.

## Synthetic-data extensions

Batch `5.0.0` adds:

| Extension | Purpose |
| --- | --- |
| `isaacsim.replicator.incident` | Box-topple, fire, and fluid-spill events |
| `isaacsim.anim.robot` | AMR animation control |
| `isaacsim.replicator.caption` | 2D natural-language descriptions and 3D spatial graphs |
| `isaacsim.sensors.rtx.placement` | Scene-aware camera placement and calibration |

`isaacsim.replicator.agent` gains custom commands, NavMesh Area integration,
and a built-in RTSP writer.

`isaacsim.replicator.object` gains:

- Embedded preview.
- Transform-distribution visualization.
- Parallel I/O.
- Dependency-randomization examples.

Robot setup tooling adds Robot Assembler, Gains Tuner, and Robot Schema,
alongside a UR10e manipulation workflow.

## Actor SDG changes

Batch `5.1.0` updates the Actor SDG Navigation Mesh API and removes unused
Actor SDG settings. Review scripts and configuration that use those surfaces
when moving to 5.1.

## Replicator Agent 1.x migration

Batch `6.0.0-migration` treats Replicator Agent 1.x as an architectural
replacement for 0.x. Old configuration, Python APIs, dependencies, and
internal-module imports do not run unchanged.

| 0.x surface | 1.x replacement |
| --- | --- |
| `scene.asset_path` | Required `environment.base_stage_asset_path` |
| `simulation_length` in 30-FPS frames | `simulation_duration` in seconds |
| `sdg_scheduler.py` | `actor_sdg.py` |
| `omni.anim.people` | `omni.anim.behavior.core` |
| Text command files and JSON transition maps | Inline YAML `routines` and `triggers` |
| Top-level `response`, `event`, and `incident` sections | Triggers on actor groups |
| Character `filters` | Removed |

`environment.base_stage_asset_path` accepts an Isaac asset-relative path,
URL, or absolute path. Select robot onboard cameras with
`camera_prim_paths`.

Configurations are Pydantic v2 models. Validate them before long generation
jobs so schema errors fail early. The UI contracts from five steps to three:
Generate Random Commands and Save Commands are replaced by the configuration
and behavior-tree workflow.

## Replicator and data collection in 6.0

Batch `6.0.0` adds collision triggers, explicit stop/halt behavior, and custom
writers to Replicator Agent.

It also adds extensions for:

- Teleoperation.
- HDF5 episode recording.
- HDF5 episode replay.

Replicator extension namespaces also move toward experimental families:

- `isaacsim.replicator.mobility_gen` becomes
  `isaacsim.replicator.experimental.mobility_gen`; its UI extension does not
  change.
- `isaacsim.replicator.domain_randomization` becomes
  `isaacsim.replicator.experimental.domain_randomization`.

See [extensions-and-core.md](extensions-and-core.md) for the broader extension
deprecation and removal map.
