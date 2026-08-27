# MoveIt Task Constructor

## Stage result flow and containers

Stage order is constrained by result flow:

- generators create states independently and send them in both directions;
- propagators extend a neighboring result forward or backward;
- connectors bridge independently produced states at their two interfaces;
- wrappers modify or filter one child;
- serial containers accept only end-to-end child solutions; and
- parallel containers select alternatives, provide fallbacks, or merge
  independent solutions.

## Task lifecycle and solution handling

Set root properties before adding stages. Then initialize, request a bounded
number of successful plans, and explicitly select a solution to visualize or
execute. `init()` can throw `InitStageException`; `plan(5)` stops after five
successful solutions.

```cpp
mtc::Task task;
task.stages()->setName("pick and place");
task.loadRobotModel(node);
task.setProperty("group", arm_group_name);
task.setProperty("eef", hand_group_name);
task.setProperty("ik_frame", hand_frame);

task.init();
if (task.plan(5)) {
  const auto& solution = *task.solutions().front();
  task.introspection().publishSolution(solution);
  auto result = task.execute(solution);
}
```

## Planners and connector stages

MTC supplies `PipelinePlanner(node)`, `JointInterpolationPlanner`, and
`CartesianPath`. Stages receive shared planner objects. `Connect` takes a
`GroupPlannerVector`, allowing different planners for multiple groups while
bridging two generated states.

```cpp
auto pipeline = std::make_shared<mtc::solvers::PipelinePlanner>(node);
auto joint = std::make_shared<mtc::solvers::JointInterpolationPlanner>();
auto cartesian = std::make_shared<mtc::solvers::CartesianPath>();
cartesian->setStepSize(0.01);

auto connect = std::make_unique<mtc::stages::Connect>(
    "move to place", mtc::stages::Connect::GroupPlannerVector{
                         {arm_group_name, pipeline},
                         {hand_group_name, joint}});
connect->setTimeout(5.0);
connect->properties().configureInitFrom(mtc::Stage::PARENT);
task.add(std::move(connect));
```

## Property forwarding

Task properties are not automatically inherited through nested stages. Expose
selected task properties to a container, configure them from `Stage::PARENT`,
and let an IK wrapper import generated `target_pose` from `Stage::INTERFACE`.

```cpp
auto pick = std::make_unique<mtc::SerialContainer>("pick object");
task.properties().exposeTo(pick->properties(), {"eef", "group", "ik_frame"});
pick->properties().configureInitFrom(
    mtc::Stage::PARENT, {"eef", "group", "ik_frame"});
```

## Monitored pose generators and IK wrappers

`GenerateGraspPose` must monitor the earlier `CurrentState` so it sees object
state. `GeneratePlacePose` instead monitors the saved attach-object stage so it
knows how the object is attached. Move pose generators into `ComputeIK`, where
IK count, joint-space separation, and IK frame are configured.

```cpp
auto current = std::make_unique<mtc::stages::CurrentState>("current");
auto* current_state_ptr = current.get();
task.add(std::move(current));

auto poses = std::make_unique<mtc::stages::GenerateGraspPose>("grasp poses");
poses->setPreGraspPose("open");
poses->setObject("object");
poses->setAngleDelta(M_PI / 12);
poses->setMonitoredStage(current_state_ptr);

auto ik = std::make_unique<mtc::stages::ComputeIK>("grasp IK", std::move(poses));
ik->setMaxIKSolutions(8);
ik->setMinSolutionDistance(1.0);
ik->setIKFrame(grasp_frame_transform, hand_frame);
ik->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
ik->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
```

For placement, `GeneratePlacePose::setPose()` accepts a stamped target that may
use the object frame, and `ComputeIK::setIKFrame("object")` makes the object the
IK frame.

## Relative motions and planning-scene transitions

`MoveRelative` combines a Cartesian planner, minimum and maximum travel, and a
stamped direction whose frame determines how its vector is interpreted. Pick
and place transitions use `ModifyPlanningScene` to allow hand-object collision,
attach the object, later forbid collision, and detach it.

```cpp
auto lift = std::make_unique<mtc::stages::MoveRelative>("lift", cartesian);
lift->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
lift->setMinMaxDistance(0.1, 0.3);
lift->setIKFrame(hand_frame);
geometry_msgs::msg::Vector3Stamped up;
up.header.frame_id = "world";
up.vector.z = 1.0;
lift->setDirection(up);

auto attach = std::make_unique<mtc::stages::ModifyPlanningScene>("attach");
attach->attachObject("object", hand_frame);
auto detach = std::make_unique<mtc::stages::ModifyPlanningScene>("detach");
detach->detachObject("object", hand_frame);
```

When `ModifyPlanningScene` propagates backward, its operation reverses. In that
direction, allowing collisions notably uses `allowCollisions(..., false)`
rather than `true`.

## Stage diagnostics

The terminal stage diagram reports, left to right, solutions propagated
backward, generated locally, and propagated forward. Arrows show propagation
direction, so the first stage with zero generation or forwarding identifies
where composition failed. Retrieve a stage visualization identifier with
`task.stages()->findChild(name)->introspectionId()`.
