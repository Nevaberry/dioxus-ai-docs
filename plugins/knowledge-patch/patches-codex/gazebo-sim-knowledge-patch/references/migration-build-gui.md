# Migration, Build, and GUI

## Jetty migration checklist

### Port custom GUI plugins to Qt 6

Gazebo GUI now uses `gz-gui10` and Qt 6. Port custom Qt 5 plugins before
upgrading. QML references to C++ objects gain a leading underscore, while the
C++ names stay unchanged (jetty-migration):

```qml
_MyClass.FunctionFoo()
```

Remove version numbers from Qt 6 QML imports, for example change
`import QtQuick.Dialogs 1.0` to `import QtQuick.Dialogs`. Migrate types such as
`FileDialog` and `TreeView` to their Qt 6 forms.

### Treat application access as nullable

`gz::gui::App()` is not guaranteed to return a non-null `qGuiApp` pointer.
Validate it before use, and do not manually call
`QCoreApplication::processEvents()` from Qt 6 plugins (jetty-migration).

### Replace compile-time path macros

`config.hh` and the install-directory macros are removed. Use the runtime APIs
instead (jetty-migration):

| Removed macro | Runtime API |
| --- | --- |
| `GZ_SIM_GUI_CONFIG_PATH` | `gz::sim::getGUIConfigPath()` |
| `GZ_SIM_SYSTEM_CONFIG_PATH` | `gz::sim::getSystemConfigPath()` |
| `GZ_SIM_SERVER_CONFIG_PATH` | `gz::sim::getServerConfigPath()` |
| `GZ_SIM_PLUGIN_INSTALL_DIR` | `gz::sim::getPluginInstallDir()` |
| `GZ_SIM_GUI_PLUGIN_INSTALL_DIR` | `gz::sim::getGUIPluginInstallDir()` |
| `GZ_SIM_WORLD_INSTALL_DIR` | `gz::sim::getWorldInstallDir()` |

### Update component factory registration

The `std::string` overloads of
`gz::sim::components::Factory::Register` and parameterless `Unregister()` are
removed. Register with a C-string type name and explicit registration-object
ID; unregister with that ID (jetty-migration):

```cpp
Register(const char *_type, ComponentDescriptorBase *_compDesc,
         RegistrationObjectId _regObjId);
Unregister(RegistrationObjectId _regObjId);
```

### Repackage command-line applications

The `gz` tool no longer loads Ruby CLI libraries. Commands are standalone
applications, so package and debug command implementations as executables
(jetty-highlights). Gazebo package names also lose major-version suffixes;
update dependency declarations to the unversioned names.

## Build systems and packaging

### Track the Bazel support boundary

The initial Bazel build covers only the core Gazebo Sim library, not the GUI,
physics, or systems (9.2.0). System targets are supported later (9.3.0), but
do not infer GUI or physics coverage from that addition.

Gazebo packages use Bzlmod rather than the legacy workspace setup. Jetty and
Ionic libraries and their required third-party packages are available from the
Bazel Central Registry (jetty-highlights). Repository-default builds use Bazel
9.1.1, including the corresponding CI workflow default (10.5.0).

### Account for relocatable installation

`gz-sim-main` is relocatable. Do not assume its runtime path matches the
original installation layout (10.1.0); use runtime path discovery where
installation-relative resources matter.

### Use the Blender exporter with current Blender

`sdf_exporter.py` works with newer Blender versions (10.5.0). Do not preserve
local compatibility workarounds without first checking the current exporter.

## GUI and visualization

### Visualize frustums and pose data

Gazebo Sim can visualize frustums (9.1.0). Pose attributes can also be plotted
again from the Component Inspector (9.2.0), so use its plotting path instead
of treating pose plots as unavailable.

### Expect marker-array contact visualization

Contact visualization uses marker arrays (10.5.0). Consumers and tests should
handle the array representation rather than a previous single-marker shape.

### Handle WSLg display detection

The rendering fallback checks both `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE`.
In WSLg, `WAYLAND_DISPLAY=wayland-0` with an empty `XDG_SESSION_TYPE` is
recognized and forced to X rendering (10.5.0).

### Respect the Windows Quick Start default

The Quick Start dialog is disabled by default on Windows (10.1.0). Tests and
startup automation should not assume that it appears there.

## Standalone tools

### Use the model executable directly

`gz model` is available as a standalone executable (9.2.0). Invoke and package
it as an application rather than assuming the former library-loaded CLI path.
