---
name: rtcm3-knowledge-patch
description: "RTCM3 protocol knowledge (latest: 2026-04-07) — frame parsing, CRC-24Q, MSM vs legacy observations, SSR phases 1-3, NTRIP v1/v2 connections. Load before working with RTCM3 or NTRIP."
version: "2026-04-07"
license: MIT
metadata:
  author: Nevaberry
---

# RTCM3 Knowledge Patch

RTCM SC-104 standard for differential GNSS corrections. Current version: **RTCM 10403.4** (December 2023). This patch covers protocol details needed to parse RTCM3 frames, handle message types, and implement NTRIP client/server connections.

**Source**: RTCM Special Committee 104 standards, IGS documentation, u-blox integration guides

## Quick Reference

| Area | What it covers | Details |
|------|----------------|---------|
| Message types | Version 3.1-3.4 message number ranges, constellation coverage | [Message Types and SSR](references/message-types.md) |
| SSR corrections | Extended SSR (1240-1270), SSR phases 1-3, PPP-RTK | [Message Types and SSR](references/message-types.md) |
| MSM vs Legacy | Resolution limits, timestamp alignment, format selection | [MSM vs Legacy](references/msm-and-legacy.md) |
| NTRIP protocol | v1/v2 client connections, base station upload, VRS | [NTRIP Protocol](references/ntrip.md) |

## Key Pragmas

- Use **MSM messages** (1071+) for all new implementations — legacy (1001-1012) only covers GPS/GLONASS.
- Use **MSM4** for RTK corrections, **MSM7** for full observables with Doppler.
- Default to **NTRIP v1** for maximum compatibility (RTKLIB and most low-cost devices only support v1).
- When parsing RTCM3, the frame starts with preamble `0xD3`, followed by 6 reserved bits, 10-bit length, the message payload, and a 24-bit CRC (CRC-24Q).
- VRS casters require sending NMEA GGA before corrections flow — always implement GGA feedback in NTRIP clients.
- Watch for the **1 ms timestamp problem**: receivers that don't align to round milliseconds can cause RTK failures. Compensate pseudorange/phase when adjusting timestamps.

## Frame Format

```
┌──────────┬──────┬──────────┬─────────────────┬──────────┐
│ Preamble │ Res. │ Length   │ Payload         │ CRC-24Q  │
│ 0xD3     │ 6b   │ 10 bits │ 0-1023 bytes    │ 3 bytes  │
│ (1 byte) │      │          │ (starts with    │          │
│          │      │          │  12-bit msg ID) │          │
└──────────┴──────┴──────────┴─────────────────┴──────────┘
```

Total overhead: 6 bytes per frame (3 header + 3 CRC). Max payload: 1023 bytes. First 12 bits of payload are always the message type number.

### Header Byte Layout

```
Byte 0:    0xD3 (preamble)
Byte 1:    00LLLLLL  (6 reserved bits = 0, upper 6 bits of length)
Byte 2:    LLLLLLLL  (lower 8 bits of length, giving 10-bit length total)
Bytes 3+:  payload (length bytes)
Last 3:    CRC-24Q
```

Length field = payload size only (excludes header and CRC).

### CRC-24Q

Polynomial: `0x1864CFB` (CRC-24 Qualcomm). Computed over bytes 0 through 2+length (header + payload). The CRC is big-endian in the stream.

```python
def crc24q(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    return crc & 0xFFFFFF
```

### Parsing a Frame from a Byte Stream

```python
def read_rtcm3_frame(stream: bytes, offset: int) -> tuple[int, bytes] | None:
    """Returns (message_type, payload) or None if no valid frame found."""
    while offset < len(stream) - 5:
        if stream[offset] != 0xD3:
            offset += 1
            continue
        # Extract 10-bit length from bytes 1-2
        length = ((stream[offset + 1] & 0x03) << 8) | stream[offset + 2]
        frame_end = offset + 3 + length + 3  # header + payload + CRC
        if frame_end > len(stream):
            return None  # incomplete frame
        frame = stream[offset:offset + 3 + length]
        crc_recv = int.from_bytes(stream[offset + 3 + length:frame_end], 'big')
        if crc24q(frame) != crc_recv:
            offset += 1
            continue
        payload = stream[offset + 3:offset + 3 + length]
        msg_type = (payload[0] << 4) | (payload[1] >> 4)
        return msg_type, payload
    return None
```

## Common Message Type Quick Look

| Msg | Description | Notes |
|-----|-------------|-------|
| 1005 | Station coordinates (ARP, no antenna height) | Minimal base position |
| 1006 | Station coordinates + antenna height | Preferred over 1005 |
| 1033 | Receiver/antenna descriptor strings | Informational |
| 1077 | GPS MSM7 (full observables) | Most common GPS message |
| 1087 | GLONASS MSM7 | Most common GLO message |
| 1097 | Galileo MSM7 | |
| 1127 | BDS MSM7 | |
| 1230 | GLONASS code-phase bias | Required for GLO ambiguity resolution |
| 1019 | GPS ephemeris | |
| 1020 | GLONASS ephemeris | |
| 1042 | BDS ephemeris | |
| 1045/1046 | Galileo F/NAV / I/NAV ephemeris | |

## SSR Phase Summary

| Phase | Components | Use case |
|-------|------------|----------|
| Phase 1 | Orbit + clock + code bias | PPP (e.g. IGS real-time service) |
| Phase 2 | + phase bias + vertical iono | PPP-RTK (requires denser networks) |
| Phase 3 | + slant iono + tropo | Full PPP-RTK |

## Legacy vs MSM Resolution

| Field | Legacy (1002/1010) | MSM (1077/1087) |
|-------|-------------------|-----------------|
| Pseudorange | 0.02 m | Higher resolution |
| Carrier phase | 0.5 mm | Higher resolution |
| Doppler | Not supported | Supported (MSM5/7) |
| Half-cycle invalid | Not supported | Supported |
| Constellations | GPS + GLONASS only | All constellations |

## NTRIP Connection (v1)

```
GET /mountPt HTTP/1.0
User-Agent: NTRIP client/1.0
Authorization: Basic dXNlcjpwYXNzd29yZA==

# Success: ICY 200 OK
# Then raw RTCM3 binary stream follows
```

Auth is Base64-encoded `user:password`. Default caster port: **2101**. For VRS, send `$GPGGA` sentences on the same connection before corrections arrive.

## Reference Index

- [Message Types and SSR](references/message-types.md) — Version 3.1-3.4 progression, message number ranges, MSM subtypes, extended SSR (1240-1270), SSR phases
- [MSM vs Legacy](references/msm-and-legacy.md) — Resolution comparison table, timestamp alignment problem, format selection guide
- [NTRIP Protocol](references/ntrip.md) — v1 vs v2 differences, client/server connection examples, VRS, base station upload
