# Standards and framing

## Current standards and assignment registries

The current published Version 3 specification is RTCM 10403.4 plus Amendment 1, dated 2024-11-01. Do not treat 10403.3 as the newest edition.

RTCM maintains separate CSV assignment tables for proprietary message types (Table 3.6-1) and SSR provider IDs (DF414). Look up allocated values instead of guessing IDs or relying on stale copies.

RTCM 13500.1, published 2023-09-06, defines an interoperable radio layer for real-time DGNSS applications. It standardizes the correction-radio link so radios from different manufacturers can interoperate; it does not redefine RTCM payloads or Ntrip transport.

## Version 2 framing

An RTCM 2.x frame is a sequence of 30-bit words. Each word contains 24 data bits followed by 6 GPS-style Hamming parity bits. On ASCII-like serial links, wrap each 6-bit chunk with leading `1` and trailing `0` bits and send most-significant bit first.

```text
word 1 = preamble 01100110 [8] | message type [6] | station ID [10] | parity [6]
word 2 = z-count [13] | sequence [3] | total word count [5] | health [3] | parity [6]
```

The word count includes both header words. Health value `111` declares the station unhealthy.

## Version 2 message-set evolution

- Version 2.0: type 1 complete corrections, type 2 compact updates, type 3 reference-station location, type 6 null fill, type 16 test text, and type 59 proprietary messages.
- Version 2.1: types 18/19 RTK raw measurements, types 20/21 corrections, and alternative correction type 9.
- Version 2.2: GLONASS types 31–37.
- Version 2.3: antenna identification/description type 23 and antenna-height type 24.

## Version 2 to Version 3 migration

Version 3 is a semantic migration, not just a new envelope. Version 2 has fixed words and per-word parity; Version 3 has variable-length frames and one 24-bit CRC over the complete message. Version 2 types 18 and 19 become combined Version 3 type 1003. Version 3 types 1001/1002 are L1-only, while 1003/1004 add L2. A bridge must decode and re-encode rather than copy payload bytes.

## OEM7 RTCMV3 preset

OEM7 7.09.05 adds `RTCM1230` to the `GENERATERTKCORRECTIONS` preconfigured `RTCMV3` message sets. Expect type 1230 after this upgrade and revise explicit downstream allowlists when retaining the older set is necessary.

## Streaming binary decode with `pyrtcm`

`RTCMReader` accepts a binary stream such as a configured pyserial `Serial` instance. Iteration returns one `(raw_data, parsed_data)` pair for each RTCM message.

```python
from serial import Serial
from pyrtcm import RTCMReader

stream = Serial("/dev/ttyS10", 921600, timeout=3)
for raw_data, parsed_data in RTCMReader(stream):
    print(parsed_data)
```

Retain `raw_data` for the original frame and consume `parsed_data` for decoded fields.
