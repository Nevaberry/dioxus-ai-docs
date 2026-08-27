---
name: mqtt-knowledge-patch
description: MQTT
version: "MQTT-SN 2.0 CSD01"
license: MIT
metadata:
  author: Nevaberry
---


# MQTT Knowledge Patch

Use this skill when implementing, reviewing, testing, or operating MQTT 5 or
MQTT-SN. Start with the protocol family and packet flow involved, then open the
matching reference before changing encoders, state machines, or broker policy.

## Reference index

| Reference | Topics |
| --- | --- |
| [MQTT-SN migration and wire format](references/mqtt-sn-migration-and-wire.md) | 1.2 migration, framing, packet types, identifiers, CONNECT, publish and subscription packets, reason codes |
| [MQTT-SN sessions and delivery](references/mqtt-sn-sessions-and-delivery.md) | Virtual Connections, retries, aliases, retained messages, client states, sleep, discovery |
| [MQTT-SN authentication and protection](references/mqtt-sn-authentication-and-protection.md) | Enhanced authentication, payload profiles, transport security, Protection and prefix encapsulation |
| [MQTT 5 framing and properties](references/mqtt5-framing-and-properties.md) | Canonical VBI encoding, property registry, omission defaults, failure-code scopes |
| [MQTT 5 publish and subscriptions](references/mqtt5-publish-and-subscriptions.md) | QoS flow, Will Delay, aliases, expiry, identifiers, shared subscriptions, retransmission |
| [MQTT 5 operations and transports](references/mqtt5-operations-and-transports.md) | Request/response, re-authentication, error scope, redirection, WebSocket framing |

## Choose the protocol family first

- Do not reuse MQTT 5 packet layouts for MQTT-SN. MQTT-SN has its own Length
  encoding, packet registry, flags, identifier matrix, aliases, and reason-code
  scopes.
- Treat MQTT-SN Sessions and Virtual Connections separately. A Session belongs
  to a Client Identifier and may outlive or span Virtual Connections.
- Treat MQTT 5 Session state separately from Network Connection state. Topic
  Alias mappings and Receive Maximum windows belong to one connection.
- Validate packet-specific legality, not just the numeric validity of a reason
  code or property identifier.

## Breaking MQTT-SN migration checks

When moving from MQTT-SN 1.2 behavior:

1. Rename Topic Id, Message Id, and Message Type concepts to Topic Alias,
   Packet Identifier, and Packet Type.
2. Carry Will data in CONNECT; do not implement the old Will control-packet
   exchange.
3. Do not expect a response to DISCONNECT.
4. Do not use a two-byte Short Topic Name for ordinary publishing.
5. Use the new contiguous Packet Type registry and reject reserved types.
6. Accept both short and extended Length forms.
7. Use protocol version byte `0x02` in CONNECT.
8. Implement QoS −1 PUBLISH only as the optional legacy PUBWOS-compatible form.

See [MQTT-SN migration and wire format](references/mqtt-sn-migration-and-wire.md)
for the exact encodings.

## MQTT-SN decoder invariants

- Length includes its own encoding and the Packet Type. Extended Length is
  `0x01` followed by an unsigned big-endian `u16`.
- Topic Type is `00` Session Alias, `01` Predefined Alias, `10` reserved, and
  `11` Topic Name or Filter.
- A QoS 0 PUBLISH has no Packet Identifier; QoS 1 and 2 PUBLISH packets do.
- PUBWOS has no Packet Identifier, response, or retry and is accepted as QoS 0.
- Reject malformed UTF-8, surrogate code points, and U+0000. Preserve U+FEFF.
- Interpret every optional field from its packet's flags and remaining length;
  do not infer one packet's layout from another.
- MQTT-SN has no fragmentation layer. Enforce the underlying network limit and
  the peer's negotiated Maximum Packet Size.

## MQTT-SN state-machine invariants

- Except for CONNECT, PUBWOS, optional legacy QoS −1 PUBLISH, and discovery
  packets, require an existing Virtual Connection.
- Permit only one outstanding request per direction across the controlled
  request classes. A different identifier while one is pending is reason
  `0x93` and deletes the Virtual Connection.
- Do not retry CONNECT or AUTH. Retry only allowed packets, byte-identically,
  and delete the Virtual Connection after the retry budget expires.
- On session resume, resend unfinished QoS 1/2 PUBLISH and PUBREL with their
  original identifiers; do not resend QoS 0.
- Enforce the None, Disconnected, Active, Asleep, and Awake send/receive
  restrictions.
- A new CONNECT always replaces the Client's current Virtual Connection.

