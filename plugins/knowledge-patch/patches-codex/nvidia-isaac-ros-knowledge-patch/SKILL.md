---
name: nvidia-isaac-ros-knowledge-patch
description: NVIDIA Isaac ROS
version: "4.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# NVIDIA Isaac ROS Knowledge Patch

Use this skill when selecting an Isaac ROS platform, package, camera path,
deployment mode, or troubleshooting workflow. Check the runtime matrix before
reusing older launch files: platform support, package names, and known failure
modes vary substantially across the recent package sets.

## Reference index

| Reference | Topics |
| --- | --- |
| [platforms-and-environments.md](references/platforms-and-environments.md) | JetPack and hardware support, simulator compatibility, Docker-optional modes, tested runtime matrix |
| [perception-and-cameras.md](references/perception-and-cameras.md) | DNN stereo, detection and pose packages, RGB-D and SIPL cameras, segmentation and model conversion |
| [nitros-and-media.md](references/nitros-and-media.md) | GXF removal, CUDA streaming and point clouds, H.264, NITROS Bridge interoperability |
| [manipulation-and-teleoperation.md](references/manipulation-and-teleoperation.md) | Isaac for Manipulation, cuMotion, XR teleoperation, robot integrations, Unitree G1 |
| [mapping-cloud-and-data.md](references/mapping-cloud-and-data.md) | Nvblox, mapping and localization names, Cloud Control packages, MCAP conversion |
| [troubleshooting.md](references/troubleshooting.md) | Runtime output gaps, GPU and TensorRT failures, simulation stalls, model repository hygiene |

## Start with compatibility

### Select the environment from the current matrix

For current quickstarts, use the Isaac ROS CLI-managed environment and one of
the tested combinations:

- Jetson Thor T5000 or T4000 on JetPack 7.1 with at least 128 GB NVMe storage.
- `x86_64` with Ubuntu 24.04, CUDA 13.0 or newer, driver 580 or newer, an
  Ampere-or-newer NVIDIA GPU with at least 8 GB RAM, and at least 32 GB storage.
- DGX Spark on DGX OS 7.2.3 with at least 32 GB storage.

Other GB10 systems are outside the test matrix. Virtual Environment and Bare
Metal modes do not relax the platform and dependency requirements merely
because they avoid Docker. See
[platforms and environments](references/platforms-and-environments.md).

### Distinguish system support from package support

DGX Spark is supported by the current environment even though it was excluded
in Isaac ROS 4.1. That does not imply that every package works there: cuVSLAM
is still unsupported on DGX Spark. Validate both the host platform and the
individual package before choosing a workflow.

### Match JetPack, Jetson, and simulator together

- Use the `v3.2-1` package set, rather than base `v3.2`, for JetPack 6.2 or
  Jetson Orin Nano Super.
- The JetPack 7.0 stack introduced Ubuntu 24.04, CUDA 13.0, and Jetson AGX Thor;
  its camera constraints differ from later JetPack 7 procedures.
- Isaac Sim 5.1 has known NITROS Bridge and sample-scene issues.
- For newer workflows, check the JetPack 7.2 and Isaac Sim 6.0 notes before
  assuming a 5.x simulator recipe is preferred.

## Breaking changes and migrations

### Remove assumptions about GXF-backed NITROS

NITROS sunset its GXF implementation in 4.5. Treat this as a build and runtime
foundation change for integrations, not a minor transport tweak. At the same
time, NITROS messaging added CUDA streaming. Review custom type adaptation,
build dependencies, and launch assumptions. See
[NITROS and media](references/nitros-and-media.md).

### Move DNN stereo workflows to the decoder package

ESS and FoundationStereo workflows moved into the DNN stereo-decoder package,
which also adds Fast-FoundationStereo. RealSense, ZED, and Isaac Sim workflows
resize without retaining aspect ratio. Account for the changed geometry and
for intermittent `CameraInfo` synchronization gaps before trusting disparity
or point-cloud output.

Fast-FoundationStereo is research-only. Use FoundationStereo for commercial
work. See [perception and cameras](references/perception-and-cameras.md).

### Update hand ordering as one coordinated change

The cuMotion controller and Isaac ROS Teleop revised `PoseArray` hand order to
match each other. Update producers and consumers together; changing only one
side can silently swap hands. cuMotion also moved to 1.1.0 and added planning
changes described in
[manipulation and teleoperation](references/manipulation-and-teleoperation.md).

### Reconcile Unitree G1 interfaces

