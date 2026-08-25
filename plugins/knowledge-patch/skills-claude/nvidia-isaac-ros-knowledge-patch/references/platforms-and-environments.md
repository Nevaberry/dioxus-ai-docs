# Platforms and environments

Use this reference to choose a supported hardware, operating-system,
JetPack, simulator, development-mode, and camera combination.

## Tested runtime matrix snapshot

The runtime matrix recorded on 2026-07-28 targets ROS 2 Jazzy through the
Isaac ROS CLI-managed environment:

| Family | Tested requirements |
| --- | --- |
| Jetson | Thor T5000 or T4000 on JetPack 7.1 with at least 128 GB NVMe storage |
| x86_64 | Ampere-or-newer NVIDIA GPU with at least 8 GB RAM, Ubuntu 24.04, CUDA 13.0 or newer, driver 580 or newer, and at least 32 GB storage |
| DGX Spark | DGX OS 7.2.3 with at least 32 GB storage |

Other GB10 systems are outside that test matrix. Virtual Environment and Bare
Metal deployments still have to satisfy the dependency and platform matrix;
their Docker-free nature does not broaden hardware support.

## JetPack 6.2 and Orin Nano Super (3.2-1)

The `v3.2-1` package set adds JetPack 6.2 and Jetson Orin Nano Super support.
Use that update rather than base `v3.2` for either target.

## Jetson AGX Thor and JetPack 7.0 (4.0.0)

Isaac ROS 4.0 adds Jetson AGX Thor and a JetPack 7.0 stack based on Ubuntu
24.04 and CUDA 13.0. The tested simulator for this package set is Isaac Sim
5.1.

The platform boundary is narrower than the headline support:

- Isaac Perceptor and Nova packages are not yet optimized for AGX Thor.
- The ZED SDK is incompatible with Jetson Thor in this release, so ZED cameras
  were not tested.
- RealSense SDK support on JetPack 7 can become unstable and stop publishing
  images.

## Docker-optional modes and camera setup (4.1.0)

Virtual Environment and Bare Metal are supported development and deployment
modes, so Docker is no longer required for those workflows.

Use the dedicated Isaac ROS 4.1 RealSense-on-JetPack-7 setup procedure. It
addresses the RealSense SDK stability issue on that platform. The
`sensor_mounting_rig` package also adds support for the Jetson AGX Thor
RealSense Rig.

DGX Spark is not supported by the 4.1 package set. Do not apply that historical
exclusion to later package sets without checking their newer platform matrix.

## SAM2 outside Docker (4.5.0)

The SAM2 quickstart dependency problems that affected Virtual Environment and
Bare Metal flows are fixed in 4.5. Older environments may still need their
release-specific workaround; see [Troubleshooting](troubleshooting.md).

## DGX Spark, JetPack 7.1, and early SIPL support

DGX Spark and JetPack 7.1 support arrived on 2026-02-19, superseding the 4.1
DGX Spark exclusion for the newer environment. Early SIPL and Leopard Imaging
Eagle stereo Camera-over-Ethernet support followed on 2026-03-23.
`isaac_ros_sipl_camera` publishes SIPL camera images through zero-copy NITROS.

## JetPack 7.2 and simulator selection (4.6.0)

Isaac ROS 4.6 adds Jetson Orin and JetPack 7.2 support. Isaac Sim 6.0 is the
recommended tested simulator. Legacy Isaac Sim 5.0 and 5.1 remain supported.

These additions do not erase package-specific platform exceptions. In
particular, cuVSLAM remains unsupported on DGX Spark; see
[Perception, mapping, and localization](perception-mapping-and-localization.md).

## Selection procedure

1. Identify the exact Isaac ROS package set.
2. Match the Jetson or desktop target to its operating-system, JetPack, CUDA,
   driver, GPU-memory, and storage requirements.
3. Select a simulator tested by that package set.
4. Check the camera SDK against the exact Jetson model and JetPack line.
5. Select Docker, Virtual Environment, or Bare Metal only after the dependency
   matrix is satisfied.
6. Apply later support announcements only when the corresponding packages are
   actually installed.
