---
name: ros2-knowledge-patch
description: ROS 2
version: Kilted Kaiju
license: MIT
metadata:
  author: Nevaberry
---


# ROS 2 Knowledge Patch

Use this skill when selecting ROS 2 platforms or middleware, updating build
configuration, writing `rclcpp` or `rclpy` code, operating Rosbag2, or working
with interfaces and launch substitutions. Check migration hazards first, then
open the topic reference that matches the task.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Compatibility, middleware, and builds](references/compatibility-middleware-builds.md) | Platform tiers, language levels, Gazebo, RMW implementations, Windows dependencies, test fixtures, CMake, and typesupport |
| [Client libraries and execution](references/client-libraries-execution.md) | Python generic typing, the experimental events executor, subordinate nodes, and DDS topic instances |
| [Rosbag2 and actions](references/rosbag2-actions.md) | Action introspection, generic action clients, merged playback, message ordering, inspection, logging, and snapshots |
| [Interfaces and launch](references/interfaces-launch.md) | `nav_msgs/Goals`, NV12 images, and compound `PathJoinSubstitution` components |

## Migration Hazards

### Replace `ament_target_dependencies()`

`ament_target_dependencies()` is deprecated. Link imported modern CMake
targets directly:

```cmake
target_link_libraries(my_target PUBLIC SomePackage::SomeTarget)
```

Do not mix the plain and keyword signatures for one target. If an existing
`target_link_libraries()` call uses the plain form, leave out `PUBLIC`,
`PRIVATE`, and `INTERFACE` in later calls for that target.

### Update Fast DDS profile configuration names

The underlying `fastrtps` name is now `fastdds`. RMW implementation names do
not change, but environment-variable names used for XML profiles do. Audit
scripts, CI variables, and launch environments that configure Fast DDS rather
than renaming the selected RMW implementation.

### Stop planning new work around Connext Micro

`rmw_connextddsmicro` is deprecated and receives no further Kilted updates.
Choose a supported RMW implementation for maintained deployments.

### Remove `float128` from dynamic typesupport paths

`rosidl_dynamic_typesupport` no longer supports `float128`. Change dynamic
type descriptions and consumers to a supported numeric representation before
upgrading.

### Expect one bag per snapshot trigger

Snapshot recording no longer reuses the same output bag. Every trigger writes
a new bag file. Automation that discovers, uploads, rotates, or counts snapshot
outputs must handle multiple files.

### Preserve subordinate-node semantics

Generic clients created from an `rclcpp` subordinate node now honor its
sub-namespace. Parameter access through that node uses the parent node's
`rclcpp::node_interfaces::NodeParametersInterface`. Recheck resolved client
names and parameter behavior if older code depended on the previous behavior.

## Platform and Middleware Selection

Use the detailed compatibility tables before choosing an operating system,
architecture, compiler, or RMW implementation. Important constraints include:

- Ubuntu 24.04 on amd64 and arm64, and Windows 10 with Visual Studio 2019 on
  amd64, are Tier 1 targets.
- RHEL 9 on amd64 is Tier 2.
- Debian 12 and macOS on amd64 are Tier 3.
- The minimum language levels are C++17 and Python 3.9.
- Ionic is the recommended Gazebo release.

`rmw_fastrtps_cpp` remains the default RMW implementation and uses Fast DDS
2.14.4. Fast DDS, Cyclone DDS 0.10.5, Connext DDS 7.3, and Zenoh 1.0.4 are Tier
1 middleware implementations. Connext excludes arm64 and is limited to
Ubuntu, Windows, and macOS. `rmw_zenoh_cpp` is newly Tier 1.

See
[Compatibility, middleware, and builds](references/compatibility-middleware-builds.md)
for the full matrices and build guidance.

## Rosbag2 Quick Reference

### Merge bags during playback

Repeat `-i` or `--input` to merge multiple bags into one playback:

```sh
ros2 bag play -i bag1 -i bag2 -i bag3
```

### Choose timestamp ordering

Publication-time order is opt-in:

```sh
ros2 bag play <bag> --message-order sent
```

`sent` orders by publication timestamp. The default, `received`, orders by
reception timestamp.

### Sort and size bag contents

`ros2 bag info --sort` sorts topics, services, and actions by name, type, or
recorded-message count. In verbose output, add `--size-contribution` to report
each topic's share of the bag size:

```sh
ros2 bag info -v --sort <criterion> --size-contribution <bag>
```

### Set Rosbag2 log verbosity

Both playback and recording accept `--log-level`:

```sh
ros2 bag play <bag> --log-level debug
ros2 bag record <topics...> --log-level debug
```

## Action Introspection

Inspect a running action from the CLI:

```sh
ros2 action echo <action_name>
```

Rosbag2 can record and replay action data. `rclcpp` also provides the generic
action client support underlying generic action tooling. See
[Rosbag2 and actions](references/rosbag2-actions.md) before building generic
action inspection or replay workflows.

## Python Typing Quick Reference

`rclpy` publishers, subscriptions, services, actions, tasks, futures, and
parameters support generic type annotations. Clients carry request and
response types; action clients carry goal, result, and feedback types:

```python
client: Client[GetParameters.Request, GetParameters.Response]
action: ActionClient[Fibonacci.Goal, Fibonacci.Result, Fibonacci.Feedback]
future: Future[bool] = Future()
```

Use these parameters in application annotations and reusable APIs instead of
erasing the ROS interface types. See
[Client libraries and execution](references/client-libraries-execution.md) for
executor and node-behavior changes that commonly accompany client-library
updates.

## Launch Path Composition

`PathJoinSubstitution` accepts a list of strings or substitutions as one path
component. Use a nested list when a filename combines a substituted basename
and a literal suffix:

```python
PathJoinSubstitution([
    'robot_description', 'urdf',
    [LaunchConfiguration('model'), '.xacro'],
])
```

This avoids a separate concatenation helper. More interface and encoding
changes are in [Interfaces and launch](references/interfaces-launch.md).

## New Capability Checklist

When the task touches these areas, account for the corresponding capability:

- Use `rmw_test_fixture` and its provider implementation package for
  RMW-specific communication isolation in tests.
- Consider the experimental Python `EventsExecutor` when evaluating an
  event-driven executor, but keep its experimental status explicit.
- Use `nav_msgs/msg/Goals` when a message needs an array of navigation goals.
- Permit NV12 in common-interface image encoding paths, especially for
  hardware-decoder output.
- Expect Rust interfaces to be generated by default because `rosidl_rust` is
  in the default generator set.
- Consider DDS topic instances when multiple logical objects should publish
  updates on one topic.

## Review Checklist

Before finalizing ROS 2 changes:

1. Verify the target platform tier, architecture, compiler, and language
   minimums.
2. Confirm the RMW implementation is supported on the selected platform and
   that Fast DDS configuration uses the renamed profile environment variables.
3. Replace deprecated CMake dependency calls without mixing CMake signature
   styles.
4. Remove unsupported dynamic `float128` types and avoid new Connext Micro
   dependencies.
5. Recheck subordinate-node client names and parameter access.
6. Decide explicitly whether bag playback needs reception or publication
   ordering, and handle a new output bag for every snapshot trigger.
7. Apply concrete generic parameters to Python ROS entities where static
   typing is part of the task.
8. Treat the Python events executor as experimental in design and deployment
   decisions.
