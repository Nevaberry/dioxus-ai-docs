# Collision Monitor

## Command pipeline and fail-safe timeouts

Collision Monitor normally consumes desired velocity on `cmd_vel_smoothed`
(`cmd_vel_raw` before Jazzy) and publishes the safety-adjusted command on
`cmd_vel`.

If any observation source is stale for `source_timeout`, the monitor stops the
robot. The node default is `2.0` seconds; `0.0` disables the check, and a
source-specific value overrides the node value. `stop_pub_timeout`, default
`1.0`, controls how long zero commands continue after a stop.

```yaml
cmd_vel_in_topic: cmd_vel_smoothed
cmd_vel_out_topic: cmd_vel
source_timeout: 2.0
stop_pub_timeout: 1.0
scan:
  source_timeout: 0.2
```

Keep a complete command chain: controller, optional smoother, Collision
Monitor, then the hardware-facing command consumer.

## Motion compensation and action state

`base_shift_correction` defaults to `true`. It compensates sensor points for
base motion between the observation timestamp and the current processing
cycle. Disabling it reduces processing but is not recommended for fast robots
at modest sensor rates.

Setting the otherwise-empty `state_topic` creates a publisher that reports the
active polygon name and action type.

```yaml
base_shift_correction: true
state_topic: collision_monitor_state
```

## Zone actions and arbitration

Every entry in `polygons` names a zone with `type` and `action_type`:

| Action | Effect |
| --- | --- |
| `stop` | Zero all commanded motion |
| `slowdown` | Multiply speed by `slowdown_ratio` |
| `limit` | Cap linear and angular speed |
| `approach` | Scale motion to maintain `time_before_collision` |

At least `min_points` readings must fall inside a zone. If several zones
trigger, the most restrictive action wins.

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

Polygon `points` are a string containing at least three `[x, y]` pairs;
circles use `radius`. When static geometry is omitted, stop, slowdown, and limit
zones can consume `polygon_sub_topic`, containing polygon points or a circle
radius. An approach polygon can consume `footprint_topic`.

Static geometry wins when both static and subscribed forms are configured.
`polygon_subscribe_transient_local` selects transient-local durability.

```yaml
dynamic_stop:
  type: polygon
  polygon_sub_topic: safety_zone
  polygon_subscribe_transient_local: true
  action_type: stop
  min_points: 4
```

## Humble point-threshold migration

Humble's `max_points` represented the largest safe point count. Newer releases
use `min_points`, the smallest triggering count. Preserve the boundary with:

```text
min_points = max_points + 1
```

## Velocity-dependent safety zones

A `velocity_polygon` chooses the first named sub-polygon whose linear and
angular ranges contain the current command. Order overlaps deliberately and
finish with a range that covers every velocity as a fallback.

For non-holonomic robots, `linear_min` and `linear_max` are signed x velocity,
so reverse is negative. With `holonomic: true`, they are nonnegative resultant
speed magnitudes and may also be constrained with `direction_start_angle` and
`direction_end_angle`.

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

## Observation-source filtering

Point-cloud sources retain points between `min_height` and `max_height` and
beyond `min_range`. `use_global_height: true` filters on an already-global
`height` field instead of transformed `z`. Point-cloud sources may use a
compressed `point_cloud_transport` by selecting `transport_type`; it defaults
to `raw`.

Range sources synthesize arc points at `obstacles_angle` spacing, which defaults
to one degree. Polygon sources sample their boundary at `sampling_distance`,
default `0.1`.

```yaml
observation_sources: [depth, sonar]
depth:
  type: pointcloud
  topic: camera/points
  min_height: 0.05
  max_height: 0.5
  min_range: 0.2
sonar:
  type: range
  topic: sonar
  obstacles_angle: 0.0174533
```

## Costmap observation source

Collision Monitor and Collision Detector accept `nav2_msgs/Costmap` through
`CostmapSource`. Treat this source as caution-required safety configuration and
validate its update timing and cost policy on the deployed map pipeline.

For a configured costmap source, `cost_threshold` defaults to `253`, so only
inscribed or lethal cells become obstacle points. Cost `255` is handled
separately by `treat_unknown_as_obstacle`, which defaults to `true`. Disable it
when large unknown regions must not trigger the monitor.

```yaml
costmap:
  type: costmap
  topic: local_costmap/costmap
  cost_threshold: 254
  treat_unknown_as_obstacle: false
```

## Runtime toggle and temporal debounce

The `Toggle` service and `ToggleCollisionMonitor` BT node can disable all
Collision Monitor polygons while leaving sensor checking active.

Each polygon may set `trigger_consecutive_points` and
`release_consecutive_points` to debounce activation and release across cycles.
Values of `1` and `1` preserve single-cycle behavior.
