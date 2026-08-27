# Behavior trees and navigation

## Navigation action nodes

Kilted adds `GetPoseFromPath`, `RemoveInCollisionGoals`, and `IsStopped`, and
extends `GoalUpdater` to lists of goals. In Lyrical, `IsStopped` becomes
`CheckStopStatus`, `IsPathValid` becomes `ValidatePath`, and `IsPoseOccupied`
becomes `CheckPoseOccupancy`. These can return `RUNNING`, so treat them as
actions, not conditions.

`NavigateThroughPoses`, `ComputePathThroughPoses`, and related nodes use
`nav_msgs/Goals`. Access fields as `poses.goals` for navigation and
`goals.goals` for compute-path requests. `NavigateThroughPoses` returns
`WaypointStatus` values (`PENDING`, `COMPLETED`, `SKIPPED`, and `FAILED`) rather
than `MissedWaypoint`. Goal-pruning nodes must preserve the status sequence via
`input_waypoint_statuses` and `output_waypoint_statuses`.

## Action cancellation and logging

BT Navigator's `default_cancel_timeout` defaults to `50` ms for action
cancellation. `bt_log_idle_transitions` defaults to `true`; set it to `false`
to suppress idle transition noise. `IsWithinPathTrackingBounds` lets a tree
test whether the robot remains within configured path-tracking bounds.

## ValidatePath semantics

`ValidatePath` and the `IsPathValid` service use `stop_at_first_collision`
instead of the inverse `check_full_path`. Old `false` maps to new `true`, which
is the default. `max_lookahead_distance: -1.0` checks the full path; a positive
value restricts validation to that forward distance.

`TruncatePathLocal` uses `robot_base_frame` instead of `robot_frame`. When the
port is omitted, it inherits BT Navigator's `robot_base_frame` parameter.

```xml
<TruncatePathLocal robot_base_frame="base_link" ... />
```

## Control-node semantics

`NonblockingSequence` keeps ticking later children while an earlier child is
`RUNNING`.

`PauseResumeController` exposes pause and resume services. Pair it with
`PersistentSequence`; the sequence's bidirectional child-index port preserves
the point from which execution should resume.

`RoundRobin` defaults to `wrap_around="false"` and returns failure after its
last child. Set `wrap_around="true"` only when legacy cyclic behavior is
required.

## Navigator-private blackboards and subtree discovery

Blackboard-ID parameters belong under navigator plugins rather than at the BT
Navigator top level. Examples include:

- `navigate_to_pose.goal_blackboard_id`
- `navigate_through_poses.waypoint_statuses_blackboard_id`

Load reusable subtree XML from directories listed in `bt_search_directories`.
When selecting a tree by ID, assign each tree a unique ID rather than reusing
the shared `MainTree` identifier.

## Runtime navigation-plugin selectors

The default tree has selectors for the progress checker, goal checker, path
handler, controller, and planner. Each selector publishes the chosen plugin ID
to a blackboard port, listens on a named selector topic, and supplies a default
ID. Pass the output port to the action that consumes the plugin.

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

This arrangement changes navigation behavior at runtime without replacing the
tree.

## Near-goal replanning suppression

The default `ComputePathToPose` subtree retains the existing plan only when all
of these gates pass:

1. The global goal has not changed.
2. The robot is near the goal.
3. The truncated remaining path is still valid.

If any gate fails, the fallback computes a new path. This prevents feasible
planners from repeatedly replanning because of localization drift or tracking
error during final approach.

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
                     planner_id="{selected_planner}"
                     error_code_id="{compute_path_error_code}"
                     error_msg="{compute_path_error_msg}"/>
</Fallback>
```

## Introspection and live tree control

Kilted's `service_introspection_mode` accepts `disabled`, `metadata`, or `contents` and
defaults to `disabled`. The standard navigators also provide disabled-by-default
Groot 2 live monitoring, blackboard JSON inspection, and BT XML replacement on
a new goal request.

The Nav2 RViz panel can select BT XML for each request, enter exact coordinates
and frame IDs, and build, edit, save, or load multi-goal lists for
`NavigateThroughPoses` and Waypoint Following.

## Route-based navigation

Kilted's `nav2_route` computes and tracks routes on a predefined graph. It can replace
free-space global planning or provide long-range graph structure while a
planner produces the nearby feasible path. Node and edge events can trigger
contextual operations such as changing speed or activating equipment.

Route Server can smooth graph corners with tangent circular arcs using
`smooth_corners` and `smoothing_radius`. It falls back to linear interpolation
for nearly straight edges and for arcs that cannot fit inside their edges.
