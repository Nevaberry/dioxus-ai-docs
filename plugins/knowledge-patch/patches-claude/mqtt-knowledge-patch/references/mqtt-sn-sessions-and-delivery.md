# MQTT-SN Sessions and Delivery

Use this reference for Virtual Connection lifecycle, retry logic, topic
routing, retained messages, and sleeping Clients. Source batch attribution:
`mqtt-sn-2.0-csd01-guidance`.

## Sessions and Virtual Connections

A Session is associated with a Client Identifier and may continue across
multiple Virtual Connections. It ends after the latest Virtual Connection is
deleted and its Session Expiry Interval passes; `0xFFFFFFFF` means it never
passes. Both peers retain Session State while a Virtual Connection exists, and
the Server discards it after expiry.

Session State includes unfinished QoS 1/2 exchanges and Session Topic Aliases
on both peers. Server state also includes subscriptions, queued messages, Will
data, and expiry time. Retained messages are not Session State. If CONNECT
omits Client Identifier, CONNACK assigns one unused by every current Session.

CONNECT creates a Virtual Connection. Keep Alive timeout, Retry timeout,
DISCONNECT, or Protocol Error deletes it. Every packet except CONNECT, PUBWOS,
optional legacy QoS −1 PUBLISH, and ADVERTISE/SEARCHGW/GWINFO requires an
existing Virtual Connection.

The network may lose or reorder packets but must deliver each received packet
complete and unaltered. On networks that duplicate packets, use the Protection
Encapsulation Monotonic Counter for connection traffic. Bind a sender by
network address, encapsulated sender/connection information, or DTLS
Connection ID. For UDP, configure MTU above the largest MQTT-SN packet and
avoid fragmentation.

## PUBWOS

PUBWOS publishes without a Session or Virtual Connection. It has no response
or retry and may reach multiple receivers. Support is optional. A receiver may
accept ownership, but treats an accepted message as QoS 0. RETAIN still
applies.

A transparent Gateway needs a dedicated MQTT connection to forward PUBWOS
received without a Virtual Connection. An aggregating Gateway may use its
aggregating MQTT connection.

## Outstanding requests and retries

Each direction permits one unacknowledged request across QoS 1/2 PUBLISH,
PUBREC, PUBREL, REGISTER, SUBSCRIBE, UNSUBSCRIBE, PINGREQ, SLEEPREQ, and AUTH.
Do not send a new request while one waits. Receiving a different Packet
Identifier then requires DISCONNECT `0x93` and Virtual Connection deletion. A
retry with the same identifier is allowed; PUBWOS may be interleaved.

Either peer may retry REGISTER, QoS 1/2 PUBLISH, and PUBREL. Clients may also
retry SUBSCRIBE, UNSUBSCRIBE, SLEEPREQ, and PINGREQ. CONNECT and AUTH cannot be
retried, so CONNECT, zero or more AUTH packets, and CONNACK finish without
retries.

After Maximum Retry Count and one additional Retry Interval without response,
delete the Virtual Connection. A retry is packet-identical. If the original
used Protection Encapsulation, retry with protection again, though the outer
encapsulation may differ.

On reconnect with Clean Start zero and an existing Session, both peers resend
unfinished QoS 1/2 PUBLISH and PUBREL with original identifiers. QoS 0 is not
resent. PUBACK/PUBREC reason `>=0x80` ends retransmission. A resent QoS 2
PUBLISH has DUP one.

## Congestion and timers

CONNECT, PUBLISH, SUBSCRIBE, and REGISTER may return Congestion. Wait a
configured Congestion Delay. Informative examples use a delay over five
minutes, the first retry at about six seconds, 3–5 retries, and a 60-second
maximum interval.

Recalculate jitter no greater than the initial interval on each retry:

```text
wait = min((2^n * scaling_factor) + random_jitter, maximum_interval)
```

Informative sleep tolerance is 10% above durations over one minute and 50%
above shorter durations.

## Topic Names and filters

Full Topic Names and Filters are nonempty hierarchical UTF-8 strings up to
65,535 encoded bytes. They contain no U+0000, remain case-sensitive and
unnormalized, and compare character-for-character. PUBLISH names have no
wildcards.

`#` occupies the final whole level. `+` occupies one whole level. A filter
beginning with either wildcard does not match a Topic Name beginning with `$`.

## Topic Alias namespaces

