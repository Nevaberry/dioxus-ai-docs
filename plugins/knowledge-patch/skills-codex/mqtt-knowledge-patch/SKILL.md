---
name: mqtt-knowledge-patch
description: MQTT
version: MQTT-SN 2.0 CSD01
license: MIT
metadata:
  author: Nevaberry
---


# MQTT Compatibility Guidance

Use this skill when implementing, reviewing, debugging, or testing MQTT 5.0 or
MQTT-SN 2.0 protocol behavior. Start by identifying which protocol is on the
wire: their packet layouts, connection abstractions, retry rules, aliases, and
error handling are different.

## Reference index

| Reference | Topics |
| --- | --- |
| [MQTT 5 wire format](references/mqtt5-wire-format.md) | Canonical Variable Byte Integers, property encoding and registry, packet-scoped failure codes, WebSocket transport |
| [MQTT 5 connections and publishing](references/mqtt5-connections-publishing.md) | CONNECT/CONNACK defaults, Will timing, pipelining, diagnostics, aliases, expiry, Receive Maximum, acknowledgments |
| [MQTT 5 subscriptions and operations](references/mqtt5-subscriptions-operations.md) | Shared subscriptions, Subscription Identifiers, retransmission and ordering, request/response, redirection, authentication, protocol errors |
| [MQTT-SN packets](references/mqtt-sn-packets.md) | 1.2 migration, framing, registries, identifiers, CONNECT/CONNACK, publish and subscription packets, encapsulation |
| [MQTT-SN sessions and topics](references/mqtt-sn-sessions-topics.md) | Sessions and Virtual Connections, PUBWOS, retries, flow control, topic aliases, retained delivery, discovery |
| [MQTT-SN authentication, sleep, and protection](references/mqtt-sn-auth-sleep-protection.md) | Authentication profiles, client states, sleeping delivery, security profiles, protection schemes and nonces |

## First distinguish MQTT from MQTT-SN

- Treat MQTT 5 Network Connections and MQTT-SN Virtual Connections as
  different lifecycles.
- Decode MQTT Remaining Length and properties with MQTT's canonical
  base-128 Variable Byte Integer rules.
- Decode MQTT-SN Length as either the short one-byte form or the extended
  `0x01` plus unsigned big-endian 16-bit form.
- Do not apply MQTT timeout retransmission behavior to MQTT-SN. MQTT 5 resends
  QoS flows only across a qualifying reconnect; MQTT-SN defines retry timers
  and retry limits for selected request packets.
- Keep MQTT Topic Aliases scoped to one direction of one Network Connection.
  Keep MQTT-SN Predefined and Session Topic Aliases in independent namespaces.

## Breaking MQTT-SN 1.2 assumptions

For MQTT-SN 2.0 work, remove these 1.2-era assumptions:

- Use Topic Alias, Packet Identifier, and Packet Type instead of Topic Id,
  Message Id, and Message Type.
- Carry Will data in CONNECT; do not implement the old Will Message
  control-packet exchange.
- Do not expect a response to DISCONNECT.
- Do not use Short Topic Name for ordinary 2.0 PUBLISH.
- Accept both short and extended packet Length encodings.
- Use protocol version byte `0x02` in CONNECT.
- Use the new contiguous Packet Type registry; legacy numeric values are not
  interchangeable.

Optional MQTT-SN 1.2 QoS −1 PUBLISH compatibility is a PUBWOS-equivalent
extension, not an ordinary 2.0 publish flow. Read
[MQTT-SN sessions and topics](references/mqtt-sn-sessions-topics.md) before
accepting it.

## MQTT 5 correctness rules

### Never retransmit on an acknowledgment timer

On an established MQTT Network Connection, do not resend QoS 1/2 PUBLISH or
PUBREL because a timer expired. Resend after reconnect only when Clean Start is
`0` and the Session is present, preserving original Packet Identifiers and
required ordering.

### Apply omission defaults field by field

Do not treat absent CONNECT or CONNACK properties uniformly:

- Session Expiry defaults to `0` on CONNECT and to the CONNECT value on
  CONNACK.
- Receive Maximum defaults to `65535`.
- Topic Alias Maximum defaults to `0`.
- Maximum QoS defaults to `2`.
- Retain, wildcard, Subscription Identifier, and shared-subscription
  availability default to enabled.
- Server Keep Alive defaults to the CONNECT Keep Alive.
- Request Problem Information defaults to `1`.

Read the full table in
[MQTT 5 connections and publishing](references/mqtt5-connections-publishing.md).

### Track flow-control completion precisely

