# Sensors and Rendering

## RTX lidar and radar before the experimental API

Batch `4.5.0` adds control over auxiliary-data output for RTX lidar and radar,
and RTX lidar can report velocity. Legacy SICK lidar configurations are no
longer included; update scenes and applications to another configuration.

Batch `5.0.0` makes these changes:

- OmniSensor prims gain native USD support. Using Camera prims as RTX sensors
  is deprecated; migrate the stage to OmniSensor prims.
- `SingleViewDepthSensor` provides configurable noise.
- The Camera API gains native OpenCV pinhole and fisheye lens-distortion
  models.
- Lidar RTX no longer attaches annotators or writers implicitly. Explicitly
  attach every output the client needs.
- Legacy RTX point-cloud and scan-buffer nodes are removed in favor of
  `OgnIsaacExtractRTXSensorPointCloud`.
- `OgnIsaacReadRTXLidarData` is removed; use the supported standalone-example
  workflow.
- OmniLidar USD assets move to `/Isaac/Sensors`; update authored references
  and asset lookup paths.

## Sensor changes in 5.1

Batch `5.1.0` adds Object ID semantic segmentation to RTX sensors. Non-visual
RTX materials can be represented with USD attributes and new APIs, and IMU
processing can execute on-device.

For RTX lidar, the per-frame output of
`OgnIsaacCreateRTXLidarScanBuffer` replaces
`OgnIsaacExtractRTXSensorPointCloud`. Update graphs that adopted the
5.0-specific node.

Motion BVH is disabled by default for RTX sensors. The release also corrects:

- Lidar timestamps.
- Sensor transforms.
- Camera lens-distortion attributes.
- Depth-sensor transforms.

Update consumers and tests instead of retaining assumptions based on the
older incorrect values.

## Camera authoring and acquisition

Batch `6.0.0-migration` replaces the deprecated
`isaacsim.sensors.camera` extension with
`isaacsim.sensors.experimental.rtx`. USD authoring and runtime acquisition
are separate, and camera construction is no longer command-based:

- Author with `RtxCamera`.
- Acquire with `CameraSensor`, `TiledCameraSensor`, or
  `SingleViewDepthCameraSensor`.
- Use `tick_rate` instead of `frequency` or `dt`.
- Pass transforms as plural N×3 translation and N×4 orientation arrays.
- Request annotators explicitly and retrieve each output with `get_data()`.

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

Apply these object-level migrations:

| Deprecated pattern | Replacement |
| --- | --- |
| `CameraView(prim_paths_expr=..., output_annotators=...)` | `TiledCameraSensor(paths=[...], annotators=[...])` |
| Regular-expression prim selection | Enumerated sensor paths |
| Implicit tiled result | `get_data("rgb", tiled=True)` |
| `SingleViewDepthSensor` | `SingleViewDepthCameraSensor(RtxCamera.create(...), annotators=[...])` |
| Polynomial distortion setters | Native OpenCV fisheye or pinhole USD schemas |
| `name` argument | Remove it |

## Lidar, radar, and acoustic authoring

The 6.0 migration also moves the deprecated
`isaacsim.sensors.rtx` authoring/runtime API into
`isaacsim.sensors.experimental.rtx`.

Replace old Kit create commands with `Lidar.create()`, `Radar.create()`, or
`Acoustic.create()`, then wrap the result in `LidarSensor`, `RadarSensor`, or
`AcousticSensor`. Ultrasonic becomes Acoustic and authors `OmniAcoustic`
prims with `OmniSensorGenericAcousticWpmAPI`.

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

Replace `get_current_frame()` with explicit annotator acquisition, such as
`get_data("generic-model-output")`. Parse generic output with
`parse_generic_model_output_data`; parse stable identifiers with the
module-level `parse_stable_id_map_data` and `parse_object_ids` functions.

Additional API changes:

- Short annotator names replace the legacy long names.
- The `draw-point-cloud` annotator replaces `enable_visualization()`.
- The Omniverse timeline replaces per-sensor initialize, pause, and resume.
- Non-visual materials use USD `omni:simready:nonvisual:*` attributes instead
  of CSV mappings.
- Transforms are plural N×3 and N×4 arrays.
- The unused `name` argument is removed.

## Exceptions and auxiliary outputs

- There is no experimental replacement for `IsaacSensorCreateRtxIDS`; keep
  the deprecated command or author USD directly.
- The active point-cloud annotator remains in
  `isaacsim.sensors.rtx.nodes`.
- Radar Doppler requires Motion BVH.
- Author auxiliary-output levels through
  `_replicator:rendervar:GenericModelOutput:channels`; old per-modality
  attributes are ignored.
- Attaching render products for sensors with different auxiliary-output
  levels is currently last-attach-wins.

## New camera workflows

Batch `6.0.0` adds structured-light camera support and USD-native camera ISP
configuration. It also makes multitick rendering the active path for cameras
and RTX lidar; see
[physics-and-simulation.md](physics-and-simulation.md) for timing guidance.
