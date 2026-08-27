# Planner Plugins and Adapters

## OMPL optimization and termination

An OMPL planner configuration can select any of these objectives:

- `PathLengthOptimizationObjective` (default)
- `MechanicalWorkOptimizationObjective`
- `MaximizeMinClearanceObjective`
- `StateCostIntegralObjective`
- `MinimaxObjective`

`termination_condition` accepts `Iteration[num]`,
`CostConvergence[solutionsWindow,epsilon]`, or `ExactSolution`.
`allowed_planning_time` remains a hard upper bound.

```yaml
RRTstarkConfigDefault:
  type: geometric::RRTstar
  optimization_objective: MaximizeMinClearanceObjective
  termination_condition: CostConvergence[10,.1]
```

## Persistent OMPL roadmaps

PRM, PRM*, LazyPRM, and LazyPRM* retain a roadmap between requests with
`multi_query_planning_enabled`. `store_planner_data` and `load_planner_data`
persist it at `planner_data_path`; storage occurs when the planner instance is
destroyed.

```yaml
PersistentLazyPRMstar:
  type: geometric::LazyPRMstar
  multi_query_planning_enabled: 1
  store_planner_data: 1
  load_planner_data: 0
  planner_data_path: /tmp/roadmap.graph
```

Lazy variants revalidate nodes and edges after modest scene changes. Use
non-lazy variants only for static scenes. Setting both load and store to `0`
still reuses and extends the roadmap for the node's lifetime. A common
persistent workflow builds and saves with a star planner, then loads with its
corresponding non-star planner for faster queries.

## Pilz industrial motion planning

### Pipeline and motion limits

Load Pilz as `pilz_industrial_motion_planner/CommandPlanner`. Cartesian limits
must resolve under `<robot_description>_planning.cartesian_limits`; with a
`robot_description` URDF parameter, use the `robot_description_planning`
namespace.

```yaml
cartesian_limits:
  max_trans_vel: 1
  max_trans_acc: 2.25
  max_trans_dec: -5
  max_rot_vel: 1.57
```

Joint parameters can define `has_deceleration` and a negative
`max_deceleration`. Parameter limits must be at least as strict as URDF limits,
and Pilz applies the strictest common joint limits. It derives rotational
acceleration and deceleration from the corresponding translational ratio and
`max_rot_vel`.

### Request semantics

Set `MotionPlanRequest.planner_id` to `PTP`, `LIN`, or `CIRC`.

- PTP synchronizes trapezoidal joint profiles using the slowest lead axis.
- LIN and CIRC synchronize Cartesian translation with quaternion-slerped
  rotation, require a zero-velocity start, and interpret request scaling
  factors as Cartesian limits.

### Circular-path constraints

CIRC identifies its defining point using `path_constraints.name`, set to
`center` or `interim`, and stores the point in
`path_constraints.position_constraints[].constraint_region.primitive_poses[].position`.
A center selects the shorter arc and cannot create a half-circle. An interim
point forces the arc through that point but cannot create a full circle.

```cpp
request.planner_id = "CIRC";
request.path_constraints.name = "interim";
moveit_msgs::msg::PositionConstraint via;
via.constraint_region.primitive_poses.emplace_back();
via.constraint_region.primitive_poses.back().position = via_point;
request.path_constraints.position_constraints.push_back(via);
```

### Blended motion sequences

Each `MotionSequenceItem` holds an ordinary request in `req` and a
`blend_radius`. A positive radius permits motion toward the next goal without
stopping. Only the first item may specify a start state. Adjacent blend spheres
must not overlap: their radii must sum to less than the distance between their
goals. A sequence can span planning groups; if any item fails to plan, none are
executed.

### Sequence interfaces

Enable these `move_group` capabilities:

- `pilz_industrial_motion_planner/MoveGroupSequenceService`
- `pilz_industrial_motion_planner/MoveGroupSequenceAction`

`/plan_sequence_path` plans a `MotionSequenceRequest` and returns trajectories
without executing them. `/sequence_move_group` plans and executes unless
`planning_options.plan_only` is set. Unlike the ordinary MoveGroup action, the
sequence action still executes when the robot already meets the goal, preserving
circular and similar motions.

## CHOMP configuration

### Objective and termination controls

Configure CHOMP in `chomp_planning.yaml`. `planning_time_limit`,
`max_iterations`, and `max_iterations_after_collision_free` bound optimization.
Its objective uses `smoothness_cost_weight`, `obstacle_cost_weight`, and the
separate `smoothness_cost_velocity`, `smoothness_cost_acceleration`, and
`smoothness_cost_jerk` terms. `obstacle_cost_weight: 0.0` ignores obstacles,
whereas `1.0` treats them as a hard constraint.

### Numerical and recovery controls

`learning_rate`, `joint_update_limit`, `collision_clearance`, and
`collision_threshold` govern updates and collision handling. `ridge_factor`
adds diagonal noise to the quadratic cost matrix; at least `0.001` can help
escape obstacles at the cost of smoothness. `use_pseudo_inverse` has a separate
`pseudo_inverse_ridge_factor`.

`use_stochastic_descent` updates one random trajectory point instead of all
points. `enable_failure_recovery` retries with varied parameters up to
`max_recovery_attempts`.

### Trajectory initialization

`trajectory_initialization_method` accepts `quintic-spline`, `linear`, `cubic`,
or `fillTrajectory`. Interpolation modes synthesize a start-to-goal seed;
`fillTrajectory` consumes a trajectory from another planner such as OMPL and
can avoid poor local minima.

```yaml
ridge_factor: 0.001
trajectory_initialization_method: fillTrajectory
```

## Legacy planning-adapter material

The CHOMP planning-adapter examples are MoveIt 1/Melodic material. Their Catkin,
`roslaunch`, XML launch, and legacy identifiers are migration guidance, not
copy-paste MoveIt 2 syntax. In that API, adapter order matters:
`chomp/OptimizerAdapter` invokes the base planner (OMPL or STOMP) before CHOMP,
both planners' YAML files must be loaded, and CHOMP must use `fillTrajectory`.

The legacy `stomp_moveit/StompSmoothingAdapter` post-processes an OMPL or CHOMP
path when STOMP's `initialization_method` is `4` (`FILL_TRAJECTORY`). Its source
describes the smoothing adapter as work in progress.
