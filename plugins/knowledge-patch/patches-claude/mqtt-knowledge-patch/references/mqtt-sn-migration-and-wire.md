# MQTT-SN Migration and Wire Format

Use this reference for MQTT-SN encoders, decoders, packet validation, and
migration from MQTT-SN 1.2. Source batch attributions:
`mqtt-sn-2.0-csd01-foundations` and `mqtt-sn-2.0-csd01`.

## MQTT-SN 1.2 migration

The newer terminology is Topic Alias, Packet Identifier, and Packet Type, in
place of Topic Id, Message Id, and Message Type. Will data moves into CONNECT,
the Will control-packet exchange is removed, Short Topic Name is removed from
ordinary publishing, and DISCONNECT never receives a response.

An implementation may accept the legacy MQTT-SN 1.2 QoS −1 PUBLISH from
either Clients or Servers as a PUBWOS equivalent. It needs neither Session nor
Virtual Connection, is handled as QoS 0, has `DUP=0`, and retains normal
RETAIN behavior:

```text
QoS bits       = 0b11
Topic Type     = 0b00 full Topic Name
               | 0b01 Predefined Topic Alias
               | 0b10 two-byte Short Topic Name
full name data = u16 name_length || UTF-8 name
reserved flag bits = 0
```

## Packet framing and primitive encoding

Every packet begins with total Length and a one-byte Packet Type. Length
includes its own bytes:

```text
short:    total_length:u8 | packet_type:u8 | variable_part
extended: 0x01 | total_length:u16be | packet_type:u8 | variable_part
```

Both forms must be accepted. Extended Length reaches 65,535; short Length is
more efficient through 255. Two Byte and Four Byte Integers are unsigned
big-endian. MQTT-SN supplies no fragmentation or reassembly, so the underlying
network's packet limit is effective.

The CSD01 Packet Type registry is:

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

Types `0x00` and `0x19..0xFC` are reserved and forbidden. Session Encapsulation
is a Client-to-Server envelope that adds Session identification.

## Packet Identifiers

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

A QoS 0 PUBLISH omits the field. Newly allocated Client identifiers and new
Server QoS 1/2 PUBLISH identifiers are nonzero and unused. PUBLISH, SUBSCRIBE,
and UNSUBSCRIBE share one identifier set per sender; the peers allocate
independently and may use the same number concurrently.

Reuse is allowed after PUBACK for QoS 1; PUBCOMP or a failure PUBREC for QoS 2;
and SUBACK or UNSUBACK for their requests. Flow acknowledgments and
SUBACK/UNSUBACK echo the initiating identifier.

## Topic encoding and UTF-8

Topic Type has this exact two-bit mapping:

```text
0b00 Session Topic Alias
0b01 Predefined Topic Alias
0b10 reserved
0b11 Topic Name or Topic Filter
```

All UTF-8 fields must be well formed and must not encode surrogate code points
or U+0000. Either violation makes the packet Malformed. Other C0/C1 controls
and Unicode noncharacters are discouraged but may be accepted. Bytes
`EF BB BF` mean U+FEFF and must not be stripped. Because peers may differ on
the discouraged characters, reject them consistently at the Server or make
subscribers tolerate/discard them without repeatedly dropping connections.

## CONNECT wire contract

CONNECT uses protocol version `0x02`. Reserved flags are zero. A Server must
support present Client Identifiers of 1–23 UTF-8 bytes when they contain only
ASCII letters and digits.

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

Will QoS `0b11` is malformed. Every presence flag must agree with its field;
when Authentication is set, both Authentication Method and Data are present.

Keep Alive is mandatory in `1..65535` seconds; zero is a Protocol Error. An
idle Client sends PINGREQ. After 1.5 times the negotiated interval without a
packet, the Server deletes the Virtual Connection. A Client that exhausts
PINGREQ retries deletes its connection through DISCONNECT.

Maximum Packet Size is zero for no added limit or at least 10. A Server never
sends a larger packet. A Client receiving one uses DISCONNECT `0x95`. If an
Application Message cannot fit, the Server discards it and proceeds as though
that delivery completed.

## Will, takeover, and CONNACK

The CONNECT Will is Session State and is published when the Virtual Connection
is deleted or the Session ends. Client DISCONNECT reason `0x00` first deletes
it. The Server removes the Will after publication or normal disconnection.

If a successful CONNECT takes over a connected Client Identifier, the Server
sends the old Client DISCONNECT `0x8E`, deletes the old Virtual Connection, and
publishes its Will.

CONNECT bit 6 authorizes Server overrides as one group: Keep Alive and Session
Expiry in CONNACK, and Sleep Duration in SLEEPRESP. If clear, all override
fields are forbidden. A present override controls both peers; an absent one
leaves the Client request in effect.

```text
CONNACK flags:
bit 0 Session Present       bit 2 Server Keep Alive present
bit 1 Session Expiry present
bit 3 Authentication fields present
```

