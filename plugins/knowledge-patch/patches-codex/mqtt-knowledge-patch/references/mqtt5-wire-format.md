# MQTT 5 Wire Format and Transport

## Canonical Variable Byte Integers

Encode Remaining Length, Property Length, Property Identifiers, and
Subscription Identifiers as base-128 Variable Byte Integers. Put the low
seven-bit group first and use bit 7 as the continuation marker. Accept only the
shortest encoding, at most four bytes, for the range `0..268435455`.

```text
00..7F             0..127
80 01..FF 7F       128..16,383
80 80 01..FF FF 7F 16,384..2,097,151
80 80 80 01..FF FF FF 7F
                    2,097,152..268,435,455
```

Thus `128` is `80 01`; reject the overlong `80 00` as forbidden
[MQTT-1.5.5-1].

## Property framing and registry

Encode a property set as:

```text
property_length:VBI | (property_id:VBI | typed_value)*
```

Encode no properties as `00`. Property order has no general significance.
Treat an identifier illegal for the containing packet, or a value encoded with
the wrong type, as a Malformed Packet [MQTT-2.2.2-1]. Every MQTT 5 property
identifier happens to fit in one byte, but its wire field remains a VBI.

| Hex | Property | Type | Legal packet/property set |
| --- | --- | --- | --- |
| `01` | Payload Format Indicator | Byte | PUBLISH, Will |
| `02` | Message Expiry Interval | U32 | PUBLISH, Will |
| `03` | Content Type | UTF-8 | PUBLISH, Will |
| `08` | Response Topic | UTF-8 | PUBLISH, Will |
| `09` | Correlation Data | Binary | PUBLISH, Will |
| `0B` | Subscription Identifier | VBI | PUBLISH, SUBSCRIBE |
| `11` | Session Expiry Interval | U32 | CONNECT, CONNACK, DISCONNECT |
| `12` | Assigned Client Identifier | UTF-8 | CONNACK |
| `13` | Server Keep Alive | U16 | CONNACK |
| `15` | Authentication Method | UTF-8 | CONNECT, CONNACK, AUTH |
| `16` | Authentication Data | Binary | CONNECT, CONNACK, AUTH |
| `17` | Request Problem Information | Byte | CONNECT |
| `18` | Will Delay Interval | U32 | Will |
| `19` | Request Response Information | Byte | CONNECT |
| `1A` | Response Information | UTF-8 | CONNACK |
| `1C` | Server Reference | UTF-8 | CONNACK, DISCONNECT |
| `1F` | Reason String | UTF-8 | CONNACK, PUBACK, PUBREC, PUBREL, PUBCOMP, SUBACK, UNSUBACK, DISCONNECT, AUTH |
| `21` | Receive Maximum | U16 | CONNECT, CONNACK |
| `22` | Topic Alias Maximum | U16 | CONNECT, CONNACK |
| `23` | Topic Alias | U16 | PUBLISH |
| `24` | Maximum QoS | Byte | CONNACK |
| `25` | Retain Available | Byte | CONNACK |
| `26` | User Property | UTF-8 pair | Every property-bearing packet and Will |
| `27` | Maximum Packet Size | U32 | CONNECT, CONNACK |
| `28` | Wildcard Subscription Available | Byte | CONNACK |
| `29` | Subscription Identifier Available | Byte | CONNACK |
| `2A` | Shared Subscription Available | Byte | CONNACK |

Example:

```text
no properties:          00
User Property `k`=`v`:  07 26 00 01 6B 00 01 76
```

## Failure Reason Code scope

Do not accept failure codes on packet types outside their defined scope.

```text
80 Unspecified error              CONNACK PUBACK PUBREC SUBACK UNSUBACK DISCONNECT
81 Malformed Packet               CONNACK DISCONNECT
82 Protocol Error                 CONNACK DISCONNECT
83 Implementation specific error CONNACK PUBACK PUBREC SUBACK UNSUBACK DISCONNECT
84 Unsupported Protocol Version   CONNACK
85 Client Identifier not valid    CONNACK
86 Bad User Name or Password      CONNACK
88 Server unavailable             CONNACK
89 Server busy                    CONNACK DISCONNECT
8A Banned                         CONNACK
8B Server shutting down           DISCONNECT
8D Keep Alive timeout             DISCONNECT
8F Topic Filter invalid           SUBACK UNSUBACK DISCONNECT
90 Topic Name invalid             CONNACK PUBACK PUBREC DISCONNECT
96 Message rate too high          DISCONNECT
97 Quota exceeded                 CONNACK PUBACK PUBREC SUBACK DISCONNECT
98 Administrative action         DISCONNECT
9F Connection rate exceeded       CONNACK DISCONNECT
A0 Maximum connect time           DISCONNECT
```

## MQTT over WebSocket

Send MQTT Control Packets only in WebSocket binary data frames. Close the
Network Connection after receiving another data-frame type
[MQTT-6.0.0-1] [MQTT-6.0.0-2].

Treat frame boundaries as unrelated to MQTT packet boundaries: one frame can
hold several packets, and one packet can span frames. Feed binary-frame bytes
to a streaming MQTT decoder.

The Client must offer subprotocol `mqtt`; the Server must select and return
exactly `mqtt`. The WebSocket URI has no MQTT protocol meaning
[MQTT-6.0.0-3] [MQTT-6.0.0-4].

```text
Client: Sec-WebSocket-Protocol: mqtt
Server: Sec-WebSocket-Protocol: mqtt

binary frame 1: CONNECT || first part of PUBLISH
binary frame 2: rest of PUBLISH || PINGREQ
```
