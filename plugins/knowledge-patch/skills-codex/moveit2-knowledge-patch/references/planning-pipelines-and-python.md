# Planning Pipelines and Python

## Jazzy setup and migration (`jazzy-release`)

MoveIt 2 version 2.10 targets ROS 2 Jazzy Jalisco LTS and Rolling Ridley,
replacing Humble as the recommended MoveIt release. On Jazzy, install ROS
Debian binaries on Ubuntu Noble 24.04 or build from source.

Jazzy adds parallel planning pipelines. Its planning-pipeline refactor also
represents request and response adapters more clearly, so treat Humble-era
pipeline integrations as migration-sensitive.

## `moveit_py` planning and execution

`MoveItPy.get_planning_component()` returns the group-specific planning API.
The plan result carries the trajectory, but execution belongs to the
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

Use `set_start_state(configuration_name=...)` or
`set_goal_state(configuration_name=...)` for named SRDF states. To provide a
concrete state, use `set_goal_state(robot_state=...)`.

## Named planning parameter profiles

`planning_pipelines.pipeline_names` selects the pipelines loaded into a
`moveit_py` node. Separate top-level profiles map reusable names to
`plan_request_params`; each profile can choose the pipeline, planner ID,
attempt count, scaling factors, and planning time.

```yaml
planning_pipelines:
  pipeline_names: [ompl, chomp]

ompl_fast:
  plan_request_params:
    planning_pipeline: ompl
    planner_id: RRTConnectkConfigDefault
    planning_attempts: 1
    planning_time: 1.0

chomp_profile:
  plan_request_params:
    planning_pipeline: chomp
    planning_time: 1.5
```

## Parallel planning profile selection

Construct `MultiPipelinePlanRequestParameters` with the `MoveItPy` instance
and profile names—not just planner plugin names—and pass it through the
dedicated `multi_plan_parameters` argument.

```python
params = MultiPipelinePlanRequestParameters(
    moveit, ["ompl_fast", "chomp_profile"]
)
result = arm.plan(multi_plan_parameters=params)
```

## Constraint goals

Pass constraint messages as a list with
`set_goal_state(motion_plan_constraints=...)`. The joint-constraint helper
builds a constraint from a populated `RobotState` and the target joint model
group.

```python
state.joint_positions = {"panda_joint1": -1.0, "panda_joint2": 0.7}
constraint = construct_joint_constraint(
    robot_state=state,
    joint_model_group=moveit.get_robot_model().get_joint_model_group(
        "panda_arm"
    ),
)
arm.set_goal_state(motion_plan_constraints=[constraint])
```

## Planning-scene monitor contexts

Scope collision-object changes through `read_write()` and checks through
`read_only()`. After changing scene state or solving IK, call
`scene.current_state.update()` or `robot_state.update()` so transforms and
collision checks use the changed state.

```python
monitor = moveit.get_planning_scene_monitor()
with monitor.read_write() as scene:
    scene.apply_collision_object(collision_object)
    scene.current_state.update()

with monitor.read_only() as scene:
    state = scene.current_state
    state.set_from_ik("panda_arm", pose_goal, "panda_hand")
    state.update()
    colliding = scene.is_state_colliding(
        robot_state=state, joint_model_group_name="panda_arm"
    )
```

## Built-in request adapters

- `CheckStartStateBounds` can clamp a slightly out-of-bounds starting joint to
  its URDF limit, subject to configured tolerance.
- `ValidateWorkspaceBounds` supplies a 10 m × 10 m × 10 m workspace only when
  the request omits one.
- `CheckStartStateCollision` samples nearby states using `jiggle_fraction` and
  a retry limit.
- `ResolveConstraintFrames` rewrites constraints expressed in object
  subframes such as `cup/handle` into object or robot frames.

## Exported CMake targets (`2.15.0`)

Downstream packages should link MoveIt's exported, namespaced CMake targets
instead of sending MoveIt dependencies to `ament_target_dependencies()`.

```cmake
target_link_libraries(my_target
  moveit_ros_planning::moveit_ros_planning
)
```