The G1 bridge and bringup changed defaults, topic and frame names, controller
configuration, GR00T launch behavior, and acknowledgement checks. Treat older
launch files and recorded data as migration inputs. Firmware 1.5.1 workflows
must handle acknowledgements correctly.

### Resolve package renames before editing launch files

The supported mapping and localization set is release-dependent, and the 4.4
changes included package renames. Resolve names against the current package
index first. The active names are collected in
[mapping, cloud, and data](references/mapping-cloud-and-data.md).

## High-value capabilities

### Run without Docker when appropriate

Virtual Environment and Bare Metal are supported development and deployment
modes. SAM2 dependency problems in those modes were fixed in 4.5, and CloudXR
teleoperation can also run without Docker. Still follow the tested runtime
matrix and any workflow-specific dependency instructions.

### Stream CUDA data through NITROS

NITROS supports CUDA point clouds and CUDA streaming. Use those capabilities
to keep compatible data paths on the GPU, while accounting for the GXF removal
in custom integrations.

### Use the expanded perception surface

The package surface includes FoundationStereo, Fast-FoundationStereo,
GroundingDINO, SAM2, RT-DETR, YOLOv8, CenterPose, and FoundationPose. Choose the
documented package name and observe the model-specific licensing and runtime
limits in [perception and cameras](references/perception-and-cameras.md).

### Choose current camera paths

SIPL publishes camera images through zero-copy NITROS. Support includes early
Leopard Imaging Eagle stereo Camera-over-Ethernet and a paired, timestamp-aligned
Leopard Imaging Hawk GMSL2 stereo path. RealSense, ZED, and VPI paths have
version- and platform-specific failures, so read both the camera guidance and
the troubleshooting reference.

### Build manipulation workflows from current components

Isaac for Manipulation supplies gear assembly and behavior-tree multi-object
pick-and-place references. Current integrations include UR10e, Flexiv Rizon,
bring-your-own-robot guidance, XR teleoperation, and Unitree G1 physical-AI and
cloud-control workflows.

### Convert robot data to LeRobot

The MCAP-to-LeRobot converter supports multiple sessions, FPS resampling, and
`action.effort` export. Preserve session boundaries and choose a target FPS
deliberately rather than treating conversion as a byte-for-byte rewrite.

## Troubleshooting priorities

### When a graph runs but produces no output

Check known synchronization and encoding boundaries before changing QoS at
random:

1. DNN stereo may omit disparity or point clouds when `CameraInfo` and disparity
   tensors are not synchronized.
2. RealSense mask workflows can send `mono8` into an encoder expecting `rgb8`,
   terminating the encoder before Visual SLAM receives a mask.
3. Jetson VPI RealSense SGM failures can exit the component container.
4. Paired H.264 encoder and decoder nodes can intermittently leave the decoder
   without output.
5. Isaac Sim 5.1 NITROS Bridge topics may fail to arrive through DDS.

Use [troubleshooting](references/troubleshooting.md) for precise symptoms and
workarounds.

### When model conversion or inference fails

- For MobileSAM conversion under PyTorch 2.6, restore the previous checkpoint
  loading behavior for that process:

  ```bash
  export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
  ```

- FoundationStereo FP16 conversion can exceed memory with the TensorRT version
  in Isaac ROS 4.1.
- DOPE conversion on Jetson AGX Thor can fail on unsupported layers.
- If PeopleNet cannot find `trtexec` at its expected path, generate the
  TensorRT engine manually.
- Triton initialization can be broken by unrelated models in its repository.

### When live segmentation exhausts memory

SAM2 with a live ZED or RealSense camera may continually consume GPU memory
after an object prompt until CUDA reports out of memory. Monitor allocation
growth and avoid treating the first successful frames as proof of stability.

### When manipulation stops accepting goals

A stalled multi-object pick-and-place goal may ignore cancellation or shutdown
and retain the action server, causing subsequent goals to be rejected. Diagnose
the original active goal and server state before retrying repeatedly.

## Working method

1. Identify the host architecture, Jetson or DGX model, OS, JetPack or CUDA,
   driver, storage, camera, and simulator.
2. Confirm the combination against the current runtime matrix.
3. Resolve current package and launch names rather than copying older examples.
4. Apply breaking interface changes, especially NITROS foundations, DNN stereo
   packaging, hand ordering, and G1 topic or frame changes.
5. Check the relevant known limitations before diagnosing generic ROS 2, DDS,
   QoS, TensorRT, or CUDA causes.
6. Keep unsupported or research-only combinations out of production plans.

