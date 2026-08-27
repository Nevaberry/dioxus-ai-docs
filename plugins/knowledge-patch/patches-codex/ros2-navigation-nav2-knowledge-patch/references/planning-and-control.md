# Planning and Control

## Choose a planner by geometry and motion model

NavFn, Smac 2D, and Theta Star plan in grid space. They are best suited to
circular differential or omnidirectional robots because they do not guarantee
drivable paths for non-circular bodies or curvature-constrained Ackermann and
legged platforms. NavFn specifically collision-checks a circular radius derived
from the footprint.

Smac Hybrid-A* uses full-footprint collision checks with Dubins or Reeds-Shepp
motion models, making it appropriate for arbitrary-shaped Ackermann and legged
robots. Smac Lattice provides kinematically valid control sets for
differential, omnidirectional, and Ackermann vehicles of any shape.

## Choose a controller by task

DWB normally targets differential and omnidirectional robots; Ackermann and
legged use requires a curvature-aware trajectory generator. TEB and MPPI cover
differential, omnidirectional, Ackermann, and legged systems. RPP and Vector
Pursuit omit omnidirectional motion.

As a task-oriented starting point, use DWB or TEB for dynamic-obstacle
avoidance, RPP for exact path following, MPPI for model-predictive control, and
Vector Pursuit for high-speed or resource-constrained tracking.

## Planner and controller costmap freshness

Before work begins, each server waits for its costmap to be fully updated:

```yaml
controller_server:
  ros__parameters:
    costmap_update_timeout: 0.3
planner_server:
  ros__parameters:
    costmap_update_timeout: 1.0
```

The shown values are the respective defaults. Increase them when costmap
latency is expected; do not use the controller's shorter default as the
planner's implicit value.

## Controller execution and failure timing

`control_frequency` is no longer dynamically mutable. Set it before Controller
Server starts.

`use_realtime_priority: true` raises the controller execution thread to
priority `90`. It defaults to false, and the process user needs a sufficient
`rtprio` limit first, for example:

```text
robot soft rtprio 99
robot hard rtprio 99
```

`failure_tolerance` is the number of seconds controller-plugin exceptions may
continue before `FollowPath` fails. Its default `0.0` disables tolerance,
`-1.0` allows failures indefinitely, and a positive value is the timeout.

```yaml
controller_server:
  ros__parameters:
    failure_tolerance: 0.3
```

Controller Server buffers odometry for `odom_duration` seconds when estimating
speed. The default topic is `odom` and the default window is `0.3` seconds.

```yaml
controller_server:
  ros__parameters:
    odom_topic: odom
    odom_duration: 0.3
```

`publish_zero_velocity` defaults to `true`. Disable it only if another command
owner must suppress Controller Server's final zero-velocity publication.

## DWB and Graceful Controller changes

DWB's `limit_vel_cmd_in_traj`, default `false`, makes trajectory generation
respect the robot's current velocity when limiting candidate commands.

Graceful Controller changes its lookahead and rotation interface:

- Replace `motion_target_dist` with `min_lookahead` and `max_lookahead`.
- Rename `final_rotation` to `prefer_final_rotation`.
- Use `v_angular_min_in_place` for the minimum in-place angular speed.
- Missing path orientations are synthesized rather than required from the
  input path.

## Rotation Shim configuration

Rotation Shim can disengage at `angular_disengage_threshold`, decelerate toward
its target with `max_angular_accel`, and use path-point orientations when
`use_path_orientations: true`; that option defaults to false.

`closed_loop` defaults to `true` and uses odometry. Setting it false estimates
state from the last commanded velocity, which requires responsive hardware and
appropriate acceleration limits.

The primary controller is now a nested parameter group. Move both its plugin
and parameters under `primary_controller`:

```yaml
primary_controller:
  plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
  desired_linear_vel: 1.0
  lookahead_dist: 0.6
```

## SMAC planning changes

Smac Hybrid and Smac Lattice accept `goal_heading_mode`, allowing one planning
request to consider multiple acceptable goal orientations. This supports
bidirectional or all-direction approaches without separate requests. Lattice
also exposes `coarse_search_resolution` for its orientation search.

