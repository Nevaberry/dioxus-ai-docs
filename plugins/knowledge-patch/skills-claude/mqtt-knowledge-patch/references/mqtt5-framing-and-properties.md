# MQTT 5 Framing and Properties

Use this reference when implementing MQTT 5 Variable Byte Integers, property
sets, connection defaults, and failure-code validation.

## Canonical Variable Byte Integers

Remaining Length, Property Length, Property Identifiers, and Subscription
Identifiers use base-128 Variable Byte Integers. The low seven-bit group comes
first and bit seven indicates continuation. The range is `0..268435455` in at
most four bytes.

Encoding must use the fewest bytes. Thus `128` is `80 01`; `80 00` is illegal.

```text
00..7F             0..127
80 01..FF 7F       128..16,383
80 80 01..FF FF 7F 16,384..2,097,151
80 80 80 01..FF FF FF 7F
                    2,097,152..268,435,455
```

## Property set encoding

A set is `property_length:VBI` followed by zero or more
`property_id:VBI | typed_value` entries. Encode an empty set as Property Length
zero. Identifier ordering has no significance. An identifier illegal for its
packet or a wrongly typed value makes the packet Malformed. MQTT 5 identifiers
fit in one byte but remain VBI fields.

```text
Hex  Property                          Type       Legal packet / set
01   Payload Format Indicator          Byte       PUBLISH, Will
02   Message Expiry Interval           U32        PUBLISH, Will
03   Content Type                      UTF-8      PUBLISH, Will
08   Response Topic                    UTF-8      PUBLISH, Will
09   Correlation Data                  Binary     PUBLISH, Will
0B   Subscription Identifier           VBI        PUBLISH, SUBSCRIBE
11   Session Expiry Interval           U32        CONNECT, CONNACK, DISCONNECT
12   Assigned Client Identifier        UTF-8      CONNACK
13   Server Keep Alive                 U16        CONNACK
15   Authentication Method             UTF-8      CONNECT, CONNACK, AUTH
16   Authentication Data               Binary     CONNECT, CONNACK, AUTH
17   Request Problem Information       Byte       CONNECT
18   Will Delay Interval               U32        Will
19   Request Response Information      Byte       CONNECT
1A   Response Information              UTF-8      CONNACK
1C   Server Reference                  UTF-8      CONNACK, DISCONNECT
1F   Reason String                     UTF-8      CONNACK, PUBACK, PUBREC,
                                                  PUBREL, PUBCOMP, SUBACK,
                                                  UNSUBACK, DISCONNECT, AUTH
21   Receive Maximum                   U16        CONNECT, CONNACK
22   Topic Alias Maximum               U16        CONNECT, CONNACK
23   Topic Alias                       U16        PUBLISH
24   Maximum QoS                       Byte       CONNACK
25   Retain Available                  Byte       CONNACK
26   User Property                     UTF-8 pair every property packet, Will
27   Maximum Packet Size               U32        CONNECT, CONNACK
28   Wildcard Subscription Available   Byte       CONNACK
29   Subscription Identifier Available Byte       CONNACK
2A   Shared Subscription Available     Byte       CONNACK
```

Examples:

```text
no properties:         00
User Property k=v:     07 26 00 01 6B 00 01 76
```

## Omission defaults

Defaults differ by property:

```text
CONNECT absent:
  Session Expiry=0
  Receive Maximum=65535
  Topic Alias Maximum=0
  no additional Maximum Packet Size
  Request Response Information=0
  Request Problem Information=1

CONNACK absent:
  Session Expiry=CONNECT value
  Receive Maximum=65535
  Maximum QoS=2
  Topic Alias Maximum=0
  no additional Maximum Packet Size
  Retain Available=1
  Wildcard Subscription Available=1
  Subscription Identifier Available=1
  Shared Subscription Available=1
  Server Keep Alive=CONNECT Keep Alive
```

## Failure Reason Code scopes

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

Validate the receiving packet's allowed set; a known numeric value is not
automatically legal everywhere.
