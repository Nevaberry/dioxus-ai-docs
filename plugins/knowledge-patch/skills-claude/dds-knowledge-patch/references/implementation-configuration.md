# Implementation configuration and interoperability

Use this reference when configuring Cyclone DDS, Fast DDS, or Connext, or when
building a mixed-implementation deployment. These are implementation
facilities from `dds-open-implementations`, not portable DDS APIs unless stated
otherwise.

## Cyclone DDS

### Select configuration resources

`CYCLONEDDS_URI` selects one or more XML configuration resources. Resources may
be files or inline XML rooted at `CycloneDDS`.

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

`Domain/@Id="any"` allows one configuration to apply to multiple domains. It
does not set the domain ID of a participant; the application or ROS
environment still chooses that ID.

Use the configuration reference for the exact deployed release. An unknown or
misplaced XML element can prevent startup, and defaults may change between
releases.

### Select interfaces and reachable peers

Cyclone advertises addresses selected through its interface configuration.
Automatic selection can be wrong on multi-homed hosts, in containers, across
VPNs, or where routes are asymmetric. Select the intended interface and its
priority explicitly when necessary.

When multicast is disabled, configure reachable unicast seeds under
`Discovery/Peers`. Peer seeding only initiates discovery; it does not eliminate
the need for bidirectional reachability of the locators advertised after peers
discover one another.

DDSI ports normally derive from the domain and participant-index mapping.
Check for port conflicts, participant-index search limits, and firewalls when a
configuration that looks correct still fails discovery.

### Handle liveliness and shutdown

Current Cyclone documentation identifies automatic liveliness as the supported
mode. Before selecting manual liveliness, verify that the deployed release
supports the required mode.

Writer linger may delay final deletion so reliable acknowledgements can arrive.
It does not make abrupt process exit a general flushing mechanism. Delete
entities in an orderly sequence when shutdown must preserve the opportunity
for final reliable delivery.

## Fast DDS

### Choose a discovery mode

Simple discovery dynamically announces endpoints. Static EDP instead loads
endpoint definitions from XML, so endpoint IDs and definitions must be
consistent across the deployment.

Discovery Server makes participants clients of explicitly configured servers;
servers may be redundant. Manual discovery APIs can assert selected remote
entities. Discovery Server and manual assertion are implementation facilities,
not portable DDSI discovery services.

`ROS_DISCOVERY_SERVER` is part of the supported Fast DDS and ROS 2 integration.
It is not a standalone DDS setting and does not configure other
implementations. For mixed implementations, validate standard simple
discovery or use another discovery architecture that is explicitly compatible
across all participants.

### Load XML profiles deterministically

Fast DDS XML can describe:

- named or default participant and endpoint profiles;
- transports;
- types;
- logging; and
- discovery.

`FASTDDS_DEFAULT_PROFILES_FILE` selects the current default profile file.
`SKIP_DEFAULT_XML` can disable default-profile loading in releases that support
it. Default-name lookup and programmatic loading may also add profiles, so
verify their precedence in the deployed release.

A profile name is a local configuration identifier. It is not a topic name or
partition name and is not discovered by remote participants. When code asks
for a missing profile, behavior follows the local creation API's documented
error or default path; it does not locate a remote profile with the same name.

### Preserve a usable publication path

Fast DDS provides UDP and documented TCP, shared-memory, and custom transports.
Shared-memory and data-sharing delivery are local optimizations subject to
eligibility constraints. Remote or cross-implementation peers still require a
network path supported on both sides.

Synchronous publication performs transport work on the calling write thread.
Asynchronous publication queues work for background processing and may use
flow control. This selection changes the publication execution path; it does
not change DDS reliability or history semantics.

## Connext

### Match the API and QoS profile identity

The modern C++ and classic C++ APIs are distinct language mappings. Use
examples, types, and entity-creation calls for the installed release and
binding.

XML QoS uses named profiles within libraries and can apply base-profile
inheritance and defaults. Selection is by library/profile identity. To make a
deployment repeatable, record:

- every loaded XML file;
- the selected QoS library and profile;
- inherited base profiles;
- default profiles; and
- programmatic overrides.

### Preserve wire interoperability

Connext supports UDPv4, UDPv6, and shared memory, with additional transports
available through plugins. Shared memory is local and
implementation-specific. Keep an interoperable network transport enabled for
remote or mixed-implementation communication.

Across implementations, align:

- IDL type names;
- keys and extensibility;
- type-consistency rules;
- XCDR representation;
- topic and partition names; and
- requested/offered QoS.

Different implementations may generate different source APIs from the same
data model. Source-level similarity is not required, but the wire type,
representation, names, keys, and matching policies must remain compatible.
