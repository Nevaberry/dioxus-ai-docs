# Behavior Trees

## Contextual action errors

Nav2 action results propagate contextual `error_msg` strings through BT
Navigator. Replace the removed `error_code_names` parameter with prefixes; the
old parameter causes a startup exception.

```yaml
error_code_name_prefixes: [compute_path, follow_path, spin, route]
```

Each relevant BT action node must expose matching `error_code_id` and
`error_msg` ports:

```xml
<FollowPath path="{path}" error_code_id="{follow_path_error_code}"
            error_msg="{follow_path_error_msg}"/>
```

Carry both ports through recovery and fallback subtrees if callers need the
original failure context.

## Added and renamed nodes

Kilted adds `GetPoseFromPath`, `RemoveInCollisionGoals`, and `IsStopped`, and
extends `GoalUpdater` to lists of goals. When pruning a multi-goal list with
`RemoveInCollisionGoals`, preserve the corresponding waypoint statuses through
`input_waypoint_statuses` and `output_waypoint_statuses`.

In Lyrical, action-like nodes that may return `RUNNING` receive action-oriented
names:

| Earlier name | Lyrical name |
| --- | --- |
| `IsStopped` | `CheckStopStatus` |
| `IsPathValid` | `ValidatePath` |
| `IsPoseOccupied` | `CheckPoseOccupancy` |

Update XML tags and any plugin registration or test expectations together.

## Nonblocking, pause/resume, persistent, and round-robin control

`NonblockingSequence` keeps ticking later children while an earlier child is
`RUNNING`; use it only when those children are safe to overlap.

`PauseResumeController` exposes pause and resume services. It pairs with
`PersistentSequence`, whose bidirectional child-index port records and restores
the point of progress.

`RoundRobin` defaults to `wrap_around="false"`. After its final child it returns
failure instead of restarting. Set `wrap_around="true"` to retain legacy
wrapping.

## Navigator-private blackboards and reusable subtrees

Blackboard-ID parameters live under each navigator plugin rather than at BT
Navigator's top level. Examples include:

```yaml
navigate_to_pose:
  goal_blackboard_id: goal
navigate_through_poses:
  waypoint_statuses_blackboard_id: waypoint_statuses
```

BT XML may load reusable subtree files from directories listed in
`bt_search_directories`. Select a tree by a unique ID; do not reuse the shared
`MainTree` ID across alternatives.

## Runtime navigation-plugin selectors

The current default tree selects progress checker, goal checker, path handler,
controller, and planner plugins at runtime. Each selector writes a plugin ID to
a blackboard port, listens on its named selector topic, and provides a default
ID.

```xml
<ProgressCheckerSelector selected_progress_checker="{selected_progress_checker}"
  default_progress_checker="progress_checker" topic_name="progress_checker_selector"/>
<GoalCheckerSelector selected_goal_checker="{selected_goal_checker}"
  default_goal_checker="general_goal_checker" topic_name="goal_checker_selector"/>
<PathHandlerSelector selected_path_handler="{selected_path_handler}"
  default_path_handler="PathHandler" topic_name="path_handler_selector"/>
<ControllerSelector selected_controller="{selected_controller}"
  default_controller="FollowPath" topic_name="controller_selector"/>
<PlannerSelector selected_planner="{selected_planner}"
  default_planner="GridBased" topic_name="planner_selector"/>
```

Ensure configured default IDs match loaded server plugins; a topic update only
selects an existing plugin.

## Near-goal replanning suppression

The default `ComputePathToPose` subtree retains the existing plan when all of
these conditions hold:

1. The global goal has not changed.
2. `IsGoalNearby` finds the robot near the goal, using a `4.0` proximity
   threshold and `1.5` maximum robot-pose search distance in the default tree.
3. `TruncatePathLocal` produces the remaining forward path with no backward
   segment.
4. `ValidatePath` accepts that remaining path.

If any guard fails, the fallback invokes `ComputePathToPose` with the selected
planner and both contextual error ports. This prevents localization drift or
tracking error from causing repeated feasible-planner loops during final
approach while still replanning stale or invalid paths.

```xml
<Fallback name="FallbackComputePathToPose">
  <ReactiveSequence name="CheckIfNewPathNeeded">
    <Inverter><GlobalUpdatedGoal/></Inverter>
    <IsGoalNearby path="{path}" proximity_threshold="4.0"
                  max_robot_pose_search_dist="1.5"/>
    <TruncatePathLocal input_path="{path}" output_path="{remaining_path}"
                       distance_forward="-1" distance_backward="0.0"/>
    <ValidatePath path="{remaining_path}"/>
  </ReactiveSequence>
  <ComputePathToPose goal="{goal}" path="{path}"
                     planner_id="{selected_planner}"/>
</Fallback>
```

## Path validation migration

The `ValidatePath` node and `IsPathValid` service rename `check_full_path` to
the oppositely worded `stop_at_first_collision`. Old `false` maps to new `true`,
which remains the default. `max_lookahead_distance` defaults to `-1.0` for
full-path validation; set a positive value to validate only that forward
distance.

## Local path truncation port

`TruncatePathLocal` renames its `robot_frame` input to `robot_base_frame`. If
omitted, the port inherits BT Navigator's `robot_base_frame` parameter.

```xml
<TruncatePathLocal robot_base_frame="base_link" ... />
```

## Cancellation, logging, and bounds

BT Navigator adds:

- `default_cancel_timeout`, default `50` ms, for action cancellation.
- `bt_log_idle_transitions`, default `true`; set it false to suppress idle
  transition noise.
- `IsWithinPathTrackingBounds`, which tests whether the robot remains within
  configured path-tracking bounds.

The standard navigators can also select BT XML with each new goal, expose
blackboard JSON, and use disabled-by-default Groot 2 live monitoring. Coordinate
those facilities with `service_introspection_mode` when debugging tree state.
