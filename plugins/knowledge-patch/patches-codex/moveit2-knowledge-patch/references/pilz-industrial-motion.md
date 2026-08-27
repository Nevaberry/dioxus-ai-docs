# Pilz Industrial Motion

## Pipeline loading and Cartesian limits

Load Pilz as `pilz_industrial_motion_planner/CommandPlanner`. Cartesian limits
must resolve under `<robot_description>_planning.cartesian_limits`; therefore,
the standard `robot_description` URDF parameter uses the
`robot_description_planning` namespace.

```yaml
cartesian_limits:
  max_trans_vel: 1
  max_trans_acc: 2.25
  max_trans_dec: -5
  max_rot_vel: 1.57
```

Joint parameters can additionally set `has_deceleration` and a negative
`max_deceleration`. Parameterized limits must be at least as strict as URDF
limits, and Pilz applies the strictest common joint limits. Rotational
acceleration and deceleration are derived from the corresponding translational
ratio and `max_rot_vel`.

## PTP, LIN, and CIRC request semantics

Set `MotionPlanRequest.planner_id` to `PTP`, `LIN`, or `CIRC`.

- PTP synchronizes trapezoidal joint profiles using the slowest lead axis.
- LIN and CIRC synchronize Cartesian translation with quaternion-slerped
  rotation, require a zero-velocity start state, and interpret the request's
  scaling factors as Cartesian limits.

## Circular-path constraints

CIRC names its defining-point mode in `path_constraints.name`: use `center` or
`interim`. Put the actual point in the `.position` field under
`path_constraints.position_constraints[].constraint_region.primitive_poses[]`.

A center selects the shorter arc and cannot produce a half-circle. An interim
point forces the arc through that point but cannot produce a full circle.

```cpp
request.planner_id = "CIRC";
request.path_constraints.name = "interim";
moveit_msgs::msg::PositionConstraint via;
via.constraint_region.primitive_poses.emplace_back();
via.constraint_region.primitive_poses.back().position = via_point;
request.path_constraints.position_constraints.push_back(via);
```

## Blended motion sequences

Each `MotionSequenceItem` stores a normal motion request in `req` and a
`blend_radius`. A positive radius permits motion toward the next goal without
stopping.

Apply all sequence constraints:

- only the first item may specify a start state;
- adjacent blend spheres must not overlap—the two radii must sum to less than
  the distance between their goals;
- a sequence may use multiple planning groups;
- if any item fails to plan, none of the items execute.

## Service and action interfaces

Enable these `move_group` capabilities:

- `pilz_industrial_motion_planner/MoveGroupSequenceService`
- `pilz_industrial_motion_planner/MoveGroupSequenceAction`

The `/plan_sequence_path` service plans a `MotionSequenceRequest` and returns
trajectories without executing them. The `/sequence_move_group` action plans
and executes unless `planning_options.plan_only` is set.

Unlike the ordinary MoveGroup action, the sequence action still executes when
the robot already satisfies the goal. This preserves circular and similar
motions that would otherwise be skipped.
