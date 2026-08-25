---
name: ros2-knowledge-patch
description: ROS 2
version: Kilted Kaiju
license: MIT
metadata:
  author: Nevaberry
---


# ROS 2 Compatibility Guide

Use this skill when writing, reviewing, migrating, or debugging ROS 2 code whose
behavior depends on the covered distribution. Prefer the project's manifests,
source, configuration, and tests when they show different behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Clients, Interfaces, and Launch](references/clients-interfaces-and-launch.md) | Python typing, executors, interfaces, subordinate nodes, CMake, launch substitutions, Rust generation, and image encoding |
| [Platform, Middleware, and Migration](references/platform-and-migration.md) | Supported platforms, language floors, Gazebo, Windows setup, RMW implementations, test isolation, topic instances, and middleware migration |
| [Rosbag and Actions](references/rosbag-and-actions.md) | Action introspection, generic action clients, action recording and replay, multi-bag playback, ordering, inspection, logging, and snapshots |

## Migration priorities

### Replace `ament_target_dependencies()`

The helper is deprecated. Link imported modern CMake targets directly with
`target_link_libraries()`:

```cmake
target_link_libraries(my_target PUBLIC SomePackage::SomeTarget)
```

Do not mix the keyword and plain signatures for one target. If an earlier call
for that target is plain, leave `PUBLIC`, `PRIVATE`, and `INTERFACE` out of later
calls too.

### Update Fast DDS naming in configuration

The underlying middleware name changed from `fastrtps` to `fastdds`. ROS
middleware implementation identifiers did not change, but XML-profile
environment-variable names did. Audit environment configuration and deployment
scripts even when the selected RMW implementation name remains valid.

### Move away from Connext Micro

`rmw_connextddsmicro` is deprecated and receives no further updates for this
distribution. Choose another supported RMW implementation for maintained
deployments.

### Remove dynamic `float128` assumptions

`rosidl_dynamic_typesupport` no longer supports `float128`. Change schemas or
dynamic-type handling that relies on it.

## Build and platform quick reference

Use at least C++17 and Python 3.9. The recommended Gazebo release is Ionic.

Tier 1 targets are:

- Ubuntu 24.04 on amd64 and arm64.
- Windows 10 with Visual Studio 2019 on amd64.

RHEL 9 on amd64 is Tier 2. Debian 12 and macOS on amd64 are Tier 3. Treat these
tiers as support expectations when selecting CI runners and deployment targets.

For Windows source work, provision dependencies with Pixi/Conda plus pip and
isolate them per workspace instead of installing them globally.

## Middleware quick reference

`rmw_fastrtps_cpp` remains the default and uses Fast DDS 2.14.4. Tier 1
middleware implementations include:

- Fast DDS.
- Cyclone DDS 0.10.5.
- Connext DDS 7.3.
- Zenoh 1.0.4 through the newly Tier 1 `rmw_zenoh_cpp`.

Connext does not support arm64 here and is limited to Ubuntu, Windows, and
macOS. Check that constraint before selecting it for multi-architecture builds.

Use `rmw_test_fixture` to define communication isolation around an RMW test.
The companion `rmw_test_fixture_implementation` package discovers, loads, and
invokes the provider-specific implementation.

DDS topic instances are supported, so updates for multiple objects of one
logical kind can share one topic.

## Rosbag playback quick reference

Merge several bags during playback by repeating `-i` or `--input`:

```sh
ros2 bag play -i bag1 -i bag2 -i bag3
```

Reception order remains the default. To order by publication timestamp, use:

```sh
ros2 bag play <bag> --message-order sent
```

Use `--log-level` with both playback and recording when command-level logging
must be adjusted:

```sh
ros2 bag play <bag> --log-level debug
ros2 bag record <topics...> --log-level debug
```

Every trigger in snapshot recording mode now creates a new bag file. Do not
design workflows around a previous snapshot file being reused.

## Rosbag inspection quick reference

`ros2 bag info --sort` sorts topics, services, and actions by name, type, or
recorded-message count. In verbose mode, `--size-contribution` reports each
topic's share of the bag size:

```sh
ros2 bag info -v --sort <criterion> --size-contribution <bag>
```

## Actions quick reference

The CLI can inspect action traffic directly:

```sh
ros2 action echo <action_name>
```

Rosbag2 can record and replay action data. `rclcpp` supplies the generic action
client support used for action tooling and type-independent clients.

## Python client typing

Publishers, subscriptions, services, actions, tasks, futures, and parameters
support generic type annotations. Service clients take request and response
types; action clients take goal, result, and feedback types:

```python
client: Client[GetParameters.Request, GetParameters.Response]
action: ActionClient[
    Fibonacci.Goal,
    Fibonacci.Result,
    Fibonacci.Feedback,
]
future: Future[bool] = Future()
```

Use these generics in annotations rather than falling back to unparameterized
client and future types.

## Executors and subordinate nodes

`rclpy` includes an experimental `EventsExecutor`, bringing the event-driven
executor concept from `rclcpp` to Python. Keep the experimental status in mind
when choosing it for long-lived APIs.

Generic clients created from an `rclcpp` subordinate node honor that node's
sub-namespace. Parameter access through a subordinate node uses the parent
node's `rclcpp::node_interfaces::NodeParametersInterface`.

## Interfaces and generated code

`nav_msgs/msg/Goals` carries an array of navigation goals. Use it when an API
needs a collection of goals rather than inventing a parallel message shape.

`rosidl_rust` is enabled among the default ROS interface code generators, so
default interface generation includes Rust artifacts.

NV12 is a common-interface pixel encoding and can represent frames from
hardware-accelerated decoders directly.

## Launch path composition

`PathJoinSubstitution` accepts a list of strings or substitutions as one path
component. This supports a substituted basename plus a suffix without a
separate concatenation helper:

```python
PathJoinSubstitution([
    'robot_description',
    'urdf',
    [LaunchConfiguration('model'), '.xacro'],
])
```

Use the nested list only for pieces that form one component; keep separate path
components as separate outer-list entries.
