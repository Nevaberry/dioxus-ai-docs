---
name: dds-knowledge-patch
description: Data Distribution Service (DDS)
version: "DDSI-RTPS 2.5"
license: MIT
metadata:
  author: Nevaberry
---


# Data Distribution Service (DDS) Knowledge Patch

Use this skill when designing, reviewing, debugging, or operating DDS systems,
DDSI-RTPS interoperability, open DDS implementations, or ROS 2 RMW data paths.
Start with portable DDS semantics, then separate endpoint matching from
discovery transport and implementation-specific configuration.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/core-data-and-qos.md](references/core-data-and-qos.md) | Reader-cache state, status conditions, requested/offered QoS, topic QoS, durability, resource limits, presentation, and partitions |
| [references/rtps-discovery-and-reliability.md](references/rtps-discovery-and-reliability.md) | GUIDs, locators, message context, sequence numbers, reliable repair, SPDP, and SEDP |
| [references/implementation-configuration.md](references/implementation-configuration.md) | Cyclone DDS, Fast DDS, Connext, profiles, transports, discovery modes, and cross-implementation constraints |
| [references/ros2-rmw.md](references/ros2-rmw.md) | ROS 2 QoS selection and optional RMW data-path capabilities |

## Diagnose silence in layers

Do not treat participant discovery as proof that user endpoints can exchange
data. Work through these layers in order:

1. Confirm that the intended participants use the intended domain.
2. Confirm SPDP participant visibility and lease health.
3. Confirm SEDP publication and subscription announcements.
4. Confirm that advertised user-data locators are reachable in both
   directions.
5. Confirm exact topic, type, key, representation, and partition agreement.
6. Check requested/offered QoS compatibility.
7. Check reader state masks and `SampleInfo.valid_data`.
8. Inspect resource limits, reliable repair, and writer lifetime.

A visible participant with no user match points toward endpoint discovery,
advertised addressing, or matching data. A discovered endpoint pair with no
delivery points toward QoS, transport reachability, reader selection, resource
limits, or lifecycle behavior.

See
[references/rtps-discovery-and-reliability.md](references/rtps-discovery-and-reliability.md)
for the SPDP/SEDP boundary and
[references/implementation-configuration.md](references/implementation-configuration.md)
for product configuration.

## Apply requested/offered QoS directionally

Compatibility compares a reader's request with a writer's offer policy by
policy. Keep the direction explicit:

| Reader request | Compatible writer offer |
| --- | --- |
| Reliable reliability | Reliable reliability |
| A durability level | The same or a higher durability level |
| A deadline period | A period no greater than the requested period |

Discovery can still expose an incompatible pair. Inspect requested- and
offered-incompatible-QoS status instead of concluding that discovery failed.
For the complete matching and endpoint-lifecycle rules, load
[references/core-data-and-qos.md](references/core-data-and-qos.md).

## Treat `read`, `take`, and lifecycle samples distinctly

- `read` leaves matching samples in the reader cache and marks them read.
- `take` removes matching samples from the reader cache.
- Selection combines independent sample, view, and instance state masks.
- Always inspect `SampleInfo.valid_data`.
- A lifecycle notification may carry metadata without a new valid value.

Do not deserialize or apply a value merely because a sample was returned.
Handle invalid-data samples as lifecycle information using the accompanying
metadata.

## Treat statuses as state, not queued events

Status structures expose cumulative counts plus changes since the relevant
status was last accessed. Reading status, taking data, or running a listener
may clear a change value or status flag. Do not assume one callback or one
queued notification per occurrence.

Listener callbacks normally run on implementation-controlled threads. Keep
them short, avoid blocking and application locks, capture only the required
information, and hand work to an application-owned executor or queue.

## Recreate entities for immutable QoS changes

Topic QoS copied during reader or writer creation is a template, not a live
link. Later topic-QoS changes do not automatically update existing endpoints.
Check each policy's mutability before changing it; recreate the entity when an
immutable policy must change after enablement.

## Bound durability and history expectations

`TRANSIENT_LOCAL` history resides in the originating writer, so it disappears
with that writer. Do not expect it to behave like an external durability
service. Verify implementation support before depending on `TRANSIENT` or
`PERSISTENT`.

`KEEP_ALL` is still constrained by resource limits. With reliable delivery,
exhaustion can block writes or prevent slow readers from being served. Size
history and resource limits together, and include slow-reader behavior in
tests.

## Keep coherent access in scope