Multiple SMAC planner instances can coexist and be selected at runtime. Smac
Lattice automatically enables omnidirectional analytic expansion when its
primitive metadata declares `motion_model: "omni"`.

Custom `BaseGlobalPlanner` implementations must update `createPath()` to accept
a vector of intermediate `PoseStamped` viapoints.

## MPPI safety, plugins, and observability

The MPPI cost critic's `near_collision_cost` defaults to `253`, applying
critical cost before actual collision. `publish_optimal_trajectory` publishes
poses, velocities, and timestamps as `nav2_msgs/Trajectory` for visualization
or downstream control.

Motion models require a named plugin group even though `motion_model` defaults
to `diff_drive`. Plugin groups replace the old `DiffDrive`, `Omni`, and
`Ackermann` string values.

```yaml
motion_model: "diff_drive"
diff_drive:
  plugin: "mppi::DiffDriveMotionModel"
```

`OptimalTrajectoryValidator` validates the selected trajectory separately;
the default validator performs collision checks.

Set `open_loop: true` to estimate the initial state from the last command.
Per-axis delay compensation uses `model_delay_vx`, `model_delay_vy`, and
`model_delay_wz`, each defaulting to `0.0`.

With visualization enabled, `critic_index_to_visualize` selects total or
per-critic trajectory coloring. Remove `publish_critics_stats`; critic
statistics publish automatically in visualization mode.

## RPP obstacle checking and dynamic-window control

RPP enforces `min_distance_to_obstacle` beyond a velocity-scaled carrot, capped
by `max_lookahead_dist`. `allow_obstacle_checking_beyond_goal`, default false,
continues checking beyond the goal up to that minimum distance. It requires
velocity-scaled lookahead and a positive minimum distance.

RPP can opt into Dynamic Window Pure Pursuit so velocity and acceleration
constraints participate directly in command generation. In that mode the
maximum-speed parameter is renamed from `desired_linear_vel` to
`max_linear_vel`. Velocity Smoother limits must be at least as permissive as
the controller's matching limits.

## Goal handling and goal checkers

`PositionGoalChecker` ignores goal orientation.

Kilted RPP's `stateful` mode remembered XY completion while aligning yaw.
Lyrical removes that controller parameter and moves the behavior to goal
checkers through `isGoalXYReached()`, making it consistent across RPP,
Graceful, and Rotation Shim.

Additional goal-checking options include:

- Symmetric yaw tolerance, which avoids needless 180-degree final rotation for
  symmetric robots.
- `AxisGoalChecker`, with independent along-path and cross-track tolerances and
  optional valid overshoot.
- Adaptive Tolerance Goal Checker, which accepts either fine tolerance or a
  coarse tolerance plus evidence that the robot stopped, stalled, or crossed
  the finish line.

Custom `GoalChecker::isGoalReached()` implementations now receive the
transformed plan.

## Centralized controller path handling

Controller Server owns transformed-plan pruning through a configurable
path-handler plugin such as `nav2_controller::FeasiblePathHandler`. Move
path-transformation and pruning parameters formerly held by DWB, RPP, Graceful,
and MPPI to the server's path handler.

The plugin contracts change with that ownership:

- `Controller::setPlan()` becomes lightweight `newPathReceived()`.
- `computeVelocityCommands()` receives the processed plan and global goal.
- `GoalChecker::isGoalReached()` receives the transformed plan.

## Partial multi-pose planning

Planner Server's dynamic `allow_partial_planning` parameter lets
`compute_path_through_poses` return the reachable prefix instead of failing the
entire request. It defaults to disabled. When enabled, inspect
`last_reached_index` in the result to identify the final reached goal.

## Smoother retuning and controls

The Savitzky-Golay smoother exposes `window_size`, default `7`, and
`poly_order`, default `3`, instead of fixing those values.

Constrained Smoother corrects its cost formula from effectively quartic
weighted residuals to `weight * residual²`. Retune existing weights; identical
numbers no longer represent the same optimization.

## Speed-zone anticipation

Speed Filter's disabled-by-default `enable_path_lookahead` mode examines a
velocity-dependent window along the planned path and applies the strictest
speed limit early. Use it when the robot needs distance to decelerate before
entering a restricted zone.
