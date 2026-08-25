---
name: ros2-navigation-nav2-knowledge-patch
description: Nav2
version: 1.3.12
license: MIT
metadata:
  author: Nevaberry
---


# Nav2 Knowledge Patch

Use this skill when designing, configuring, migrating, extending, or debugging
Nav2 systems. Start with the migration notes when upgrading a robot, then open
the task-specific reference for complete parameters, defaults, and constraints.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-interfaces.md](references/migrations-and-interfaces.md) | Distribution status, message and action migrations, namespaces, lifecycle wrappers, docking, RViz, and testing |
| [behavior-trees-and-navigation.md](references/behavior-trees-and-navigation.md) | BT nodes and controls, navigator blackboards, plugin selectors, route following, waypoint status, and introspection |
| [planning-control-and-smoothing.md](references/planning-control-and-smoothing.md) | Planner and controller selection, path handling, SMAC, RPP, DWB, MPPI, goal checking, and smoothers |
| [servers-behaviors-and-tools.md](references/servers-behaviors-and-tools.md) | Controller, Planner, Behavior, Following, Vector Object, Route, and loopback servers |
| [costmaps-and-localization.md](references/costmaps-and-localization.md) | Costmap layers and filters, transport, inflation, speed zones, footprint handling, and AMCL |
| [collision-monitor.md](references/collision-monitor.md) | Command pipeline, fail-safe timing, zones, observation sources, runtime controls, and costmap sources |

## Upgrade-critical interface changes

### Velocity commands are stamped by default

Nav2 nodes publish and subscribe to `geometry_msgs/TwistStamped` on the existing
`cmd_vel` topic names. Set `enable_stamped_cmd_vel: false` on every affected
node only when the complete command chain must retain `Twist`.

### Propagate action errors by prefix and BT ports

Remove `error_code_names`; it now causes startup failure. Configure
`error_code_name_prefixes`, and expose matching `error_code_id` and
`error_msg` ports on relevant BT action nodes.

```yaml
error_code_name_prefixes: [compute_path, follow_path, spin, route]
```

### Use `nav_msgs/Goals` for multi-pose requests

`NavigateThroughPoses`, `ComputePathThroughPoses`, and their BT nodes no longer
use raw `PoseStamped` vectors. Read navigation poses from `poses.goals` and
compute-path poses from `goals.goals`. Preserve the new `WaypointStatus` list
through pruning nodes using `input_waypoint_statuses` and
`output_waypoint_statuses`.

### Apply namespaces without `use_namespace`

Remove the `nav2_bringup.use_namespace` argument. `namespace` is always applied
and defaults to `/`. Relative topics such as `scan` resolve under the robot
namespace; `/scan` remains global.

### Move and rename migrated parameters

- Put `map_topic` on each costmap `StaticLayer`, not `Costmap2DROS`.
- Nest the Rotation Shim controller under `primary_controller`.
- Replace Graceful Controller `motion_target_dist` with `min_lookahead` and
  `max_lookahead`, and `final_rotation` with `prefer_final_rotation`.
- Replace Dynamic Window Pure Pursuit `desired_linear_vel` with
  `max_linear_vel`.
- Move transformed-plan pruning and its parameters to Controller Server's path
  handler; controller plugins receive the processed plan and global goal.
- Replace `ValidatePath.check_full_path` with the inverse
  `stop_at_first_collision`; old `false` maps to new `true`.
- Rename `TruncatePathLocal.robot_frame` to `robot_base_frame`.
- Remove `action_server_result_timeout` and configure `control_frequency`
  before Controller Server startup.

### Update custom plugins and ROS wrappers

Use `nav2::LifecycleNode` and its `create_*` factories for Nav2 service, action,
publisher, and subscription wrappers. Service callbacks include an
`rmw_request_id_t` header. Custom planner `createPath()` implementations accept
intermediate viapoints; goal checkers receive the transformed plan; controllers
use `newPathReceived()` instead of a heavy `setPlan()` path handoff.

## Behavior-tree essentials

### Choose plugins at runtime

The standard tree can select progress checker, goal checker, path handler,
controller, and planner IDs from named selector topics. Always set a default ID
on each selector and pass its blackboard output to the consuming action.

### Preserve valid paths near the goal

Suppress replanning only when the goal is unchanged, the robot is near it, and
the truncated remaining path validates. If any check fails, compute a new path.

### Understand control-node execution

- `NonblockingSequence` ticks later children while an earlier one is running.
- `PauseResumeController` pairs with `PersistentSequence` to resume at a saved
  bidirectional child index.
