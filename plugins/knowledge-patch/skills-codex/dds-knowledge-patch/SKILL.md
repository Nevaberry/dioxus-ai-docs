---
name: dds-knowledge-patch
description: Data Distribution Service (DDS)
version: DDSI-RTPS 2.5
license: MIT
metadata:
  author: Nevaberry
---


# Data Distribution Service (DDS)

Use this skill when implementing or debugging DDS data access, QoS matching,
discovery, reliable RTPS delivery, product configuration, interoperability, or
ROS 2 RMW behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core DDS semantics](references/core-dds-semantics.md) | Reader-cache state, status handling, requested/offered QoS, topic QoS, durability, presentation, and partitions |
| [RTPS discovery and reliability](references/rtps-discovery-reliability.md) | GUIDs, locators, message context, sequencing, repair, SPDP, and SEDP |
| [Implementation configuration](references/implementation-configuration.md) | Cyclone DDS, Fast DDS, Connext, transports, discovery modes, profiles, and wire interoperability |
| [ROS 2 RMW behavior](references/ros2-rmw.md) | Discovery-derived QoS and optional data-path capabilities |

## Compatibility-critical behavior

### Separate discovery from endpoint matching

A remote participant can be visible while its readers and writers remain
unmatched.

Check the layers in order:

1. Confirm SPDP participant visibility and lease health.
2. Confirm SEDP endpoint announcements arrive.
3. Inspect advertised locators for bidirectional reachability.
4. Compare topic and type identity.
5. Compare partitions.
6. Compare every requested/offered QoS policy.

Multicast discovery success does not prove that advertised unicast user-data
locators are reachable.

### Apply requested-versus-offered QoS directionally

Compatibility is not an equality test:

| Policy | Compatibility direction |
| --- | --- |
| Reliability | A reliable request requires a reliable offer |
| Durability | Offered durability must be at least the requested level |
| Deadline | The offered period must be no greater than the requested period |

Incompatible endpoints may still discover one another. Use requested- and
offered-incompatible-QoS status to distinguish discovery from matching.

### Treat configuration as release-specific

Configuration schemas, accepted elements, defaults, file-loading rules, and
feature support can vary by deployed release.

For repeatable diagnosis, record:

- the implementation and release;
- every loaded configuration file;
- selected profile or participant configuration;
- inherited profile bases;
- environment-selected configuration;
- programmatic overrides;
- active transports and advertised interfaces.

An unknown or misplaced configuration element may prevent startup rather than
being ignored.

### Preserve a common network transport

Shared memory, data sharing, loaning, and zero-copy are local optimizations with
eligibility and support constraints. They do not replace a mutually supported
network path for remote or cross-implementation communication.

## Data access quick reference

### Choose `read` or `take` deliberately

`read` returns matching samples, leaves them in the reader cache, and marks
them read. `take` removes returned samples.

Selection masks combine three independent dimensions:

- sample state: `READ` or `NOT_READ`;
- view state: `NEW` or `NOT_NEW`;
- instance state: `ALIVE`, `NOT_ALIVE_DISPOSED`, or
  `NOT_ALIVE_NO_WRITERS`.

Always inspect `SampleInfo.valid_data`. A lifecycle notification can provide
instance metadata without a new valid value.

### Do not treat status as an event queue

Statuses expose cumulative counts and changes since the relevant status was
last accessed. Reading a status, taking data, or invoking a listener can reset
the corresponding change or status flag.

Do not assume one queued callback per occurrence. Listener callbacks normally
run on implementation-controlled threads, so keep them short and hand work to
application-owned execution without blocking or taking application locks.

### Treat topic QoS as a creation-time template

Copying topic QoS into a reader or writer does not keep the endpoint linked to
later topic-QoS changes. Check each policy's mutability before updating an
enabled entity; recreate the entity when an immutable policy must change.

## Delivery and presentation quick reference

### Bound durability and history expectations

`TRANSIENT_LOCAL` history lives in the originating writer and disappears with
that writer. `TRANSIENT` and `PERSISTENT` depend on durability-service support
that differs among implementations.

`KEEP_ALL` is still bounded by resource limits. With reliable delivery, a slow
reader can cause writes to block or make historical delivery fail.

### Keep coherent access in scope

