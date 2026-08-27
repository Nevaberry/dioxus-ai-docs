# MQTT 5 Operations and Transports

Use this reference for connection-phase authentication, request/response,
redirection, protocol-error scope, and MQTT over WebSocket.

## Connection-phase AUTH and DISCONNECT

A Server cannot send DISCONNECT until it has sent successful CONNACK with
Reason Code below `0x80`. Report connection-attempt failure through CONNACK,
not pre-CONNACK DISCONNECT.

AUTH Reason Code `0x00` Success is Server-only. A Client-originated AUTH
success is invalid.

## Request/response

A request PUBLISH carries Response Topic and optional Correlation Data. The
responder publishes to that topic, copies Correlation Data, and omits Response
Topic from the response.

```text
request  topic=rpc/get
         Response-Topic=client/c1/reply Correlation-Data=2a
response topic=client/c1/reply          Correlation-Data=2a
```

Both are ordinary publications. The requester normally subscribes first,
because a response without a subscriber is not delivered.

Request Response Information one in CONNECT asks for optional UTF-8 Response
Information in CONNACK. Its format is unspecified; it may supply a globally
unique part of the topic tree reserved for the Client for at least the Session.

## Server Reference

Server Reference is a UTF-8, space-separated list for redirection. Individual
reference grammar is unspecified. `host[:port]` and bracketed IPv6 are
recommendations only, and the Client may ignore the property.

```text
myserver.xyz.org:8883 10.10.151.22:8883 [fe80::9610:3eff:fe1c]:1883
```

## Re-authentication

A Client that supplied Authentication Method may start re-authentication after
CONNACK using AUTH reason `0x19` and the same method. Ordinary packets may
continue under the previous authentication during the exchange. On failure,
either peer should send DISCONNECT and must close the Network Connection.

## Malformed and Protocol Error scope

When a Reason Code is specified, a Server detecting Malformed Packet or
Protocol Error closes that Network Connection. It may first send CONNACK for a
CONNECT error and should send DISCONNECT for another packet. A Client should
close too; it may first send DISCONNECT for AUTH and should for other packets.
Other Sessions are unaffected.

## MQTT over WebSocket

MQTT Control Packets use WebSocket binary data frames. Receiving another
data-frame type requires closing the Network Connection. WebSocket frame
boundaries do not align with MQTT packet boundaries: one frame may hold
several packets or part of one packet. Maintain a streaming MQTT decoder across
frames.

The Client offers subprotocol `mqtt`; the Server selects and returns exactly
`mqtt`. The WebSocket URI has no MQTT protocol meaning.

```text
Client: Sec-WebSocket-Protocol: mqtt
Server: Sec-WebSocket-Protocol: mqtt

binary frame 1: CONNECT || first part of PUBLISH
binary frame 2: rest of PUBLISH || PINGREQ
```
