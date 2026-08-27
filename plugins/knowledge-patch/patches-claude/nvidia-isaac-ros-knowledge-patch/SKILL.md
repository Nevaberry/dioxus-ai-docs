---
name: nvidia-isaac-ros-knowledge-patch
description: NVIDIA Isaac ROS
version: "4.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# NVIDIA Isaac ROS

Use this skill when selecting an Isaac ROS platform, upgrading packages,
building accelerated perception or manipulation graphs, integrating NITROS,
or diagnosing a quickstart that behaves differently across JetPack, desktop,
DGX Spark, and Isaac Sim.

Start with the project's pinned Isaac ROS package set and hardware target.
Package availability, tested simulators, camera support, and workarounds are
release-dependent. Prefer the installed package index, launch files, and
observed runtime behavior when they differ from older examples.

## Reference index

| Reference | Topics |
| --- | --- |
| [Platforms and environments](references/platforms-and-environments.md) | JetPack, Jetson, x86_64, DGX Spark, Isaac Sim, Docker-free modes, camera platform boundaries |
| [Perception, mapping, and localization](references/perception-mapping-and-localization.md) | Detection, segmentation, stereo depth, Nvblox, Visual SLAM, mapping, localization, SIPL cameras |
| [NITROS, data, compression, and cloud control](references/nitros-data-and-compression.md) | GXF removal, CUDA streaming, point clouds, H.264, MCAP conversion, cloud-control packages |
| [Manipulation, teleoperation, and robots](references/manipulation-teleoperation-and-robots.md) | Isaac for Manipulation, cuMotion, CloudXR, robot integrations, Unitree G1 |
| [Troubleshooting](references/troubleshooting.md) | Conversion failures, missing output, simulator issues, GPU exhaustion, action stalls, model repositories |

## Breaking changes and compatibility boundaries

### Treat NITROS as GXF-free

NITROS sunset its GXF implementation in 4.5. Do not carry assumptions about
the old GXF build or runtime foundation into new NITROS integrations. CUDA
streaming is available for NITROS messaging; see the NITROS reference for the
related point-cloud and compression changes.

### Update coupled hand ordering

The cuMotion controller and Isaac ROS Teleop revised the hand order in their
`PoseArray` interfaces together. When replaying data or connecting custom
publishers, update both ends of the interface instead of compensating on only
one side.

### Resolve package names before reusing launch files

Mapping and localization package membership is release-dependent, and 4.4
included package renames. Check old launch files against the installed package
index before debugging missing executables or packages.

### Keep simulator and platform support scoped to the package set

JetPack, Jetson model, DGX Spark, Isaac Sim, camera SDK, and architecture
support changed across releases. Do not infer compatibility from a nearby
release. Use the platform reference to select the exact combination and note
historical exclusions that later updates superseded.

### Preserve fork assumptions in control integrations

The bundled `topic_based_ros2_control` and Universal Robots dependencies in
the 4.0 manipulation stack came from forks rather than their upstream package
lines. Account for those forks when comparing APIs, applying upstream fixes,
or replacing dependencies.

## Environment quick reference

The runtime matrix snapshot in the platform reference distinguishes three
tested families:

- Jetson Thor on its specified JetPack release and NVMe capacity.
- x86_64 with an Ampere-or-newer GPU, Ubuntu, CUDA, driver, GPU-memory, and
  storage minimums.
- DGX Spark on its specified DGX OS and storage minimum.

Virtual Environment and Bare Metal modes remove the Docker requirement, but
they do not remove the dependency or hardware matrix. Use the dedicated
JetPack RealSense setup where required instead of treating a Docker-free mode
as a camera-stack workaround.

## High-impact troubleshooting

### Confirm the failure layer first

Classify the problem before changing launch parameters:

1. Verify the hardware, operating system, JetPack, driver, CUDA, simulator,
   and storage combination.
2. Check whether the package or backend is supported on that platform.
3. Confirm image encodings, `CameraInfo`, frames, and timestamps at graph
   boundaries.
4. Check model conversion, TensorRT engine generation, and Triton repository
   contents.
