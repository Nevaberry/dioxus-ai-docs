---
name: nmea0183-knowledge-patch
description: NMEA 0183
license: MIT
version: "4.30"
metadata:
  author: Nevaberry
---

# NMEA 0183 Knowledge Patch

> Baseline: NMEA 0183 through 4.11, including common sentences and checksums; covered range: additional implementation details and changes through 4.30.

Use this patch when implementing, reviewing, configuring, or diagnosing NMEA 0183 links, emitters, parsers, and navigation integrations. Start with the quick references below, then read the topic file that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [protocol-and-wiring.md](references/protocol-and-wiring.md) | EIA-422-A wiring, legacy single-ended links, topology, baud rates, framing, checksums, gateways |
| [sentences-and-navigation.md](references/sentences-and-navigation.md) | Address forms, APB, RTE, XDR, signed values, BOD, R00, STN, RMB, NMEA 2.3 modes |
| [gnss-and-receiver-output.md](references/gnss-and-receiver-output.md) | NMEA 0183 4.30 GNSS additions, Emlid, Fixposition, NovAtel, Trimble Alloy |
| [garmin-and-sirf.md](references/garmin-and-sirf.md) | Garmin PGRM/PSLIB control and telemetry, SiRF PSRF configuration and reset behavior |
| [inertial-and-motion.md](references/inertial-and-motion.md) | Advanced Navigation output and SBG fused, inertial, attitude, motion, status, and compatibility sentences |
| [parsers-and-tools.md](references/parsers-and-tools.md) | Rust `nmea0183` 0.6.0, Hazer C semantics, `gpstool`, filtering, recovery, builds |
| [opencpn-integration.md](references/opencpn-integration.md) | OpenCPN core and Dashboard input, heading selection, target routing, MDA/XDR constraints |

## Breaking and compatibility-critical changes

### Update fixed lookup tables for 4.30

NMEA 0183 4.30 replaces 4.11 and expands the GNSS suite for GPS, GLONASS, Galileo, BDS, QZSS, and NavIC. Update fixed talker, formatter, GNSS identification, and observation-code tables. In particular, recognize the new or expanded `GIR`, `GRP`, `GGC`, `GCF`, `GSN`, `RLM`, and `SMV` coverage. Read [gnss-and-receiver-output.md](references/gnss-and-receiver-output.md) before changing a decoder table.

### Keep protocol syntax separate from electrical compatibility

- Treat v2.x and later links as EIA-422-A differential `A`/`B`, normally `4800 8N1`.
- Never ground a conventional differential talker's driven `B/-` output.
- Allow one continuously driving talker per pair; use a multiplexer for several talkers and a buffer for isolated fan-out.
- Do not infer signal levels from sentence version, product labels, connector names, or wire colors.
- Use optical isolation for computer connections where ground loops or induced spikes are possible.

Read [protocol-and-wiring.md](references/protocol-and-wiring.md) before connecting legacy single-ended equipment.

### Do not confuse high-speed 0183 with NMEA 2000

NMEA 0183-HS is `38400 8N1` serial NMEA 0183. NMEA 2000 is a 250 kbps CAN network with binary PGNs. Require a protocol gateway for sentence/PGN conversion; neither a multiplexer nor a level adapter performs it.

### Preserve nulls and validate versioned suffixes

Keep commas for unavailable fields. For v2.0 and later, require the two-digit checksum and calculate the XOR over every byte between, but excluding, the opening `$` or `!` and `*`. For NMEA 2.3 modes, do not equate a syntactically valid sentence with an active navigation solution: only `A` and `D` are active/reliable in the covered navigation behavior; `E`, `N`, `S`, and null are not.

## Framing quick reference

```text
$ttsss,d1,,d3*HH\r\n
!ttsss,fields*HH\r\n
$Pmmm,data*HH\r\n
$CCGPQ,GGA*2B\r\n
```

- Parse a standard address as two talker characters plus a three-character formatter.
- Parse `$P` plus a three-character manufacturer identifier as a proprietary address.
- Parse a query as requester talker, target talker, `Q`, then requested formatter.
- Accept printable ASCII `0x20` through `0x7e` with the high data bit clear.
- Retain the exact opening delimiter for checksum and sentence-class handling.
- Expect CRLF; device command envelopes may reject otherwise valid input without it.

## GNSS talkers and multi-constellation output

Do not assume `GP` means the receiver tracks only GPS. A configuration may force `GP` while the solution uses several constellations. Conversely, `AUTO` commonly chooses `GN` for a combined solution and constellation-specific identifiers such as `GP`, `GL`, `GA`, `GB`/`BD`, `GI`, and `GQ` for single-system data.

Treat `GSV` as a common exception: Emlid, NovAtel, and SBG output it under separate constellation talkers rather than `GNGSV`. For `GSA`, prefer an explicit NMEA 4.10 System ID over satellite-number ranges because identifiers overlap.

