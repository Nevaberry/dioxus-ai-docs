# GUI, Transport, and ROS

## GUI plugin migration

### Port custom plugins to Qt6 (`jetty-migration`)

Jetty's `gz-gui10` moves the GUI from Qt5 to Qt6. Port custom Qt5 plugins, omit version numbers from Qt6 QML imports, and update Qt6-sensitive types such as `FileDialog` and `TreeView`. QML references to exposed C++ objects gain a leading underscore, while the C++ name remains unchanged:

```qml
_MyClass.FunctionFoo()
```

### Guard Qt application access (`jetty-migration`)

`gz::gui::App()` may return a null `qGuiApp` pointer; validate it before use. Qt6 plugins should not manually call `QCoreApplication::processEvents()`.

## Inspection and visualization

### Visualize frustums (since 9.1.0)

Gazebo Sim can visualize frustums.

### Plot poses in Component Inspector (since 9.2.0)

Pose attributes can be plotted from the Component Inspector.

## Transport and ROS integration

### Select Zenoh (`jetty-highlights`)

Zenoh is available as an alternative Gazebo Transport implementation. Select it per process:

```sh
export GZ_TRANSPORT_IMPLEMENTATION=zenoh
```

### Use the ROS standard simulation interface (`jetty-highlights`)

Gazebo's ROS integration supports the community standard simulation interface, allowing robot code written against that interface to move between compatible simulators.

### Export occupancy-grid maps (`jetty-highlights`)

Export occupancy grids with the `/scan_image` topic. Begin exploration by publishing:

```sh
gz topic -t /start_exploration -m gz.msgs.Boolean -p 'data: true'
```

## Platform behavior

### Windows Quick Start default (since 10.1.0)

The Quick Start dialog is disabled on Windows.

### WSLg Wayland detection (since 10.5.0)

Rendering fallback considers `WAYLAND_DISPLAY` as well as `XDG_SESSION_TYPE`. A WSLg environment with `WAYLAND_DISPLAY=wayland-0` and an empty `XDG_SESSION_TYPE` is detected and forced to X rendering.
