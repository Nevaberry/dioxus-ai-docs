# Migration, Build, and Packaging

## Build systems

### Observe initial Bazel limits (since 9.2.0)

The initial Bazel build covers the core Gazebo Sim library, not the GUI, physics, or systems.

### Build systems with Bazel (since 9.3.0)

Bazel support extends to system targets; verify target availability rather than retaining the earlier core-only assumption.

### Migrate to Bzlmod (`jetty-highlights`)

Gazebo packages use Bzlmod rather than legacy workspace-based Bazel setup. Jetty and Ionic libraries, plus required third-party packages, are available through the Bazel Central Registry.

### Follow the repository Bazel default (since 10.5.0)

The repository default and CI use Bazel 9.1.1. Builds that follow the repository default should use that version.

## Command and package layout

### Use the standalone model executable (since 9.2.0)

`gz model` is available as a standalone executable.

### Package standalone `gz` applications (`jetty-highlights`)

The `gz` tool no longer relies on Ruby-based CLI library loading. Package and debug command implementations as standalone applications.

### Depend on unversioned packages (`jetty-highlights`)

Major version numbers have been removed from Gazebo package names. Update package dependencies to the unversioned names.

## Removed APIs and paths

### Use runtime path functions (`jetty-migration`)

The `config.hh` path and install-directory macros are removed. Replace them as follows:

```text
GZ_SIM_GUI_CONFIG_PATH        -> gz::sim::getGUIConfigPath()
GZ_SIM_SYSTEM_CONFIG_PATH     -> gz::sim::getSystemConfigPath()
GZ_SIM_SERVER_CONFIG_PATH     -> gz::sim::getServerConfigPath()
GZ_SIM_PLUGIN_INSTALL_DIR     -> gz::sim::getPluginInstallDir()
GZ_SIM_GUI_PLUGIN_INSTALL_DIR -> gz::sim::getGUIPluginInstallDir()
GZ_SIM_WORLD_INSTALL_DIR      -> gz::sim::getWorldInstallDir()
```

### Supply component registration IDs (`jetty-migration`)

The `std::string` overloads of `gz::sim::components::Factory::Register` and parameterless `Unregister()` are removed. Registration takes a C-string type name and explicit registration-object ID; unregistration requires that ID.

```cpp
Register(const char *_type, ComponentDescriptorBase *_compDesc,
         RegistrationObjectId _regObjId);
Unregister(RegistrationObjectId _regObjId);
```

### Rename the time API (since 10.0.0)

Replace `systemTimeISO` with `systemTimeIso`.

## Relocation and tooling

### Relocate the simulation executable (since 10.1.0)

`gz-sim-main` is relocatable. Installation and packaging may place it at a runtime location different from its original layout.

### Use the exporter with newer Blender (since 10.5.0)

`sdf_exporter.py` works with newer Blender versions.
