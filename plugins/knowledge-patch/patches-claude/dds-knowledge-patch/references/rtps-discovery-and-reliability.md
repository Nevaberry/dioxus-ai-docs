# RTPS discovery and reliable delivery

Use this reference to analyze DDSI-RTPS packet captures, distinguish
participant discovery from endpoint discovery, and follow reliable repair. The
protocol details here correspond to `ddsi-rtps-2.5`.

## Resolve wire identities and locators

An RTPS `GUID` combines a participant `GuidPrefix` with an entity-local
`EntityId`. Predefined entity IDs identify the built-in discovery endpoints.

A `Locator` supplies:

- a transport kind;
- a port; and
- an address.

Successful multicast discovery proves neither that advertised unicast
user-data locators are reachable nor that user traffic can return in the
opposite direction. Validate the advertised locators, routing, firewall rules,
and bidirectional reachability independently.

RTPS messages can update the context applied to following submessages:

| Context submessage | Context changed |
| --- | --- |
| `INFO_SRC` | Source |
| `INFO_DST` | Destination |
| `INFO_TS` | Timestamp |

Carry that context forward when decoding a compound RTPS message.

## Track sequencing per writer

A change is identified by the writer GUID plus a monotonically increasing,
writer-local sequence number. Sequence numbers are not global across writers
and are not wall-clock timestamps.

Do not merge changes from multiple writers by comparing their sequence
numbers. If application-wide ordering is required, implement it with an
appropriate DDS ordering policy or application-level data rather than
inventing a global RTPS order.

## Follow reliable repair

The principal whole-change repair exchange is:

1. `HEARTBEAT` advertises the writer's available sequence-number range.
2. `ACKNACK` reports the reader's next expected sequence number and a bitmap
   of missing numbers.
3. The writer retransmits changes that are available and requested.
4. `GAP` tells the reader to stop requesting changes that are filtered,
   removed, or otherwise unavailable.

For a fragmented sample, `DATA_FRAG` carries fragments.
`HEARTBEAT_FRAG` and `NACK_FRAG` provide fragment-level advertisement and
repair. Inspect both whole-change and fragment-level exchanges before
classifying repeated traffic as a stalled repair.

## Diagnose SPDP participant discovery

SPDP periodically announces participant-level information over multicast
and/or configured unicast, including:

- participant identity;
- protocol and vendor data;
- metatraffic and default locators;
- built-in endpoint availability; and
- lease duration.

Receiving SPDP creates proxy state for the remote participant. Lease expiry or
explicit disposal removes that proxy state and its dependent matches.

SPDP establishes participant visibility only. It does not carry the complete
catalog of user publications and subscriptions. A participant appearing in a
discovery tool or packet capture is therefore not proof that a user endpoint
was announced or matched.

## Diagnose SEDP endpoint discovery

SEDP uses reliable built-in writers and readers to exchange publication and
subscription announcements. Those announcements include:

- endpoint GUIDs;
- association with the participant;
- topic and type information;
- locators; and
- QoS relevant to endpoint matching.

This exchange can wait on reliable communication between the built-in
endpoints. When SPDP shows a participant but no user endpoints match, inspect
SEDP for missing announcements, incomplete built-in reliable repair,
unreachable advertised addressing, and mismatched topic/type/QoS data.

Use the boundary explicitly:

| Observation | First diagnostic layer |
| --- | --- |
| No remote participant proxy | SPDP transport, peers, leases, or locators |
| Remote participant but no endpoint announcement | Built-in endpoint availability and SEDP reliability |
| Endpoint announcements but no match | Topic, type, partitions, QoS, or user-data locators |
| Match exists but samples stall | Data path, reliable repair, resource limits, or reader state |
