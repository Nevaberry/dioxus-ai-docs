# Clients, Interfaces, and Launch

Coverage attribution: `kilted-kaiju`.

## Generic typing in `rclpy`

Publishers, subscriptions, services, actions, tasks, futures, and parameters
support generic type annotations. Parameterize service clients with their
request and response types. Parameterize action clients with their goal,
result, and feedback types.

```python
client: Client[GetParameters.Request, GetParameters.Response]
action: ActionClient[
    Fibonacci.Goal,
    Fibonacci.Result,
    Fibonacci.Feedback,
]
future: Future[bool] = Future()
```

Carry the concrete type arguments through application-facing annotations so
type checking can validate request, result, feedback, and future use.

## Experimental Python events executor

`rclpy` provides an experimental `EventsExecutor`. It ports the event-driven
executor concept from `rclcpp`. Treat it as experimental when establishing
public APIs, operational expectations, or compatibility commitments.

## Generic clients on subordinate nodes

Generic clients constructed from an `rclcpp` subordinate node honor the
subordinate node's sub-namespace. Resolve names with that sub-namespace in mind
instead of assuming the parent node's namespace alone.

Parameters accessed through a subordinate node use the parent node's
`rclcpp::node_interfaces::NodeParametersInterface`. Account for that shared
parameter interface when reasoning about parameter declaration and access.

## Navigation goals interface

The `nav_msgs/msg/Goals` interface carries an array of navigation goals. It is
the common interface to reach for when exchanging a collection of navigation
goals.

## Rust interface generation

`rosidl_rust` is enabled as one of the default ROS interface code generators.
Default interface-generation workflows therefore produce Rust code without
requiring it to be added as an extra generator.

## NV12 images

NV12 is included in the common-interface pixel formats. Images produced by
hardware-accelerated decoders can identify this encoding directly rather than
being forced through an unrelated pixel-format label.

## Dynamic typesupport restriction

`rosidl_dynamic_typesupport` no longer supports `float128`. Remove dynamic
typesupport paths that depend on that type, or choose a supported field type.
Do not assume that static interface support implies dynamic `float128` support.

## Modern CMake dependency linking

`ament_target_dependencies()` is deprecated. Prefer imported CMake targets
with `target_link_libraries()`:

```cmake
target_link_libraries(my_target PUBLIC SomePackage::SomeTarget)
```

CMake does not allow the plain and keyword signatures of
`target_link_libraries()` to be mixed for one target. If the target already has
a plain-signature call, make subsequent calls plain too:

```cmake
target_link_libraries(my_target SomePackage::SomeTarget)
```

Use `PUBLIC`, `PRIVATE`, or `INTERFACE` only when the target's existing calls
use the keyword signature consistently.

## Compound launch path components

`PathJoinSubstitution` accepts a list of strings or substitutions as a single
path component. A nested list can therefore combine a launch substitution with
a suffix:

```python
PathJoinSubstitution([
    'robot_description',
    'urdf',
    [LaunchConfiguration('model'), '.xacro'],
])
```

Here the outer list describes path components, while the nested list forms one
component from the selected model name and `.xacro`. This avoids a separate
concatenation helper.
