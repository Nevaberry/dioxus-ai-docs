---
name: moveit2-knowledge-patch
description: MoveIt 2
version: "2.14.3"
license: MIT
metadata:
  author: Nevaberry
---


# MoveIt 2 Knowledge Patch

Load this skill when implementing or migrating MoveIt 2 planning pipelines,
planner plugins, MoveIt Task Constructor tasks, Servo integrations, trajectory
processing, or downstream CMake linkage. Prefer the project's manifests,
configuration, installed headers, and observed runtime behavior when they differ
from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core planning and pipelines](references/core-planning.md) | Jazzy migration, `moveit_py`, planning profiles, parallel planning, constraints, planning scenes, adapters, trajectories, CMake linkage |
| [Planner plugins and adapters](references/planner-plugins.md) | OMPL objectives and persistent roadmaps, Pilz limits and sequences, CHOMP configuration, legacy optimizer adapters |
| [MoveIt Servo](references/servo.md) | Safety scaling, IK configuration, realtime scheduling, C++ and ROS interfaces, smoothing plugins |
| [MoveIt Task Constructor](references/task-constructor.md) | Stage flow, task lifecycle, planners, properties, pose generation, IK, scene transitions, diagnostics |

## Breaking and migration-sensitive changes

### Link exported CMake targets

Downstream packages should link MoveIt's exported namespaced targets. Do not pass
MoveIt dependencies to `ament_target_dependencies()`.

```cmake
target_link_libraries(my_target
  moveit_ros_planning::moveit_ros_planning
)
```

See [Core planning and pipelines](references/core-planning.md#downstream-cmake-linkage).

### Recheck planning-adapter integrations

The planning-pipeline API now represents request and response adapters more
explicitly. Treat integrations written against the Humble-era API as
migration-sensitive. Examples using Catkin, `roslaunch`, XML launch files,
`chomp/OptimizerAdapter`, or `stomp_moveit/StompSmoothingAdapter` describe the
legacy API and are not copy-paste MoveIt 2 configuration.

See [Core planning and pipelines](references/core-planning.md#planning-pipeline-and-adapter-migration)
and [Planner plugins and adapters](references/planner-plugins.md#legacy-planning-adapter-material).

### Consume multi-DOF derivatives

Multi-DOF trajectories are executable, and newer trajectories populate their
`velocities` and `accelerations`. Consumers must not assume those derivative
arrays are empty.

See [Core planning and pipelines](references/core-planning.md#multi-dof-trajectories).

## `moveit_py` quick reference

### Plan with a group and execute with `MoveItPy`

Obtain a group-specific component from `MoveItPy`, configure start and goal
state on it, then execute the successful result's trajectory through the
`MoveItPy` instance.

```python
moveit = MoveItPy(node_name="moveit_py")
arm = moveit.get_planning_component("panda_arm")
arm.set_start_state_to_current_state()
arm.set_goal_state(pose_stamped_msg=goal, pose_link="panda_link8")

result = arm.plan()
if result:
    moveit.execute(result.trajectory, controllers=[])
```

Named SRDF states use `set_start_state(configuration_name=...)` or
`set_goal_state(configuration_name=...)`. A `RobotState` goal uses
`set_goal_state(robot_state=...)`.

### Configure profiles before parallel planning

`planning_pipelines.pipeline_names` loads pipelines. Separately named top-level
profiles contain `plan_request_params` and select the pipeline, planner ID,
attempts, scaling factors, and planning time.

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

Build `MultiPipelinePlanRequestParameters` from the `MoveItPy` instance and
profile names, then pass it as `multi_plan_parameters`:

```python
params = MultiPipelinePlanRequestParameters(moveit, ["ompl_fast", "chomp_profile"])
result = arm.plan(multi_plan_parameters=params)
```

### Update states before collision checks

Use planning-scene monitor `read_write()` contexts for changes and `read_only()`
contexts for checks. After changing the scene's current state or solving IK,
call `update()` before transforms or collision checks.

See [Core planning and pipelines](references/core-planning.md#planning-scene-monitor-contexts).

## Planner selection quick reference

### OMPL objectives and termination

OMPL configurations can choose path length, mechanical work, minimum-clearance,
state-cost-integral, or minimax objectives. A configured termination condition
such as `Iteration[...]`, `CostConvergence[...]`, or `ExactSolution` does not
replace `allowed_planning_time`; that remains the hard upper bound.

### Persistent roadmaps

PRM-family planners reuse a roadmap across requests when
`multi_query_planning_enabled` is set. `store_planner_data` and
`load_planner_data` persist it at `planner_data_path`; storage happens when the
planner instance is destroyed. Prefer lazy variants when modest scene changes
require node and edge revalidation; reserve non-lazy variants for static scenes.

### Pilz commands

Set `MotionPlanRequest.planner_id` to `PTP`, `LIN`, or `CIRC`. LIN and CIRC
require a zero-velocity start and apply request scaling factors to Cartesian
limits. For sequences, only the first item may specify a start state, adjacent
blend spheres must not overlap, and any planning failure prevents all execution.

See [Planner plugins and adapters](references/planner-plugins.md) for complete
configuration, circular constraints, and sequence interfaces.

## MoveIt Task Constructor quick reference

### Respect result flow

Generators produce states in both directions, propagators extend neighboring
results forward or backward, and connectors bridge independently generated
states. Serial containers accept end-to-end child solutions; parallel
containers select, fall back among, or merge alternatives.

### Forward properties deliberately

Nested stages do not automatically inherit task properties. Expose selected
properties to containers, configure them from `Stage::PARENT`, and let wrappers
such as `ComputeIK` import generated values such as `target_pose` from
`Stage::INTERFACE`.

### Monitor the correct scene stage

`GenerateGraspPose` monitors the earlier `CurrentState`. `GeneratePlacePose`
monitors the saved attach-object stage so it sees the attached-object transform.
Move each generator into `ComputeIK`, then configure solution count, separation,
IK frame, and property sources.

See [MoveIt Task Constructor](references/task-constructor.md) for lifecycle,
planner, motion, planning-scene transition, and diagnostic details.

## MoveIt Servo quick reference

### Supply IK parameters explicitly

Pass `robot_description_kinematics` parameters to `ServoNode`. Parameters appear
under `robot_description_kinematics.<group_name>.<param_name>`. A custom IK
plugin must declare its own custom parameters because Servo does not accept
undeclared values from `kinematics.yaml`.

### Choose the command and output interfaces

Servo accepts `JointJog`, `TwistStamped`, and `PoseStamped` commands on its
parameterized inputs. Twist and pose messages require `header.frame_id`; twist
commands use the robot planning frame. `command_out_type` selects either
`JointTrajectory` or `Float64MultiArray` output.

### Choose smoothing by constraint needs

- `ButterworthFilterPlugin` is inexpensive and avoids joint-space overshoot,
  but does not explicitly constrain acceleration or jerk.
- `AccelerationLimitedPlugin` respects acceleration where feasible and
  preserves direction when kinematics allow, but may overshoot and does not
  constrain jerk.
- `RuckigFilterPlugin` gives the smoothest joint-limit- and acceleration-aware
  output, but may overshoot or swirl at sharp Cartesian corners.

See [MoveIt Servo](references/servo.md) for collision behavior, scheduling,
direct C++ control, services, status, and OSQP compatibility.
