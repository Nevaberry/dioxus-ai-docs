# Planning, control, and smoothing

## Planner selection by geometry

NavFn, Smac 2D, and Theta Star plan in grid space. They suit circular
differential or omnidirectional robots because they do not guarantee drivable
paths for non-circular bodies or curvature-constrained Ackermann and legged
platforms. NavFn specifically checks a circular radius derived from the
footprint.

Smac Hybrid-A* uses full-footprint collision checking and Dubins or
Reeds-Shepp motion models for arbitrary-shaped Ackermann and legged robots.
Smac Lattice supplies kinematically valid control sets for differential,
omnidirectional, and Ackermann vehicles of any shape.

## Controller selection by motion and task

DWB normally targets differential and omnidirectional robots. Ackermann or
legged use requires a curvature-aware trajectory generator. TEB and MPPI cover
differential, omnidirectional, Ackermann, and legged robots. RPP and Vector
Pursuit omit omnidirectional motion.

Choose DWB or TEB when their dynamic-obstacle avoidance fits the task, RPP for
exact path following, MPPI for model-predictive control, and Vector Pursuit for
high-speed or resource-constrained tracking.

## Controller Server timing and execution

Controller Server waits up to `costmap_update_timeout` (default `0.3` seconds)
for a fully updated local costmap before computing a command. Planner Server
uses the same parameter with a `1.0`-second default before planning.

```yaml
controller_server:
  ros__parameters:
    costmap_update_timeout: 0.3
planner_server:
  ros__parameters:
    costmap_update_timeout: 1.0
```

`use_realtime_priority: true` raises the controller execution thread to
priority `90`. It defaults to `false`; grant the process user an adequate
`rtprio` limit first.

```text
robot soft rtprio 99
robot hard rtprio 99
```

`failure_tolerance` is the time controller-plugin exceptions may continue
before `FollowPath` fails. `0.0` (the default) disables tolerance, `-1.0`
permits failures indefinitely, and a positive value is the timeout.

```yaml
controller_server:
  ros__parameters:
    failure_tolerance: 0.3
```

Controller Server buffers odometry for `odom_duration` seconds when estimating
robot speed. The default window is `0.3` seconds and `odom_topic` defaults to
`odom`.

```yaml
controller_server:
  ros__parameters:
    odom_topic: odom
    odom_duration: 0.3
```

`control_frequency` is fixed after startup. `publish_zero_velocity` defaults
to `true`; disable it only when the server must not emit a final zero command.

## Centralized path handling

Controller Server owns transformed-plan pruning through a configurable path
handler such as `nav2_controller::FeasiblePathHandler`. Move path-handling
parameters out of DWB, RPP, Graceful Controller, and MPPI and into the server.

Custom `GoalChecker::isGoalReached()` receives the transformed plan.
`Controller::setPlan()` becomes a lightweight `newPathReceived()`, and
`computeVelocityCommands()` receives both the processed plan and global goal.

## DWB and Graceful Controller

DWB's `limit_vel_cmd_in_traj` defaults to `false`. When enabled, trajectory
generation is constrained using the robot's current velocity.

Graceful Controller replaces `motion_target_dist` with `min_lookahead` and
`max_lookahead`, renames `final_rotation` to `prefer_final_rotation`, creates
orientations when the path omits them, and adds `v_angular_min_in_place`.

## Rotation Shim

Rotation Shim can disengage at `angular_disengage_threshold`, decelerate toward
the target using `max_angular_accel`, and honor path-point orientations with
`use_path_orientations` (default `false`).

`closed_loop` defaults to `true` and uses odometry. Setting it to `false` uses
the last commanded velocity and requires responsive hardware plus appropriate
acceleration limits.

The primary controller is a nested parameter group. Move both its plugin and
its parameters beneath `primary_controller`:

```yaml
primary_controller:
  plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
  desired_linear_vel: 1.0
  lookahead_dist: 0.6
```

## Regulated and Dynamic Window Pure Pursuit

RPP enforces `min_distance_to_obstacle` beyond a velocity-scaled carrot, capped
by `max_lookahead_dist`. `allow_obstacle_checking_beyond_goal` defaults to
`false`; when enabled, it checks past the goal up to the minimum distance. This
requires velocity-scaled lookahead and a positive minimum distance.

Dynamic Window Pure Pursuit lets velocity and acceleration constraints
participate directly in command generation. Its maximum-speed parameter is
`max_linear_vel`, replacing `desired_linear_vel`. Velocity Smoother limits must
be at least as permissive as corresponding controller limits.

The former RPP `stateful` parameter retained XY completion while the robot
aligned yaw. Goal checkers now provide this via `isGoalXYReached()`, making the
behavior consistent across RPP, Graceful Controller, and Rotation Shim.

## SMAC planners

Smac Hybrid and Smac Lattice accept `goal_heading_mode`, which considers
multiple acceptable goal orientations in one request. Lattice also provides
`coarse_search_resolution` for its orientation search. These settings support
bidirectional or all-direction approaches without issuing separate plans.

Multiple SMAC planner instances can coexist and be selected at runtime. Smac
Lattice enables omnidirectional analytic expansion automatically when primitive
metadata declares `motion_model: "omni"`.

Custom `BaseGlobalPlanner::createPath()` implementations must accept a vector
of intermediate `PoseStamped` viapoints.

## MPPI safety, plugins, and observability

Kilted's MPPI Cost Critic `near_collision_cost` defaults to `253` and applies critical
cost before actual collision. `publish_optimal_trajectory` publishes poses,
velocities, and timestamps as `nav2_msgs/Trajectory` for visualization or
downstream control.

Motion models require a named plugin group even though `motion_model` defaults
to `diff_drive`. Plugins replace the old `DiffDrive`, `Omni`, and `Ackermann`
string values.

```yaml
motion_model: "diff_drive"
diff_drive:
  plugin: "mppi::DiffDriveMotionModel"
```

`OptimalTrajectoryValidator` separately checks the selected trajectory; its
default validator checks collisions.

Set `open_loop: true` to estimate the initial state from the last command.
Compensate per-axis model delay with `model_delay_vx`, `model_delay_vy`, and
`model_delay_wz`, each defaulting to `0.0`.

With visualization enabled, `critic_index_to_visualize` selects total or
per-critic trajectory coloring. Remove `publish_critics_stats`; critic
statistics publish automatically in visualization mode.

## Partial multi-pose planning

Planner Server's dynamic `allow_partial_planning` parameter lets
`compute_path_through_poses` return the reachable prefix instead of failing the
whole request. The result reports the last reached goal in
`last_reached_index`. This behavior is disabled by default.

## Goal checkers

`PositionGoalChecker` ignores goal orientation. Symmetric yaw tolerance lets a
symmetric robot avoid an unnecessary 180-degree final rotation.

`AxisGoalChecker` provides independent along-path and cross-track tolerances
and can permit valid overshoot. Adaptive Tolerance Goal Checker accepts either
a fine tolerance or a coarse tolerance combined with stopped, stalled, or
finish-line-passed evidence.

## Smoothing

Route Server can replace graph corners with tangent circular arcs using
`smooth_corners` and `smoothing_radius`. Nearly straight edges and arcs that do
not fit inside their edges fall back to linear interpolation.

Savitzky-Golay exposes `window_size` (default `7`) and `poly_order` (default
`3`).

Constrained Smoother now evaluates `weight * residual²`; the former behavior
was effectively quartic. Retune existing weights after adopting the corrected
formulation.
