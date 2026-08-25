# MQTT-SN Packet Contracts

This reference carries the packet and foundation details from
`mqtt-sn-2.0-csd01-foundations` and `mqtt-sn-2.0-csd01`.

## Migration from MQTT-SN 1.2

MQTT-SN 2.0 replaces Topic Id, Message Id, and Message Type with Topic Alias,
Packet Identifier, and Packet Type. It carries Will data in CONNECT instead of
using the Will Message control-packet exchange, removes Short Topic Name from
ordinary publishing, and gives DISCONNECT no response.

## Length and primitive encoding

Every packet begins with total Length and a one-byte Packet Type. Length
includes its own bytes.

```text
short:    total_length:u8 | packet_type:u8 | variable_part
extended: 0x01 | total_length:u16be | packet_type:u8 | variable_part
```

The extended form supports total lengths through 65,535. Accept either form,
even though the short form is more efficient through 255
[MQTT-SN-2.1.2-1]. MQTT-SN has no fragmentation or reassembly; the underlying
network's maximum packet size is the effective limit. Encode all Two Byte and
Four Byte Integers as unsigned big-endian.

## Packet Type registry

Use this MQTT-SN 2.0 CSD01 registry:

```text
0x01 CONNECT       0x02 CONNACK       0x03 PUBLISH
0x04 PUBACK        0x05 PUBREC        0x06 PUBREL
0x07 PUBCOMP       0x08 SUBSCRIBE     0x09 SUBACK
0x0A UNSUBSCRIBE   0x0B UNSUBACK      0x0C PINGREQ
0x0D PINGRESP      0x0E DISCONNECT    0x0F AUTH
0x10 REGISTER      0x11 REGACK        0x12 PUBWOS
0x13 SLEEPREQ      0x14 SLEEPRESP     0x15 WAKEUP
0x16 ADVERTISE     0x17 SEARCHGW      0x18 GWINFO
0xFD Forwarder Encapsulation
0xFE Session Encapsulation
0xFF Protection Encapsulation
```

Forbid reserved values `0x00` and `0x19..0xFC`. Session Encapsulation is a
Client-to-Server envelope carrying session identification.

## Packet Identifier matrix

```text
required:    CONNECT CONNACK AUTH
             PUBACK PUBREC PUBREL PUBCOMP
             REGISTER REGACK SUBSCRIBE SUBACK UNSUBSCRIBE UNSUBACK
             PINGREQ PINGRESP SLEEPREQ SLEEPRESP
conditional: PUBLISH only when QoS > 0
optional:    DISCONNECT
absent:      ADVERTISE SEARCHGW GWINFO PUBWOS WAKEUP
             Forwarder Encapsulation Protection Encapsulation
```

QoS 0 PUBLISH must omit Packet Identifier. A new Client-generated identifier
must be nonzero and unused; the same holds for a new Server QoS 1/2 PUBLISH
[MQTT-SN-2.2-1] [MQTT-SN-2.2-2] [MQTT-SN-2.2-3].

PUBLISH, SUBSCRIBE, and UNSUBSCRIBE share one identifier set per sending peer.
Client and Server allocate independently and may concurrently use the same
numeric value. Echo the initiator's identifier in publish-flow
acknowledgments, SUBACK, and UNSUBACK.

Allow reuse after:

- PUBACK for QoS 1;
- PUBCOMP or a failing PUBREC for QoS 2;
- SUBACK or UNSUBACK for the corresponding request [MQTT-SN-2.2-4].

## Topic Type bits

```text
0b00  Session Topic Alias
0b01  Predefined Topic Alias
0b10  reserved
0b11  Topic Name or Topic Filter
```

## UTF-8 validation

Require well-formed UTF-8. Reject surrogate code points and U+0000 as
Malformed [MQTT-SN-1.7.4-1] [MQTT-SN-1.7.4-2]. C0/C1 controls other than
U+0000 and Unicode noncharacters are discouraged rather than absolutely
forbidden, so receivers may differ. Always interpret bytes `EF BB BF` as
U+FEFF; never strip them [MQTT-SN-1.7.4-3].

Avoid a permissive-publisher/strict-subscriber disconnect loop by either
rejecting discouraged strings at the Server or making subscribers discard or
tolerate them without deleting their Virtual Connection.

## MQTT-SN-specific Reason Codes

Treat Reason Codes as packet-scoped.

