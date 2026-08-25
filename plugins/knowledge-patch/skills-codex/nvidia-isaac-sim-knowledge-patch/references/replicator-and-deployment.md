# Replicator, synthetic data, and deployment

## Build modular synthetic-data workflows

Replicator added modular behavior scripts in 4.5. Behaviors can be reusable,
persistent, and configurable (`4.5.0`).

Isaac Sim 5.0 adds these synthetic-data extensions (`5.0.0`):

- `isaacsim.replicator.incident` for box-topple, fire, and fluid-spill events.
- `isaacsim.anim.robot` for AMR animation control.
- `isaacsim.replicator.caption` for 2D natural-language descriptions and 3D
  spatial graphs.
- `isaacsim.sensors.rtx.placement` for scene-aware camera placement and
  calibration.

`isaacsim.replicator.agent` gains custom commands, NavMesh Area integration,
and a built-in RTSP writer. `isaacsim.replicator.object` adds embedded
preview, transform-distribution visualization, parallel I/O, and
dependency-randomization examples (`5.0.0`).

Actor SDG changes its Navigation Mesh API and removes unused settings in 5.1.
Review scripts and configuration using those surfaces (`5.1.0`).

Isaac Sim 6.0 adds teleoperation and HDF5 episode recording/replay
extensions. Replicator Agent adds collision triggers, explicit stop/halt
behavior, and custom writers (`6.0.0`).

## Migrate Replicator Agent configurations

Replicator Agent 1.x is an architectural replacement for 0.x. Old
configuration, Python APIs, dependencies, and internal-module imports do not
run unchanged (`6.0.0-migration`).

| 0.x | 1.x |
| --- | --- |
| `scene.asset_path` | Required `environment.base_stage_asset_path` |
| `simulation_length` in 30-FPS frames | `simulation_duration` in seconds |
| `sdg_scheduler.py` | `actor_sdg.py` |
| `omni.anim.people` | `omni.anim.behavior.core` |
| Text command files and JSON transition maps | Inline YAML `routines` and `triggers` |
| Top-level `response`, `event`, and `incident` sections | Triggers on actor groups |
| Character `filters` | Removed |

`environment.base_stage_asset_path` accepts an Isaac asset-relative path, a
URL, or an absolute path. Select robot onboard cameras through
`camera_prim_paths`.

Configurations are Pydantic v2 models; validate them before long generation
jobs. The UI contracts from five steps to three because Generate Random
Commands and Save Commands are replaced by configuration and behavior-tree
workflows.

## Account for container and architecture behavior

Isaac Sim 5.1 adds DGX Spark support and multi-architecture Docker packaging.
Containers run as a rootless user by default. Live streaming remains
unsupported on `aarch64` in that release (`5.1.0`).

## Select packaged artifacts

The 6.0 documentation line is distributed at patch level 6.0.1, and package
families version independently (`6.0.0`):

| Artifact | Version | Platforms or packaging |
| --- | --- | --- |
| Isaac Sim | 6.0.1 | Linux x86_64, Linux aarch64, Windows |
| Isaac Sim Assets | 6.0.1 | Complete pack split into five parts |
| WebRTC Streaming Client | 2.0.0 | Linux x86_64, Linux aarch64, Windows, macOS x86_64, macOS aarch64 |

For offline use, download, verify, combine, and extract all five parts of the
complete asset pack. In headless Docker Compose web-viewer deployments, the
WebRTC desktop client is optional (`6.0.0`).

## Replace retired workstation services

Omniverse Launcher, Nucleus Workstation, and Nucleus Cache entered removal
beginning October 1, 2025 (`6.0.0`). Use Enterprise Nucleus Server when
Nucleus and Live Sync are required. Replace Nucleus Cache with Hub
Workstation Cache.
