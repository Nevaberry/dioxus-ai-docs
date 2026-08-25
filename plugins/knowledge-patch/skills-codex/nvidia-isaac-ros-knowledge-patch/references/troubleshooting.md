# Troubleshooting

## Intermittent output and visualization issues

In 4.0.0, running `isaac_ros_h264_decoder` alongside
`isaac_ros_h264_encoder` can intermittently leave the decoder without output.
DOPE can miss objects in manipulation workflows, DetectNet can emit overlapping
duplicate boxes because of its DBScan implementation, and the Nvblox RealSense
people-segmentation example can display an incorrect RViz color overlay.

For Isaac Sim 5.1, if the Nvblox sample scene fails to load normally, open it
through Content Window → Samples → NvBlox → `nvblox_sample_scene.usd` (4.0.0).

## FoundationStereo FP16 conversion memory

FoundationStereo FP16 conversion can run out of memory with the TensorRT
version used by Isaac ROS 4.1.0.

## Unsupported Triton PyTorch backend

The Triton Inference Server PyTorch backend is not supported in Isaac ROS
4.1.0.

## DOPE conversion on AGX Thor

The DOPE quickstart cannot convert its ONNX model to a TensorRT Plan on Jetson
AGX Thor because the model contains unsupported layers (4.1.0).

## DNN stereo output gaps

DNN stereo with RealSense, ZED, or Isaac Sim can intermittently omit disparity
or point-cloud output because the decoder does not synchronize `CameraInfo`
messages with disparity tensors (4.5.0).

## PeopleNet TensorRT engine setup

If `trtexec` is absent from `/usr/src/tensorrt/bin/trtexec`, the PeopleNet
quickstart may require manual TensorRT engine generation (4.5.0).

## Isaac Sim stereo point-cloud visualization

The Isaac Sim stereo-image-processing workflow may fail to show its point cloud
in RViz because of `PointCloud2` conversion or frame metadata (4.5.0).

## Live-camera SAM2 GPU exhaustion

After adding an object prompt, `isaac_ros_segment_anything2` pipelines with a
live ZED or RealSense camera may continuously consume GPU memory until CUDA
runs out of memory (4.6.0).

## RealSense Visual SLAM mask encoding

The RealSense segmentation-mask workflow sends a `mono8` infrared stream to a
DNN encoder expecting `rgb8`. The encoder terminates on a fatal assertion, and
Visual SLAM receives no mask (4.6.0).

## Jetson VPI RealSense SGM

The `isaac_ros_stereo_image_proc` RealSense SGM workflow can encounter a VPI
backend error on Jetson Orin or Thor. The error exits the component container
and prevents disparity or point-cloud output (4.6.0).

## Manipulation action-server stalls

In multi-object pick-and-place, a stalled goal may ignore cancellation or
shutdown and retain the action server. Later goals are then rejected (4.6.0).
Resolve the active goal and server state instead of submitting repeated goals.

## Simulated manipulation failures

In the simulated UR10e pick-and-place workflow, grasp planning for
`mac_and_cheese` can fail with `TRAJECTORY_OPTIMIZATION_FAILURE`, aborting the
goal or reporting partial success. The RT-DETR object-following workflow can
produce unstable detections, and the reach policy can fail while loading its
checkpoint (4.6.0).

## Gear Assembly test failure on Debian

The Gear Assembly pose-estimation accuracy test may fail to launch on Debian
because `parse_joint_state_from_yaml()` omits the required `joint_names`
argument. The robot then cannot move above the peg stand for the visual
pose-error check (4.6.0).

## DetectNet Triton repository hygiene

DetectNet can fail during Triton initialization when the model repository
contains stale or non-Triton models. Remove unrelated models, or put Triton
models under `${ISAAC_ROS_WS}/isaac_ros_assets/models/triton`, before launching
the workflow (4.6.0).