```text
0x04 Disconnect with will message   Client DISCONNECT
0x10 No matching subscribers        PUBACK, PUBREC; publication accepted
0x11 No subscription existed        UNSUBACK
0x1A Topic Alias Exists             REGACK
0x91 Packet identifier in use       PUBACK, PUBREC, SUBACK, UNSUBACK,
                                    REGACK, PINGRESP, SLEEPRESP
0x92 Packet identifier not found    PUBREL, PUBCOMP; recovery, not error

0xE6 Only PROTECTION supported      any packet except Protection or
                                    Forwarder Encapsulation
0xE7 Protection scheme invalid      DISCONNECT
0xE8 Unknown Sender Id              DISCONNECT
0xF0 Unknown Topic Alias            PUBACK, PUBREC, SUBACK, UNSUBACK, REGACK
0xF1 Congestion                     SUBACK, REGACK, CONNACK, PUBACK, PUBREC
0xF2 Protection packet unsupported  DISCONNECT
0xF3 Forwarder Encapsulation
     unsupported                    DISCONNECT
0xF4 No Virtual Connection exists   DISCONNECT
0xF5..0xFF                          reserved for MQTT-SN
```

For Transparent Gateways, also scope:

- `0x94` Topic alias invalid to Server DISCONNECT;
- `0x99` Payload format invalid to PUBACK, PUBREC, or Server DISCONNECT;
- `0x9A` Retain not supported and `0x9B` QoS not supported to CONNACK or
  Server DISCONNECT;
- `0x9E`, `0xA1`, and `0xA2` to unsupported shared,
  subscription-identifier, and wildcard subscriptions through SUBACK or
  Server DISCONNECT.

The CSD01 Maximum connect time registry entry pairs decimal `160` with
hexadecimal `0xAD`; preserve awareness of that internal inconsistency instead
of assuming those values are equivalent.

## CONNECT

Use protocol version `0x02`. Require reserved flags to be zero
[MQTT-SN-3.1.2-1]. A Server must support a present Client Identifier of 1–23
UTF-8 bytes when it contains only ASCII letters and digits
[MQTT-SN-3.1.18-3].

```text
Connect Flags:
bit 0 Clean Start          bit 4 Default Awake Messages present
bit 1 Will present         bit 5 Allow Network Address Changes
bit 2 Authentication      bit 6 Allow Server Suggested Values
bit 3 Session Expiry      bit 7 reserved

CONNECT =
  flags:u8 | [will_flags:u8] | packet_id:u16 | 0x02:u8
  | keep_alive:u16 | maximum_packet_size:u16
  | [default_awake_messages:u8] | [session_expiry:u32]
  | [will_topic_alias_or_name_length:u16 | will_topic_name?
     | will_payload_length:u16 | will_payload]
  | [auth_method_length:u8 | auth_method
     | auth_data_length:u16 | auth_data]
  | [client_identifier]

Will Flags:
bits 1..0 Topic Type | bits 3..2 Will QoS | bit 4 Will Retain
```

Will QoS `0b11` is Malformed. Every presence flag must match its field.
Authentication Method and Authentication Data must both be present when
Authentication is set [MQTT-SN-3.1.2.2-1] through [MQTT-SN-3.1.2.5-2].

## Keep Alive and Maximum Packet Size

Keep Alive is mandatory in `1..65535` seconds; `0` is a Protocol Error. An
otherwise-idle Client sends PINGREQ. The Server deletes the Virtual Connection
after 1.5 times the negotiated interval without receiving a packet. A Client
that exhausts PINGREQ retries deletes its Virtual Connection by DISCONNECT
[MQTT-SN-3.1.6-1] through [MQTT-SN-3.1.6-4].

Maximum Packet Size is `0` for no added limit or at least `10`. The Server must
not exceed it. A Client receiving an oversized packet uses DISCONNECT `0x95`.
If an Application Message cannot fit, the Server discards it and acts as
though sending completed [MQTT-SN-3.1.7-1] through [MQTT-SN-3.1.7-3].

## Will lifecycle and takeover

Store CONNECT Will data in Session State. Publish it after Virtual Connection
deletion or Session end unless Client DISCONNECT reason `0x00` first deletes
it. Remove the Will after publication or that normal disconnection
[MQTT-SN-3.1.2.2-2] through [MQTT-SN-3.1.2.2-4].

On successful CONNECT with an already-connected Client Identifier, send the
old Client DISCONNECT `0x8E`, delete the old Virtual Connection, and publish
its Will if present [MQTT-SN-3.1.19-3].

## CONNACK reconciliation and suggested values

CONNECT bit 6 authorizes the Server, as one group, to override Keep Alive and
Session Expiry in CONNACK and Sleep Duration in SLEEPRESP. If clear, forbid all
three response overrides. If an override is present, the Client uses it;
otherwise the Server uses the Client's requested value
[MQTT-SN-3.1.2.7-1] through [MQTT-SN-3.16.3-2].

```text
CONNACK flags:
bit 0 Session Present       bit 2 Server Keep Alive present
bit 1 Session Expiry present
bit 3 Authentication fields present
```

If Session Present is `1` but the Client has no Session State, the Client
deletes the Virtual Connection. If it is `0` but the Client has Session State,
the Client discards that state if it continues. A nonzero CONNACK reason
requires Session Present `0` [MQTT-SN-3.2.2.1-3] through
[MQTT-SN-3.2.2.1-5].

## Directional REGISTER and REGACK

