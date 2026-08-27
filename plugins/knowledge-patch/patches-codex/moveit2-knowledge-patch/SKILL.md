---
name: moveit2-knowledge-patch
description: MoveIt 2
version: "2.14.3"
license: MIT
metadata:
  author: Nevaberry
---


# MoveIt 2 Knowledge Patch

Use this skill when implementing, migrating, configuring, or debugging MoveIt 2
planning, execution, Servo, or Task Constructor code. Start with the quick
references below, then load the topic file that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Planning Pipelines and Python](references/planning-pipelines-and-python.md) | Jazzy setup and migration, `moveit_py`, named and parallel pipelines, constraints, planning-scene access, request adapters, exported CMake targets |
| [OMPL, CHOMP, and Trajectory Processing](references/ompl-chomp-and-trajectory-processing.md) | OMPL objectives and persistent roadmaps, CHOMP tuning and initialization, legacy adapters, STOMP, trajectory processing, multi-DOF derivatives, smoothing compatibility |
| [Pilz Industrial Motion](references/pilz-industrial-motion.md) | Pilz loading and limits, PTP/LIN/CIRC semantics, circular constraints, blended sequences, service and action interfaces |
| [MoveIt Servo Control](references/servo-control.md) | Safety scaling, IK parameters, realtime scheduling, direct C++ control, ROS interfaces, smoothing filters |
| [MoveIt Task Constructor](references/task-constructor.md) | Stage flow, lifecycle, planners, property forwarding, pose generation and IK, scene transitions, diagnostics |

## Breaking changes and migration traps

### Link exported CMake targets

Link namespaced MoveIt targets with `target_link_libraries()`; do not pass
MoveIt dependencies through `ament_target_dependencies()`.

```cmake
target_link_libraries(my_target
  moveit_ros_planning::moveit_ros_planning
)
```

### Treat planning-adapter integrations as migration-sensitive

The planning pipeline API now represents request and response adapters more
explicitly. Rework Humble-era integrations against the current API instead of
copying legacy adapter configurations.

Examples using Catkin, `roslaunch`, XML launch files,
`chomp/OptimizerAdapter`, or `stomp_moveit/StompSmoothingAdapter` are MoveIt 1
migration material, not direct MoveIt 2 configuration.

### Update changed state before collision checks

After changing a planning scene's current state or solving IK on a
`RobotState`, call `update()` so transforms and collision checks observe the
new values.

```python
with monitor.read_only() as scene:
    state = scene.current_state
    state.set_from_ik("panda_arm", pose_goal, "panda_hand")
    state.update()
    colliding = scene.is_state_colliding(
        robot_state=state, joint_model_group_name="panda_arm"
    )
```

### Distinguish pipeline profiles from plugin names

`MultiPipelinePlanRequestParameters` receives names of top-level parameter
profiles. Those profiles select their own pipeline and planner; do not pass
bare planner plugin names.

```python
params = MultiPipelinePlanRequestParameters(
    moveit, ["ompl_fast", "chomp_profile"]
)
result = arm.plan(multi_plan_parameters=params)
```

### Respect Pilz request constraints

Use `planner_id` values `PTP`, `LIN`, or `CIRC`. LIN and CIRC require a
zero-velocity start state and apply request scaling factors to Cartesian
limits. For a motion sequence:

- only the first item may specify a start state;
- adjacent blend radii must sum to less than the distance between goals;
- one planning failure prevents the entire sequence from executing.

### Forward Task Constructor properties explicitly

Nested stages do not automatically inherit task properties. Expose properties
to containers, initialize them from `Stage::PARENT`, and import generated
`target_pose` values into `ComputeIK` from `Stage::INTERFACE`.

```cpp
task.properties().exposeTo(
    pick->properties(), { "eef", "group", "ik_frame" });
pick->properties().configureInitFrom(
    mtc::Stage::PARENT, { "eef", "group", "ik_frame" });
```

## Planning and execution quick reference

### Plan with `moveit_py`

Obtain the group planning component from `MoveItPy`. The component plans and
the owning `MoveItPy` object executes the result trajectory.

