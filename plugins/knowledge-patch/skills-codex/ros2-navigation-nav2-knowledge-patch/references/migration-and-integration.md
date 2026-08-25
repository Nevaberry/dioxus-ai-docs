# Migration and Integration

## Distribution support status

Rolling Ridley is the development distribution. Kilted Kaiju and Jazzy Jalisco
have active support, Humble Hawksbill is maintained, and Iron Irwini and
Galactic Geochelone are end-of-life. Account for backports and mixed package
sources by checking installed interfaces rather than inferring them solely from
the distribution name.

## Stamped velocity is the default

Nav2 command-velocity publishers and subscribers use
`geometry_msgs/TwistStamped` by default without changing their topic names.
Timestamps allow consumers to reject stale commands. Set
`enable_stamped_cmd_vel: false` on every affected node only when retaining the
legacy `Twist` interface; a partially migrated pipeline has incompatible topic
types.

## Multi-pose actions and waypoint status

`NavigateThroughPoses`, `ComputePathThroughPoses`, and related BT nodes use
`nav_msgs/Goals` instead of a raw vector of `PoseStamped` messages. Read
navigation poses from `poses.goals` and compute-path goals from `goals.goals`.

`NavigateThroughPoses` reports `WaypointStatus` values: `PENDING`, `COMPLETED`,
`SKIPPED`, and `FAILED`. This replaces `MissedWaypoint`. A pruning BT node must
carry the status array beside the goal list through matching
`input_waypoint_statuses` and `output_waypoint_statuses` ports so indices remain
aligned.

## Namespaced bringup

`use_namespace` was removed from `nav2_bringup`. `namespace` is always applied
and defaults to `/`. Shared RViz and parameter files should use relative topics,
such as `scan`, so they resolve beneath the robot namespace. An absolute topic,
such as `/scan`, intentionally stays global.

Costmap layers can call `joinWithParentNamespace()` when a topic should resolve
beneath the parent costmap rather than beneath the layer's private namespace.

## Nav2 ROS wrapper migration

In Lyrical, `nav2_ros_common` replaces the `nav2_util` lifecycle utilities.
Custom plugins and task servers should derive from or use
`nav2::LifecycleNode` and create Nav2 service, action, publisher, and
subscription wrappers through that lifecycle node's `create_*` factories.
Do not construct the wrappers directly.

```cpp
main_client_ = node->create_client<SrvT>(service_name, false);
action_client_ = node->create_action_client<ActionT>(action_name, callback_group);
```

When QoS is omitted, wrappers use `nav2::qos::StandardTopicQoS`: reliable,
volatile, depth 10. An explicit subscription QoS argument now follows the
callback. Service callbacks include the `rmw_request_id_t` request header.

Wrapper configuration uses `introspection_mode` and
`allow_parameter_qos_overrides`. Remove `action_server_result_timeout`; that
parameter no longer exists.

## Service and navigator introspection

`service_introspection_mode` accepts `disabled`, `metadata`, or `contents` and
defaults to `disabled`. The standard navigate-to-pose and
navigate-through-poses navigators also offer disabled-by-default Groot 2 live
monitoring, blackboard JSON inspection, and BT XML selection on a new goal.
Enable content introspection only when the data exposure and overhead are
acceptable.

## RViz navigation panel

The Nav2 panel can select BT XML for each request, accept exact coordinates and
frame IDs, and build, edit, save, or load multi-goal lists for
`NavigateThroughPoses` and Waypoint Following.

## Lifecycle bond timing

`bond_heartbeat_period` defaults to `0.25` seconds for lifecycle nodes and
Lifecycle Manager, up from `0.1`. Explicit old values still win; remove or
update them to adopt the newer default.

## Isolated middleware tests

Use the following CMake option to run `rmw_zenoh_cpp` tests without launching a
separate Zenoh router:

```text
--cmake-args -DUSE_ISOLATED_TESTS=ON
```