Topic Alias ownership makes these forms asymmetric:

```text
Client REGISTER = flags(alias_present=0) | packet_id | topic_name
Server REGISTER = flags(alias_present=1) | packet_id | alias | topic_name
Server REGACK   = flags(topic_type, alias_present)
                  | packet_id | [alias] | reason
Client REGACK   = flags(topic_type, alias_present=0)
                  | packet_id | reason
```

A successful Server REGACK returns an alias for Client REGISTER. Client REGACK
omits it. Limit REGACK Topic Type to Session or Predefined Topic Alias
[MQTT-SN-3.4-1] [MQTT-SN-3.4-2] [MQTT-SN-3.5.2.1-1]
[MQTT-SN-3.5.4-1].

## Compact publish forms

```text
PUBWOS        = flags | topic_datum:u16 | [topic_name] | payload
PUBLISH QoS 0 = flags | topic_datum:u16 | [topic_name] | payload
PUBLISH QoS 1/2
               = flags | packet_id:u16 | topic_datum:u16
                 | [topic_name] | payload

flags: bits 1..0 Topic Type | bit 4 RETAIN
       bits 6..5 QoS (PUBLISH)
       bit 7 DUP (defined for retransmitted QoS 2)
```

PUBWOS and QoS 0 PUBLISH omit Packet Identifier. QoS 1/2 inserts it before the
two-byte topic datum. The datum is an alias or a Topic Name byte length,
followed by the UTF-8 name only for the latter
[MQTT-SN-3.6.1.4-1] through [MQTT-SN-3.6.3.5-2].

PUBWOS allows only Topic Name or Predefined Topic Alias. PUBLISH also permits
Session Topic Alias. Bit 7 is reserved for QoS 0; QoS `0b11` is reserved.

When one message matches multiple subscriptions for one Client, deliver at the
maximum QoS across all matches. The Server may additionally send one copy per
further match at that subscription's QoS [MQTT-SN-3.6.3.7-2].

## SUBSCRIBE and replacement

```text
bit 7      No Local
bits 6..5  Maximum QoS
bit 4      Retain As Published
bits 3..2  Retain Handling
bits 1..0  Topic Type

SUBSCRIBE = flags | packet_id:u16
            | (topic_alias:u16 | topic_filter:utf8-to-packet-end)
```

Treat Retain Handling `0b11` and Maximum QoS `0b11` as Protocol Errors. No
Local blocks forwarding to a Virtual Connection whose Client Identifier
equals the publishing Virtual Connection's identifier
[MQTT-SN-3.7.2.5-1].

An identical Topic Filter replaces the Subscription and may change options.
Retain Handling `0` sends matching retained messages again. Replacement must
not lose Application Messages [MQTT-SN-3.7.6-3] [MQTT-SN-3.7.6-4].

## UNSUBSCRIBE drain

Expand an alias before comparing the Topic Filter character-for-character.
Then stop adding new matching messages, finish started QoS 1/2 deliveries, and
optionally continue already-buffered matches. Always send UNSUBACK, even if no
Subscription existed [MQTT-SN-3.9.6-1] through [MQTT-3.9.6-6].

## DISCONNECT

```text
flags: bit 0 Packet Identifier present
       bit 1 Session Expiry present
       bit 2 Reason Code present

DISCONNECT = flags | [packet_id:u16] | [reason:u8]
             | [session_expiry:u32] | [reason_string:utf8]
```

The Reason String has no presence flag; infer it from packet length. An absent
Reason Code means `0x00`. A Server must not send Session Expiry in DISCONNECT,
and a Client whose CONNECT expiry was zero cannot change it to nonzero
[MQTT-SN-3.13.5-1].

After sending DISCONNECT, send nothing else and delete the Virtual Connection.
A receiver also sends nothing further and should delete it
[MQTT-SN-3.13.7-1] [MQTT-SN-3.13.7-2] [MQTT-SN-3.13.7-4].

## Connection and Forwarder Encapsulation

Connection Encapsulation is Client-only, requires CONNECT Allow Network
Address Changes, and may wrap only Client PUBLISH, SUBSCRIBE, UNSUBSCRIBE,
REGISTER, DISCONNECT, SLEEPREQ, or PINGREQ. Server use, another inner packet,
or missing permission is a Protocol Error [MQTT-SN-3.18-1] through
[MQTT-SN-3.18-3].

Both envelopes use an unusual prefix length. Outer Length ends at Client
Identifier or Client Addressing Information; the self-framed inner packet
follows outside that length.

```text
Connection = length_through_client_id | type | client_identifier
             | mqtt_sn_packet
Forwarder  = length_through_address_info | type | client_address_info
             | mqtt_sn_packet
```

Client Identifier binds Connection Encapsulation to an existing Virtual
Connection, but this mechanism is insecure and must not bypass connection
security. Forwarder addressing is opaque to MQTT-SN; the Gateway returns it so
the Forwarder can route a response.
