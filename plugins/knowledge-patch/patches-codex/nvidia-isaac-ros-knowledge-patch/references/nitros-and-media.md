# NITROS and media

## NITROS foundation and CUDA streaming

NITROS sunsets its GXF implementation in 4.5.0. Revisit custom integrations'
build dependencies and runtime assumptions rather than expecting GXF-backed
behavior. The same package set adds CUDA streaming support to NITROS messaging.

## CUDA point clouds

`isaac_ros_nitros` adds CUDA point-cloud support with NITROS (4.1.0). Keep the
data on compatible GPU paths when composing downstream nodes.

## Native V4L2 H.264

`isaac_ros_compression` adds native V4L2 H.264 encoding and decoding, dynamic
image-size support, and revised QoS behavior (4.5.0). Revalidate QoS assumptions
when moving existing encoder or decoder graphs to this path.

## Isaac Sim 5.1 NITROS Bridge

NITROS Bridge topics from Isaac Sim 5.1 may not arrive through DDS (4.0.0).
This breaks the object-following manipulation simulation tutorial even when the
graph otherwise appears to start normally.

