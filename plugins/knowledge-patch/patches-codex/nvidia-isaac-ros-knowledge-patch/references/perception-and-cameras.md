# Perception and cameras

## Added perception families

Isaac ROS 4.0.0 added FoundationStereo to `isaac_ros_dnn_stereo_depth`,
GroundingDINO to `isaac_ros_object_detection`, and Segment Anything 2 to
`isaac_ros_image_segmentation`.

The current-runtime-and-packages package index also includes RT-DETR and YOLOv8
as `isaac_ros_rtdetr` and `isaac_ros_yolov8`, and CenterPose and FoundationPose
as `isaac_ros_centerpose` and `isaac_ros_foundationpose`.

## MobileSAM conversion with PyTorch 2.6

PyTorch 2.6 changed the `weights_only` default, which can break MobileSAM to
ONNX conversion. Restore the former behavior for the conversion process:

```bash
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
```

This workaround belongs to the conversion environment; do not apply it more
broadly than needed (4.0.0).

## AprilTag transforms

Isaac ROS 4.0.0 fixes TF broadcasting for AprilTags detected by
`isaac_ros_apriltag`.

## RGB-D Visual SLAM and Thor mounting

`isaac_ros_visual_slam` supports RGB-D cameras, and `sensor_mounting_rig`
supports the Jetson AGX Thor RealSense Rig (4.1.0).

## DNN stereo decoder migration

In 4.5.0, `isaac_ros_dnn_stereo_depth` adds a DNN stereo-decoder package. ESS
and FoundationStereo workflows move into that package, and Fast-FoundationStereo
is added. RealSense, ZED, and Isaac Sim workflows resize images without
retaining aspect ratio, so downstream geometry must account for the resize.

Fast-FoundationStereo is a research-only model. Use FoundationStereo for
commercial work.

## SAM2 outside Docker

The SAM2 quickstart dependency failures in Virtual Environment and Bare Metal
flows were fixed in 4.5.0. This supersedes the 4.1.0 workaround of downgrading
NumPy to 1.26.4 for a SAM2 visualization-script mismatch in Virtual
Environment flows.

## SIPL camera paths

Early SIPL and Leopard Imaging Eagle stereo Camera-over-Ethernet support
arrived on 2026-03-23. In the current-runtime-and-packages surface,
`isaac_ros_sipl_camera` publishes SIPL camera images with zero-copy NITROS.

In 4.6.0, `isaac_ros_sipl_camera` adds the Leopard Imaging Hawk GMSL2 stereo
camera. Its paired stereo outputs have aligned timestamps.

