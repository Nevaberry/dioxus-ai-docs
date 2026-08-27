---
name: gazebo-sim-knowledge-patch
description: Gazebo Sim
version: "10.1.1"
license: MIT
metadata:
  author: Nevaberry
---


# Gazebo Sim compatibility guidance

Use this skill when migrating, building, configuring, integrating, or testing
Gazebo Sim. Inspect the project's manifests, SDF, plugins, and observed runtime
behavior first. Apply only guidance relevant to the installed release, and
prefer the project and its tests when they disagree with this material.

## Working method

1. Identify the installed Gazebo Sim, GUI, Transport, and SDF package versions.
2. Locate affected custom systems, GUI plugins, SDF files, build definitions,
   launch processes, and downstream message consumers.
3. Read the topic reference that matches the change before editing code.
4. Make migration changes together: API spelling, packaging, QML, and runtime
   path changes often cross source, build, and deployment files.
5. Run focused unit or system tests, then launch representative worlds and
   inspect transport, physics, rendering, and shutdown behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/migration-build-gui.md](references/migration-build-gui.md) | Qt 6 migration, runtime paths, component registration, CLI packaging, Bazel, installation, GUI, rendering |
| [references/physics-environment.md](references/physics-environment.md) | physics queries, inertia, constraints, aerodynamics, wind, gravity, terrain, numerical behavior |
| [references/runtime-integration-testing.md](references/runtime-integration-testing.md) | lifecycle, reset, plugins, Python, transport, ROS, networking, WebSocket, commands, time, ECM |
| [references/systems-control-data.md](references/systems-control-data.md) | pose and sensor data, entity semantics, controllers, drives, battery, wind, publication rates |

## Breaking migration changes

### Port custom GUI plugins to Qt 6

- Build against `gz-gui10` and Qt 6.
- Prefix QML references to exposed C++ objects with `_`; do not rename the C++
  objects solely for this convention.
- Remove version numbers from Qt QML imports.
- Port `FileDialog`, `TreeView`, and other changed QML types to Qt 6 APIs.
- Check `gz::gui::App()` before dereferencing it.
- Avoid manual `QCoreApplication::processEvents()` calls in plugins.

### Replace removed path macros

Do not include `config.hh` to obtain Gazebo Sim configuration or install
directories. Replace macros with these runtime functions:

| Purpose | Function |
| --- | --- |
| GUI configuration | `gz::sim::getGUIConfigPath()` |
| System configuration | `gz::sim::getSystemConfigPath()` |
| Server configuration | `gz::sim::getServerConfigPath()` |
| System plugin install directory | `gz::sim::getPluginInstallDir()` |
| GUI plugin install directory | `gz::sim::getGUIPluginInstallDir()` |
| World install directory | `gz::sim::getWorldInstallDir()` |

Runtime discovery also keeps code compatible with relocatable installations.

### Update component factory registration

Pass a C-string type name and a `RegistrationObjectId` to
`gz::sim::components::Factory::Register`. Retain the ID and pass it to
`Unregister`; the parameterless form is removed.

```cpp
Register(const char *_type, ComponentDescriptorBase *_compDesc,
         RegistrationObjectId _regObjId);
Unregister(RegistrationObjectId _regObjId);
```

### Repackage commands and dependencies

- Treat `gz` commands as standalone applications, not Ruby-loaded CLI
  libraries.
- Use unversioned Gazebo package names in dependency declarations.
- Use Bzlmod and registry modules instead of legacy Bazel workspace setup.
- Invoke `gz model` as a standalone executable.

### Update renamed APIs

Replace `systemTimeISO` with `systemTimeIso`. Search source and tests for the
old casing because it is easy to preserve in mocks or wrapper names.

## Runtime behavior that changes contracts

### Propagate real command results

UserCommands service responses report whether the command itself succeeded.
Do not reduce the outcome to transport-call success; propagate the returned
status to clients and tests.

### Treat invalid SDF handling as corrected

Do not rely on behavior from the bad-SDF server regression. Test malformed SDF
as an error path against the corrected server contract.

### Shut down and reset cleanly

- Allow service managers and containers to terminate the simulator with
  `SIGTERM`.
- Use the public reset API where application code needs a reset.
- Exercise `ISystemReset` through `TestFixture` for reset-aware systems.
- Account for startup detection of an already-running server.

