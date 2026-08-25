---
name: gazebo-sim-knowledge-patch
description: Gazebo Sim
version: 10.1.1
license: MIT
metadata:
  author: Nevaberry
---


# Gazebo Sim Knowledge Patch

Use this skill when writing, migrating, building, configuring, or debugging Gazebo Sim applications, systems, GUI plugins, SDF worlds, transport integrations, physics behavior, or test fixtures.

Prefer the project's manifests, source, tests, and observed runtime behavior when they disagree with general guidance. Determine the installed Gazebo Sim and related library versions before applying version-sensitive changes.

## Reference Index

| Reference | Topics |
| --- | --- |
| [GUI, Transport, and ROS](references/gui-transport-and-ros.md) | Qt6 GUI migration, QML, visualization, Zenoh, ROS interfaces, occupancy maps, Windows and WSLg |
| [Migration, Build, and Packaging](references/migration-build-and-packaging.md) | Bazel, Bzlmod, package naming, standalone tools, runtime paths, component registration, relocatability |
| [Physics, Sensors, and Environment](references/physics-sensors-and-environment.md) | Physics queries, inertia, gravity, wind, aerodynamics, collision commands, rendering and sensor fixes |
| [Server, Runtime, and APIs](references/server-runtime-and-apis.md) | Shutdown, plugin registries, Python, services, ECM, reset, networking, WebSocket, invalid SDF |
| [Systems, Control, and Modeling](references/systems-control-and-modeling.md) | Controllers, pose publication, entity semantics, detachable joints, drive systems, particle and state publishers |

## Start With Compatibility Checks

1. Identify the installed `gz-sim` package and the versions of `gz-gui`, `gz-transport`, and SDF libraries used by the project.
2. Inspect `CMakeLists.txt`, Bazel modules, package manifests, SDF files, and plugin loading paths.
3. Separate migration failures from simulation-behavior changes: Qt, packaging, and API breaks often fail at build or startup, while physics changes alter results.
4. For a regression claim, reproduce against the actual installed patch release before preserving a workaround.
5. Use the topic references to check related changes that may affect the same subsystem.

## Breaking Migration Changes

### Port custom GUI plugins to Qt6

Jetty's `gz-gui10` uses Qt6. Port Qt5 GUI plugins and QML imports before debugging plugin logic.

- Omit version numbers from Qt6 QML imports.
- Update Qt6-sensitive types such as `FileDialog` and `TreeView`.
- Access C++ objects exposed to QML with a leading underscore, for example:

```qml
_MyClass.FunctionFoo()
```

The C++ object itself does not need to be renamed.

Treat `gz::gui::App()` as nullable. Check the returned pointer before use, and avoid manually calling `QCoreApplication::processEvents()` in Qt6 plugins.

### Replace removed configuration macros

Do not include the removed `config.hh` path or rely on install-directory macros. Use runtime path functions:

| Removed macro | Runtime function |
| --- | --- |
| `GZ_SIM_GUI_CONFIG_PATH` | `gz::sim::getGUIConfigPath()` |
| `GZ_SIM_SYSTEM_CONFIG_PATH` | `gz::sim::getSystemConfigPath()` |
| `GZ_SIM_SERVER_CONFIG_PATH` | `gz::sim::getServerConfigPath()` |
| `GZ_SIM_PLUGIN_INSTALL_DIR` | `gz::sim::getPluginInstallDir()` |
| `GZ_SIM_GUI_PLUGIN_INSTALL_DIR` | `gz::sim::getGUIPluginInstallDir()` |
| `GZ_SIM_WORLD_INSTALL_DIR` | `gz::sim::getWorldInstallDir()` |

### Update component factory registration

The string-based `Factory::Register` overloads and parameterless `Unregister()` are gone. Register with a C-string type name and an explicit registration-object ID; unregister that same ID.

```cpp
Register(const char *_type, ComponentDescriptorBase *_compDesc,
         RegistrationObjectId _regObjId);
Unregister(RegistrationObjectId _regObjId);
```

### Update packaging and command assumptions

- Gazebo package dependencies use unversioned package names.
- The `gz` tool uses standalone applications instead of Ruby-loaded CLI libraries.
- Bazel consumers should use Bzlmod rather than legacy workspace setup.
- Rename `systemTimeISO` calls to `systemTimeIso`.

See [Migration, Build, and Packaging](references/migration-build-and-packaging.md) for the full migration and build guidance.

## Build Quick Reference

### Know the Bazel boundaries

Initial Bazel support covered only the core library, excluding GUI, physics, and systems. Systems were added later. Do not assume CMake and Bazel expose identical targets without checking the project version and module definitions.

Use Bazel 9.1.1 when following the repository default that declares it. Jetty and Ionic libraries and their required third-party packages are available through the Bazel Central Registry.