```python
moveit = MoveItPy(node_name="moveit_py")
arm = moveit.get_planning_component("panda_arm")
arm.set_start_state_to_current_state()
arm.set_goal_state(pose_stamped_msg=goal, pose_link="panda_link8")

result = arm.plan()
if result:
    moveit.execute(result.trajectory, controllers=[])
```

Named SRDF states use
`set_start_state(configuration_name=...)` or
`set_goal_state(configuration_name=...)`. A concrete `RobotState` can be
passed as `set_goal_state(robot_state=...)`.

### Configure reusable planning profiles

List loaded pipelines under `planning_pipelines.pipeline_names`. Define each
reusable request profile at the top level under `plan_request_params`.

```yaml
planning_pipelines:
  pipeline_names: [ompl, chomp]

ompl_fast:
  plan_request_params:
    planning_pipeline: ompl
    planner_id: RRTConnectkConfigDefault
    planning_attempts: 1
    planning_time: 1.0
```

### Pass constraint goals as a list

Build a joint constraint from a populated `RobotState` and its joint model
group, then pass it through `motion_plan_constraints`.

```python
constraint = construct_joint_constraint(
    robot_state=state,
    joint_model_group=moveit.get_robot_model().get_joint_model_group(
        "panda_arm"
    ),
)
arm.set_goal_state(motion_plan_constraints=[constraint])
```

### Scope planning-scene access

Use `monitor.read_write()` when applying collision objects and
`monitor.read_only()` for checks. Update `scene.current_state` after mutation.

### Choose OMPL termination deliberately

`optimization_objective` can select path length, mechanical work, clearance,
state-cost integral, or minimax optimization. `termination_condition` accepts
`Iteration[num]`, `CostConvergence[solutionsWindow,epsilon]`, or
`ExactSolution`; `allowed_planning_time` is still a hard ceiling.

```yaml
RRTstarkConfigDefault:
  type: geometric::RRTstar
  optimization_objective: MaximizeMinClearanceObjective
  termination_condition: CostConvergence[10,.1]
```

### Seed CHOMP from another planner

Set `trajectory_initialization_method: fillTrajectory` when OMPL or another
planner should supply CHOMP's seed. A `ridge_factor` of at least `0.001` can
help escape obstacles, trading away some smoothness.

## Servo quick reference

### Supply IK plugin parameters

Pass `moveit_config.robot_description_kinematics` into `ServoNode`. Custom IK
plugin parameters must be declared inside the plugin because Servo does not
accept undeclared parameters from `kinematics.yaml`.

### Select and monitor command interfaces

Servo accepts `JointJog`, `TwistStamped`, and `PoseStamped`. Twist and pose
commands require `header.frame_id`; twist commands currently use the robot's
planning frame. Switch type through `/<node_name>/switch_command_type`, pause
through `/<node_name>/pause_servo`, and watch `/<node_name>/status`.

### Pick a smoothing filter for the constraint that matters

- Butterworth is inexpensive and avoids joint-space overshoot but does not
  explicitly constrain acceleration or jerk.
- Acceleration-limited smoothing respects acceleration where feasible and
  preserves direction when kinematics allow, but may overshoot and does not
  constrain jerk.
- Ruckig gives the smoothest joint-limit- and acceleration-aware output, but
  may overshoot or swirl at sharp Cartesian corners.

## Task Constructor quick reference

### Match stages to result flow

- Generators create states independently and send them both directions.
- Propagators extend a neighboring result forward or backward.
- Connectors bridge states produced independently on their two interfaces.
- Wrappers modify or filter one child.
- Serial containers require end-to-end child solutions; parallel containers
  select alternatives, provide fallbacks, or merge independent solutions.

### Complete the task lifecycle

Set root properties before adding stages, load the robot model, call `init()`,
plan a bounded number of successful solutions, choose one explicitly, and
publish or execute it. Handle `InitStageException` from initialization.

### Diagnose composition from the stage diagram

Read each stage's counts left to right as backward-propagated, locally
generated, and forward-propagated solutions. The first stage with zero
generation or forwarding identifies the failed composition point. Retrieve a
visualization ID with
`task.stages()->findChild(name)->introspectionId()`.