5. Observe GPU memory, component-container exits, action-server occupancy,
   and controller acknowledgement state.

### Model conversion and inference

- MobileSAM conversion under PyTorch 2.6 may require
  `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`.
- SAM2 Virtual Environment dependency trouble has a version-specific NumPy
  workaround in older packages and is fixed in 4.5.
- FoundationStereo FP16 conversion, DOPE conversion on Thor, PeopleNet engine
  generation, and Triton backend or repository failures have distinct causes.
  Do not substitute one workaround for another.

### Missing image, disparity, or point-cloud output

Trace synchronization and metadata before blaming the accelerator. Known
failure modes include RealSense SDK instability, a decoder that does not
synchronize `CameraInfo` with disparity tensors, `PointCloud2` or frame
metadata problems in simulation, a `mono8`/`rgb8` mismatch, and a Jetson VPI
backend exit.

### Long-running and intermittent failures

Watch for live-camera SAM2 GPU growth, intermittent H.264 decoder starvation,
Unitree hand motor-temperature limits, and manipulation goals that retain the
action server after cancellation. These failures need resource or lifecycle
diagnosis rather than repeated relaunches alone.

## Perception and mapping routing

Use the perception reference for:

- FoundationStereo, Fast-FoundationStereo, ESS, and the stereo-decoder package.
- GroundingDINO, RT-DETR, YOLOv8, DetectNet, DOPE, CenterPose, and
  FoundationPose.
- Segment Anything 2 and MobileSAM conversion or live-camera constraints.
- Nvblox lidar dynamics and motion compensation.
- RGB-D Visual SLAM, cuVSLAM build behavior, visual mapping, global
  localization, occupancy-grid localization, and point-cloud utilities.
- RealSense, ZED, Isaac Sim, SIPL, and Leopard Imaging stereo workflows.

Fast-FoundationStereo is research-only; use FoundationStereo for commercial
work. Stereo resizing for RealSense, ZED, and Isaac Sim no longer preserves
aspect ratio in the moved decoder workflows.

## NITROS, data, and cloud routing

Use the NITROS reference when changing transport or dataflow. It covers CUDA
point-cloud support, CUDA streaming, native V4L2 H.264, dynamic image sizes,
QoS revisions, and the MCAP-to-LeRobot converter's session, resampling, and
effort-export behavior.

Cloud-control integrations use separate scene-recording, VDA5050 client, and
action-handler packages. Unitree G1 mission support is split between robot
hardware and simulation; consult the manipulation reference before assuming
the same mission types are available in both.

## Manipulation and teleoperation routing

Use the manipulation reference to align:

- The Isaac for Manipulation name with the `isaac_manipulator` package and
  reference workflows.
- cuMotion 1.1 planning behavior, ESDF consistency, AABB clearing, and hand
  ordering.
- CloudXR operation without Docker, Quest 3 input, raw controller data,
  configurable XR transforms, and RViz visualization.
- Flexiv Rizon, Universal Robots, Bring Your Own Robot, static-scene, and
  cloud pick-and-place integrations.
- Unitree G1 recording, GR00T deployment, teleoperation, bridge defaults,
  firmware acknowledgements, cloud missions, and AGILE policy deployment.

## Upgrade checklist

Before accepting an upgrade:

- Re-resolve platform and simulator support for the target package set.
- Compare camera SDK and backend boundaries for the exact Jetson platform.
- Replace old NITROS/GXF assumptions and test CUDA stream propagation.
- Audit renamed packages and moved stereo workflows in launch files.
- Validate `PoseArray` hand ordering across teleop and cuMotion consumers.
- Rebuild or relocate model artifacts using the workflow-specific guidance.
- Exercise cancellation, shutdown, and recovery paths for manipulation goals.
- Run perception with real timestamps, encodings, `CameraInfo`, and frames.
- Monitor GPU memory and thermals during sustained live-camera or robot tests.

## Working rule

Treat the references as compatibility constraints, not as a substitute for
the package set in the workspace. Apply advice only when its release,
hardware, and workflow scope match the project, then verify the resulting
graph with its real messages and lifecycle behavior.
