# Routing, Docking, and Behaviors

## Route Server

`nav2_route` computes and tracks routes over a predefined graph. It can replace
free-space global planning or provide long-range graph structure while another
planner produces a locally feasible path. Route progress can trigger contextual
operations on node and edge events, such as changing a speed limit or activating
equipment.

## Route corner smoothing

Route Server can replace graph corners with tangent circular arcs through
`smooth_corners` and `smoothing_radius`. It falls back to linear interpolation
for nearly straight edges or whenever an arc cannot fit inside its adjacent
edges.

## Loopback simulation

`nav2_loopback_sim` integrates commanded velocity into ideal odometry for tests
and high-level simulation. It deliberately excludes physics and localization
error.

In Lyrical it becomes a C++ node with an embedded clock publisher. Launch only
`loopback_simulator`, rather than a separate clock publisher. `speed_factor` is
dynamically adjustable, and the simulator also supports `publish_scan`,
`odom_publish_dur`, and `scan_noise_std`.

## Dock types and direction

Docking supports charging and non-charging static infrastructure as well as
dynamic docks. The built-in options include `simple_non_charging_dock`, and
RViz provides a docking panel.

Docking Server collision checking is enabled by default. The old server-wide
`dock_backwards` setting moves to each plugin as `dock_direction`, whose values
are `forward` (the default) or `backward`.

For simple plugins, `reverse_to_dock: true` allows detection from a forward
staging pose followed by dead-reckoned backward entry. This is distinct from a
plugin whose normal docking direction is backward.

## Docking plugin migration

In Lyrical, external detection rotations for simple dock plugins change from
Rz→Rx→Ry to Rx→Ry→Rz. Recalculate non-default configurations that use
all three axes; reusing the old angles changes the composed rotation.

Custom `ChargingDock` and `NonChargingDock` plugins must implement
`startDetectionProcess()` and `stopDetectionProcess()`. Simple plugins add:

- `detector_service_name`
- `detector_service_timeout`
- `subscribe_toggle`

These parameters support on-demand perception and its service/subscription
coordination.

## Following Server

The `opennav_following` server follows either a dynamically detected object or
a named reference frame while maintaining a configured distance. It supports
topic-based detections and TF-based tracking.

## Behavior Server shared collision context

Behavior plugins share the raw local and global costmaps, published footprints,
and TF frames. The server runs plugins at `10.0` Hz by default with a `0.1`
second transform tolerance.

```yaml
behavior_server:
  ros__parameters:
    local_costmap_topic: local_costmap/costmap_raw
    global_costmap_topic: global_costmap/costmap_raw
    local_footprint_topic: local_costmap/published_footprint
    global_footprint_topic: global_costmap/published_footprint
    local_frame: odom
    global_frame: map
    robot_base_frame: base_link
    cycle_frequency: 10.0
    transform_tolerance: 0.1
```

## Default behaviors and request-owned inputs

Without an override, Behavior Server loads Spin, BackUp, DriveOnHeading, and
Wait. Configured plugin names become their action-server names.

```yaml
behavior_plugins: [spin, backup, drive_on_heading, wait]
spin:
  plugin: nav2_behaviors::Spin
backup:
  plugin: nav2_behaviors::BackUp
drive_on_heading:
  plugin: nav2_behaviors::DriveOnHeading
wait:
  plugin: nav2_behaviors::Wait
```

Wait duration, Spin distance, and the BackUp or DriveOnHeading distance, speed,
and time allowance belong to each action request rather than server parameters.

## Collision bypass and linear-motion limits

Spin, BackUp, and DriveOnHeading accept `disable_collision_checks`, default
`false`. BackUp and DriveOnHeading also support these defaults:

```yaml
acceleration_limit: 2.5
deceleration_limit: -2.5
minimum_speed: 0.10
```

Disabling checks transfers collision responsibility outside the behavior; keep
the default for normal autonomous operation.

## Spin motion limits

Spin projects collision risk `2.0` seconds ahead by default and bounds angular
motion to `0.4`–`1.0` rad/s with a `3.2` rad/s² acceleration limit.

```yaml
simulate_ahead_time: 2.0
min_rotational_vel: 0.4
max_rotational_vel: 1.0
rotational_acc_lim: 3.2
```

## Assisted teleoperation

AssistedTeleop is not in the default behavior list. Add it explicitly when
needed. It listens on `cmd_vel_teleop` and, by default, projects motion for
`1.0` second in `0.1`-second steps.

```yaml
behavior_plugins: [spin, backup, drive_on_heading, wait, assisted_teleop]
assisted_teleop:
  plugin: nav2_behaviors::AssistedTeleop
projection_time: 1.0
simulation_time_step: 0.1
cmd_vel_teleop: cmd_vel_teleop
```
