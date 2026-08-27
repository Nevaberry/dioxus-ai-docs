# Mapping, cloud, and data

## Nvblox lidar dynamics

`isaac_ros_nvblox` adds dynamics support for lidar inputs and lidar motion
compensation (4.1.0).

## MCAP-to-LeRobot conversion

`isaac_ros_data_tools` adds an MCAP-to-LeRobot converter with multi-session
conversion, FPS resampling, and `action.effort` export (4.5.0). Choose session
boundaries and resampling rate deliberately when preparing training data.

## Cloud Control packages

The current-runtime-and-packages Cloud Control surface includes:

- `isaac_ros_scene_recorder`
- `isaac_ros_vda5050_client`
- `vda5050_action_handler`

Together these receive fleet tasks and actions and report progress, state, and
errors.

## Current mapping and localization names

The current-runtime-and-packages mapping and localization surface comprises:

- `isaac_ros_visual_global_localization`
- `isaac_mapping_ros`
- `isaac_ros_visual_mapping`
- `isaac_ros_occupancy_grid_localizer`
- `isaac_ros_pointcloud_utils`

Resolve older launch files against the current package index. The supported set
is release-dependent, and the 4.4 changes included package renames.

