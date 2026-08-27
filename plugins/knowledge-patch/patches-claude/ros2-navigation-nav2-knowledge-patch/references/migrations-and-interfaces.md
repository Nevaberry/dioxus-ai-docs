# Migrations and interfaces

## Distribution support status

Rolling Ridley is the development distribution. Kilted Kaiju and Jazzy Jalisco
have active support, Humble Hawksbill is maintained, and Iron Irwini and
Galactic Geochelone are end-of-life.

## Action errors and result ports

In Kilted, Nav2 action results carry contextual `error_msg` strings through BT Navigator.
The old `error_code_names` parameter causes a startup exception. Replace it
with prefixes, and expose corresponding `error_code_id` and `error_msg` ports
on the relevant BT action nodes.

```yaml
error_code_name_prefixes: [compute_path, follow_path, spin, route]
```

```xml
<FollowPath path="{path}" error_code_id="{follow_path_error_code}"
            error_msg="{follow_path_error_msg}"/>
```

## Stamped velocity commands

In Kilted, Nav2 `cmd_vel` publishers and subscribers use `geometry_msgs/TwistStamped` by
default without changing topic names. Stamps allow stale-command rejection.
Set `enable_stamped_cmd_vel: false` on every affected node only when retaining
the legacy `Twist` interface.

## Multi-pose messages and waypoint status

`NavigateThroughPoses`, `ComputePathThroughPoses`, and related BT nodes use
`nav_msgs/Goals`, not a raw `PoseStamped` vector. Access navigation poses as
`poses.goals` and compute-path goals as `goals.goals`.

`NavigateThroughPoses` reports `WaypointStatus` values: `PENDING`, `COMPLETED`,
`SKIPPED`, or `FAILED`. This replaces `MissedWaypoint`. Pruning BT nodes must
connect matching `input_waypoint_statuses` and `output_waypoint_statuses` ports.

## Namespaced bringup

`use_namespace` was removed from `nav2_bringup`; `namespace` is always applied
and defaults to `/`. Shared RViz and parameter files use relative topics such
as `scan`, which resolve beneath the robot namespace. An absolute `/scan`
deliberately remains global. Costmap layers can use `joinWithParentNamespace()`
to avoid resolving beneath a layer's private namespace.

## Costmap construction API

`Costmap2DROS.map_topic` was removed. Configure `map_topic` on the Static Layer:

```yaml
static_layer:
  plugin: "nav2_costmap_2d::StaticLayer"
  map_topic: my_map
```

Constructors consolidate to
`Costmap2DROS(name, parent_namespace = "/", use_sim_time = false)`; the local
namespace is inferred from the node name. The Plugin Container Layer can group
selected costmap layers before combining them with the parent costmap.

## Lifecycle and ROS wrapper migration

In Lyrical, `nav2_ros_common` replaces `nav2_util` lifecycle utilities with
`nav2::LifecycleNode` and Nav2 wrappers for services, actions, publishers, and
subscriptions. Custom plugins and task servers must call the lifecycle node's
`create_*` factories instead of directly constructing wrappers.

```cpp
main_client_ = node->create_client<SrvT>(service_name, false);
action_client_ = node->create_action_client<ActionT>(action_name, callback_group);
```

When QoS is omitted, wrappers use `nav2::qos::StandardTopicQoS`: reliable,
volatile, depth 10. An explicit subscription QoS argument now follows the
callback. Service callbacks include the `rmw_request_id_t` header. Wrappers use
`introspection_mode` and `allow_parameter_qos_overrides`. Remove
`action_server_result_timeout`; it no longer exists.

## Docking migration

Kilted docking supports non-charging static infrastructure and dynamic docks, with a
`simple_non_charging_dock` plugin and an RViz docking panel. Docking-server
collision checking is enabled by default.

`dock_backwards` moved from the server into each plugin as `dock_direction`,
whose default is `forward` and whose other value is `backward`.
`reverse_to_dock: true` lets simple plugins detect from a forward staging pose
and then dead-reckon backward into the dock.

