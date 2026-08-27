---
name: ros2-navigation-nav2-knowledge-patch
description: Nav2
version: "1.3.12"
license: MIT
metadata:
  author: Nevaberry
---


# Nav2 Knowledge Patch

Use this skill when configuring, migrating, extending, or troubleshooting Nav2.
Start with the breaking interface and parameter changes below, then open the
topic reference that matches the subsystem being changed. Treat the running
distribution's packages, interfaces, and tests as authoritative when a mixed or
backported installation differs from these defaults.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and integration](references/migration-and-integration.md) | Distribution status, messages, namespaces, ROS wrappers, simulation, RViz, lifecycle, and test builds |
| [Behavior Trees](references/behavior-trees.md) | Error propagation, node and port renames, selectors, subtrees, cancellation, validation, and replanning |
| [Planning and control](references/planning-and-control.md) | Planner/controller selection, server behavior, MPPI, RPP, SMAC, Rotation Shim, goal checking, and smoothing |
| [Costmaps, localization, and mapping](references/costmaps-localization-and-mapping.md) | Costmap APIs, layers, transports, clearing, inflation, AMCL, footprints, and vector objects |
| [Routing, docking, and behaviors](references/routing-docking-and-behaviors.md) | Route Server, docking, Following Server, Behavior Server, loopback simulation, and motion behaviors |
| [Collision Monitor](references/collision-monitor.md) | Command pipeline, fail-safe timing, zones, sources, runtime controls, debounce, and costmap input |

## Migration triage

Check these first when moving launch files, parameter files, plugins, or trees:

- `cmd_vel` uses `geometry_msgs/TwistStamped` by default. Set
  `enable_stamped_cmd_vel: false` on every affected node only for a deliberately
  retained `Twist` pipeline.
- Replace BT Navigator's removed `error_code_names` with
  `error_code_name_prefixes`, and wire both `error_code_id` and `error_msg` on
  relevant action nodes.
- Multi-pose actions now carry `nav_msgs/Goals`; use `poses.goals` or
  `goals.goals`. Preserve the parallel `WaypointStatus` list through pruning
  nodes.
- Remove `use_namespace` from `nav2_bringup`. `namespace` is always applied,
  defaults to `/`, and relative topics resolve inside it.
- Move `Costmap2DROS.map_topic` to the `StaticLayer`; use the consolidated
  `Costmap2DROS(name, parent_namespace, use_sim_time)` constructor.
- Treat `control_frequency` as startup-only configuration.
- In Rotation Shim, nest the primary controller's `plugin` and parameters
  beneath `primary_controller`.
- In MPPI, configure a named motion-model plugin group rather than legacy
  `DiffDrive`, `Omni`, or `Ackermann` string values.
- Replace `ValidatePath.check_full_path` with the oppositely worded
  `stop_at_first_collision`; old `false` maps to new `true`.
- Move controller-specific plan transformation and pruning parameters to
  Controller Server's path-handler plugin.
- Retune Constrained Smoother weights because its corrected objective is
  `weight * residual²`.
- Move navigator blackboard-ID parameters beneath each navigator plugin, and
  rename `TruncatePathLocal.robot_frame` to `robot_base_frame`.

See [Migration and integration](references/migration-and-integration.md) and
[Behavior Trees](references/behavior-trees.md) for the complete migration set.

## Action error propagation

Configure contextual action errors with prefixes:

```yaml
error_code_name_prefixes: [compute_path, follow_path, spin, route]
```

Expose matching tree ports:

```xml
<FollowPath path="{path}" error_code_id="{follow_path_error_code}"
            error_msg="{follow_path_error_msg}"/>
```

The removed `error_code_names` parameter causes a startup exception rather
than silently falling back.

## Namespaces and message interfaces

- Prefer relative topics such as `scan` for namespaced robots. Keep `/scan`
  only when the source is intentionally global.
- Costmap layers that must resolve relative to their parent costmap can use
  `joinWithParentNamespace()` instead of their private layer namespace.
- With stamped velocity enabled, preserve timestamps through smoothing and
  safety nodes so stale commands can be rejected.
- For dynamic footprints, enable `subscribe_to_stamped_footprint` only when
  publishing `PolygonStamped`; the subscription type changes from `Polygon`.

## Planning and control quick reference

- Use NavFn, Smac 2D, or Theta Star primarily for circular differential or
  omnidirectional robots. Use Smac Hybrid-A* for footprint-aware,
  curvature-constrained platforms and Smac Lattice for explicit kinematic
  control sets.
- DWB normally serves differential and omnidirectional bases. RPP and Vector
  Pursuit do not support omnidirectional motion; MPPI and TEB span differential,
  omnidirectional, Ackermann, and legged platforms.
- Controller Server's costmap freshness timeout defaults to `0.3` seconds;
  Planner Server's defaults to `1.0` second.
