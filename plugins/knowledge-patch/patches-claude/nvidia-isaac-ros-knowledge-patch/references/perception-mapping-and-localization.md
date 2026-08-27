# Perception, mapping, and localization

This reference routes detection, pose, segmentation, stereo depth, Nvblox,
Visual SLAM, mapping, localization, and SIPL camera work. Known failures and
workarounds are centralized in [Troubleshooting](troubleshooting.md).

## Detection, segmentation, and pose packages (4.0.0)

The 4.0 package set adds:

- FoundationStereo to `isaac_ros_dnn_stereo_depth`.
- GroundingDINO to `isaac_ros_object_detection`.
- Segment Anything 2 to `isaac_ros_image_segmentation`.

The release also fixes TF broadcasting for AprilTags detected by
`isaac_ros_apriltag`.

## Lidar and RGB-D inputs (4.1.0)

`isaac_ros_nvblox` adds dynamics support for lidar inputs and lidar motion
compensation. `isaac_ros_visual_slam` adds RGB-D camera support.

These features expand input support but do not remove downstream requirements
for consistent encodings, timestamps, frames, and camera metadata.

## DNN stereo decoder and workflow moves (4.5.0)

`isaac_ros_dnn_stereo_depth` adds a DNN stereo-decoder package and moves the
ESS and FoundationStereo workflows into it. It also adds
Fast-FoundationStereo.

RealSense, ZED, and Isaac Sim workflows now resize without preserving aspect
ratio. Revalidate calibration and any downstream assumptions about image
geometry after adopting the moved workflows.

Fast-FoundationStereo is a research-only model. Use FoundationStereo for
commercial work.

The decoder has a known synchronization limitation: RealSense, ZED, or Isaac
Sim runs can intermittently omit disparity or point-cloud output because
`CameraInfo` messages are not synchronized with disparity tensors. Diagnostic
steps are in the troubleshooting reference.

## Current mapping and localization package surface

The 2026-07-28 package index contains:

- `isaac_ros_visual_global_localization`
- `isaac_mapping_ros`
- `isaac_ros_visual_mapping`
- `isaac_ros_occupancy_grid_localizer`
- `isaac_ros_pointcloud_utils`

Resolve older launch files against the installed package index. The supported
set is release-dependent, and 4.4 included package renames.

## Additional detection and pose integrations

The 2026-07-28 package index includes:

- RT-DETR as `isaac_ros_rtdetr`
- YOLOv8 as `isaac_ros_yolov8`
- CenterPose as `isaac_ros_centerpose`
- FoundationPose as `isaac_ros_foundationpose`

Keep the package name distinct from the model name when resolving launch files,
assets, and graph components.

## SIPL camera integrations

Early SIPL and Leopard Imaging Eagle stereo Camera-over-Ethernet support uses
`isaac_ros_sipl_camera` to publish camera images through zero-copy NITROS.

### Leopard Imaging Hawk stereo (4.6.0)

`isaac_ros_sipl_camera` adds SIPL support for the Leopard Imaging Hawk GMSL2
stereo camera. The paired stereo output has aligned timestamps, which should be
preserved through downstream stereo processing.

## cuVSLAM source builds (4.6.0)

`isaac_ros_visual_slam` builds the cuVSLAM library from source on both
`x86_64` and `aarch64`. cuVSLAM remains unsupported on DGX Spark even though
the broader Isaac ROS environment supports DGX Spark.

## Workflow checks

When composing a perception or mapping graph:

1. Confirm that the model integration exists in the installed package index.
2. Match camera SDK support to the platform and JetPack release.
3. Verify encoding, timestamps, frame IDs, `CameraInfo`, and resize behavior.
4. Treat DNN stereo disparity, point-cloud, and visualization output as
   separate checkpoints.
5. Distinguish research-only models from models suitable for commercial use.
6. Check architecture-specific library support before building Visual SLAM.
