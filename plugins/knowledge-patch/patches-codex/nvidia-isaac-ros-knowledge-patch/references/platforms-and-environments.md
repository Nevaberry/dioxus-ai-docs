# Platforms and environments

## JetPack 6.2 and Orin Nano Super

For JetPack 6.2 or Jetson Orin Nano Super, use the `v3.2-1` package set rather
than the base `v3.2` release (since 3.2-1).

## Jetson AGX Thor and JetPack 7.0

Isaac ROS 4.0.0 added Jetson AGX Thor and a JetPack 7.0 stack based on Ubuntu
24.04 and CUDA 13.0. That package set was tested with Isaac Sim 5.1.

Isaac Perceptor and Nova packages were not yet optimized for AGX Thor. The ZED
SDK was incompatible with Jetson Thor, so ZED cameras were not tested. RealSense
SDK support on JetPack 7 could become unstable and stop publishing images.

## Docker-optional modes

Virtual Environment and Bare Metal became supported development and deployment
modes in 4.1.0; Docker is not mandatory for those workflows. These modes must
still satisfy the same host, dependency, and hardware matrix as containerized
workflows.

## RealSense on JetPack 7

Use the dedicated Isaac ROS 4.1.0 setup procedure for RealSense on JetPack 7.
It addresses the SDK stability problem that affected the earlier platform path.

## DGX Spark support is time- and package-specific

Isaac ROS 4.1.0 did not support DGX Spark. General DGX Spark and JetPack 7.1
support arrived on 2026-02-19, so that older blanket exclusion is no longer an
accurate description of the current environment.

Do not generalize host support to every package: cuVSLAM remains unsupported on
DGX Spark even though `isaac_ros_visual_slam` builds the cuVSLAM library from
source on both `x86_64` and `aarch64` (4.6.0).

## Current tested runtime matrix

The current-runtime-and-packages quickstarts target ROS 2 Jazzy through the
Isaac ROS CLI-managed environment. Tested targets are:

- Jetson Thor T5000 or T4000 on JetPack 7.1, with at least 128 GB NVMe storage.
- `x86_64` on Ubuntu 24.04 with an Ampere-or-newer NVIDIA GPU with at least
  8 GB RAM, CUDA 13.0 or newer, NVIDIA driver 580 or newer, and at least 32 GB
  storage.
- DGX Spark on DGX OS 7.2.3, with at least 32 GB storage.

Other GB10 systems are outside this test matrix. Docker-optional Virtual
Environment and Bare Metal deployments remain subject to these constraints.

## JetPack 7.2 and simulator selection

Isaac ROS 4.6.0 adds Jetson Orin and JetPack 7.2 support. Isaac Sim 6.0 is the
recommended tested simulator; legacy Isaac Sim 5.0 and 5.1 remain supported.

