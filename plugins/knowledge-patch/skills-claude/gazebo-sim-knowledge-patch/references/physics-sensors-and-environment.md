# Physics, Sensors, and Environment

## Queries, sensors, and geometry

### Query ray intersections (since 9.1.0)

The Physics system supports ray-intersection queries.

### Configure battery-current sign (since 9.1.0)

The battery plugin has a parameter for selecting the current-sign convention required by an integration.

### Access link sensors (since 9.1.0)

The public C++ `Link` API provides accessors for sensors associated with a link.

### Derive link bounds from collisions (since 9.2.0)

Obtain a link's axis-aligned bounding box from its collision geometry.

### Detect nested models with LogicalCamera (since 9.2.0)

The `LogicalCamera` plugin detects nested models.

## Inertia and mass

### Calculate mesh inertia from SDF strings (since 9.2.0)

`MeshInertialCalculator` is registered when loading a simulation from an SDF string, enabling mesh-inertia calculation for that path.

### Tune mesh-inertia optimization (since 9.2.0)

`MeshInertialCalculator` accepts mesh-optimization parameters.

### Derive automatic inertia from mass (`jetty-highlights`)

When `inertial/@auto` is enabled, specify mass instead of density and let Gazebo derive density and inertial parameters:

```xml
<inertial auto="true">
  <mass>5.0</mass>
</inertial>
```

## Wind and aerodynamics

### Publish wind information (since 9.2.0)

Wind information can be published to both Gazebo and ROS topics.

### Model reversible airfoils (since 9.3.0)

The `LiftDrag` system supports reversible airfoils.

### Calculate wind-aware airspeed (since 9.3.0)

Airspeed under wind influence uses the wind triangle. Tests and consumers should expect the corrected windy-condition result.

### Use corrected advanced LiftDrag moments (since 10.5.0)

Advanced LiftDrag moment computation is corrected. Revalidate results that depended on the earlier calculation.

## Wheel slip and friction

### Map texture colors to wheel slip (`jetty-highlights`)

The `LookupWheelSlip` system uses an 8-bit RGB lookup map to translate texture colors into material-friction values, allowing friction to vary across a surface.

### Resolve the slip map as a resource (since 10.0.0)

`LookupWheelSlip` locates its slip map with `common::findFile`; configure resource lookup accordingly.

## Physics engines and constraints

### Enforce fixed constraints (since 10.0.0)

The Physics system has a parameter for enforcing fixed constraints.

### Load statically registered physics engines (since 10.0.0)

Physics-engine plugins can load from the static plugin registry.

### Enforce detachable-joint fixed constraints (since 10.5.0)

The ECS provides a `DetachableJointEnforceFixedConstraint` component for detachable-joint fixed-constraint enforcement.

### Command collision bitmasks (since 10.5.0)

The ECS provides `CollideBitmaskCmd` and `CategoryBitmaskCmd` components for collision and category bitmask commands.

### Apply partial physics updates (since 10.5.0)

Physics update messages change only parameters present in the message; omitted parameters remain unchanged.

## Runtime corrections and visualization

### Propagate runtime gravity changes (since 10.1.0)

The IMU system reacts to gravity changes. Gravity updates through the GUI and the gravity-setting command are also corrected.

### Ignore quaternion sign-flip spikes (since 10.5.0)

Quaternion sign flips no longer cause angular-velocity spikes. Such spikes are not expected simulation output.

### Use corrected tactile behavior (since 10.5.0)

A tactile plugin regression is fixed; behavior from affected builds is not the intended contract.

### Consume contact marker arrays (since 10.5.0)

Contact visualization uses marker arrays.
