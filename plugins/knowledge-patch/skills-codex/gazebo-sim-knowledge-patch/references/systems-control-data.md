# Systems, Control, and Data

## Pose, sensors, and entity data

### Publish non-top-level poses

The pose publisher is not limited to top-level model poses (9.1.0). Subscribers
must be prepared for poses from deeper entity scopes.

It also suppresses empty poses (10.1.0), so absence of an empty entry is normal
and should not be treated as a dropped message.

### Access sensors through Link

The public C++ `Link` API has sensor accessor methods for sensors associated
with a link (9.1.0). Prefer these accessors over reconstructing link-to-sensor
relationships externally.

### Read configurable particle-emitter topics

`ParticleEmitter` accepts its topic from SDF (10.1.0). Read or set the topic in
configuration rather than assuming a fixed topic.

### Assign entity semantics

The `EntitySemantics` system assigns categories and tags to entities (10.0.0).
Use it for machine-readable entity classification instead of encoding all
semantics in names.

## Controllers and drive systems

### Configure force-mode braking

`JointController` can disable braking in force mode (9.3.0). Set the option
when force-controlled joints must coast instead of applying braking
unconditionally.

### Change position PID parameters dynamically

`JointPositionController` supports dynamic PID parameters (9.3.0). Update its
PID configuration at runtime rather than treating gains as immutable startup
state.

### Control nested joints

`JointController` supports nested joints (10.0.0). Resolve and command nested
joint entities through the controller instead of limiting control to
top-level joints.

### Drive to a target pose

The `DriveToPoseController` system plugin is available (9.2.0). Use it when a
system should drive an entity toward a requested pose.

### Use Mecanum drive outputs

The `MecanumDrive` plugin provides odometry and TF output (10.0.0). Integrations
can consume those outputs directly rather than recreating them from wheel
commands.

## Power, wind, and publication rates

### Select the battery-current convention

The battery plugin exposes a parameter that adjusts current sign (9.1.0).
Configure the convention required by the integration instead of negating
measurements downstream.

### Publish wind to Gazebo and ROS

Wind information can be published to both Gazebo and ROS topics (9.2.0). Use
the appropriate topic for native or ROS-connected consumers.

### Set Joint State Publisher frequency

The Joint State Publisher has an update-rate parameter (10.5.0). Configure it
to control publication frequency instead of rate-limiting the output later.