Session Present `1` when the Client has no Session State requires connection
deletion. Session Present `0` when the Client has state requires discarding
that state if it continues. A nonzero CONNACK reason requires Session Present
zero.

## REGISTER and REGACK

Alias ownership makes the forms directional:

```text
Client REGISTER = flags(alias_present=0) | packet_id | topic_name
Server REGISTER = flags(alias_present=1) | packet_id | alias | topic_name
Server REGACK   = flags(topic_type, alias_present)
                  | packet_id | [alias] | reason
Client REGACK   = flags(topic_type, alias_present=0)
                  | packet_id | reason
```

A successful Server REGACK returns the alias for a Client request. Client
REGACK omits it. REGACK Topic Type is limited to Session or Predefined Alias.

## Publish packet forms

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

The topic datum is an alias or a Topic Name byte length; the name follows only
for the latter. PUBWOS permits Topic Name or Predefined Alias. PUBLISH also
permits Session Alias. Bit 7 is reserved for QoS 0, and QoS `0b11` is reserved.

When one message matches multiple subscriptions in a Session, deliver at the
maximum QoS across all matches. The Server may additionally send one copy for
each further match at that subscription's QoS.

## SUBSCRIBE, UNSUBSCRIBE, and DISCONNECT

```text
SUBSCRIBE flags:
bit 7 No Local | bits 6..5 Maximum QoS
bit 4 Retain As Published | bits 3..2 Retain Handling
bits 1..0 Topic Type

SUBSCRIBE = flags | packet_id:u16
            | (topic_alias:u16 | topic_filter:utf8-to-packet-end)
```

Retain Handling `0b11` and Maximum QoS `0b11` are Protocol Errors. No Local
blocks forwarding from a Virtual Connection with the same Client Identifier.
An identical filter replaces options rather than adding a subscription.
Retain Handling zero resends matching retained messages, but replacement
cannot lose queued Application Messages.

UNSUBSCRIBE expands aliases before character-for-character comparison. It
stops adding new matches, finishes started QoS 1/2 deliveries, may deliver
already buffered matches, and sends UNSUBACK even if no subscription existed.

```text
DISCONNECT flags:
bit 0 Packet Identifier present
bit 1 Session Expiry present
bit 2 Reason Code present

DISCONNECT = flags | [packet_id:u16] | [reason:u8]
             | [session_expiry:u32] | [reason_string:utf8]
```

Reason String is inferred from packet length; an absent reason is `0x00`.
Server DISCONNECT cannot include Session Expiry. A Client whose CONNECT expiry
was zero cannot change it to nonzero here. After sending or receiving
DISCONNECT, send nothing further. The sender must delete the Virtual
Connection; the receiver should delete it.

## Sleep packet forms

SLEEPREQ duration is a strictly positive `u32`; flag bit zero requests
retention of Session Topic Aliases:

```text
SLEEPREQ  = flags | packet_id:u16 | sleep_duration:u32
SLEEPRESP = flags(bit 0 Sleep Duration present)
            | packet_id:u16 | [sleep_duration:u32] | [reason:u8]
```

Successful SLEEPREQ suspends Keep Alive and starts, or restarts, sleep timing
without deleting the Virtual Connection. A replacement duration is legal only
when CONNECT allowed Server-suggested values. Absent SLEEPRESP Reason Code
means success.

## Packet-scoped Reason Codes

Reason Codes are not interchangeable:

```text
04 Disconnect with will message  Client DISCONNECT
10 No matching subscribers       PUBACK, PUBREC; accepted
11 No subscription existed       UNSUBACK
1A Topic Alias Exists            REGACK
91 Packet identifier in use      PUBACK/PUBREC/SUBACK/UNSUBACK/REGACK/
                                 PINGRESP/SLEEPRESP
92 Packet identifier not found   PUBREL, PUBCOMP; recovery, not error
E6 Only PROTECTION supported     except Protection/Forwarder Encapsulation
E7 Protection scheme invalid     DISCONNECT
E8 Unknown Sender Id             DISCONNECT
F0 Unknown Topic Alias           PUBACK/PUBREC/SUBACK/UNSUBACK/REGACK
F1 Congestion                    SUBACK/REGACK/CONNACK/PUBACK/PUBREC
F2 Protection unsupported       DISCONNECT
F3 Forwarder unsupported        DISCONNECT
F4 No Virtual Connection        DISCONNECT
F5..FF                          reserved for MQTT-SN
```

Transparent Gateways additionally scope `0x94` Topic alias invalid to Server
DISCONNECT; `0x99` Payload format invalid to PUBACK, PUBREC, or Server
DISCONNECT; `0x9A` Retain not supported and `0x9B` QoS not supported to
CONNACK or Server DISCONNECT; and `0x9E`, `0xA1`, and `0xA2` to unsupported
shared, identifier, and wildcard subscriptions through SUBACK or Server
DISCONNECT.

The CSD01 Maximum connect time registry entry is internally inconsistent:
decimal `160` does not equal hexadecimal `0xAD`. Do not silently treat those
representations as the same value.