`PRESENTATION` chooses `INSTANCE`, `TOPIC`, or `GROUP` access scope separately
from coherent and ordered access. Coherent-change brackets may make a write
set visible together to a compatible subscriber, but they do not provide
database isolation or rollback. Verify implementation support when using group
scope.

## Use partitions for matching, not authorization

Partitions belong to publishers and subscribers. Their default is one empty
string, and matching requires the two string sequences to intersect under DDS
expression rules.

For portable matching, put a literal on at least one side; do not assume two
wildcard expressions are intersected as regular expressions. Partition QoS is
mutable, so a change can add or remove endpoint matches after enablement.
Because partitions are discovery-visible metadata, they are not a security
boundary.

## Read reliable RTPS traffic per writer

An RTPS change is identified by writer GUID and a monotonically increasing
writer-local sequence number. Do not derive a global order from sequence
numbers or interpret them as wall-clock time.

Use the repair exchange as a diagnostic map:

| Submessage | Role |
| --- | --- |
| `HEARTBEAT` | Advertises a writer's available sequence-number range |
| `ACKNACK` | Reports the reader's next expected number and missing bitmap |
| `GAP` | Ends repair attempts for unavailable, removed, or filtered changes |
| `DATA_FRAG` | Carries fragmented sample data |
| `HEARTBEAT_FRAG` / `NACK_FRAG` | Coordinates fragment-level repair |

See
[references/rtps-discovery-and-reliability.md](references/rtps-discovery-and-reliability.md)
before interpreting captures.

## Keep a portable network path

Shared memory, data sharing, and zero-copy paths are local optimizations with
eligibility constraints. They do not replace a mutually supported network
transport for remote or cross-implementation peers.

For interoperable deployments, align all of the following:

- IDL type names, keys, and extensibility;
- type-consistency behavior and XCDR representation;
- topic and partition names;
- requested/offered QoS;
- reachable advertised locators; and
- a common network transport.

Generated source APIs may differ without preventing wire interoperability, but
wire-level type and matching details must agree.

## Configure Cyclone DDS deliberately

`CYCLONEDDS_URI` selects XML configuration resources. A `Domain` with
`Id="any"` makes configuration reusable; it does not choose the participant's
domain ID.

On multi-homed hosts, containers, VPNs, or asymmetric networks, select and
prioritize the intended interface explicitly when automatic selection
advertises unreachable addresses. If multicast is disabled, configure
reachable unicast peers and preserve bidirectional reachability of the
locators learned through discovery.

Check domain/participant-index port mapping, port conflicts, participant-index
search limits, and firewalls. Use configuration documentation for the deployed
release because unknown or misplaced XML elements can stop startup and
defaults can change.

## Configure Fast DDS discovery and profiles deliberately

Choose simple discovery, static EDP, Discovery Server, or manual discovery
APIs as implementation facilities with distinct behavior. Static EDP requires
consistent endpoint IDs and definitions. Discovery Server clients require
explicit server configuration and may use redundant servers.

`ROS_DISCOVERY_SERVER` is an integration facility for Fast DDS with ROS 2, not
a portable standalone DDS or cross-implementation setting. Validate a standard
simple-discovery path or another explicitly compatible architecture for mixed
implementations.

`FASTDDS_DEFAULT_PROFILES_FILE` selects the default XML profile file.
`SKIP_DEFAULT_XML` can disable default loading where the deployed release
supports it. Profile names are local identifiers, not remote topic or partition
names; verify file, default-name, and programmatic-loading precedence for the
deployed version.

## Keep Connext bindings and profile identity aligned

Do not mix modern C++ and classic C++ examples or entity-creation APIs. Match
code to the installed release and language binding.

For repeatable XML QoS, record the loaded file list, library/profile identity,
base-profile inheritance, defaults, and programmatic overrides. Keep UDP or
another interoperable network path enabled when local shared memory is active.

## Handle optional ROS 2 RMW behavior

`SYSTEM_DEFAULT` delegates a QoS policy to the selected RMW or DDS vendor.
`BEST_AVAILABLE`, where supported, derives values from discovered endpoints.
Choose explicit profiles when behavior must remain stable across RMW
implementations.

Loaned messages, zero-copy/shared-memory paths, content filters, and unique
network-flow requirements are optional capabilities. Query support, handle an
unsupported result, and do not assume that changing RMW implementations
preserves vendor-specific acceleration.

See [references/ros2-rmw.md](references/ros2-rmw.md) for the portable
decision rules.
