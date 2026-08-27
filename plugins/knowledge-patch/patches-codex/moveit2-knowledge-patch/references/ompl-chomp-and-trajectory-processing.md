# OMPL, CHOMP, and Trajectory Processing

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

PRM, PRM*, LazyPRM, and LazyPRM* can retain their roadmap across requests when
`multi_query_planning_enabled` is set. `store_planner_data` and
`load_planner_data` persist the roadmap at `planner_data_path`; storage occurs
when the planner instance is destroyed.

```yaml
PersistentLazyPRMstar:
  type: geometric::LazyPRMstar
  multi_query_planning_enabled: 1
  store_planner_data: 1
  load_planner_data: 0
  planner_data_path: /tmp/roadmap.graph
```

With both load and store set to `0`, the planner still reuses and extends its
roadmap for the node's lifetime. Lazy variants revalidate nodes and edges and
therefore tolerate modest scene changes; non-lazy variants are appropriate
only for static scenes. A typical persistent workflow builds and saves using a
star planner, then loads using the corresponding non-star planner for faster
queries.

## CHOMP objective and termination

Configure CHOMP in `chomp_planning.yaml`:

- `planning_time_limit`, `max_iterations`, and
  `max_iterations_after_collision_free` bound optimization;
- `smoothness_cost_weight` and `obstacle_cost_weight` balance the objective;
- `smoothness_cost_velocity`, `smoothness_cost_acceleration`, and
  `smoothness_cost_jerk` tune its smoothness terms.

An `obstacle_cost_weight` of `0.0` ignores obstacles; `1.0` treats them as a
hard constraint.

## CHOMP numerical and recovery controls

`learning_rate`, `joint_update_limit`, `collision_clearance`, and
`collision_threshold` control numerical updates and collision handling.
`ridge_factor` adds diagonal noise to the quadratic cost matrix; `0.001` or
more can help escape obstacles at the cost of smoothness.

`use_pseudo_inverse` has a separate `pseudo_inverse_ridge_factor`.
`use_stochastic_descent` updates a random trajectory point rather than every
point. `enable_failure_recovery` retries with varied parameters up to
`max_recovery_attempts`.

## CHOMP trajectory initialization

`trajectory_initialization_method` accepts `quintic-spline`, `linear`,
`cubic`, or `fillTrajectory`. The interpolation modes synthesize a
start-to-goal seed. `fillTrajectory` consumes another planner's trajectory,
such as one from OMPL, and can avoid a poor CHOMP local minimum.

```yaml
ridge_factor: 0.001
trajectory_initialization_method: fillTrajectory
```

## Legacy optimizer and smoothing adapters

Examples using Catkin, `roslaunch`, XML launch files, and legacy adapter IDs
are MoveIt 1/Melodic migration material, not copy-paste MoveIt 2 syntax.

In that older API, adapter order matters:

- `chomp/OptimizerAdapter` invokes the base planner (OMPL or STOMP) before
  CHOMP. Load both planners' YAML files and configure CHOMP with
  `fillTrajectory`.
- `stomp_moveit/StompSmoothingAdapter` post-processes an OMPL or CHOMP path
  when STOMP uses `initialization_method: 4` (`FILL_TRAJECTORY`). The source
  characterizes this smoothing adapter as work in progress.

## Jazzy planners and trajectory processing

The `jazzy-release` adds a new STOMP motion-planner implementation, execution
of multi-DOF trajectories, and trajectory-processing updates spanning TOTG,
Ruckig, and Butterworth filtering.

## Multi-DOF trajectory derivatives

MoveIt now populates `velocities` and `accelerations` in multi-DOF joint
trajectories. Consumers must not assume that those fields are empty.

## Acceleration-limited smoothing and OSQP

`online_signal_smoothing::AccelerationLimitedPlugin` supports both the OSQP
v0.6.x API and the redesigned v1.0 C API. Humble, Jazzy, and Kilted use the
apt-provided v0.6.x; Lyrical and Rolling use the MoveIt `osqp_vendor` fork with
v1.0.
