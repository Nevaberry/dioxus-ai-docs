# RTPS Discovery and Reliability

Source batch: `ddsi-rtps-2.5`.

## Wire identities and locators

An RTPS `GUID` combines:

- a participant `GuidPrefix`; and
- an entity-local `EntityId`.

Predefined entity IDs identify built-in discovery endpoints. Do not interpret
an entity's GUID as a host-wide or deployment-wide sequence.

A `Locator` identifies a transport kind, port, and address. Connectivity must
be evaluated for the locator actually advertised for the traffic in question.
Successful multicast participant discovery does not prove that advertised
unicast user-data locators are reachable.

On multi-homed or filtered networks, verify:

1. which locators were announced;
2. whether each peer can route to those addresses;
3. whether the relevant ports are open in both directions;
4. whether a common transport is active.

RTPS messages can carry context-changing submessages:

- `INFO_SRC` changes source context for following submessages;
- `INFO_DST` changes destination context for following submessages;
- `INFO_TS` changes timestamp context for following submessages.

Decode later submessages using the active context rather than treating every
field as self-contained.

## Per-writer sequencing

A change is identified by the writer GUID and a monotonically increasing,
writer-local sequence number. There is no global ordering across writers, and
the sequence number is not wall-clock time.

Applications that require cross-writer ordering must establish it separately;
packet arrival order and unrelated writers' sequence values do not provide it.

## Reliable repair

Reliable RTPS repair coordinates reader state with a particular writer:

| Submessage | Role |
| --- | --- |
| `HEARTBEAT` | Advertises the writer's available sequence-number range |
| `ACKNACK` | Reports the reader's next expected number and missing-number bitmap |
| `GAP` | Ends repair attempts for filtered, removed, or unavailable changes |

A `GAP` is meaningful protocol state. It tells the reader not to continue
requesting the listed sequence numbers; it does not represent successful data
delivery.

Large samples carried in `DATA_FRAG` use fragment-level repair:

- `HEARTBEAT_FRAG` advertises fragment availability;
- `NACK_FRAG` requests missing fragments.

When a reliable large sample stalls, inspect both sequence-level and
fragment-level traffic. A healthy `HEARTBEAT`/`ACKNACK` exchange alone does not
show that all fragments were repaired.

## SPDP participant discovery

SPDP periodically announces participant-level information, including:

- participant identity;
- protocol and implementation information;
- metatraffic locators;
- default locators;
- built-in endpoint availability;
- lease duration.

Announcements can travel over multicast and/or configured unicast.

Receiving a valid announcement creates remote-participant proxy state. Further
announcements refresh it. Lease expiry or explicit disposal removes the proxy
state and the endpoint matches that depend on it.

SPDP proves participant visibility only. It does not carry the complete catalog
of user publications and subscriptions.

If participants repeatedly appear and disappear, inspect announcement
periodicity, lease values, loss, routing, and disposal traffic before debugging
user endpoint QoS.

## SEDP endpoint discovery

SEDP uses reliable built-in writers and readers to announce publications and
subscriptions. Endpoint announcements include:

- endpoint GUID;
- association with a participant;
- topic and type information;
- endpoint locators;
- relevant QoS.

This exchange can wait on built-in reliable communication. A participant may
therefore be visible through SPDP while no user endpoints are yet available for
matching.

For a visible participant with no user matches:

1. verify the expected built-in SEDP endpoints were announced;
2. inspect reliable SEDP traffic and repair;
3. confirm publication and subscription announcements arrived;
4. check their participant association;
5. validate advertised locators;
6. compare topic, type, partition, and requested/offered QoS.

This layered diagnosis avoids treating participant visibility as proof of a
complete and compatible endpoint catalog.
