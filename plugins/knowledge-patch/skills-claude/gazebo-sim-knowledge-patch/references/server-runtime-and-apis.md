# Server, Runtime, and APIs

## Process lifecycle and startup

### Stop gracefully with SIGTERM (since 9.1.0)

Gazebo Sim handles `SIGTERM` gracefully, including shutdown initiated by service managers and container runtimes.

### Detect an existing server (since 9.2.0)

Startup detects an already-running Gazebo Sim server.

### Handle invalid SDF safely (since 10.1.1)

Server behavior with a bad SDF file includes a regression fix. Do not preserve behavior from an affected build as the intended invalid-SDF contract.

## Plugin and language runtimes

### Load systems from the static registry (since 9.2.0)

System plugins can load through the static plugin registry in addition to dynamic plugin-loading paths.

### Release the Python GIL correctly (since 9.2.0)

GIL-release behavior is corrected for Python systems and the Python `TestFixture`.

## Services and ECM state

### Read actual UserCommands status (since 10.0.0)

UserCommands services return the status of the command they execute. Use that result as command success or failure.

### Clear ECM change tracking (since 10.0.0)

The Entity Component Manager exposes APIs for clearing its internal tracking of additions and removals.

### Reset through the public API (since 10.0.0)

Simulation reset is publicly callable.

### Reset test fixtures through ISystemReset (since 10.0.0)

The test fixture supports `ISystemReset`.

## WebSocket protocol

### Use the Gazebo-owned server (since 10.0.0)

The WebSocket server formerly housed in `gz-launch` is part of Gazebo Sim.

### Consume top-level enums (since 10.1.0)

WebSocket protocol definitions expose top-level enum declarations to schema consumers.

## Distributed simulation

### Create entities on network secondaries (since 10.1.0)

`NetworkManager` creates entities correctly on network secondaries. Distributed simulation checks should expect secondary entity creation.