## GGA is not semantically uniform

Before consuming `GGA`, identify the configured source and profile:

| Source/profile | Important behavior |
| --- | --- |
| Fixposition high precision | Non-standard extra precision; altitude is ellipsoidal; geoid fields are null |
| Fixposition GNSS1TOS | Strict 1 Hz top-of-second output for PPS timing |
| Fixposition NTRIP | Synthetic quality/satellite/DOP fields; never use for navigation |
| NovAtel | Quality values overload correction states; selected datum may not be WGS 84 |
| SBG | Reports fused INS quality and synthesized DOP, not raw aiding-receiver quality |
| SiRF | Quality `6` is a valid dead-reckoning fix |

Do not enable multiple Fixposition GGA solution variants on one port: they are indistinguishable on the wire. Read [gnss-and-receiver-output.md](references/gnss-and-receiver-output.md) and [inertial-and-motion.md](references/inertial-and-motion.md) for field-level rules.

## Navigation sentence traps

### APB

Parse both status fields, cross-track error and steering direction, arrival and perpendicular flags, origin-to-destination bearing, waypoint, present-position-to-destination bearing, and heading-to-steer references. Some autopilots interpret the origin-to-destination field with APA semantics, so verify interoperability when far from the route leg.

### RTE and RMB

- Reassemble `RTE` with total/current message numbers. Mode `c` is complete; mode `w` is working and begins with the waypoint just left, then the destination.
- Interpret `RMB` closing velocity as waypoint VMG, `SOG * cos(COG - bearing)`, not raw SOG.

### BOD, XDR, and legacy route data

- Keep `BOD` fixed to the selected waypoint-to-waypoint leg; it is not present-position bearing.
- Parse every repeating `type,value,unit,name` group in `XDR`.
- Support `R00` plus alternating `WPL` where legacy active-route exchange is required.
- Apply an `STN` source ID to the sentence immediately following it.

Read [sentences-and-navigation.md](references/sentences-and-navigation.md) for exact layouts and sign conventions.

## Direction, sign, and validity

Do not normalize signs without the sentence/profile convention:

- Negative `ROT` means port; negative `RPM` pitch means astern.
- Negative `RSA` means port; negative `VBW` longitudinal/transverse values mean astern/port.
- Negative `VPW` means downwind.
- SBG native heave is commonly positive down, while its WASSP `PASHR`, `PHLIN`, and some compatibility forms use positive up.
- SBG body velocity is forward/starboard/down, but `PHLIN` sway is positive left.

Honor accompanying validity fields; a parsed number is not automatically usable.

## Device command safety

- Preserve null command fields when they mean “no change.”
- Send the exact checksum and CRLF required by SiRF `$PSRF<MID>` commands.
- Remember that SiRF input commands work only after the receiver is in NMEA mode.
- Treat reset numbering as platform-specific; SiRFLoc and non-SiRFLoc assignments differ.
- Treat Garmin baud and binary-phase changes as deferred until reset or power cycle where documented.
- Do not identify two same-address `PASHR` layouts by the address alone; use configured-log context.

Read [garmin-and-sirf.md](references/garmin-and-sirf.md) before emitting configuration commands and [inertial-and-motion.md](references/inertial-and-motion.md) before decoding proprietary motion output.

## Parser selection and error handling

### Rust `nmea0183` 0.6.0

Use `parse_from_byte` for streaming and `parse_from_bytes` for chunks. Distinguish `Ok(ParseResult::<type>(None))` from `Err`: the former is a valid sentence with no navigation solution. Check actual decoder support rather than inferring it from public data structures. Account for the API spelling `Source::Gallileo`, string errors, and the strict 79-character versus non-strict 120-character limit.

### Hazer and `gpstool`

On a negative Hazer parse result, inspect `errno`: zero means valid input with no valid solution; positive values classify rejection. Keep stream state machines alive across recoverable errors. Use `gpstool` masks deliberately when mixed NMEA/UBX/RTCM/CPO data is present, and do not treat `0.` trace placeholders as measured zero.

Read [parsers-and-tools.md](references/parsers-and-tools.md) for APIs, error mappings, routing switches, trace priority, and build steps.

## OpenCPN integration checks

- Do not assume OpenCPN core and Dashboard accept the same sentence set.
- Do not send routes expecting core `RTE` import; incoming `RTE` is not processed.
- Enable the AIS option explicitly before treating `WPL` as an APRS position report.
- Expect `TTM` and `TLL` radar targets to flow through the AIS decoder.
- Validate Dashboard `MDA` and `XDR` against its narrow field, range, unit, and name rules.
- For heading, apply the documented `HDG` variation fallback and accept only autonomous `THS` mode `A`.

Read [opencpn-integration.md](references/opencpn-integration.md) before mapping NMEA inputs to OpenCPN features.
