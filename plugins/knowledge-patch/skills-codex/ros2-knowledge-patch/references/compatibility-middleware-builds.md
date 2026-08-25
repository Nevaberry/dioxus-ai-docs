# Compatibility, Middleware, and Builds

## Platform Compatibility

For Kilted Kaiju (batch `kilted-kaiju`), use the following platform tiers:

| Tier | Operating system and toolchain | Architecture |
| --- | --- | --- |
| 1 | Ubuntu 24.04 | amd64, arm64 |
| 1 | Windows 10 with Visual Studio 2019 | amd64 |
| 2 | RHEL 9 | amd64 |
| 3 | Debian 12 | Not further constrained by this guidance |
| 3 | macOS | amd64 |

The minimum language levels are C++17 and Python 3.9. Ionic is the recommended
Gazebo release.

## Middleware Compatibility

At initial release, `rmw_fastrtps_cpp` remains the default and uses Fast DDS
2.14.4.

| Tier 1 middleware | Version or RMW note | Platform constraint |
| --- | --- | --- |
| Fast DDS | 2.14.4 for the default `rmw_fastrtps_cpp` | No additional constraint stated |
| Cyclone DDS | 0.10.5 | No additional constraint stated |
| Connext DDS | 7.3 | Ubuntu, Windows, and macOS only; no arm64 support |
| Zenoh | 1.0.4; `rmw_zenoh_cpp` is newly Tier 1 | No additional constraint stated |

### Fast DDS naming migration

The underlying `fastrtps` name changed to `fastdds`. The RMW implementation
names did not change, so retain names such as `rmw_fastrtps_cpp` when selecting
the RMW. XML-profile environment-variable names do change; update the variables
used by shell scripts, CI, launch files, and deployment configuration.

### Connext Micro deprecation

Connext Micro's `rmw_connextddsmicro` is deprecated and receives no further
Kilted updates. Do not select it for work that needs ongoing updates.

## Windows Source Dependencies

The Windows source-install workflow uses Pixi/Conda together with pip.
Dependencies are isolated per workspace instead of being installed globally.
Create and enter the workspace's dependency environment before resolving or
building source dependencies, and do not assume packages installed for one
workspace are visible to another.

## RMW-Isolated Tests

The `rmw_test_fixture` package defines an extension API that configures
communication isolation around an RMW test. The
`rmw_test_fixture_implementation` package discovers, loads, and invokes the
provider-specific implementation.

Keep tests coupled to the extension API and leave provider discovery and
execution to the implementation package. This separates the test's isolation
request from the selected RMW's isolation mechanism.

## CMake Dependency Migration

`ament_target_dependencies()` is deprecated. Prefer imported modern CMake
targets with `target_link_libraries()`:

```cmake
target_link_libraries(my_target PUBLIC SomePackage::SomeTarget)
```

CMake requires one signature style per target. If earlier calls for a target
use the plain signature, later calls must also be plain:

```cmake
target_link_libraries(my_target SomePackage::SomeTarget)
```

Do not add `PUBLIC`, `PRIVATE`, or `INTERFACE` to later calls unless all calls
for that target use the keyword signature.

## Interface Generation and Dynamic Types

`rosidl_rust` is now part of the default ROS interface generator set. Builds
that run the default generators should expect Rust interface output without
explicitly opting in. Check packaging and generated-artifact assumptions if a
project previously expected only its explicitly selected generators.

`rosidl_dynamic_typesupport` no longer supports `float128`. Dynamic interface
descriptions, conversion code, and generic consumers must use a supported
numeric type instead.
