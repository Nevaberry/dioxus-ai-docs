# Runtime, Integration, and Testing

## Process and server lifecycle

### Stop cleanly with SIGTERM

Gazebo Sim handles `SIGTERM` gracefully (9.1.0). Service managers and
container runtimes can use their normal termination signal without requiring
an immediate hard kill.

### Detect an existing server

Startup detects an already-running server (9.2.0). Launch orchestration should
surface that condition rather than assuming a second server starts normally.

### Handle invalid SDF as corrected behavior

`Server` behavior with a bad SDF file was corrected in 10.1.1 after a
regression. Do not use the affected invalid-SDF behavior as an API contract.

### Reset through public APIs

Simulation reset has a public callable API (10.0.0). Test fixtures also support
`ISystemReset`, so exercise system reset behavior through the fixture rather
than rebuilding all state solely to simulate reset.

## Plugin and language integration

### Load statically registered systems

System plugins can be loaded through the static plugin registry (9.2.0).
Treat statically linked systems as available to the normal system-loading
path.

### Let Python bindings release the GIL

GIL-release behavior is corrected for Python systems and Python
`TestFixture` (9.2.0). Parallel Python work should not preserve workarounds
whose only purpose was the earlier GIL handling.

### Detect nested models with LogicalCamera

The `LogicalCamera` plugin detects nested models (9.2.0). Consumers should
accept nested detections instead of filtering expectations to top-level models.

## Transport, ROS, and networking

### Select Zenoh per process

Zenoh is an alternative Gazebo Transport implementation. Select it for a
process with (jetty-highlights):

```sh
export GZ_TRANSPORT_IMPLEMENTATION=zenoh
```

Keep this choice in the process environment when different processes need
different transport implementations.

### Target the standard ROS simulation interface

Gazebo's ROS integration supports the community standard simulation interface
(jetty-highlights). Robot code written to that interface can move among
compatible simulators without a Gazebo-specific control surface.

### Expect entity creation on network secondaries

`NetworkManager` creates entities correctly on network secondaries (10.1.0).
Distributed-simulation tests should expect secondary instances to receive
those entities.

### Use the in-process WebSocket server

The WebSocket server moved from `gz-launch` into Gazebo Sim (10.0.0). Package,
configure, and debug it with the simulator rather than expecting launch to own
it. Protocol definitions also expose top-level enums (10.1.0), so schema
consumers should handle those declarations.

## Commands, time, and state

### Trust UserCommands service status

UserCommands services return the actual status of the command they execute
(10.0.0). Use the service result as command success or failure rather than
assuming transport success means command success.

### Update the time API spelling

Replace `systemTimeISO` with `systemTimeIso` (10.0.0). The former casing is no
longer the callable API.

### Clear ECM change tracking explicitly

The Entity Component Manager provides APIs to clear its internal tracking of
entity additions and removals (10.0.0). Use them when a consumer establishes a
new change-tracking baseline.