### Keep installed layouts relocatable

Use the runtime path APIs rather than compiled-in install paths. `gz-sim-main` supports relocation, so packaging should not reintroduce assumptions about its original installation prefix.

## Runtime and API Quick Reference

### Handle shutdown and startup explicitly

Gazebo Sim handles `SIGTERM` gracefully. Service managers and containers should send `SIGTERM` and allow cleanup time before escalating termination.

Startup detects an already-running server. Treat that diagnostic as a distinct startup condition rather than a generic server failure.

### Load statically registered plugins

System plugins and physics engines can load from the static plugin registry. When dynamic discovery finds nothing, check static registration before diagnosing a missing plugin.

### Trust service results

UserCommands services return the actual command status. Use the service result to decide whether a command succeeded; do not infer success merely from transport-level completion.

### Reset through public APIs

Simulation reset has a public callable API, and test fixtures support `ISystemReset`. Prefer those reset paths over reconstructing internal server state.

### Reject invalid SDF safely

Server handling for bad SDF files includes a regression fix. Do not treat behavior from an affected build as the intended invalid-input contract.

See [Server, Runtime, and APIs](references/server-runtime-and-apis.md) for Python GIL, ECM, networking, and WebSocket details.

## Physics and Environment Quick Reference

### Use automatic inertia from mass

With `inertial/@auto`, an SDF object may specify mass and let Gazebo derive density and inertial parameters:

```xml
<inertial auto="true">
  <mass>5.0</mass>
</inertial>
```

Mesh inertia also works when loading from an SDF string and accepts mesh-optimization parameters.

### Apply partial physics updates safely

Physics update messages change only fields present in the message. Omitted parameters retain their previous values, so partial updates need not resend the complete physics configuration.

### Revalidate aerodynamic expectations

The `LiftDrag` system supports reversible airfoils. Wind-influenced airspeed uses the wind triangle, and advanced LiftDrag moment calculation has been corrected. Rebaseline tests that depended on earlier results.

### Treat quaternion sign as equivalent orientation

Quaternion sign flips no longer produce angular-velocity spikes. Do not build downstream filters around those spikes as if they were physical motion.

See [Physics, Sensors, and Environment](references/physics-sensors-and-environment.md) for collision bounds, gravity, wheel slip, sensors, and visualization behavior.

## Systems and Control Quick Reference

### Configure controllers deliberately

- `JointController` can disable braking in force mode and can address nested joints.
- `JointPositionController` accepts dynamic PID parameters.
- `DriveToPoseController` provides drive-to-pose behavior.
- `MecanumDrive` provides odometry and TF output.
- Joint State Publisher has a configurable update rate.

### Expect scoped pose output

Pose Publisher can publish more than top-level model poses and suppresses empty poses. Consumers should tolerate the broader entity scope while not expecting placeholder entries.

### Model entity meaning explicitly

Use `EntitySemantics` to assign categories and tags to entities. Use `CollideBitmaskCmd` and `CategoryBitmaskCmd` components when commanding collision and category bitmasks.

See [Systems, Control, and Modeling](references/systems-control-and-modeling.md) for detachable joints, particle emitters, static environments, and controller details.

## GUI, Transport, and ROS Quick Reference

### Select transport per process

Set Zenoh as the Gazebo Transport implementation for a process with:

```sh
export GZ_TRANSPORT_IMPLEMENTATION=zenoh
```

### Export occupancy maps

Use the `/scan_image` topic for occupancy-grid export. Start exploration with:

```sh
gz topic -t /start_exploration -m gz.msgs.Boolean -p 'data: true'
```

### Account for platform defaults

The Quick Start dialog is disabled on Windows. In WSLg, rendering detection considers `WAYLAND_DISPLAY` as well as `XDG_SESSION_TYPE` and may force X rendering.

See [GUI, Transport, and ROS](references/gui-transport-and-ros.md) for QML migration, plotting, visualization, ROS interfaces, and platform behavior.

## Diagnostic Checklist

- Build failure after migration: check Qt6 imports, package names, Bzlmod, runtime path APIs, component registration IDs, and `systemTimeIso` casing.
- Plugin not found: check both dynamic discovery and the static system or physics registry.
- Unexpected dynamics: check partial physics updates, gravity propagation, aerodynamic corrections, quaternion sign handling, and fixed-constraint settings.
- Missing or changed messages: check pose suppression and scope, configured particle topics, Joint State Publisher rate, marker arrays, and WebSocket schemas.
- Distributed entity mismatch: verify `NetworkManager` secondary creation behavior.
- Rendering startup issue: check Windows defaults and WSLg Wayland environment variables.
- Test reset issue: use the public reset API and `ISystemReset` support.
