# MQTT 5 Subscriptions and Operations

## Shared-subscription options and retained messages

Treat No Local on a Shared Subscription as a Protocol Error
[MQTT-3.8.3-4]. Never send retained messages when creating or joining a Shared
Subscription, regardless of Retain Handling. An identical shared filter adds
the Session to the existing Shared Subscription.

## Subscription Identifier updates

A SUBSCRIBE may contain at most one Subscription Identifier, in
`1..268435455`. Store its value or absence on every subscription created or
modified by that packet.

When the same filter is subscribed again with a different identifier or none,
remove the old identifier. A retransmitted PUBLISH may still carry the old or
new value, but once the Server sends the new value it cannot revert to the old
one.

## QoS downgrade and duplicates

Set delivery QoS to the minimum of the original publication QoS and the
Server-granted Maximum QoS [MQTT-3.8.4-8]. If an original QoS 1 publication is
delivered at granted QoS 0, the Server may send duplicate copies even though
the outgoing PUBLISH has QoS 0.

## Pre-CONNACK failure reporting

The Server must not send DISCONNECT until it has sent a successful CONNACK
whose Reason Code is below `0x80` [MQTT-3.14.0-1]. Report connection-attempt
failures with CONNACK.

AUTH Reason Code `0x00` Success is Server-only. Treat a Client-originated AUTH
success as invalid.

## Reconnect-only retransmission

On an established Network Connection, neither peer may resend QoS 1/2 PUBLISH
or PUBREL merely because an acknowledgment timer expires. The required resend
occurs only after reconnect with Clean Start `0` and a present Session, using
the original Packet Identifiers [MQTT-4.4.0-1].

## Client flow ordering

The Client must:

- resend PUBLISH packets in original send order;
- send PUBACK and PUBREC in the order their PUBLISH packets arrived;
- send PUBREL in the order their PUBREC packets arrived
  [MQTT-4.6.0-1] through [MQTT-4.6.0-4].

An ordered QoS 1 stream can still appear as `1,2,3,2,3,4` after reconnect.
Configure Receive Maximum `1` in both directions when an older retransmission
must never follow a later message.

## Shared-subscription lifetime

A Shared Subscription is Server-scoped and remains alive while at least one
Session is associated, even if its creating Session ends. Session termination
or UNSUBSCRIBE of the full Shared Subscription filter detaches that Session.
The last detachment deletes the Shared Subscription and its undelivered
messages. Re-subscribing the same Session changes its options without adding a
second membership.

## Shared-delivery failures

If the selected consumer disconnects during QoS 2 delivery, finish with that
same Session after reconnect. Do not transfer the message, and do not transfer
it if that Session ends [MQTT-4.8.2-4] [MQTT-4.8.2-5].

For QoS 1, the Server may reroute immediately or wait for reconnect and should
reroute if the chosen Session then ends. If PUBACK or PUBREC reports an error,
discard the message rather than trying another subscriber [MQTT-4.8.2-6].

## Request/response publications

Implement request/response with ordinary publications:

```text
request  topic=rpc/get       Response-Topic=client/c1/reply  Correlation-Data=2a
response topic=client/c1/reply                                Correlation-Data=2a
```

The request carries Response Topic and optional Correlation Data. The response
uses that Topic, copies Correlation Data, and omits Response Topic. Subscribe
to the response topic before requesting when a response must not be lost; the
Server performs normal routing and does not deliver a response with no
subscriber.

## Response Information

Set Request Response Information to `1` in CONNECT to ask for optional UTF-8
Response Information in CONNACK. Its content is unspecified. It may describe
a globally unique portion of the topic tree reserved for the Client for at
least the Session lifetime.

## Server Reference

Parse Server Reference as a UTF-8, space-separated list for redirection. The
individual reference grammar is unspecified; `host[:port]` and bracketed IPv6
are recommendations only, and a Client may ignore the property.

```text
myserver.xyz.org:8883 10.10.151.22:8883 [fe80::9610:3eff:fe1c]:1883
```

## Re-authentication

A Client that supplied Authentication Method may begin re-authentication after
CONNACK with AUTH reason `0x19` and the same method
[MQTT-4.12.1-1]. Ordinary packets may continue under the prior authentication
during this exchange. On failure, the Client or Server should send DISCONNECT
and must close the Network Connection [MQTT-4.12.1-2].

## Malformed Packets and Protocol Errors

When the specification supplies a Reason Code, a Server detecting a Malformed
Packet or Protocol Error must close the affected Network Connection. It may
first send CONNACK for a CONNECT error and should send DISCONNECT for another
packet [MQTT-4.13.1-1].

A Client should also close the affected connection. It may first send
DISCONNECT for an AUTH error and should do so for another packet. Do not affect
other Sessions.
