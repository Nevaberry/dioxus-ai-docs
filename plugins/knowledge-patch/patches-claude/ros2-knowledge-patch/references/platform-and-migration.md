# Platform, Middleware, and Migration

Coverage attribution: `kilted-kaiju`.

## Supported platforms and language levels

Tier 1 targets are Ubuntu 24.04 on amd64 and arm64, plus Windows 10 with Visual
Studio 2019 on amd64. RHEL 9 on amd64 is Tier 2. Debian 12 and macOS on amd64
are Tier 3.

The minimum language levels are C++17 and Python 3.9. Ionic is the recommended
Gazebo release.

Use the target tier to set support expectations, CI coverage, and release
claims. In particular, do not infer arm64 support for a component solely from
Ubuntu's Tier 1 status; middleware-specific architecture restrictions still
apply.

## Windows source dependencies

The Windows source-install workflow uses Pixi/Conda together with pip. Keep
dependencies isolated per workspace rather than installing them globally. This
workspace boundary should be reflected in setup documentation and automation.

## Default and Tier 1 middleware

`rmw_fastrtps_cpp` remains the default RMW implementation and uses Fast DDS
2.14.4.

The Tier 1 middleware implementations are Fast DDS, Cyclone DDS 0.10.5,
Connext DDS 7.3, and Zenoh 1.0.4. `rmw_zenoh_cpp` is newly Tier 1.

Connext support excludes arm64. Its supported operating systems are limited to
Ubuntu, Windows, and macOS. Apply both the operating-system and architecture
constraints when creating a support matrix.

## Middleware naming migration

The name of the underlying `fastrtps` project changed to `fastdds`. RMW
implementation names are unchanged, so an RMW identifier should not be renamed
merely because of this migration. XML-profile environment-variable names did
change; update those variables in shell profiles, launch environments,
containers, CI, and deployment manifests.

## Connext Micro deprecation

Connext Micro's `rmw_connextddsmicro` is deprecated and receives no further
updates for this distribution. New deployments should select a maintained RMW
implementation, and existing deployments should plan a migration rather than
expecting later fixes on this package.

## Isolated RMW tests

The `rmw_test_fixture` package defines an extension API for configuring
communication isolation around an RMW test. Use the fixture boundary to keep
test traffic from leaking into other concurrent ROS graphs.

`rmw_test_fixture_implementation` is responsible for discovering, loading, and
invoking the provider-specific implementation. Keep provider mechanics in that
implementation layer instead of coupling a test directly to one isolation
provider.

## DDS topic instances

ROS 2 supports DDS topic instances. Multiple objects of one logical kind can
publish updates over a shared topic while retaining their object identity at
the DDS instance level. Consider this capability before splitting a data model
into one topic per object.