- `RoundRobin` no longer wraps by default; set `wrap_around="true"` for legacy
  cycling.

Navigator plugin parameters own their blackboard IDs. Load reusable BT subtrees
from `bt_search_directories`, and give selectable trees unique IDs rather than
reusing `MainTree`.

## Planning and control choices

### Match the planner to geometry

Use NavFn, Smac 2D, or Theta Star for circular differential or omnidirectional
robots. Use Smac Hybrid-A* when arbitrary footprint and curvature constraints
matter, or Smac Lattice for kinematically valid differential, omnidirectional,
or Ackermann control sets.

### Match the controller to motion and task

- DWB normally serves differential and omnidirectional bases; Ackermann and
  legged bases need a curvature-aware trajectory generator.
- TEB and MPPI cover differential, omnidirectional, Ackermann, and legged
  motion; use them when their optimization or dynamic-obstacle behavior fits.
- RPP emphasizes exact path tracking and does not support omnidirectional
  motion.
- Vector Pursuit targets high-speed or resource-constrained tracking and does
  not support omnidirectional motion.

### Treat controller-path handling as a server concern

Configure a Controller Server path-handler plugin such as
`nav2_controller::FeasiblePathHandler`. Move pruning parameters out of DWB,
RPP, Graceful, and MPPI. Keep each controller's new-path callback lightweight.

### Configure MPPI plugins explicitly

Even though `motion_model` defaults to `diff_drive`, declare its named plugin
group. Use `OptimalTrajectoryValidator` separately for final trajectory safety.

```yaml
motion_model: "diff_drive"
diff_drive:
  plugin: "mppi::DiffDriveMotionModel"
```

Retune Constrained Smoother weights after upgrading: its corrected objective is
`weight * residual²`, not the former effectively quartic weighting.

## Server timing and failure behavior

- Controller Server waits `costmap_update_timeout: 0.3` seconds by default;
  Planner Server defaults to `1.0` second.
- `failure_tolerance: 0.0` rejects the first controller exception, `-1.0`
  tolerates failures indefinitely, and positive values set a time allowance.
- `odom_duration` defaults to `0.3` seconds for Controller Server velocity
  estimation.
- `use_realtime_priority: true` requests controller-thread priority `90` and
  requires an adequate OS `rtprio` limit.
- Lifecycle bond heartbeat defaults to `0.25` seconds; explicit legacy values
  continue to override it.

## Safety and map configuration

### Keep the velocity chain ordered

Collision Monitor normally consumes `cmd_vel_smoothed` and publishes the
safety-adjusted command on `cmd_vel`. A stale source stops the robot after
`source_timeout` (default `2.0` seconds); `0.0` disables the check. Keep
`base_shift_correction` enabled for moving robots unless its processing cost is
deliberately accepted.

### Configure zones deterministically

Each polygon entry needs a geometry `type` and an `action_type`: `stop`,
`slowdown`, `limit`, or `approach`. At least `min_points` observations must be
inside, and simultaneous zones resolve to the most restrictive result. When
migrating from Humble, use `min_points = max_points + 1`.

Velocity polygons use the first matching sub-polygon, so order overlaps and end
with a range covering every velocity. For holonomic robots, linear bounds are
nonnegative speed magnitudes and may be direction-gated.

### Separate layers from filters

Costmap `plugins` build the layered map first; `filters` then apply keepout,
speed, or binary policy on top. Give every listed filter a matching namespaced
`plugin` parameter. Set a Static Layer's `map_topic` in that layer's namespace.

### Handle unsafe cost encodings deliberately

`custom_inscribed_radius: 0.0` bypasses the inscribed region and is unsafe for
ordinary planners and controllers. Collision Monitor costmap sources treat
unknown cost `255` separately from `cost_threshold`; disable
`treat_unknown_as_obstacle` only when unknown space must not stop the robot.

## Working method

1. Identify the robot geometry, motion model, ROS distribution, and every node
   that participates in velocity, planning, and safety pipelines.
2. Apply interface and parameter migrations before tuning algorithms.
3. Select planners, controllers, goal checkers, and path handlers as a coherent
   set, then configure their server-owned timing and failure policy.
4. Validate BT blackboard ports, cancellation behavior, and navigation result
   messages end to end.
5. Exercise costmap filters and Collision Monitor zones with stale, unknown,
   overlapping, and reverse-motion cases.
6. Use deterministic AMCL seeds and loopback simulation for repeatable
   integration tests where physical realism is not required.