- Controller exception tolerance defaults to disabled (`failure_tolerance:
  0.0`); `-1.0` tolerates failures indefinitely.
- `use_realtime_priority: true` requests thread priority `90` and requires an
  adequate process-user `rtprio` limit.
- `PositionGoalChecker` ignores orientation. Axis, symmetric-yaw, and adaptive
  goal checkers cover more specialized completion semantics.
- Partial multi-pose planning is opt-in with `allow_partial_planning`; inspect
  `last_reached_index` before accepting a returned prefix.
- Keep Velocity Smoother limits at least as permissive as Dynamic Window Pure
  Pursuit's controller limits.

Open [Planning and control](references/planning-and-control.md) before changing
planner, controller, goal-checker, smoother, or path-handler plugins.

## Behavior Tree quick reference

- `NonblockingSequence` ticks later children while an earlier child is still
  `RUNNING`.
- `PauseResumeController` combines pause/resume services with
  `PersistentSequence`, whose bidirectional child-index port resumes progress.
- `RoundRobin` now defaults to `wrap_around="false"` and fails after the last
  child unless wrapping is explicitly enabled.
- The default navigation tree can select progress checker, goal checker, path
  handler, controller, and planner IDs through selector topics.
- The default near-goal fallback retains a valid remaining plan when the goal
  is unchanged and nearby; it replans when any guard fails.
- Reusable subtree files come from `bt_search_directories`; select trees by a
  unique ID rather than a shared `MainTree`.

Open [Behavior Trees](references/behavior-trees.md) when modifying XML or BT
Navigator parameters; it includes all action/condition renames and port changes.

## Costmap and localization quick reference

- Keep costmap filters in `filters`, separate from ordinary `plugins`; filters
  run after the layered costmap has been combined.
- A selective clear request is atomic: an invalid or non-clearable named plugin
  makes the request fail without clearing anything.
- `transport_type` may select compressed point-cloud transports; `raw` remains
  the default.
- `custom_inscribed_radius: 0.0` bypasses the inscribed region and is unsafe for
  ordinary planners or controllers that expect standard cost semantics.
- AMCL `random_seed: -1` remains nondeterministic; a nonnegative seed makes
  particle-filter runs repeatable.
- `always_reset_initial_pose: true` requires a new initial pose after reset;
  `first_map_only: true` ignores replacement maps.

Open [Costmaps, localization, and mapping](references/costmaps-localization-and-mapping.md)
for conversion values, startup transform timing, visualization, mapping, and
layer details.

## Routing, docking, and behavior quick reference

- Route Server plans over a predefined graph, emits node/edge events, and can
  smooth corners with tangent arcs when geometry permits.
- Docking collision checking is enabled by default. Configure direction per
  plugin with `dock_direction`; use `reverse_to_dock` only for the staged
  forward-detection/backward-entry workflow.
- Custom charging and non-charging dock plugins must implement detection start
  and stop hooks.
- Behavior Server loads Spin, BackUp, DriveOnHeading, and Wait by default;
  AssistedTeleop must be added explicitly.
- `disable_collision_checks` defaults to `false` for Spin, BackUp, and
  DriveOnHeading. Do not disable it casually.
- The loopback simulator is for ideal odometry tests, not physics or localization
  error modeling.

Open [Routing, docking, and behaviors](references/routing-docking-and-behaviors.md)
for server parameters, action-owned inputs, route operations, and following.

## Collision Monitor safety checklist

- Put Collision Monitor after smoothing in the command pipeline and publish its
  safety-adjusted output on the robot command topic.
- Keep `source_timeout` enabled unless another fail-safe owns stale-source
  handling. A stale observation source stops the robot.
- `base_shift_correction` should remain enabled for fast robots or modest sensor
  rates.
- Overlapping zones resolve to the most restrictive action. For velocity
  polygons, order overlaps deliberately and finish with a catch-all range.
- Migrating Humble thresholds requires `min_points = max_points + 1`.
- Costmap source cost `255` follows `treat_unknown_as_obstacle`, separately from
  `cost_threshold`.
- Runtime `Toggle` disables polygons but leaves sensor checking active.

Open [Collision Monitor](references/collision-monitor.md) before changing zone
geometry, temporal debounce, observation filters, source types, or fail-safe
timers.

## Verification workflow

After a migration or configuration change:

1. Confirm each renamed or moved parameter is absent from its old scope.
2. Inspect actual action, service, topic, and BT port types instead of assuming
   an older interface.
3. Verify relative topic resolution under the intended robot namespace.
4. Exercise failure paths: stale sensors, controller exceptions, partial plans,
   invalid clear-plugin names, and BT cancellation.
5. Check visualization and introspection only after functional behavior; both
   are optional and may be disabled by default.
6. Run isolated middleware tests with
   `--cmake-args -DUSE_ISOLATED_TESTS=ON` when a separate Zenoh router is not
   part of the test environment.