### Follow WebSocket ownership and schema changes

Configure and package the WebSocket server with Gazebo Sim rather than
`gz-launch`. Schema consumers must also accept top-level enum declarations.

## Build and plugin loading

### Respect Bazel coverage limits

Core-library Bazel support did not initially imply GUI, physics, or systems
support. System targets were added separately. Check target availability before
converting a build, and use Bazel 9.1.1 when following the repository default.

### Load static plugins through normal paths

Both system plugins and physics engines can load from the static plugin
registry. Avoid requiring a dynamic shared-library path when the plugin is
registered statically.

### Keep installations relocatable

Do not derive resources from the original absolute location of `gz-sim-main`.
Use runtime path APIs and validate the installed layout in packaging tests.

## Physics and environment quick reference

### Send sparse physics updates

Physics update messages change only fields that are present. Omitted fields
retain their prior values, so send only the parameters intended to change.

### Choose the fixed-constraint mechanism

Use the Physics system parameter for global fixed-constraint enforcement. Use
`DetachableJointEnforceFixedConstraint` when the choice belongs to a
detachable joint's ECS state.

### Revalidate corrected numeric behavior

- Do not accept angular-velocity spikes caused only by quaternion sign flips.
- Recheck advanced `LiftDrag` moments that were tuned to the former
  calculation.
- Expect wind-aware airspeed to follow the wind triangle.
- Let the IMU react to runtime gravity changes.

### Prefer supported geometry and inertia paths

- Query ray intersections through the Physics system.
- Obtain link AABBs from collision geometry.
- Use `MeshInertialCalculator` for SDF-string loads and pass its mesh
  optimization parameters when needed.
- With automatic inertia enabled, specify mass when Gazebo should derive
  density and inertial parameters.

### Configure spatially varying slip

Use `LookupWheelSlip` with an 8-bit RGB lookup map. Ensure the map is reachable
through `common::findFile` resource resolution.

## Systems and control quick reference

### Update pose consumers

The pose publisher can emit poses below top-level models and suppresses empty
poses. Consumers should support the wider entity scope without expecting empty
placeholder entries.

### Configure joint control deliberately

- Disable force-mode braking when a joint should coast.
- Update `JointPositionController` PID parameters dynamically when retuning at
  runtime.
- Address nested joints through `JointController`.
- Use `DriveToPoseController` for target-pose motion.
- Use `MecanumDrive` when odometry and TF output are required.

### Use configurable data paths

- Select the battery-current sign convention in the battery plugin.
- Configure `ParticleEmitter` topic names in SDF.
- Set the Joint State Publisher update rate at the source.
- Publish wind on Gazebo or ROS topics for the relevant consumers.
- Use `Link` sensor accessors rather than rebuilding relationships manually.

## Integration and distributed simulation

### Select transport and ROS interfaces

Set `GZ_TRANSPORT_IMPLEMENTATION=zenoh` in each process that should use Zenoh.
For portable robot integration, target the community standard ROS simulation
interface.

### Test language and network behavior

- Remove Python workarounds that existed only because systems or
  `TestFixture` held the GIL incorrectly.
- Expect `LogicalCamera` detections for nested models.
- Expect `NetworkManager` to create entities on network secondaries.
- Use ECM APIs to clear addition and removal tracking when establishing a new
  state-consumption point.

## GUI and output checks

- Plot pose attributes through the Component Inspector.
- Use frustum visualization where sensor geometry must be inspected.
- Handle contact visualization as marker arrays.
- On WSLg, account for `WAYLAND_DISPLAY`-based fallback to X rendering.
- Do not expect the Quick Start dialog to be enabled by default on Windows.

## Validation checklist

- Build all touched C++, Python, CMake, QML, and SDF paths.
- Launch at least one representative world through the installed executable.
- Exercise static and dynamic plugin-loading configurations where supported.
- Verify command failure, invalid SDF, reset, and `SIGTERM` paths.
- Compare physics and sensor outputs after gravity, wind, inertia, PID, or
  constraint changes.
- Inspect ROS, Gazebo Transport, WebSocket, odometry, TF, pose, joint-state,
  and wind consumers for message-shape or topic assumptions.
- Test GUI plugins on Qt 6 and rendering on each supported display environment.
- Re-run distributed tests with a network secondary when networking changes.
