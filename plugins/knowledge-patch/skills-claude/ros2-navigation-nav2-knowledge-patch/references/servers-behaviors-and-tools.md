# Servers, behaviors, and tools

## Route Server

Kilted's `nav2_route` computes and tracks routes on a predefined graph. It can replace
free-space global planning, or supply long-range graph structure while a
planner computes a nearby feasible path. Progress over node and edge events can
trigger contextual operations such as changing speed or activating equipment.

Enable `smooth_corners` and set `smoothing_radius` to replace graph corners with
tangent circular arcs. The server falls back to linear interpolation when an
edge is nearly straight or an arc cannot fit within its adjacent edges.

## Loopback simulation

Kilted adds `nav2_loopback_sim`, which integrates commanded velocity into ideal odometry. Use it
for tests and high-level simulation that do not need physics or localization
error.

In Lyrical it becomes a C++ node with an embedded clock publisher, so launch only
`loopback_simulator`. `speed_factor` is dynamically adjustable. The node also
provides `publish_scan`, `odom_publish_dur`, and `scan_noise_std`.

## Vector Object Server

`nav2_map_server` includes a Vector Object Server that rasterizes configured
circles, polygons, and polygonal chains into an `OccupancyGrid`. Use
`AddShapes`, `GetShapes`, and `RemoveShapes` services to maintain dynamic
virtual obstacles, keepout areas, or speed-filter masks.

## Following Server

The `opennav_following` server follows either a dynamically detected object or
a named reference frame while maintaining configured separation. It supports
topic-based detections and TF tracking.

## Behavior Server context

Behavior plugins share raw local and global costmaps, their published
footprints, and TF frames. The server runs plugins at `10.0` Hz by default and
uses a `0.1`-second transform tolerance.

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

## Default behaviors and request inputs

Without an override, Behavior Server loads Spin, BackUp, DriveOnHeading, and
Wait. Configured plugin names also become action-server names.

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

Wait duration and Spin distance come from their action requests. BackUp and
DriveOnHeading likewise receive distance, speed, and time allowance from each
request rather than from server parameters.

In Kilted, Controller Server's `publish_zero_velocity` defaults to `true`; disable it to
suppress the final zero command. `DriveOnHeading`, `BackUp`, and `Spin` accept
`disable_collision_checks`, default `false`. DriveOnHeading and BackUp also
provide `acceleration_limit: 2.5`, `deceleration_limit: -2.5`, and
`minimum_speed: 0.10` by default:

```yaml
acceleration_limit: 2.5
deceleration_limit: -2.5
minimum_speed: 0.10
```

## Spin limits

Spin projects collision risk `2.0` seconds ahead by default. It constrains
angular velocity to `0.4`–`1.0` rad/s and angular acceleration to `3.2` rad/s².

```yaml
simulate_ahead_time: 2.0
min_rotational_vel: 0.4
max_rotational_vel: 1.0
rotational_acc_lim: 3.2
```

## Assisted teleoperation

AssistedTeleop is not loaded by default; add it explicitly. It listens on
`cmd_vel_teleop` and projects motion for `1.0` second in `0.1`-second steps by
default.

```yaml
behavior_plugins: [spin, backup, drive_on_heading, wait, assisted_teleop]
assisted_teleop:
  plugin: nav2_behaviors::AssistedTeleop
projection_time: 1.0
simulation_time_step: 0.1
cmd_vel_teleop: cmd_vel_teleop
```

## Planner and Controller Server timing

Controller Server waits `costmap_update_timeout: 0.3` seconds by default for a
fresh local costmap. Planner Server's default is `1.0` second.

Controller Server estimates speed over `odom_duration`, default `0.3` seconds,
using `odom_topic`, default `odom`. `failure_tolerance` controls how long plugin
exceptions may continue: `0.0` fails immediately, `-1.0` permits them
indefinitely, and positive values are seconds.

Set `use_realtime_priority: true` to request controller-thread priority `90`.
This defaults to false and requires the process user's OS `rtprio` limit to be
configured first.

## Service and navigator introspection

`service_introspection_mode` accepts `disabled`, `metadata`, and `contents`; it
defaults to `disabled`. The standard navigators also have disabled-by-default
Groot 2 live monitoring, blackboard JSON inspection, and BT XML selection on a
new goal request.
