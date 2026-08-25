# MQTT-SN Authentication and Protection

Use this reference for authentication state machines, protection envelopes,
cryptographic scheme selection, and forwarding. Related source content is in
`mqtt-sn-2.0-csd01-guidance`, `mqtt-sn-2.0-csd01-foundations`, and
`mqtt-sn-2.0-csd01`.

## Enhanced authentication

The Client begins enhanced authentication by setting CONNECT AUTH and
supplying Authentication Method plus optional Authentication Data.
Intermediate AUTH uses reason `0x18` Continue authentication. Success is
reported by CONNACK. Every AUTH and a successful CONNACK repeats the CONNECT
Authentication Method.

An unsupported method may receive CONNACK `0x8C` Bad authentication method or
`0x87` Not Authorized; the Server then deletes the Virtual Connection. Without
a CONNECT Authentication Method, neither peer sends AUTH and CONNACK does not
add a method.

After connection, the Client may re-authenticate with AUTH reason `0x19` and
the original method. Ordinary packet flow pauses. Failure requires DISCONNECT
and Virtual Connection deletion.

## Authentication payload profiles

For one-way username/password authentication:

```text
Authentication Method = "MQTT-BASIC"
Authentication Data   = u16 user_len || UTF-8 user
                      || u16 password_len || password_bytes
```

The response is CONNACK, not AUTH.

To carry MQTT enhanced authentication too, use outer method `MQTT-ENHANCED`
and append length-prefixed MQTT Authentication Method and binary MQTT
Authentication Data after username and password. Later AUTH and CONNACK omit
username/password and retain outer method `MQTT-ENHANCED`.

## Layered transport security

Security profiles distinguish clear communication, a secured network such as
a VPN, and secured transport using MQTT-SN authentication, Protection
Encapsulation, DTLS, or another mechanism. DTLS Client authentication may
supplement or replace Client authentication through MQTT-SN Authentication
Method and Data.

## End-to-end Protection Encapsulation

Sender Identifier names the originator, which performs protection itself
rather than delegating it to a Forwarder. If an endpoint supports PROTECTION
and shares a key with a peer, it protects every MQTT-SN packet exchanged with
that peer.

A Protected MQTT-SN Packet cannot itself be Forwarder Encapsulation. The
complete Protection envelope may be nested inside Forwarder Encapsulation.

## Protection wire format

Sender Identifier is eight bytes and Random is four. Flags select optional
cryptographic material, counter, and tag length:

```text
PROTECTION =
  flags:u8 | scheme:u8 | sender_id:8 | random:4
  | crypto_material:(0|2|4|12) | counter:(0|2|4)
  | protected_mqtt_sn_packet | authentication_tag

flags bits 1..0, counter: 00=0 bytes  01=2  10=4  11=reserved
flags bits 3..2, crypto:  00=0 bytes  01=2  10=4  11=12
flags bits 7..4, tag:     0=provider-defined  1=nominal
                              2..3=reserved
                              4..F=value*16 bits, auth-only
```

When present, the counter increases for every packet independent of Session
and destination. The Authentication Tag covers every preceding envelope
field. AEAD requires tag code `0x1`. Authentication-only schemes may use
allowed `0x4..0xF` truncation codes, taking most-significant bits first, but
cannot request more than the nominal tag.

## Scheme registry and nonce derivation

```text
0x00 HMAC-SHA256       any key size, 256-bit tag
0x01 HMAC-SHA3-256     any key size, 256-bit tag
0x02 CMAC-128          128-bit key, 128-bit tag
0x03 CMAC-192          192-bit key, 128-bit tag
0x04 CMAC-256          256-bit key, 128-bit tag

0x40..0x42 AES-CCM-64  128/192/256-bit key, 64-bit tag
0x43..0x45 AES-CCM-128 128/192/256-bit key, 128-bit tag
0x46..0x48 AES-GCM-128 128/192/256-bit key, 128-bit tag
0x49       ChaCha20/Poly1305, 256-bit key, 128-bit tag
```

Provider-defined authentication-only schemes are `0x3C..0x3F`; provider-defined
AEAD schemes are `0xF0..0xFF`. Ranges `0x05..0x3B` and `0x4A..0xEF` are
reserved.

For AES-CCM, SHA-256 the complete envelope prefix before Protected MQTT-SN
Packet and take the leftmost 104 bits as the 13-byte nonce. AES-GCM and
ChaCha20/Poly1305 use the same construction with the leftmost 96 bits.

## Connection and Forwarder prefixes

Connection Encapsulation is Client-only, requires CONNECT Allow Network
Address Changes, and may wrap only Client PUBLISH, SUBSCRIBE, UNSUBSCRIBE,
REGISTER, DISCONNECT, SLEEPREQ, or PINGREQ. Server use, a different inner
packet, or use without permission is a Protocol Error.

Both prefix formats have an unusual Length: it ends at Client Identifier or
Client Addressing Information. The independently framed inner packet follows
outside that Length.

```text
Connection = length_through_client_id | type | client_identifier
             | mqtt_sn_packet
Forwarder  = length_through_address_info | type | client_address_info
             | mqtt_sn_packet
```

Client Identifier binds Connection Encapsulation to an existing Virtual
Connection, but does not provide security and must not bypass connection
authorization. Forwarder addressing data is opaque to MQTT-SN; the Gateway
returns it so the Forwarder can route the response.
