# Collision Monitor

## Command pipeline and fail-safe timing

Collision Monitor normally receives desired commands on `cmd_vel_smoothed`
(`cmd_vel_raw` before Jazzy) and publishes the safety-adjusted command on
`cmd_vel`.

If any observation source is stale for `source_timeout`, default `2.0` seconds,
the monitor stops the robot. `0.0` disables the stale-source check. A value on a
specific source overrides the node-level value. `stop_pub_timeout`, default
`1.0`, controls how long zero commands continue after the stop.

```yaml
cmd_vel_in_topic: cmd_vel_smoothed
cmd_vel_out_topic: cmd_vel
source_timeout: 2.0
stop_pub_timeout: 1.0
scan:
  source_timeout: 0.2
```

## Motion compensation and state output

`base_shift_correction` defaults to `true`. It compensates sensor points for
base motion between the observation timestamp and the current monitor cycle.
Disabling it saves computation but is not recommended for fast robots using
modest sensor rates.

Set the otherwise empty `state_topic` to create a publisher that reports the
active polygon name and action type.

```yaml
base_shift_correction: true
state_topic: collision_monitor_state
```

## Runtime control

The `Toggle` service and `ToggleCollisionMonitor` BT node can disable all
Collision Monitor polygons while leaving sensor checking active.

Polygon parameters `trigger_consecutive_points` and
`release_consecutive_points` add temporal debounce. Values of `1` and `1`
(`1/1`) preserve single-cycle triggering and release.

## Zone actions and precedence

Every name in `polygons` identifies a zone with a geometry `type` and an
`action_type`:

- `stop` sets motion to zero.
- `slowdown` multiplies speed by `slowdown_ratio`.
- `limit` caps linear and angular speed.
- `approach` scales motion to maintain `time_before_collision`.

A zone triggers when at least `min_points` readings are inside. When zones act
simultaneously, the most restrictive action wins.

```yaml
polygons: [stop_zone, approach_zone]
stop_zone:
  type: circle
  radius: 0.3
  action_type: stop
  min_points: 4
approach_zone:
  type: polygon
  action_type: approach
  footprint_topic: local_costmap/published_footprint
  time_before_collision: 2.0
  simulation_time_step: 0.1
```

## Static and subscribed geometry

Polygon `points` is a string containing at least three `[x, y]` pairs. Circles
use `radius`. If static geometry is omitted, stop, slowdown, and limit zones can
read `polygon_sub_topic` for polygon points or a circle radius. An approach
polygon can instead consume `footprint_topic`.

Static geometry takes precedence when both static and subscribed forms are
configured. `polygon_subscribe_transient_local` selects transient-local
durability.

```yaml
dynamic_stop:
  type: polygon
  polygon_sub_topic: safety_zone
  polygon_subscribe_transient_local: true
  action_type: stop
  min_points: 4
```

## Humble point-threshold migration

Humble's `max_points` represented the largest safe observation count. Newer
releases use `min_points`, the smallest triggering count. Convert with:

```text
min_points = max_points + 1
```

## Velocity-dependent zones

A `velocity_polygon` chooses the first named sub-polygon whose linear and
angular bounds include the current command. Order overlapping entries
deliberately and finish with a range that covers every possible velocity.

For non-holonomic robots, `linear_min` and `linear_max` are signed x velocities,
so reverse is negative. With `holonomic: true`, they are nonnegative resultant
speed magnitudes and can additionally be gated with `direction_start_angle`
and `direction_end_angle`.

```yaml
velocity_stop:
  type: velocity_polygon
  action_type: stop
  min_points: 4
  holonomic: false
  velocity_polygons: [forward, fallback]
  forward:
    points: "[[0.5, 0.3], [0.5, -0.3], [-0.2, -0.3], [-0.2, 0.3]]"
    linear_min: 0.0
    linear_max: 1.0
    theta_min: -1.0
    theta_max: 1.0
  fallback:
    points: "[[0.3, 0.3], [0.3, -0.3], [-0.3, -0.3], [-0.3, 0.3]]"
    linear_min: -1.0
    linear_max: 1.0
    theta_min: -1.0
    theta_max: 1.0
```

## Point-cloud transport and filtering

Point-cloud sources support `point_cloud_transport`. `transport_type` defaults
to `raw` and can select `zstd`, `zlib`, or `draco`.

Only points between `min_height` and `max_height` and beyond `min_range` are
projected. `use_global_height: true` filters an already-global `height` field
instead of transformed `z`.

Range sources synthesize arc points at `obstacles_angle` spacing, default one
degree. Polygon sources sample their boundaries at `sampling_distance`, default
`0.1`.

```yaml
observation_sources: [depth, sonar]
depth:
  type: pointcloud
  topic: camera/points
  transport_type: zstd
  min_height: 0.05
  max_height: 0.5
  min_range: 0.2
sonar:
  type: range
  topic: sonar
  obstacles_angle: 0.0174533
```

## Costmap sources

Collision Monitor and Collision Detector accept `nav2_msgs/Costmap` via
`CostmapSource`. Use this source cautiously because map cost semantics directly
control the safety response.

For an already configured source, `cost_threshold` defaults to `253`; only
inscribed or lethal cells become obstacle points. Unknown cost `255` is handled
separately by `treat_unknown_as_obstacle`, which defaults to `true`. Disable it
only when large unknown regions must not trigger the monitor.

```yaml
costmap:
  type: costmap
  topic: local_costmap/costmap
  cost_threshold: 254
  treat_unknown_as_obstacle: false
```
