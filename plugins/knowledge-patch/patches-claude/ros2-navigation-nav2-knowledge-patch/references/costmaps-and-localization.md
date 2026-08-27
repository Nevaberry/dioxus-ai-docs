# Costmaps and localization

## Static Layer and composition

Configure `map_topic` on the Static Layer, not on `Costmap2DROS`.

```yaml
static_layer:
  plugin: "nav2_costmap_2d::StaticLayer"
  map_topic: my_map
```

The consolidated constructor is
`Costmap2DROS(name, parent_namespace = "/", use_sim_time = false)`; the node
name determines the local namespace. The Plugin Container Layer groups selected
layers before combining them into the parent costmap.

Costmap layers can use `joinWithParentNamespace()` when a relative topic should
resolve beneath the robot namespace rather than beneath a layer's private
namespace.

## Layers and filters

Costmap entries in `filters` are loaded as plugins but remain separate from
ordinary `plugins`. Filters are applied after the normal layers have been
combined, so keepout, speed, and binary policies do not interfere with the
ordinary layer update process. Every listed filter name must have a matching
namespaced `plugin` parameter.

```yaml
filters: [keepout_filter, speed_filter]
keepout_filter:
  plugin: "nav2_costmap_2d::KeepoutFilter"
speed_filter:
  plugin: "nav2_costmap_2d::SpeedFilter"
```

## Selective clearing

Requests for `ClearEntireCostmap`, `ClearCostmapAroundRobot`,
`ClearCostmapAroundPose`, and `ClearCostmapExceptRegion` accept a `plugins`
list. An empty list clears everything. Named entries clear only loaded,
clearable plugins. If any name is invalid or not clearable, the entire request
fails without clearing anything.

## Point-cloud transport

Obstacle and voxel layers can consume compressed `point_cloud_transport`
streams. `transport_type` defaults to `raw`; supported alternatives include
`zstd`, `zlib`, and `draco`.

```yaml
pointcloud:
  data_type: "PointCloud2"
  topic: /camera/points
  transport_type: "zstd"
```

Collision Monitor can use the same transport setting for its point-cloud
sources.

## Cost conversion

`inscribed_obstacle_cost_value` defaults to `99`. It controls conversion of
`INSCRIBED_INFLATED_OBSTACLE` between `Costmap2D` and `OccupancyGrid`, avoiding
the earlier `253→99→251` mismatch.

## Inflation options

An asymmetric inflation field can bias a path-dependent Voronoi boundary for
keep-left or keep-right behavior.

`custom_inscribed_radius` defaults to `-1.0`, which leaves the radius derived
from the footprint. A value such as `0.0` bypasses the inscribed region and is
unsafe for ordinary planners or controllers unless they were explicitly
designed for that cost representation.

## Speed-zone anticipation

Speed Filter's `enable_path_lookahead` mode is disabled by default. When
enabled, it examines a velocity-dependent window along the planned path and
applies the strictest speed limit early, allowing the robot to decelerate before
entering a restricted zone.

## Timestamped footprints

`subscribe_to_stamped_footprint: true` changes a costmap's footprint
subscription from `Polygon` to `PolygonStamped`. Dynamic footprint updates can
then carry their own timestamp and frame.

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      subscribe_to_stamped_footprint: true
```

## Startup transform deadline

During configuration, a costmap waits `initial_transform_timeout` seconds for
the robot-base-to-global-frame transform. The default is `60.0`; expiration
aborts configuration.

```yaml
initial_transform_timeout: 60.0
```

## Visualization height

`map_vis_z` changes only the rendered costmap's vertical offset, not planning
data. A small value such as `-0.008` can stop coplanar RViz displays from
flickering.

```yaml
map_vis_z: -0.008
```

## Repeatable AMCL runs

`random_seed` controls the AMCL particle-filter random-number generator. Any
nonnegative value makes runs repeatable. The default `-1` seeds from the current
time and preserves nondeterministic behavior.

```yaml
amcl:
  ros__parameters:
    random_seed: 42
```

## AMCL reset and map policy

AMCL normally reuses its last pose after reset and accepts replacement maps.
Set `always_reset_initial_pose: true` to require a new pose from the
initial-pose topic or from `initial_pose` together with
`set_initial_pose: true`. Set `first_map_only: true` only when later maps on
`map_topic` must be ignored.

```yaml
amcl:
  ros__parameters:
    always_reset_initial_pose: true
    set_initial_pose: true
    initial_pose: {x: 1.0, y: 2.0, z: 0.0, yaw: 0.5}
    first_map_only: false
```
