# MQTT-SN Authentication, Sleep, and Protection

## Enhanced authentication

The Client begins enhanced authentication by setting CONNECT AUTH and
providing Authentication Method plus optional Authentication Data. Use AUTH
reason `0x18` for intermediate Continue authentication packets. Report success
in CONNACK. Repeat the CONNECT Authentication Method in every AUTH packet and
in successful CONNACK [MQTT-SN-4.11.1-2] [MQTT-SN-4.11.1-3]
[MQTT-SN-4.11.1-5].

An unsupported method may receive CONNACK `0x8C` Bad authentication method or
`0x87` Not Authorized; the Server then deletes the Virtual Connection
[MQTT-SN-4.11.1-1].

If CONNECT has no Authentication Method, neither peer may send AUTH and
CONNACK must not introduce a method
[MQTT-SN-4.11.1-6] [MQTT-SN-4.11.1-7].

After connection, the Client may re-authenticate with AUTH reason `0x19` and
the original method. Pause other packet flow during MQTT-SN re-authentication.
On failure, send DISCONNECT and delete the Virtual Connection
[MQTT-SN-4.11.1.1-1] [MQTT-SN-4.11.1.1-2].

## MQTT-BASIC and MQTT-ENHANCED profiles

For one-way username/password authentication, expect CONNACK rather than AUTH:

```text
Authentication Method = "MQTT-BASIC"
Authentication Data   = u16 user_len || UTF-8 user
                      || u16 password_len || password_bytes
```

To also carry MQTT enhanced authentication, set the outer method to
`MQTT-ENHANCED` and append length-prefixed MQTT Authentication Method and
binary MQTT Authentication Data after username and password. Subsequent AUTH
and CONNACK omit username and password and retain outer Authentication Method
`MQTT-ENHANCED`.

## Client states

Use these Server-side states:

- None: no Session or Virtual Connection.
- Disconnected: Session only.
- Active: normal Virtual Connection.
- Asleep: Virtual Connection exists, but Client cannot normally receive.
- Awake: bounded receive phase.

Do not send to a Disconnected Client. Ignore its non-CONNECT packets except
PUBWOS [MQTT-SN-4.14-1] [MQTT-SN-4.14-2].

An Asleep Client may send only PINGREQ, CONNECT, or DISCONNECT. An Awake Client
may send only PUBACK, PUBREC, PUBCOMP, REGACK, CONNECT, or DISCONNECT
[MQTT-SN-4.14-3] [MQTT-SN-4.14-4].

Any CONNECT deletes and replaces the existing Virtual Connection regardless
of state [MQTT-SN-4.14-5]. The Server may send WAKEUP to hint that messages are
waiting, but the Client need not notice or act.

## Sleeping and bounded wake cycles

SLEEPREQ supplies Sleep Duration; successful SLEEPRESP enters Asleep. If the
Server receives nothing within 1.5 times that duration, delete the Virtual
Connection. While asleep, buffer QoS 1/2 Application Messages and optionally
QoS 0 [MQTT-SN-4.14.2-1] [MQTT-SN-4.14.2-2].

PINGREQ enters Awake. Send at most CONNECT Default Awake Messages, including
their full QoS exchanges. Then send PINGRESP with the exact remaining count,
or `0xFFFF` when it is unknown but positive, and return the Client to Asleep.
With no queued packets, respond immediately
[MQTT-SN-4.14.2-3] through [MQTT-SN-4.14.2-5] and [MQTT-SN-4.14.2-7].

Delete the Virtual Connection when delivery retry handling gets no response
[MQTT-SN-4.14.2-6]. An Awake Client that needs to do more than receive and
acknowledge buffered messages sends CONNECT and becomes Active.

## SLEEPREQ and SLEEPRESP packets

Require a strictly positive four-byte Sleep Duration. SLEEPREQ bit 0 chooses
whether to retain Session Topic Aliases. Successful sleep suspends Keep Alive,
starts Sleep Duration without deleting the Virtual Connection, and restarts
the timer when the Client was already Asleep
[MQTT-SN-3.15.4-1] [MQTT-SN-3.15.5-4] through [MQTT-SN-3.15.5-7].

```text
SLEEPREQ  = flags(bit 0 Retain Topic Aliases)
            | packet_id:u16 | sleep_duration:u32
SLEEPRESP = flags(bit 0 Sleep Duration present)
            | packet_id:u16 | [sleep_duration:u32] | [reason:u8]
```

The Server may replace Sleep Duration only when CONNECT allowed
server-suggested values. An absent SLEEPRESP Reason Code means success
[MQTT-SN-3.16.2.1-1] through [MQTT-SN-3.16.4-1].

## Layered transport security

Distinguish clear communication, a secured network such as a VPN, and secured
transport using MQTT-SN authentication, Protection Encapsulation, DTLS, or
another mechanism. DTLS Client authentication may supplement or replace
Client authentication through MQTT-SN Authentication Method and Data.

## End-to-end Protection Encapsulation

Sender Identifier names the originator, which performs protection itself
rather than delegating it to a Forwarder [MQTT-SN-3.17-1]. An endpoint that
handles PROTECTION must protect every MQTT-SN packet exchanged with a peer for
which it has a shared key [MQTT-SN-3.17-2] [MQTT-SN-3.17-3].

A Protected MQTT-SN Packet cannot itself be Forwarder Encapsulation. The
complete Protection envelope may be carried inside Forwarder Encapsulation
[MQTT-SN-3.17.8-1].

## Protection wire format

Sender Identifier is 8 bytes and Random is 4 bytes. Flag-selected
cryptographic material and counter fields follow. The Authentication Tag
covers every preceding envelope field.

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

Require AEAD schemes to use tag code `0x1`. Authentication-only schemes may
use permitted truncation `0x4..0xF`, taking most-significant bits first, but
must not request a tag longer than the scheme's nominal tag.

## Protection schemes and nonces

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

Provider-defined authentication-only schemes occupy `0x3C..0x3F`;
provider-defined AEAD occupies `0xF0..0xFF`. Values `0x05..0x3B` and
`0x4A..0xEF` are reserved.

For AES-CCM, derive the 13-byte nonce from the leftmost 104 bits of SHA-256
over the full envelope prefix before Protected MQTT-SN Packet. For AES-GCM and
ChaCha20/Poly1305, use the same construction truncated to the leftmost 96
bits.
