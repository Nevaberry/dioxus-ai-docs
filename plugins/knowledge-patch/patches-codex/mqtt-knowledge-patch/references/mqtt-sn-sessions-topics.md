# MQTT-SN Sessions, Topics, and Delivery

This reference carries behavioral guidance from
`mqtt-sn-2.0-csd01-guidance`.

## Sessions and Virtual Connections

A Session belongs to a Client Identifier and may continue over several Virtual
Connections. It ends only after the latest Virtual Connection is deleted and
its Session Expiry Interval passes. Retain Session State while a Virtual
Connection exists and discard it after expiry. Interval `0xFFFFFFFF` never
passes [MQTT-SN-4.1.1-1] through [MQTT-SN-4.1.1-3].

Both peers keep in-flight QoS 1/2 exchanges and Session Topic Aliases in
Session State. The Server additionally keeps subscriptions, queued messages,
Will data, and expiry time. Retained messages are not Session State. If
CONNECT omits Client Identifier, CONNACK assigns an identifier unused by every
current Session [MQTT-SN-4.1.2-1] [MQTT-SN-4.1.2-2].

## Virtual Connection boundary and duplicates

CONNECT creates a Virtual Connection. Keep Alive timeout, Retry timeout,
DISCONNECT, or a protocol error deletes it. Require every packet except
CONNECT, PUBWOS, optional legacy QoS −1 PUBLISH, ADVERTISE, SEARCHGW, and
GWINFO to belong to an existing Virtual Connection [MQTT-SN-4.2.1-1].

The network may lose or reorder packets but must deliver each received packet
complete and unaltered. On networks that can duplicate packets, use Protection
Encapsulation's Monotonic Counter for connection-oriented traffic. Bind a
sender to its Virtual Connection by network address, encapsulated
sender/connection data, or DTLS Connection ID.

For UDP, prefer an MTU larger than the largest MQTT-SN packet in use and avoid
fragmentation.

## PUBWOS

PUBWOS sends an Application Message without a Session or Virtual Connection.
It gets no response or retry and can reach multiple receivers. Support is
optional. A receiver may take ownership; if it accepts the message, process it
as QoS 0.

RETAIN applies to PUBWOS. A transparent Gateway needs a dedicated MQTT
connection for PUBWOS received outside a Virtual Connection; an aggregating
Gateway may use its aggregating MQTT connection.

## Optional 1.2 QoS −1 compatibility

An implementation may accept MQTT-SN 1.2 QoS −1 PUBLISH from Clients or
Servers as PUBWOS-equivalent QoS 0. It needs no Session or Virtual Connection.

```text
QoS bits       = 0b11
DUP            = 0
Topic Type     = 0b00 full Topic Name
               | 0b01 Predefined Topic Alias
               | 0b10 two-byte Short Topic Name
full name data = u16 name_length || UTF-8 name
```

Require both reserved flag bits to be zero. RETAIN retains its ordinary
meaning.

## One outstanding request per direction

Permit at most one unacknowledged request in each direction of a Virtual
Connection across QoS 1/2 PUBLISH, PUBREC, PUBREL, REGISTER, SUBSCRIBE,
UNSUBSCRIBE, PINGREQ, SLEEPREQ, and AUTH.

While one awaits acknowledgment, receiving another request with a different
Packet Identifier requires DISCONNECT `0x93` and Virtual Connection deletion
[MQTT-SN-4.9-1] [MQTT-SN-4.9-2]. Allow a retry of the same request and
interleaved PUBWOS.

## Retry and reconnect

Either peer may retry REGISTER, QoS 1/2 PUBLISH, and PUBREL. Clients may also
retry SUBSCRIBE, UNSUBSCRIBE, SLEEPREQ, and PINGREQ. Do not retry CONNECT or
AUTH; CONNECT, zero or more AUTH packets, and CONNACK complete without retries
[MQTT-SN-4.4.2-1] [MQTT-SN-4.4.2-2].

After Maximum Retry Count and one more Retry Interval without a response,
delete the Virtual Connection [MQTT-SN-4.4.2-3]. Make retransmissions
packet-identical. If the original used Protection Encapsulation, use it again,
though the envelope itself may differ [MQTT-SN-4.4.2-4]
[MQTT-SN-4.4.2-5].

After reconnect with Clean Start `0` and an existing Session, both peers resend
unacknowledged QoS 1/2 PUBLISH and PUBREL with original Packet Identifiers.
Do not resend QoS 0 [MQTT-SN-4.4.1-1]. PUBACK or PUBREC reason at least
`0x80` ends retransmission. Set DUP on resent QoS 2 PUBLISH
[MQTT-SN-4.4.1-2] [MQTT-SN-4.4.1-3].

## Congestion and timers

CONNECT, PUBLISH, SUBSCRIBE, and REGISTER can return Congestion. Wait a
configured Congestion Delay. Informative examples use a delay over five
minutes, the initial retry near six seconds (a five-second initial wait plus a
one-second starting interval), three to five retries, and a 60-second maximum
interval.

Recalculate jitter no greater than the initial interval on every exponential
backoff retry:

```text
wait = min((2^n * scaling_factor) + random_jitter, maximum_interval)
```

The informative sleep-timer tolerance is 10% above a requested period longer
than one minute and 50% above a shorter period.

## Full Topic Names and filters

Topic Names and Topic Filters are hierarchical UTF-8 and may occupy at most
65,535 encoded bytes. Require nonempty strings without U+0000. Compare
case-sensitively, without normalization, character-for-character. Forbid
wildcards in a PUBLISH Topic Name [MQTT-SN-4.7.1.1-1] and
[MQTT-SN-4.7.1.3-1] through [MQTT-SN-4.7.1.3-4].

`#` must be the final complete level. `+` must occupy one complete level. A
filter starting with either wildcard does not match a Topic Name starting with
`$` [MQTT-SN-4.7.1.2-1] [MQTT-SN-4.7.1.1.3-1].

## Independent alias namespaces

Predefined Topic Aliases and Session Topic Aliases are separate two-byte value
spaces. The same number may exist in both but must name different topics.
Expand aliases before further processing. If an alias exists for a Topic Name,
the sender must use it instead of the name in PUBLISH
[MQTT-SN-4.7.2-1] [MQTT-SN-4.7.2.2-6].

Predefined aliases are administratively shared by all Clients and remain
unchanged throughout a Session. An undefined Predefined Topic Alias is a
Protocol Error [MQTT-SN-4.7.2.1-1] [MQTT-SN-4.7.2.1-2].

## Server-controlled Session aliases

The Server allocates Session Topic Aliases per Session
[MQTT-SN-4.7.2.2-1]. It may:

- return one in SUBACK for a non-wildcard subscription;
- return one in REGACK after Client REGISTER;
- send REGISTER when wildcard delivery first encounters an unaliased Topic
  Name.

SUBACK must include a Predefined or Session alias for a non-wildcard filter
and must not include one for a wildcard filter
[MQTT-SN-4.7.2.2-2] [MQTT-SN-4.7.2.2-3].

A Session alias cannot duplicate the Topic Name of a Predefined alias.
REGISTER for that name returns REGACK with Topic Type Predefined Topic Alias,
the predefined value, and Topic Alias Exists
[MQTT-SN-4.7.2.2-4] [MQTT-SN-4.7.2.2-5].

Session aliases normally survive the entire Session, including sleep.
SLEEPREQ with Retain Topic Aliases `0` discards them; afterward use names or
register again while Awake.

## Subscription fan-out and order

A Subscription belongs to one Session, which may have only one Subscription
for a Topic Filter. Identical subscriptions across Sessions fan out: every
Client gets its own copy rather than load-balanced delivery.

Queue an accepted message into every matching Client's Session State
[MQTT-SN-4.5-1]. A Client acknowledges incoming PUBLISH according to QoS even
if it chooses not to process the message [MQTT-SN-4.5-2].

By default, each Topic is ordered when forwarding messages from one publisher
at one QoS. A Server may administratively opt topics out
[MQTT-SN-4.6-1] [MQTT-SN-4.6-2].

## Reason-code effects and redirection

Scope Malformed Packet and Protocol Error handling to one Virtual Connection.
A Client should send an appropriate DISCONNECT and must delete it. A Server
may send DISCONNECT and must delete the associated connection; for CONNECT
errors it may use CONNACK [MQTT-4.12.1-1] [MQTT-4.12.1-2].

An acknowledgment reason at least `0x80` rejects only its identified packet.
CONNACK or DISCONNECT at least `0x80` requires Virtual Connection deletion even
when the response is not sent [MQTT-4.12.2-1].

Reason `0x9C` Use another server is temporary; `0x9D` Server moved is
permanent. In both cases, the Client already knows the alternative Server.

## Retained messages and subscription controls

RETAIN `1` on PUBLISH or PUBWOS replaces the retained message for the Topic
Name. Empty Publish Data removes it and is not retained
[MQTT-SN-4.13-1] through [MQTT-SN-4.13-3]. A Server should store QoS 0
retained data but may discard it at any time. MQTT-SN defines no message
expiry.

Retain Handling:

- `0`: send matching retained messages on every subscription;
- `1`: send only when the subscription is new;
- `2`: send none [MQTT-SN-4.13-5] through [MQTT-SN-4.13-7].

Retain As Published `0` clears RETAIN on forwarding; `1` preserves the received
value [MQTT-SN-4.13-8] [MQTT-SN-4.13-9].

## Optional discovery and forwarding

ADVERTISE, SEARCHGW, GWINFO, PUBWOS, Forwarder Encapsulation, and Protection
Encapsulation are optional. A Gateway should advertise or answer SEARCHGW only
while it can accept subscriptions and forward messages. Clients may build an
active-Gateway list from ADVERTISE and GWINFO and select by Gateway identifier.

SEARCHGW may be randomly delayed and suppressed after hearing an identical
search. A Client that knows a Gateway may answer with GWINFO after a random
delay, cancelling if another GWINFO arrives. Retry unanswered searches with
exponential backoff.

Informative examples use ADVERTISE intervals over 15 minutes, Advertise Count
two or three, and five-second SEARCHGW and GWINFO delays.