`PRESENTATION` separately chooses `INSTANCE`, `TOPIC`, or `GROUP` access scope
and requests coherent or ordered access.

Coherent-change brackets can expose a compatible set of writes together, but
they do not provide database isolation or rollback. Group scope may also
depend on implementation support.

### Use partitions for matching, not security

`PARTITION` is configured on publishers and subscribers. Its default is one
empty string, and matching requires the two string sequences to intersect.

For portable matching, use a literal on at least one side instead of expecting
two wildcard expressions to be intersected as regular expressions.

Partitions are mutable after enablement and may add or remove matches. They are
discovery-visible metadata, not an authorization boundary.

## RTPS quick reference

### Interpret wire identity correctly

An RTPS `GUID` combines a participant `GuidPrefix` with an entity-local
`EntityId`. Predefined entity IDs identify built-in discovery endpoints.

A `Locator` carries a transport kind, port, and address. `INFO_SRC`,
`INFO_DST`, and `INFO_TS` alter source, destination, or timestamp context for
following submessages.

### Diagnose reliable repair per writer

Ordering is based on writer GUID plus monotonically increasing writer-local
sequence number, not a global sequence or wall-clock time.

- `HEARTBEAT` advertises the available sequence range.
- `ACKNACK` reports the next expected sequence and a missing-number bitmap.
- `GAP` says changes are filtered, removed, or otherwise unavailable.
- `HEARTBEAT_FRAG` and `NACK_FRAG` repair fragmented `DATA_FRAG` samples.

### Inspect SPDP before SEDP

SPDP creates and refreshes remote-participant proxy state from participant
announcements. Lease expiry or explicit disposal removes that state and its
dependent matches.

SPDP does not carry the complete user-endpoint catalog. SEDP reliably
announces publications and subscriptions, including identity, association,
topic/type data, locators, and relevant QoS.

## Implementation configuration quick reference

### Cyclone DDS

`CYCLONEDDS_URI` selects XML configuration resources. A
`Domain/@Id="any"` block is reusable across domains but does not choose the
participant's domain ID.

On multi-homed hosts, containers, VPNs, or asymmetric networks, explicitly
select and prioritize a reachable interface when automatic selection
advertises the wrong address. If multicast is disabled, configure reachable
unicast peers and preserve bidirectional reachability of discovered locators.

Check domain/participant-index port mapping, participant-index search limits,
port conflicts, and firewalls. Verify manual-liveliness support before relying
on it. Writer linger can allow final reliable acknowledgements, but orderly
entity deletion is still required.

### Fast DDS

Choose simple discovery, static EDP, Discovery Server, or manual assertion with
their distinct operational assumptions. Static EDP requires consistent
endpoint definitions and IDs. Discovery Server clients need explicitly
configured, optionally redundant servers.

`FASTDDS_DEFAULT_PROFILES_FILE` selects a default XML profile file, while
supported releases can use `SKIP_DEFAULT_XML` to suppress default loading.
Profile names are local identifiers, not topic or partition names.

Synchronous publication performs transport work on the writer's thread.
Asynchronous publication queues it for background work and can apply flow
control. Neither mode changes DDS reliability or history semantics.

### Connext

Keep modern C++ and classic C++ examples with their matching API mapping and
installed release. Select XML QoS by library/profile identity and account for
base-profile inheritance, defaults, loaded files, and programmatic overrides.

Keep an interoperable UDP path enabled when shared memory or transport plugins
are present.

## Cross-implementation checklist

Align all of the following:

- IDL type name and keyed fields;
- extensibility and type-consistency rules;
- XCDR representation;
- topic name;
- partition expressions;
- requested/offered QoS;
- reachable locators and common transports.

Generated source APIs may differ even when the wire contract is compatible.

## ROS 2 RMW quick reference

`SYSTEM_DEFAULT` delegates policy selection to the RMW or DDS implementation.
`BEST_AVAILABLE`, where supported, derives values from discovered endpoints.
Use explicit profiles when behavior must be stable across RMW implementations.

Loaned messages, zero-copy or shared-memory delivery, content filtering, and
unique network flows are optional capabilities. Query support, handle an
unsupported result, and do not assume that switching RMW implementations
preserves an implementation-specific optimized path.
