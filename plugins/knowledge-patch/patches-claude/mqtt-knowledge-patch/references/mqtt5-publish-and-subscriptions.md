# MQTT 5 Publish and Subscriptions

Use this reference for publish flow control, aliases, expiry, subscription
options, shared delivery, and reconnect behavior.

## Maximum QoS and Will Delay

CONNACK Maximum QoS caps Client-to-Server PUBLISH packets. Exceeding it is a
Protocol Error with DISCONNECT `0x9B`. It does not restrict SUBSCRIBE requested
QoS: even a Server unable to support QoS 1/2 publication accepts subscription
requests for QoS 0, 1, or 2.

Will publication occurs when Will Delay passes or the Session ends, whichever
is earlier. Reconnecting to the same Session before then suppresses it. On
Client Identifier takeover, the old Will is suppressed only when the new
CONNECT has Clean Start zero, old delay is nonzero, and the old Session
survives. Delay zero, Clean Start one, or old Session Expiry zero publishes it.

## CONNECT pipelining and problem information

Without Authentication Method, a Client may pipeline ordinary Control Packets
after CONNECT before CONNACK. With Authentication Method, it sends only AUTH
or DISCONNECT until CONNACK. If CONNECT is rejected, the Server does not
process following pipelined data other than AUTH.

Request Problem Information defaults to one. When explicitly zero, User
Property remains permitted on PUBLISH, CONNACK, and DISCONNECT, and Reason
String remains permitted on CONNACK and DISCONNECT. Both are forbidden on
other packets; receiving them there is Protocol Error `0x82`.

## Directional Topic Aliases

Topic Alias maps one direction of one Network Connection. Client and Server
maps are independent and never survive reconnection. A nonempty Topic Name and
alias establishes or replaces a mapping. An empty name uses an existing one.

```text
PUBLISH topic="sensors/a", Topic-Alias=1  # establish
PUBLISH topic="",          Topic-Alias=1  # reuse sensors/a
PUBLISH topic="sensors/b", Topic-Alias=1  # replace
```

Alias zero or above the receiver-advertised maximum causes DISCONNECT `0x94`.
An unknown alias with empty Topic Name causes DISCONNECT `0x82`.

## Message Expiry

If Message Expiry passes before onward delivery starts, delete that
subscriber's copy. Otherwise outgoing PUBLISH carries the received interval
minus time spent waiting at the Server.

## Subscription Identifiers

Client-to-Server PUBLISH cannot contain Subscription Identifier. Every
identifier in a delivered PUBLISH comes from a SUBSCRIBE that caused the
delivery. For one PUBLISH representing overlapping matches, include all
matching identifiers, including duplicate values. For separate copies, each
copy carries the identifier of its corresponding subscription when present.

A SUBSCRIBE has at most one Subscription Identifier in `1..268435455`. Its
value or absence is stored on every created or modified subscription.
Re-subscribing to a filter with a new identifier or no identifier removes the
old one. A retransmitted PUBLISH may contain old or new during transition; once
the Server sends the new one, it cannot revert to old.

## Receive Maximum and acknowledgment encoding

Receive Maximum is per Network Connection and counts only unfinished QoS 1/2
PUBLISH. A slot ends at PUBACK, PUBCOMP, or failure PUBREC `>=0x80`. Successful
PUBREC does not release a QoS 2 slot. Exceeding the window causes DISCONNECT
`0x93`; a full window cannot delay non-PUBLISH packets.

PUBACK, PUBREC, PUBREL, and PUBCOMP omit both Reason Code and Property Length
only for success with no properties:

```text
Remaining Length 2: packet_identifier
Remaining Length 3: packet_identifier | reason_code
Remaining Length 4+: packet_identifier | reason_code
                     | property_length | properties
```

## Shared-subscription rules

No Local on a Shared Subscription is a Protocol Error. Creating or joining a
Shared Subscription never sends retained messages, regardless of Retain
Handling. The same shared filter joins the Session to the existing shared
subscription.

A Shared Subscription is Server-scoped and survives the creating Session while
at least one Session remains. Session termination or UNSUBSCRIBE of the full
shared filter detaches that Session. The last detachment deletes the shared
subscription and undelivered messages. Re-subscribing the same Session can
change options without adding membership.

If the chosen consumer disconnects during QoS 2 delivery, finish with the same
Session after reconnect and never transfer it; if the Session ends, discard
it. For QoS 1, the Server may reroute immediately or await reconnect and should
reroute if the selected Session ends. An error PUBACK or PUBREC discards the
message without another subscriber attempt.

## QoS downgrade and duplicates

Delivery QoS is the minimum of publication QoS and granted Maximum QoS. If an
original QoS 1 message is delivered at granted QoS 0, the Server may deliver
duplicates even though outgoing PUBLISH says QoS 0.

## Retransmission and ordering

On an established connection, neither peer resends QoS 1/2 PUBLISH or PUBREL
on an acknowledgment timeout. Required resend occurs after reconnect with
Clean Start zero and a present Session, using original Packet Identifiers.

The Client:

- resends PUBLISH in original send order;
- sends PUBACK and PUBREC in PUBLISH arrival order; and
- sends PUBREL in PUBREC arrival order.

An ordered QoS 1 stream may still appear as `1,2,3,2,3,4` after reconnect.
Receive Maximum one at both ends prevents an older retransmission from
following a later message.
