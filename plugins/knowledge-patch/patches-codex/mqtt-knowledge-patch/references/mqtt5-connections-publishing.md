# MQTT 5 Connections and Publishing

## CONNECT and CONNACK omission defaults

Apply omission defaults per property rather than using one generic rule.

```text
CONNECT absent: Session Expiry=0, Receive Maximum=65535,
                Topic Alias Maximum=0, no added packet-size limit,
                Request Response Information=0,
                Request Problem Information=1

CONNACK absent: Session Expiry=CONNECT value, Receive Maximum=65535,
                Maximum QoS=2, Topic Alias Maximum=0,
                no added packet-size limit,
                Retain/Wildcard/Subscription-Identifier/
                Shared-Subscription Available=1,
                Server Keep Alive=CONNECT value
```

In particular, omitted Server Keep Alive inherits CONNECT Keep Alive
[MQTT-3.2.2-22].

## Maximum QoS and subscription requests

Use Maximum QoS from CONNACK only to cap Client-to-Server PUBLISH packets.
Exceeding it is a Protocol Error reported with DISCONNECT `0x9B`. Even a Server
that cannot support QoS 1 or 2 publications must accept SUBSCRIBE requests for
QoS 0, 1, or 2 [MQTT-3.2.2-9] [MQTT-3.2.2-10] [MQTT-3.2.2-11].

## Will Delay, Session expiry, and takeover

Publish the Will when Will Delay expires or when the Session ends, whichever
comes first. Suppress it when the Client reconnects to the same Session before
that point [MQTT-3.1.3-9].

For ClientID takeover, suppress the old Will only if all three conditions hold:

- the new CONNECT uses Clean Start `0`;
- the old Will Delay is nonzero;
- the old Session survives.

Publish on takeover when delay is `0`, Clean Start is `1`, or the old Session
Expiry is `0`.

## CONNECT pipelining and authentication

A Client may pipeline ordinary Control Packets after CONNECT before CONNACK.
If CONNECT specifies Authentication Method, restrict that pre-CONNACK flow to
AUTH or DISCONNECT [MQTT-3.1.2-30].

If the Server rejects CONNECT, do not process pipelined packets following it,
except AUTH packets [MQTT-3.1.4-6].

## Request Problem Information

Request Problem Information defaults to `1`. If the Client explicitly sends
`0`:

- User Property remains legal on PUBLISH, CONNACK, and DISCONNECT.
- Reason String remains legal on CONNACK and DISCONNECT.
- Both properties are forbidden on other packet types.

Receiving a now-forbidden property is a Protocol Error handled with
DISCONNECT `0x82` [MQTT-3.1.2-29].

## Directional Topic Aliases

Keep two independent mapping tables, one for each direction of a Network
Connection. Never carry a mapping into another Network Connection
[MQTT-3.3.2-7].

```text
PUBLISH topic="sensors/a", Topic-Alias=1  # establish
PUBLISH topic="",          Topic-Alias=1  # reuse sensors/a
PUBLISH topic="sensors/b", Topic-Alias=1  # replace mapping
```

A nonempty Topic Name plus Topic Alias creates or replaces a mapping. An empty
Topic Name may use only an established alias.

- Alias `0` or a value above the receiver's advertised maximum:
  DISCONNECT `0x94`.
- Unknown alias with an empty Topic Name: DISCONNECT `0x82`.

These requirements are specified by [MQTT-3.3.2-8] through
[MQTT-3.3.2-12].

## Message Expiry in transit

Delete a subscriber's copy if Message Expiry passes before onward delivery
begins [MQTT-3.3.2-5]. Otherwise, put the received Message Expiry Interval
minus time spent waiting at the Server on the outgoing PUBLISH
[MQTT-3.3.2-6].

## Subscription Identifiers on PUBLISH

Reject a Subscription Identifier on Client-to-Server PUBLISH. Every
Subscription Identifier on Server-to-Client PUBLISH must come from a
SUBSCRIBE that caused that delivery [MQTT-3.3.4-6].

For one outgoing PUBLISH representing overlapping matches, include all
matching identifiers, including duplicate values. If sending separate copies,
put the corresponding match's identifier on each copy when that subscription
has one [MQTT-3.3.4-3] [MQTT-3.3.4-4] [MQTT-3.3.4-5].

## Receive Maximum

Track Receive Maximum independently per Network Connection. Count only QoS 1
and QoS 2 PUBLISH flows.

- Release a QoS 1 slot on PUBACK.
- Release a QoS 2 slot on PUBCOMP.
- Release either slot on a PUBREC failure reason of at least `0x80`.
- Do not release a QoS 2 slot on successful PUBREC.

Exceeding the peer's window causes DISCONNECT `0x93`. A full window must not
delay any non-PUBLISH packet [MQTT-3.3.4-7] through [MQTT-3.3.4-10].

## Compact publish acknowledgments

PUBACK, PUBREC, PUBREL, and PUBCOMP may omit both Reason Code and Property
Length only for success with no properties. Those omissions imply Reason Code
`0x00` and Property Length `0`.

```text
Remaining Length 2: packet_identifier
Remaining Length 3: packet_identifier | reason_code
Remaining Length 4+: packet_identifier | reason_code
                     | property_length | properties
```
