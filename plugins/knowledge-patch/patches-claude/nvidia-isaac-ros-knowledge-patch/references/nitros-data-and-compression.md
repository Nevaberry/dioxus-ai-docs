# NITROS, data, compression, and cloud control

Use this reference for accelerated message transport, CUDA dataflow,
compression, dataset conversion, and fleet-facing cloud-control packages.

## NITROS integration changes

### CUDA point clouds (4.1.0)

`isaac_ros_nitros` adds point-cloud support for CUDA with NITROS. Keep point
clouds on the accelerated path where compatible consumers can accept the
NITROS representation.

### GXF sunset and CUDA streaming (4.5.0)

NITROS sunsets its GXF implementation in 4.5. This changes the build and
runtime foundation of NITROS integrations; remove assumptions that custom
graphs must be structured around the former GXF implementation.

NITROS messaging also gains CUDA streaming support. Preserve the CUDA stream
semantics across compatible producers and consumers rather than forcing a
host-side synchronization boundary by default.

## NITROS Bridge simulation boundary (4.0.0)

NITROS Bridge topics from Isaac Sim 5.1 might not arrive through DDS. This
breaks the object-following manipulation simulation tutorial. When the graph
works inside one transport domain but a simulator topic disappears at the DDS
boundary, treat the bridge as the primary suspect; see
[Troubleshooting](troubleshooting.md).

## Native V4L2 H.264 (4.5.0)

`isaac_ros_compression` adds native V4L2 H.264 encoding and decoding, supports
dynamic image sizes, and revises QoS behavior. Recheck QoS compatibility on
both sides of a compressed stream and test size changes instead of assuming a
fixed-resolution pipeline.

An older encoder/decoder pairing can intermittently leave the decoder without
output. The symptom and isolation advice are recorded in the troubleshooting
reference.

## MCAP-to-LeRobot conversion (4.5.0)

`isaac_ros_data_tools` adds an MCAP-to-LeRobot converter with:

- Multi-session conversion.
- FPS resampling.
- `action.effort` export.

Choose the target FPS deliberately, preserve session boundaries where they
carry experimental meaning, and include effort data when the downstream
LeRobot workflow consumes it.

## Cloud-control package surface

The 2026-07-28 Cloud Control surface includes these packages for receiving
fleet tasks and actions and reporting progress, state, and errors:

- `isaac_ros_scene_recorder`
- `isaac_ros_vda5050_client`
- `vda5050_action_handler`

Keep task transport, action execution, and scene recording as separate package
responsibilities when diagnosing a fleet workflow.

## Unitree G1 cloud-control split (4.6.0)

Unitree G1 cloud control is available on hardware and in Isaac Sim, but their
mission surfaces differ:

- On robot hardware, `isaac_ros_cloud_control` supports navigation and GR00T
  manipulation missions.
- In simulation, cloud control supports navigation missions only.
- `isaac_ros_deploy` can deploy G1 AGILE locomotion policies to Isaac Sim 6.0.

The related bridge, bringup, teleoperation, acknowledgement, and robot-policy
details are in
[Manipulation, teleoperation, and robots](manipulation-teleoperation-and-robots.md).

## Integration checklist

- Identify every accelerated-to-DDS boundary in simulation and deployment.
- Remove GXF-era build and runtime assumptions from new NITROS integrations.
- Validate CUDA stream propagation and synchronization explicitly.
- Test point-cloud types with the actual downstream consumer.
- Reconcile revised H.264 QoS on publisher and subscriber.
- Exercise dynamic image-size changes through encoder and decoder.
- Validate conversion sessions, FPS, and effort fields in generated datasets.
- Separate cloud task receipt, action handling, robot execution, and status
  reporting when tracing failures.
