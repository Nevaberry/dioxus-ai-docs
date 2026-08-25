# Implementation Configuration and Interoperability

Source batch: `dds-open-implementations`.

## Cyclone DDS configuration selection

`CYCLONEDDS_URI` selects one or more XML configuration resources. Resources can
be files or inline XML and use a `CycloneDDS` root.

```xml
<CycloneDDS xmlns="https://cdds.io/config">
  <Domain Id="any">
    <General>
      <Interfaces>
        <NetworkInterface autodetermine="true"/>
      </Interfaces>
    </General>
    <Discovery>
      <Peers>
        <Peer Address="192.0.2.10"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

`Domain/@Id="any"` makes that configuration reusable for participants in
different domains. It does not set the participant's domain ID. The application
or a surrounding environment such as ROS still selects the domain.

Use the configuration reference for the deployed Cyclone DDS release. Unknown
or misplaced elements can prevent startup, and release defaults can change.
Capture the exact selected resources when reproducing a problem.

## Cyclone DDS interfaces, peers, and ports

Cyclone DDS advertises addresses selected by its interface configuration.
Automatic choice can be wrong on multi-homed hosts, containers, VPNs, and
networks with asymmetric routes. In those environments, select the intended
interface explicitly and assign its priority as needed.

If multicast is disabled, configure reachable unicast seeds under
`Discovery/Peers`. Peer seeding only enables initial contact; it does not make
subsequently discovered locators reachable. Both sides still need bidirectional
connectivity to the addresses and transports they advertise.

DDSI port selection normally follows the domain/participant-index mapping.
Check all of the following when discovery appears absent:

- port conflicts;
- participant-index selection and search limits;
- host and network firewalls;
- container port exposure;
- reachability of advertised addresses.

## Cyclone DDS liveliness and shutdown

Current Cyclone DDS documentation identifies automatic liveliness as the
supported mode. Before designing around manual liveliness, verify that the
deployed release actually supports the requested mode.

Writer linger can delay final deletion so reliable acknowledgements have time
to arrive. It does not make process termination a general flushing API. Delete
entities in an orderly way and treat abrupt process exit as potentially losing
unacknowledged work.

## Fast DDS discovery modes

Fast DDS offers several discovery facilities with different behavior:

| Facility | Operational model |
| --- | --- |
| Simple discovery | Participants dynamically announce endpoints |
| Static EDP | XML supplies consistent endpoint definitions and IDs |
| Discovery Server | Participants act as clients of explicitly configured servers, which may be redundant |
| Manual APIs | Application code asserts selected remote entities |

These are product facilities, not portable DDSI discovery services.

`ROS_DISCOVERY_SERVER` is part of the supported Fast DDS and ROS 2 integration.
It is not a standalone-DDS setting and does not configure other
implementations. For a mixed deployment, validate a standard simple-discovery
path or design and test another explicitly compatible discovery architecture.

## Fast DDS XML profiles

Fast DDS XML can define named or default profiles for:

- participants;
- readers and writers;
- transports;
- types;
- logging;
- discovery.

`FASTDDS_DEFAULT_PROFILES_FILE` selects the current default profile file.
Supported releases can use `SKIP_DEFAULT_XML` to disable default-profile
loading. Default-name lookup and programmatic loading can also add profiles, so
resolve precedence against the deployed release.

A profile name is a local configuration identifier. It is not a topic name or
partition name and is not discovered remotely.

If code requests a profile that is absent, behavior follows that entity
creation API's documented error or default path. A remote profile with the same
name cannot satisfy the local lookup.

## Fast DDS transports and publication paths

Fast DDS provides UDP and documented TCP, shared-memory, and custom transports.
Shared memory and data sharing are local optimizations with eligibility
constraints. Remote or cross-implementation peers still need a mutually
supported network path.

Publication mode affects execution:

- synchronous publication performs transport work on the writing thread;
- asynchronous publication queues background work and can use flow control.

Publication mode does not redefine DDS reliability or history semantics.
Choose it for scheduling, latency, and flow-control needs while configuring
reliability and history independently.

## Connext API and profile identity

Connext modern C++ and classic C++ are distinct API mappings. Keep examples,
types, and entity-creation calls aligned with the installed release and
binding; similar concepts do not make source snippets interchangeable.

XML QoS is organized as named profiles inside libraries. Profiles can inherit
from base profiles and can be selected as defaults.

For a repeatable deployment, record:

- the complete loaded-file list and its order;
- selected library and profile identity;
- inherited base profiles;
- applicable defaults;
- programmatic QoS overrides.

Do not use a short profile name ambiguously when library/profile identity is
needed to select the intended configuration.

## Connext transports

Connext supplies UDPv4, UDPv6, and shared-memory transports and can use
additional transport plugins. Shared memory is local and
implementation-specific. Leave an interoperable network transport enabled
when communicating across hosts or implementations.

## Wire interoperability checklist

Different implementations can generate different source APIs while still
interoperating on the wire. Validate the shared contract explicitly:

1. IDL type names match.
2. Key definitions match.
3. Extensibility and type-consistency rules are compatible.
4. XCDR representation is compatible.
5. Topic names match.
6. Publisher and subscriber partitions match.
7. Requested/offered QoS is compatible.
8. Advertised locators are reachable.
9. At least one enabled transport is mutually supported.

Do not infer wire compatibility only from similar application-language types,
and do not infer transport reachability only from participant discovery.
