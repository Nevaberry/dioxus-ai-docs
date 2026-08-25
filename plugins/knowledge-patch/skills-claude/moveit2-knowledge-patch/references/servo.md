# MoveIt Servo

## Safety scaling and optional checks

Servo scales commanded velocity near singularities, self-collisions, and world
collisions, while enforcing joint position and velocity limits. Collision
checking and command smoothing are independently controlled by
`check_collisions` and `use_smoothing`.

## IK plugin configuration

Servo can use its inverse-Jacobian implementation or the planning group's IK
plugin from `kinematics.yaml`. Pass generated `robot_description_kinematics`
parameters to `ServoNode`; they appear as
`robot_description_kinematics.<group_name>.<param_name>`.

```python
servo_node = Node(
    package="moveit_servo",
    executable="servo_node",
    parameters=[
        servo_params,
        moveit_config.robot_description,
        moveit_config.robot_description_semantic,
        moveit_config.robot_description_kinematics,
    ],
)
```

Servo does not accept undeclared parameters from `kinematics.yaml`, so an IK
plugin with custom parameters must declare them within the plugin.

## Realtime scheduling

When a realtime kernel is available, the main `ServoNode` loop automatically
attempts `SCHED_FIFO` at priority `40`, reducing control-loop jitter without a
separate scheduler wrapper.

## Direct C++ interface

Construct `Servo` from a generated parameter listener and planning-scene
monitor. Select a `CommandType`, repeatedly pass a `JointJogCommand`,
`TwistCommand`, or `PoseCommand` to `getNextJointState()`, and consume the
returned `KinematicState`, which contains joint names, positions, velocities,
and accelerations.

```cpp
using namespace moveit_servo;

auto node = std::make_shared<rclcpp::Node>("servo_tutorial");
auto listener =
    std::make_shared<const servo::ParamListener>(node, "moveit_servo");
auto params = listener->get_params();
auto monitor = createPlanningSceneMonitor(node, params);
Servo servo(node, listener, monitor);

servo.setCommandType(CommandType::TWIST);
TwistCommand command{"panda_link0", {0.1, 0.0, 0.0, 0.0, 0.0, 0.0}};
KinematicState next = servo.getNextJointState(command);
StatusCode status = servo.getStatus();
```

## ROS command, output, and status interfaces

`ServoNode` receives `control_msgs::msg::JointJog`,
`geometry_msgs::msg::TwistStamped`, and `geometry_msgs::msg::PoseStamped` on
parameterized joint, Cartesian, and pose input topics. Twist and pose commands
require `header.frame_id`; twist commands currently use the robot planning
frame.

`command_out_type` selects either
`trajectory_msgs::msg::JointTrajectory` or
`std_msgs::msg::Float64MultiArray` on `command_out_topic`. Switch the active
input through `/<node_name>/switch_command_type`, pause through
`/<node_name>/pause_servo`, and monitor `/<node_name>/status`.

```bash
ros2 service call /servo_node/switch_command_type \
  moveit_msgs/srv/ServoCommandType "{command_type: 1}"
```

## Smoothing plugins

Set `smoothing_filter_plugin_name` when `use_smoothing` is enabled.

- `online_signal_smoothing::ButterworthFilterPlugin` is inexpensive and does
  not overshoot in joint space, but does not explicitly constrain acceleration
  or jerk.
- `online_signal_smoothing::AccelerationLimitedPlugin` respects acceleration
  limits when feasible and preserves the requested direction when kinematics
  allow, but may overshoot and does not constrain jerk.
- `online_signal_smoothing::RuckigFilterPlugin` provides the smoothest
  joint-limit- and acceleration-aware output, but may overshoot or swirl around
  sharp Cartesian corners.

Since 2.15.0, `AccelerationLimitedPlugin` supports both OSQP v0.6.x and the
redesigned v1.0 C API. Humble, Jazzy, and Kilted use apt-provided v0.6.x;
Lyrical and Rolling use the MoveIt `osqp_vendor` fork with v1.0.
