# Systems, Control, and Modeling

## Pose and state publication

### Publish poses beyond top-level models (since 9.1.0)

Pose Publisher is not limited to top-level model poses.

### Suppress empty poses (since 10.1.0)

Pose Publisher does not publish empty poses, so subscribers should not expect placeholder entries.

### Configure Joint State Publisher rate (since 10.5.0)

Joint State Publisher has an update-rate parameter for controlling publication frequency.

## Joint lifecycle and control

### Clean up detachable joints with models (since 9.1.0)

Removing a model also removes its detachable joints.

### Disable force-mode braking (since 9.3.0)

`JointController` can disable braking while operating in force mode.

### Change position PID dynamically (since 9.3.0)

`JointPositionController` supports dynamic PID parameters rather than fixed-only configuration.

### Control nested joints (since 10.0.0)

`JointController` supports nested joints.

## Drive systems

### Drive to a pose (since 9.2.0)

Use the `DriveToPoseController` system plugin for drive-to-pose behavior.

### Drive mecanum bases (since 10.0.0)

The `MecanumDrive` plugin provides odometry and TF output.

## Entity modeling and commands

### Assign entity categories and tags (since 10.0.0)

The `EntitySemantics` system assigns categories and tags to entities.

## Configurable and visualized systems

### Configure particle-emitter topics in SDF (since 10.1.0)

`ParticleEmitter` accepts its topic from SDF configuration.

### Visualize static environments (since 10.1.0)

`EnvironmentPreload` can visualize static environments.
