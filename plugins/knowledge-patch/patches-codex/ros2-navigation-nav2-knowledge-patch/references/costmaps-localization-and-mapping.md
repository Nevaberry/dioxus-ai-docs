# Costmaps, Localization, and Mapping

## Costmap API and static-map topic

`Costmap2DROS.map_topic` was removed. Configure `map_topic` on the
`StaticLayer` instead:

```yaml
static_layer:
  plugin: "nav2_costmap_2d::StaticLayer"
  map_topic: my_map
```

Constructors consolidate to:

```cpp
Costmap2DROS(name, parent_namespace = "/", use_sim_time = false)
```

The local namespace is inferred from the node name. Update custom composition
code rather than passing the removed topic or namespace shape.

## Plugin Container Layer

The Plugin Container Layer groups selected costmap layers and combines their
result before the parent costmap incorporates it. Use it when a subset of
layers needs its own compositing boundary or shared handling.

## Point-cloud transports

Obstacle and voxel costmap layers, as well as Collision Monitor, can consume
compressed `point_cloud_transport` streams. `transport_type` defaults to `raw`
and may select formats such as `zstd`, `zlib`, or `draco` when the matching
transport is available.

```yaml
pointcloud:
  data_type: "PointCloud2"
  topic: /camera/points
  transport_type: "zstd"
```

Compression changes transport and resource costs, not the point-cloud data
semantics used by the layer.

## Vector Object Server

`nav2_map_server` includes a Vector Object Server that rasterizes configured
circles, polygons, and polygonal chains into an `OccupancyGrid`. The
`AddShapes`, `GetShapes`, and `RemoveShapes` services support dynamic virtual
obstacles, keepout areas, and speed-filter masks.

## Costmap-to-occupancy conversion

`inscribed_obstacle_cost_value` defaults to `99`. It controls conversion of
`INSCRIBED_INFLATED_OBSTACLE` between `Costmap2D` and `OccupancyGrid`, avoiding
the previous `253 → 99 → 251` round-trip mismatch.

## Selective costmap clearing

Requests for `ClearEntireCostmap`, `ClearCostmapAroundRobot`,
`ClearCostmapAroundPose`, and `ClearCostmapExceptRegion` include a `plugins`
list. An empty list preserves the old behavior and clears all eligible layers.
Named entries clear only loaded, clearable plugins.

Validation is atomic: any invalid or non-clearable plugin name makes the whole
request fail without clearing any layer.

## Inflation-layer extensions

An asymmetric inflation field can bias the path-dependent Voronoi boundary for
keep-left or keep-right behavior.

`custom_inscribed_radius`, default `-1.0`, overrides the footprint-derived
radius. A value such as `0.0` bypasses the inscribed region and is unsafe for
ordinary planners or controllers unless they were explicitly designed for
that nonstandard cost representation.

## Repeatable AMCL particle-filter runs

`random_seed` controls AMCL's particle-filter random number generator. Any
nonnegative value makes runs repeatable. The default `-1` seeds from the
current time and retains nondeterministic behavior.

```yaml
amcl:
  ros__parameters:
    random_seed: 42
```

## AMCL reset and map-reload policy

By default, AMCL reuses its last known pose when reset and accepts replacement
maps. Set `always_reset_initial_pose: true` to require a new pose from the
initial-pose topic or from the configured `initial_pose` when
`set_initial_pose: true`.

Set `first_map_only: true` only when later maps arriving on `map_topic` should
be ignored.

```yaml
amcl:
  ros__parameters:
    always_reset_initial_pose: true
    set_initial_pose: true
    initial_pose: {x: 1.0, y: 2.0, z: 0.0, yaw: 0.5}
    first_map_only: false
```

## Timestamped dynamic footprints

`subscribe_to_stamped_footprint: true` changes the costmap footprint
subscription from `Polygon` to `PolygonStamped`. This lets each footprint
update carry its own timestamp and frame.

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      subscribe_to_stamped_footprint: true
```

The publisher and every remapping must agree on the changed message type.

## Startup transform deadline

During configuration, a costmap waits `initial_transform_timeout` seconds for
the robot-base-to-global-frame transform. The default is `60.0`; expiry aborts
configuration.

```yaml
initial_transform_timeout: 60.0
```

## Visualization height

`map_vis_z` vertically offsets only the visualized costmap, leaving planning
data unchanged. A small offset such as `-0.008` can prevent coplanar RViz
surfaces from flickering.

```yaml
map_vis_z: -0.008
```

## Filters run after ordinary layers

Names in `filters` are loaded as plugins but remain separate from `plugins`.
They run on top of the already combined layered costmap, preventing ordinary
layers from interfering with keepout, speed, or binary filters. Every filter
name must contain a `plugin` parameter in its matching namespace.

```yaml
filters: [keepout_filter, speed_filter]
keepout_filter:
  plugin: "nav2_costmap_2d::KeepoutFilter"
speed_filter:
  plugin: "nav2_costmap_2d::SpeedFilter"
```

Speed Filter may additionally enable path lookahead to apply the strictest
upcoming limit before entry into a speed zone; that mode is disabled by
default.