## MQTT-SN alias and subscription checks

- Keep Predefined and Session Topic Alias namespaces independent.
- Let only the Server allocate Session Topic Aliases.
- Require a SUBACK alias for a non-wildcard filter and forbid one for a wildcard
  filter.
- Expand an alias before routing, matching, or unsubscribe processing.
- Replace, rather than duplicate, a Session's subscription for the same filter.
- Fan out identical subscriptions in different Sessions; they are not a shared
  load-balancing group.
- Complete started QoS 1/2 delivery after UNSUBSCRIBE, even after new matching
  messages stop being added.
- Apply Retain Handling and Retain As Published independently.

## MQTT-SN sleep and wake checks

- Successful SLEEPREQ suspends Keep Alive without deleting the Virtual
  Connection.
- Buffer QoS 1/2 while asleep; QoS 0 buffering is optional.
- Limit each PINGREQ wake cycle to Default Awake Messages and finish full QoS
  exchanges before PINGRESP.
- Report the exact remaining queue count, or `0xFFFF` when only a positive
  unknown count is available.
- Delete the Virtual Connection after 1.5 times the sleep duration without
  activity, or when awake delivery exhausts retries.
- Discard Session Topic Aliases when SLEEPREQ does not request retention.

## MQTT-SN security checks

- If a shared protection key exists for a peer, protect every packet exchanged
  with that peer.
- The originator identified by Sender Identifier performs protection; a
  Forwarder does not substitute for it.
- Increment the optional monotonic counter across Sessions and destinations.
- Authenticate the complete Protection envelope prefix.
- Derive AEAD nonces from SHA-256 over the complete prefix before the protected
  packet, using the scheme-specific leftmost bit count.
- Treat Connection Encapsulation as insecure addressing metadata, not as an
  authorization mechanism.

## MQTT 5 encoder and decoder invariants

- Encode every Variable Byte Integer in its shortest form and reject overlong
  encodings.
- Parse Property Length before property entries, and validate each property's
  type and packet scope.
- Apply omission defaults property-by-property. Topic Alias Maximum defaults to
  zero; several advertised capability flags default to one.
- Only omit publish-acknowledgment Reason Code and Property Length for success
  with no properties.
- Use failure Reason Codes only in their permitted Control Packets.
- Decode MQTT packets as a byte stream over WebSocket binary frames; frame and
  packet boundaries are unrelated.

## MQTT 5 connection and publish checks

- Maximum QoS limits Client-to-Server PUBLISH, not requested subscription QoS.
- With enhanced authentication, allow only AUTH or DISCONNECT between CONNECT
  and successful CONNACK. Without it, ordinary packets may be pipelined.
- Never send DISCONNECT before a successful CONNACK; report connection-attempt
  failure in CONNACK.
- Keep Topic Alias mappings directional and connection-local. Alias zero,
  out-of-range aliases, and unknown aliases with empty topic names are errors.
- Decrement Message Expiry by broker residence time and delete expired queued
  copies.
- Count Receive Maximum slots only for unfinished QoS 1/2 PUBLISH flows. A
  successful PUBREC does not release a QoS 2 slot.
- Do not use acknowledgment timers to retransmit on an established connection.
  Resume unfinished flows only after Session reconnection with Clean Start 0.

## MQTT 5 subscription checks

- A SUBSCRIBE carries at most one nonzero Subscription Identifier, which is
  stored on every created or modified subscription.
- On a delivered publication, include only identifiers from subscriptions that
  caused that delivery; preserve duplicates for overlapping matches.
- No Local is invalid on a Shared Subscription.
- Joining or creating a Shared Subscription never triggers retained delivery.
- Shared-subscription membership follows Session lifetime; the last detachment
  removes the shared subscription and its undelivered messages.
- QoS 2 shared delivery remains bound to the selected Session. QoS 1 may be
  rerouted under its distinct failure rules.
- Preserve the specified client-side ordering of resent PUBLISH, PUBACK/PUBREC,
  and PUBREL flows.

## Final review

Before shipping:

1. Confirm protocol family, direction, connection/session state, and packet
   scope for every field.
2. Test omitted fields as well as explicit values.
3. Test reconnect, takeover, expiry, and duplicate behavior—not only the happy
   path on one connection.
4. Test malformed lengths, reserved bits, illegal properties, bad aliases, and
   out-of-scope reason codes.
5. For datagram MQTT-SN, test reordering, loss, duplication, and MTU limits.
6. For WebSocket MQTT, split and coalesce MQTT packets across binary frames.