In Lyrical, external detection rotations for simple dock plugins change from
Rz→Rx→Ry to Rx→Ry→Rz. Recalculate non-default configurations that use all axes. Custom
`ChargingDock` and `NonChargingDock` plugins must implement
`startDetectionProcess()` and `stopDetectionProcess()`. Simple plugins add
`detector_service_name`, `detector_service_timeout`, and `subscribe_toggle` for
on-demand perception.

## BT node and port renames

`IsStopped` becomes `CheckStopStatus`, `IsPathValid` becomes `ValidatePath`, and
`IsPoseOccupied` becomes `CheckPoseOccupancy`. These nodes may return `RUNNING`,
so they are actions rather than conditions.

`ValidatePath` and the `IsPathValid` service rename `check_full_path` to the
oppositely worded `stop_at_first_collision`. Old `false` equals new `true`,
which remains the default. `max_lookahead_distance` defaults to `-1.0` for full
path validation; a positive value limits checking to that forward distance.

`TruncatePathLocal` renames `robot_frame` to `robot_base_frame`. If omitted, it
inherits BT Navigator's `robot_base_frame` parameter.

```xml
<TruncatePathLocal robot_base_frame="base_link" ... />
```

## Controller and goal behavior migrations

Controller Server's `control_frequency` is no longer dynamically changeable;
configure it before startup.

In Kilted, `PositionGoalChecker` ignores goal orientation and RPP's `stateful`
mode keeps XY completion while aligning yaw. Lyrical removes that controller
parameter; goal checkers own the behavior through `isGoalXYReached()`,
consistently across RPP, Graceful Controller, and Rotation Shim.

Dynamic Window Pure Pursuit renames `desired_linear_vel` to `max_linear_vel`.
Velocity Smoother limits must be at least as permissive as the corresponding
controller constraints.

The lifecycle-node `bond_heartbeat_period` default is `0.25` seconds for all
lifecycle nodes and Lifecycle Manager. Explicit `0.1` values remain effective,
so remove or update them to adopt the new default.

## Planner and controller plugin API changes

Custom `BaseGlobalPlanner` implementations must change `createPath()` to accept
a vector of intermediate `PoseStamped` viapoints.

Controller Server now owns transformed-plan pruning through a path-handler
plugin such as `nav2_controller::FeasiblePathHandler`. Custom
`GoalChecker::isGoalReached()` receives the transformed plan.
`Controller::setPlan()` becomes the lightweight `newPathReceived()`, and
`computeVelocityCommands()` receives the processed plan and global goal. Move
path-handling parameters formerly owned by DWB, RPP, Graceful Controller, and
MPPI to Controller Server.

## MPPI migration

MPPI motion models require a named plugin group even though `motion_model`
defaults to `diff_drive`. Plugin implementations replace the old `DiffDrive`,
`Omni`, and `Ackermann` string values.

```yaml
motion_model: "diff_drive"
diff_drive:
  plugin: "mppi::DiffDriveMotionModel"
```

`OptimalTrajectoryValidator` validates the selected trajectory independently;
the default validator checks collisions. With visualization enabled,
`critic_index_to_visualize` selects total or per-critic coloring.
`publish_critics_stats` is removed because critic statistics publish
automatically in that mode.

## Smoother migration

The Constrained Smoother corrects its cost formulation from effectively quartic
weighted residuals to `weight * residual²`. Retune existing weights because
the same values no longer express the same optimization.

The Savitzky-Golay smoother exposes `window_size` (default `7`) and
`poly_order` (default `3`) instead of fixing those values.

## RViz and isolated testing

The Nav2 RViz panel can select BT XML per request, accept exact coordinates and
frame IDs, and build, edit, save, or load multi-goal lists for
`NavigateThroughPoses` and Waypoint Following.

Build with `--cmake-args -DUSE_ISOLATED_TESTS=ON` to run `rmw_zenoh_cpp` tests
without launching a separate Zenoh router.
