---
name: rtcm3-knowledge-patch
description: RTCM 3
license: MIT
version: 10403.4 Amendment 1
metadata:
  author: Nevaberry
---

# RTCM 3 Knowledge Patch

Baseline: RTCM 3.3 MSM and SSR message conventions available by mid-2024. Covered range: mid-2024 through 2026-04-07.

## How to use this skill

1. Identify whether the task concerns framing, stream composition, message semantics, MSM, SSR conversion, Ntrip publication, or receiver ingest.
2. Apply the breaking and interoperability constraints below before choosing messages.
3. Read the matching reference file before implementing or reviewing a stream.
4. Treat receiver-specific support tables as profiles, not as universal RTCM requirements.
5. Verify allocated proprietary message types and SSR provider IDs against the maintained RTCM CSV registries.

## Reference index

| Reference | Topics |
| --- | --- |
| [standards-and-framing.md](references/standards-and-framing.md) | RTCM 10403.4, assignment registries, Version 2 framing and evolution, Version 3 migration, RTCM 13500.1, `pyrtcm` streaming |
| [stream-design-and-station.md](references/stream-design-and-station.md) | Base-stream composition, Reach profiles, legacy observations, station coordinates, descriptors, type 1013, ephemeris scheduling, type 1230 |
| [message-catalog.md](references/message-catalog.md) | OEM7 log IDs, network RTK, CRS transformations, ephemerides, Unicode text, experimental and proprietary ranges |
| [msm-observations.md](references/msm-observations.md) | MSM rollout, numbering, signal design, precision tiers, mixed rates, Onocoy ingest |
| [ssr-and-conversion.md](references/ssr-and-conversion.md) | SSR groups, RTKLIB PPP, lossy legacy conversion, epoch adjustment, SSL-to-TCP bridging |
| [ntrip-and-igs.md](references/ntrip-and-igs.md) | IGS publication, mountpoint names, broadcaster topology, sourcetable layouts and integrity |
| [receiver-compatibility.md](references/receiver-compatibility.md) | Waypoint, Qinertia, and Septentrio RTCM ingest profiles |

## Breaking changes and interoperability constraints

### Use the maintained standard and registries

- Treat RTCM 10403.4 plus Amendment 1 dated 2024-11-01 as the current published Version 3 specification, not 10403.3.
- Obtain proprietary message allocations from the maintained Table 3.6-1 CSV and SSR provider IDs from the maintained DF414 CSV. Do not guess or reuse stale IDs.
- Keep types 1–100 experimental and temporary. Treat 4001–4095 as assignee-defined proprietary payloads, not generic formats.

### Decode and re-encode between Version 2 and Version 3

- Do not pass Version 2 payloads through a Version 3 envelope.
- Version 2 uses fixed 30-bit words with per-word parity; Version 3 uses variable-length frames with one 24-bit CRC.
- Account for the semantic regrouping: Version 2 types 18 and 19 are combined in Version 3 type 1003; types 1001/1002 are L1-only, while 1003/1004 add L2.

### Keep legacy and MSM observations on separate streams

- Include at least one observation message plus station or antenna information in an RTK base stream.
- Do not mix legacy observations `1001`–`1004` or `1009`–`1012` with MSM observations in one stream; some rovers fail on the mixture.
- Publish separate mountpoints when both legacy and MSM receiver populations must be served.
- Within an MSM stream, send one tier per constellation. Simultaneous MSM4 and MSM7 wastes bandwidth and may cause the lower-quality tier to be discarded.

### Recheck OEM7 presets and identifiers

- OEM7 7.09.05 adds `RTCM1230` to the `GENERATERTKCORRECTIONS` `RTCMV3` preset. Update downstream allowlists if they assumed the older set.
- Do not confuse an OEM7 catalog `Message ID` with the RTCM message number; use the log name and RTCM-type column.
- OEM7 always writes zero for the type 1006 antenna-height field. Configure phase-center offsets with `THISANTENNAPCO` or `THISANTENNATYPE` when needed.

### Match SSR reference points

- Combine receiver observations, SSR corrections, and navigation data for post-processing.
- Select `brdc+ssrapc` when SSR orbit corrections refer to the satellite antenna phase center; select Broadcast+SSR CoM for center-of-mass corrections.
- Never interchange the two reference points: doing so misapplies the orbit correction.
- Classic RTKLIB PPP does not resolve ambiguities; ambiguity-resolution settings have no effect.
- Enable `DBCorr`, or `pos1-posopt6` in a configuration file, for SSR PPP day-boundary anomalies.

### Shift observables when rounding epochs

- RTCM epoch resolution is 1 ms. Do not round an off-grid receiver epoch without changing its observations.
- Shift the time tag, pseudorange, and carrier phase consistently or RTKLIB may fail to fix.
- Do not assume classic RTKLIB `-TADJ` handles u-blox `RXM-RAWX`; its path covered `RXM-RAW`.
- Do not substitute `TRK_MEAS` blindly: its round timestamps avoid this issue, but its measurements lack GLONASS inter-channel frequency-delay compensation.

## Common stream profiles

### Reach base to Reach rover

Use station coordinates at low rate, one-second MSM4 observations for supported constellations, and GLONASS code-phase biases:

```text
1006  0.1 Hz  antenna-reference-point coordinates
1074  1 Hz    GPS MSM4; keep at least this MSM enabled
1084  1 Hz    GLONASS MSM4
1094  1 Hz    Galileo MSM4
1124  1 Hz    BeiDou MSM4
1230  1 Hz    GLONASS code-phase biases
```

### Reach base to a legacy rover

Use legacy extended GPS and GLONASS observations plus antenna and receiver identification:

```text
1004  1 Hz    extended L1/L2 GPS observables
1008  0.1 Hz  antenna descriptor and serial number
1012  1 Hz    extended L1/L2 GLONASS observables
1033  0.1 Hz  receiver and antenna descriptors
```

### IGS real-time station

- Sustain 1 Hz observations with less than two seconds of latency.
- Publish over Ntrip to two broadcasters when possible; otherwise choose the nearest Global or Regional Broadcaster.
- Record whether the stream is receiver-native or produced by external software.
- Use the ten-character `SSSSMRCCCF` station mountpoint convention; final digit `0` denotes the most complete RTCM 3 stream, for example `POTS00DEU0`.

## Observation and station selection

### Choose the MSM family

The first three digits select the constellation and the final digit selects MSM1–MSM7:

```text
1071–1077  GPS       1081–1087  GLONASS
1091–1097  Galileo   1101–1107  SBAS
1111–1117  QZSS      1121–1127  BeiDou
1131–1137  IRNSS
```

- RTCM 3.2 introduced GPS, GLONASS, Galileo, QZSS, and BeiDou MSM plus type 1230; RTCM 3.3 added SBAS MSM.
- Use MSM for multiple signals and additional bands beyond the legacy L1/L2, one-signal-per-band design.
- MSM1–MSM5 use standard precision. MSM6 and MSM7 are higher-resolution counterparts of MSM4 and MSM5.
- MSM2 is phase-only. On constrained links, send it frequently and interleave MSM3 for pseudorange or MSM4 for pseudorange plus carrier-to-noise refreshes.
- Only MSM5 and MSM7 include Doppler; MSM4 and MSM6 omit it.

### Represent the station correctly

- Type 1005 contains the antenna reference point in ECEF, not the phase center; its datum field is undefined.
- Type 1006 adds antenna height. Type 1032 identifies the physical reference-station antenna position.
- Type 1033 includes receiver type, firmware, and antenna information, enabling phase-bias calibration and better GLONASS ambiguity fixing.
- OEM7 recommends 1006 plus 1033, fills 1033 automatically, and always leaves the 1008 antenna-serial field null.
- Type 1230 is receiver-dependent. Keep it by default; omit it on constrained links only for tested receiver combinations that interpret missing biases as zero.

### Schedule ephemerides deliberately

- Use `1019` GPS, `1020` GLONASS, `1042` BeiDou, `1044` QZSS, `1045` Galileo F/NAV, and `1046` Galileo I/NAV.
- Ordinary RTK can use satellite-broadcast ephemerides; a separate stream such as `RTCM3EPH` can shorten startup.
- On OEM7, non-`ASYNC` `ONTIME` logs emit one satellite per interval in numeric cycles; matching `ASYNC` `ONCHANGED` logs emit new or changed ephemerides immediately.

## Parsing and transport checks

### Decode a binary stream with `pyrtcm`

```python
from serial import Serial
from pyrtcm import RTCMReader

stream = Serial("/dev/ttyS10", 921600, timeout=3)
for raw_data, parsed_data in RTCMReader(stream):
    print(parsed_data)
```

Preserve `raw_data` when exact frame bytes matter; use `parsed_data` for field-level processing.

### Advertise Ntrip streams exactly

- Use the ordered semicolon-separated CAS, NET, and STR fields in [ntrip-and-igs.md](references/ntrip-and-igs.md).
- Make an STR record's `format-details` exactly match its message types and update periods; `1004(1),1005(10)` means one second and ten seconds respectively.
- Provide a matching NET record for every STR network and leave no fields empty in an IGS sourcetable.
- Set `nmea=1` only when a client must send approximate position, and distinguish the different meaning of the CAS NMEA flag.

### Bridge SSL-only Ntrip for RTKLIB

Use BKG BNC to fetch the SSL caster and republish raw RTCM 3 on a local TCP port. Point RTKNAVI's correction input at a TCP server on `localhost:<port>` and inspect `RTCM SSR/(3) Corrections`.

## Receiver-specific gates

- Onocoy accepts MSM4 and higher but ignores MSM1–MSM3 and all SBAS MSM, including 1104 and 1107. Prefer one MSM7 set per supported constellation, with MSM4 as fallback.
- Waypoint requires one applicable legacy observation from 1002/1004 or 1010/1012, requires 1013 for GPS week recovery, and accepts MSM4–MSM7 for GPS, GLONASS, Galileo, QZSS, and BeiDou.
- Qinertia lists MSM4, MSM5, and MSM7—but not MSM6—for those five constellations, with ephemerides 1019, 1020, 1045, and 1046.
- Septentrio lists every MSM1–MSM7 subtype for GPS, GLONASS, Galileo, SBAS, QZSS, and BeiDou, along with legacy station/observation messages and type 1230.
- Read [receiver-compatibility.md](references/receiver-compatibility.md) before assuming a format accepted by one product is portable to another.