Predefined and Session aliases are independent two-byte spaces. The same
number may occur in both, but maps to different names. Expand an alias before
processing. If an alias exists for a name, the sender uses the alias in
PUBLISH.

Predefined aliases are administratively shared by all Clients and remain
unchanged during a Session. An undefined Predefined Alias is a Protocol Error.

The Server allocates Session aliases per Session. They arise from:

- SUBACK for a non-wildcard subscription;
- REGACK after Client REGISTER; or
- Server REGISTER when wildcard delivery first sees an unaliased name.

SUBACK includes a Predefined or Session alias for a non-wildcard filter and no
alias for a wildcard filter. A Session alias cannot duplicate a Predefined
alias's Topic Name. REGISTER for that name returns REGACK with Predefined Topic
Alias, its value, and Topic Alias Exists.

Session aliases normally survive the Session and sleep. SLEEPREQ Retain Topic
Aliases zero discards them, requiring names or registration while Awake.

## Subscriptions, ordering, and retained messages

A Subscription belongs to one Session, which has at most one Subscription for
a Topic Filter. Identical filters in different Sessions fan out a copy to each
Client. The Server queues an accepted message in every matching Session. A
Client acknowledges incoming PUBLISH according to QoS even if it discards the
Application Message.

By default every Topic is ordered for forwarding from one publisher at one
QoS. A Server may administratively opt topics out.

RETAIN one on PUBLISH or PUBWOS replaces the retained message for the Topic.
Empty Publish Data removes it and is not retained. A Server should store QoS 0
retained data but may discard it at any time. MQTT-SN defines no message
expiry.

Retain Handling:

```text
0 send matching retained messages on every subscription
1 send only when the subscription is new
2 send none
```

Retain As Published zero clears RETAIN on forwarding; one preserves it.

## Reason-code effects and redirection

Malformed and Protocol Error handling affects one Virtual Connection. A Client
should send suitable DISCONNECT and must delete it. A Server may send
DISCONNECT and must delete the associated connection; a CONNECT error may
instead receive CONNACK.

An acknowledgment reason `>=0x80` rejects only the identified packet.
CONNACK or DISCONNECT reason `>=0x80` deletes the Virtual Connection even when
the response cannot be sent. `0x9C` means use another Server temporarily;
`0x9D` means the Server moved permanently. In both cases the Client already
knows the alternative.

## Client states

Server-side states are:

- None: no Session or Virtual Connection.
- Disconnected: Session only.
- Active: normal Virtual Connection.
- Asleep: connection exists, but ordinary receive is unavailable.
- Awake: bounded receive phase.

Do not send to a Disconnected Client. Ignore its non-CONNECT traffic except
PUBWOS. An Asleep Client sends only PINGREQ, CONNECT, or DISCONNECT. An Awake
Client sends only PUBACK, PUBREC, PUBCOMP, REGACK, CONNECT, or DISCONNECT. Any
CONNECT replaces the existing Virtual Connection.

The Server may send WAKEUP as a hint to an Asleep Client, which need not notice
or act.

## Sleeping-client buffering and wake cycles

SLEEPREQ supplies Sleep Duration; successful SLEEPRESP enters Asleep. At 1.5
times the duration without Client traffic, delete the Virtual Connection.
While asleep, buffer QoS 1/2 Application Messages; QoS 0 buffering is optional.

PINGREQ enters Awake. Send at most CONNECT's Default Awake Messages count,
including their complete QoS exchanges. PINGRESP then reports the exact
remaining count or `0xFFFF` for an unknown positive count, and returns the
Client to Asleep. With no queued packets, respond immediately.

Delete the Virtual Connection if delivery retry handling gets no response. An
Awake Client needing to do more than receive and acknowledge buffered messages
sends CONNECT and becomes Active.

## Discovery and optional features

ADVERTISE, SEARCHGW, GWINFO, PUBWOS, Forwarder Encapsulation, and Protection
Encapsulation are optional. A Gateway advertises or answers SEARCHGW only
while it can accept subscriptions and forward messages. Clients may maintain
an active-Gateway list from ADVERTISE/GWINFO and choose among Gateway IDs.

SEARCHGW may be randomly delayed and suppressed after an identical search. A
Client knowing a Gateway may answer with GWINFO after a random delay, but
cancels if another GWINFO arrives. Unanswered searches use exponential
backoff.

Informative examples use ADVERTISE intervals over 15 minutes, an Advertise
Count of 2–3 missed announcements, and five-second SEARCHGW and GWINFO delays.