Receive Maximum counts only unfinished QoS 1/2 PUBLISH flows. Free a QoS 1
slot at PUBACK. Free a QoS 2 slot at PUBCOMP or at a failing PUBREC with reason
at least `0x80`; a successful PUBREC does not free it. A full window does not
block non-PUBLISH packets.

### Keep aliases directional

A nonempty Topic Name plus Topic Alias establishes or replaces the mapping. An
empty Topic Name may reuse only a mapping already established in that
direction. Never retain the mapping across a Network Connection.

### Scope errors to their legal packets

Validate property identifiers, property value types, and Reason Codes against
the containing packet. Before a successful CONNACK, report a connection
failure with CONNACK, never DISCONNECT. A Malformed Packet or Protocol Error
closes only the affected Network Connection.

## MQTT-SN correctness rules

### Separate Session and Virtual Connection

A Session belongs to a Client Identifier and may span multiple Virtual
Connections. A Virtual Connection begins with CONNECT and can be deleted by
Keep Alive timeout, Retry timeout, DISCONNECT, or a protocol error. Retain
Session State while any Virtual Connection exists and until Session expiry
after the last one is deleted.

Retained messages are not Session State. In-flight QoS 1/2 flows, Session Topic
Aliases, subscriptions, queued messages, Will data, and expiry state are.

### Enforce one outstanding request per direction

Each Virtual Connection direction permits at most one unacknowledged request
across QoS 1/2 PUBLISH, PUBREC, PUBREL, REGISTER, SUBSCRIBE, UNSUBSCRIBE,
PINGREQ, SLEEPREQ, and AUTH. A different Packet Identifier while one is
outstanding requires DISCONNECT `0x93` and Virtual Connection deletion. A retry
of the same request and interleaved PUBWOS remain allowed.

### Retry only eligible packets

- Either peer may retry REGISTER, QoS 1/2 PUBLISH, and PUBREL.
- Only Clients may retry SUBSCRIBE, UNSUBSCRIBE, SLEEPREQ, and PINGREQ.
- Never retry CONNECT or AUTH.
- Make a retransmission packet-identical. Reapply Protection Encapsulation when
  the original used it, although the new envelope may differ.
- Delete the Virtual Connection after the maximum retries plus one further
  Retry Interval without a response.

### Respect reconnect recovery

With Clean Start `0` and an existing Session, both peers resend unacknowledged
QoS 1/2 PUBLISH and PUBREL with original Packet Identifiers. Do not resend QoS
0. Stop retrying after a PUBACK or PUBREC failure reason of at least `0x80`;
set DUP on a resent QoS 2 PUBLISH.

### Validate packet-size boundaries

MQTT-SN supplies no fragmentation or reassembly. Configure the transport so a
packet arrives complete and unaltered, and for UDP prefer an MTU larger than
the largest packet in use. Enforce the CONNECT Maximum Packet Size negotiated
for Server-to-Client traffic.

### Treat protection as end-to-end

The originator named by Sender Identifier performs Protection Encapsulation.
Do not delegate that protection to a Forwarder. Once an endpoint uses a shared
key with a peer, protect every MQTT-SN packet exchanged with that peer.

## Implementation workflow

1. Identify MQTT 5 versus MQTT-SN before parsing the fixed header.
2. Model Session state separately from transport or connection state.
3. Build packet-specific tables for fields, properties, identifiers, defaults,
   Reason Codes, and permitted directions.
4. Make malformed, protocol-error, and negative-acknowledgment paths explicit;
   do not funnel every failure through DISCONNECT.
5. Track QoS state transitions and identifier ownership per sending peer.
6. Test reconnect recovery separately from same-connection operation.
7. Test aliases in both directions and across connection teardown.
8. For MQTT-SN, test Active, Asleep, Awake, Disconnected, and None server-side
   states independently.
9. For WebSocket transport, feed arbitrary frame splits and multiple MQTT
   packets per binary frame into a streaming decoder.
10. For protected MQTT-SN traffic, test envelope flag combinations, tag sizes,
    monotonic counters, nonce derivation, and Forwarder nesting.

## Review checklist

- Does every Variable Byte Integer use its shortest encoding?
- Are property and Reason Code registries packet-scoped?
- Are Packet Identifiers allocated, echoed, and released at the correct state
  transition?
- Are QoS windows independent of non-PUBLISH traffic?
- Are Will publication, Session expiry, and takeover evaluated together?
- Are overlapping and shared subscriptions handled with their distinct
  delivery rules?
- Is re-authentication traffic behavior correct for the selected protocol?
- Are MQTT-SN alias namespaces and directional REGISTER/REGACK forms separate?
- Do sleep transitions suspend Keep Alive and bound the Awake delivery phase?
- Does every terminal error close only the intended Network or Virtual
  Connection and preserve or discard Session State as specified?
