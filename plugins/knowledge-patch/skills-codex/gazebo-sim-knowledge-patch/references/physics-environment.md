# Physics and Environment

## Geometry and physics queries

### Query ray intersections

The Physics system supports ray-intersection queries (9.1.0). Use the
simulation capability directly when implementing picking, ranging, or
geometry checks.

### Derive link bounds from collisions

A link's axis-aligned bounding box can be obtained from its collision geometry
(9.2.0). This makes collision-derived bounds available at link scope.

### Load mesh inertia from every supported source

`MeshInertialCalculator` is registered when a simulation is loaded from an
SDF string, so mesh-inertia calculation works on that loading path (9.2.0).
The calculator also accepts mesh-optimization parameters; pass them when
tuning the inertia mesh rather than preprocessing the source unconditionally.

### Prefer mass-based automatic inertia when appropriate

With `inertial/@auto` enabled, an object may specify mass instead of density.
Gazebo derives density and inertial parameters (jetty-highlights):

```xml
<inertial auto="true">
  <mass>5.0</mass>
</inertial>
```

## Constraints, joints, and contacts

### Configure fixed-constraint enforcement

The Physics system has a parameter for enforcing fixed constraints (10.0.0).
For detachable joints, the ECS also provides the
`DetachableJointEnforceFixedConstraint` component (10.5.0); use the component
when enforcement belongs in entity state.

### Rely on detachable-joint cleanup

Removing a model also removes its detachable joints (9.1.0). Cleanup logic
should not treat leftover detachable joints as intended behavior.

### Use collision bitmask commands

The ECS provides `CollideBitmaskCmd` and `CategoryBitmaskCmd` components for
collision and category bitmask commands (10.5.0).

### Treat tactile failures as a fixed regression

The tactile plugin regression is fixed (10.5.0). Do not encode behavior from
affected builds as the plugin's intended contract.

## Aerodynamics, wind, and gravity

### Model reversible airfoils

The `LiftDrag` system supports reversible airfoils (9.3.0). Configure this for
aerodynamic surfaces whose operation reverses rather than approximating the
reverse regime externally.

### Use wind-aware airspeed

Airspeed under wind influence is calculated with the wind triangle (9.3.0).
Update expectations for windy conditions instead of comparing against a
wind-agnostic result.

### Account for corrected LiftDrag moments

The advanced `LiftDrag` implementation corrects its moment calculation
(10.5.0). Revalidate results that were calibrated against the earlier,
incorrect computation.

### Propagate runtime gravity changes

The IMU system reacts to gravity changes. GUI-based gravity updates and the
gravity-setting command also propagate correctly (10.1.0), so sensors and
tests should observe the changed gravity without a restart.

## Terrain, friction, and environment data

### Export occupancy grids

Occupancy-grid maps can be exported from the `/scan_image` topic. Start
exploration by publishing (jetty-highlights):

```sh
gz topic -t /start_exploration -m gz.msgs.Boolean -p 'data: true'
```

### Configure texture-driven wheel slip

`LookupWheelSlip` maps colors in an 8-bit RGB lookup image to material-friction
values, allowing surface friction to vary spatially (jetty-highlights). Its
slip-map lookup uses `common::findFile` (10.0.0), so configure resources for
that resolution path rather than assuming a process-relative filename.

### Visualize static environments

`EnvironmentPreload` can visualize static environments (10.1.0). Use its
visualization path when inspecting preloaded environment data.

## Runtime physics updates and numerical behavior

### Send partial physics updates safely

Physics update messages modify only parameters present in the message;
omitted parameters retain their existing values (10.5.0). Send a sparse update
when changing one setting instead of reconstructing the entire parameter set.

### Ignore quaternion representation sign flips

Quaternion sign flips no longer create angular-velocity spikes (10.5.0).
Spikes caused only by equivalent `q` / `-q` representations are not expected
simulation output.

### Load statically registered physics engines

Physics-engine plugins can be loaded from the static plugin registry
(10.0.0). Static integration does not require a separate dynamic-plugin path.
