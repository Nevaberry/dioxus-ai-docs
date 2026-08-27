# RTX sensors and rendering

## Author native sensor prims and attach outputs

OmniSensor prims gained native USD support in 5.0. Camera prims used as RTX
sensors are deprecated; migrate those stages to OmniSensor prims (`5.0.0`).

Lidar RTX no longer attaches annotators or writers implicitly. Attach every
required output explicitly. OmniLidar USD assets also moved to
`/Isaac/Sensors`, so update authored references and lookup paths (`5.0.0`).

In 4.5, RTX lidar and radar gained auxiliary-output controls, and RTX lidar
could provide velocity measurements. The legacy SICK lidar configurations
were removed, requiring another configuration for dependent stages
(`4.5.0`).

## Choose the point-cloud path by installed version

In 5.0, legacy RTX point-cloud and scan-buffer nodes were removed in favor of
`OgnIsaacExtractRTXSensorPointCloud`. `OgnIsaacReadRTXLidarData` was also
removed; use the supported standalone-example route for that workflow
(`5.0.0`).

In 5.1, the per-frame output of `OgnIsaacCreateRTXLidarScanBuffer` replaces
`OgnIsaacExtractRTXSensorPointCloud`. Update graphs that adopted the 5.0 node
path (`5.1.0`).

## Migrate the experimental camera API

The deprecated `isaacsim.sensors.camera` extension is replaced by
`isaacsim.sensors.experimental.rtx` (`6.0.0-migration`). USD authoring uses
`RtxCamera`; acquisition uses `CameraSensor`, `TiledCameraSensor`, or
`SingleViewDepthCameraSensor`.

```python
from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera

sensor = CameraSensor(
    RtxCamera(
        "/World/Camera",
        tick_rate=30.0,
        translations=[[0.0, 0.0, 1.0]],
    ),
    resolution=(640, 480),
    annotators=["rgb"],
)
data, info = sensor.get_data("rgb")
```

Construction is no longer command-based:

- Use `tick_rate` instead of `frequency` or `dt`.
- Pass transforms as plural N×3 or N×4 arrays.
- Request annotators explicitly.
- Read each output with `get_data()`.
- Remove the unused `name` argument.

Replace `CameraView(prim_paths_expr=..., output_annotators=...)` with
`TiledCameraSensor(paths=[...], annotators=[...])`. Enumerate paths instead of
using a regular expression, and request tiled output with
`get_data("rgb", tiled=True)`.

Replace `SingleViewDepthSensor` with
`SingleViewDepthCameraSensor(RtxCamera.create(...), annotators=[...])`.
Apply native OpenCV fisheye or pinhole USD schemas instead of polynomial
distortion setters.

The earlier 5.0 Camera API added native OpenCV pinhole and fisheye
lens-distortion models and `SingleViewDepthSensor` with configurable noise
(`5.0.0`); the 6.0 migration above supersedes that depth-sensor construction.

## Migrate lidar, radar, and acoustic APIs

The deprecated `isaacsim.sensors.rtx` authoring/runtime API moves to
`isaacsim.sensors.experimental.rtx` (`6.0.0-migration`).

Replace old Kit create commands with `Lidar.create()`, `Radar.create()`, or
`Acoustic.create()`. Wrap the resulting prim in `LidarSensor`, `RadarSensor`,
or `AcousticSensor`. Use plural N×3/N×4 transform arrays and remove the unused
`name` argument.

```python
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor

sensor = LidarSensor(
    Lidar.create(
        "/World/Lidar",
        config="Example_Rotary",
        orientations=[[1.0, 0.0, 0.0, 0.0]],
    ),
    annotators=["generic-model-output"],
)
data, info = sensor.get_data("generic-model-output")
```

The former Ultrasonic API is now Acoustic. It authors `OmniAcoustic` prims
with `OmniSensorGenericAcousticWpmAPI`.

Replace `get_current_frame()` with explicit acquisition such as
`get_data("generic-model-output")`. Parse it with
`parse_generic_model_output_data`; parse stable IDs through module functions
`parse_stable_id_map_data` and `parse_object_ids`.

Short annotator names replace legacy long names. Use `draw-point-cloud`
instead of `enable_visualization()`. Use the Omniverse timeline instead of
per-sensor initialize, pause, and resume methods. Author non-visual materials
with USD `omni:simready:nonvisual:*` attributes instead of CSV mappings.

Important exceptions and constraints:

- `IsaacSensorCreateRtxIDS` has no experimental replacement. IDS still
  requires the deprecated command or direct USD authoring.
- The active point-cloud annotator stays in `isaacsim.sensors.rtx.nodes`.
- Radar Doppler requires Motion BVH.
- Author auxiliary-output levels through
  `_replicator:rendervar:GenericModelOutput:channels`; old per-modality
  attributes are ignored.
- Attaching render products for sensors with different auxiliary levels is
  currently last-attach-wins.

## Rebaseline defaults and corrected values

Motion BVH is disabled by default for RTX sensors in 5.1. That release also
corrects lidar timestamps, sensor transforms, Camera lens-distortion
attributes, and depth-sensor transforms (`5.1.0`). Remove compensations based
on the older incorrect values.

RTX sensors add Object ID semantic segmentation in 5.1. Non-visual RTX
materials can be represented through USD attributes and APIs, and IMU
processing can run device-side (`5.1.0`).

## Drive rendering from simulation time

Multitick rendering allows cameras and RTX lidar to render at rates and
offsets driven by physics simulation time. It is the active route across RTX
sensors, ROS 2, UCX, and `SimulationApp`, rather than assuming one render per
application update (`6.0.0`).

Camera workflows also add structured-light cameras and USD-native camera ISP
configuration (`6.0.0`).
