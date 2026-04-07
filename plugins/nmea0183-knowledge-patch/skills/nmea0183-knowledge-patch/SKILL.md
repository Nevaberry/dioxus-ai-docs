---
name: nmea0183-knowledge-patch
description: "NMEA 0183 changes since training cutoff (latest: v4.30) — RTK quality values, FAA mode indicators, multi-GNSS extensions (GSA/GSV/RMC), satellite ID ranges. Load before working with NMEA 0183."
version: "4.30"
license: MIT
metadata:
  author: Nevaberry
---

# NMEA 0183 Knowledge Patch

Claude knows basic NMEA 0183 sentence format and common sentences (GGA, RMC, GSV, GSA). This skill provides the full field value tables and multi-GNSS extensions through v4.30 (December 2023) that are needed for writing correct parsers and validators.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Sentence Fields | [references/sentence-fields.md](references/sentence-fields.md) | GGA quality 0-8, full FAA mode table, GGA-to-FAA mapping, satellite ID ranges |
| Multi-GNSS Extensions | [references/multi-gnss-extensions.md](references/multi-gnss-extensions.md) | GSA System ID, GSV Signal ID, RMC Nav Status, v4.30 new sentences |

---

## Quick Reference

### GGA Quality Indicator (field 6)

Values 0-2 are well-known. Values 3-8 are critical for RTK and precision applications:

| Value | Meaning | Typical use |
|-------|---------|-------------|
| 0 | No fix | Receiver searching |
| 1 | GPS (SPS) fix | Standard autonomous positioning |
| 2 | DGPS fix | Differential corrections (SBAS/WAAS) |
| 3 | PPS fix | Precise Positioning Service (military) |
| 4 | Real Time Kinematic (fixed) | cm-level, integer ambiguity resolved |
| 5 | Float RTK | dm-level, ambiguity not fully resolved |
| 6 | Estimated (dead reckoning) | IMU/wheel sensor extrapolation |
| 7 | Manual input | Position entered manually |
| 8 | Simulation | Testing/demo mode |

RTK fix progression: `0 → 1 → 5 (float) → 4 (fixed)`. Quality 4 is required for survey-grade work. Receivers may oscillate between 4 and 5 in challenging environments (urban canyons, tree canopy).

---

### FAA Mode Indicator (NMEA 2.3+)

Added in NMEA 2.3 as the last field before checksum on RMC, VTG, GLL, BWC, XTE, and other sentences.

| Value | Meaning | Since |
|-------|---------|-------|
| A | Autonomous | NMEA 2.3 |
| D | Differential (DGPS) | NMEA 2.3 |
| E | Estimated (dead reckoning) | NMEA 2.3 |
| **F** | **RTK Float mode** | NMEA 2.3 |
| M | Manual input | NMEA 2.3 |
| N | No fix / not valid | NMEA 2.3 |
| **P** | **Precise (no degradation)** | NMEA 4.00 |
| **R** | **RTK Integer mode (fixed)** | NMEA 2.3 |
| S | Simulator | NMEA 2.3 |

### GGA Quality to FAA Mode Mapping

When cross-referencing GGA and RMC from the same fix:

| GGA quality | FAA mode |
|-------------|----------|
| 0 (no fix) | N |
| 1 (GPS) | A |
| 2 (DGPS) | D |
| 4 (RTK fixed) | R |
| 5 (RTK float) | F |
| 6 (estimated) | E |
| 7 (manual) | M |
| 8 (simulation) | S |

---

### Satellite ID Ranges

Parsers handling multi-constellation GSV sentences need these boundaries to map satellite numbers to constellations:

| Range | System | Notes |
|-------|--------|-------|
| 1-32 | GPS | PRN number |
| 33-54 | SBAS | WAAS, EGNOS, MSAS, GAGAN |
| 65-88 | GLONASS | 64 + slot number |
| 173-182 | IMES | Indoor Messaging System |
| 193-197 | QZSS | Quasi-Zenith Satellite System |
| 201-235 | BeiDou | u-blox non-standard mapping |
| 301-336 | Galileo | Standard NMEA mapping |
| 401-437 | BeiDou | NMEA standard mapping |

**GLONASS dual behavior**: With `$GL` talker, IDs are 1-32 (slot number — add 64 for global). With `$GN` talker, IDs are already 65-96 (global numbering). Parsers must check the talker ID before mapping.

**BeiDou dual range**: 201-235 is used by u-blox receivers (non-standard but widely deployed). 401-437 is the NMEA standard range. Accept both ranges.

---

### NMEA 4.1+ Multi-GNSS Additions

These changes are backward-incompatible for parsers that assume a fixed field count.

#### GSA — System ID (field 18)

Multi-constellation receivers emit one GSA sentence per constellation under a `$GN` talker:

```
$GNGSA,A,3,80,71,73,79,69,,,,,,,,1.83,1.09,1.47,1*17
                                                  ^-- System ID
```

| System ID | Constellation |
|-----------|---------------|
| 1 | GPS |
| 2 | GLONASS |
| 3 | Galileo |
| 4 | BeiDou (BDS) |
| 5 | QZSS |
| 6 | NavIC (IRNSS) |

Legacy parsers expect 17 fields. When `$GP` talker is used, System ID may be absent.

#### GSV — Signal ID (last field before checksum)

Signal ID values are per-system. GPS signal IDs:

| ID | Signal |
|----|--------|
| 1 | L1 C/A |
| 5 | L2C-M |
| 6 | L2C-L |
| 7 | L5-I |
| 8 | L5-Q |

Receivers tracking multiple signals per constellation emit separate GSV groups per Signal ID. Total message count in field 1 is per-signal, not per-constellation — parsers that sum GSV messages without checking Signal ID will double-count satellites.

#### RMC — Nav Status (field 13)

Added after the FAA mode indicator (field 12):

```
$--RMC,hhmmss.ss,A,ddmm.mm,a,dddmm.mm,a,x.x,x.x,xxxx,x.x,a,m,s*hh
                                                                  ^-- Nav Status (4.1+)
```

| Value | Meaning |
|-------|---------|
| A | Autonomous |
| D | Differential |
| E | Estimated (dead reckoning) |
| M | Manual input |
| N | Not valid |
| S | Simulator |
| V | Valid (older specs, equivalent to A) |

The checksum position shifts by one field. Parsers must count fields dynamically or check NMEA version support. Field 12 (FAA mode) was added in NMEA 2.3; field 13 (Nav Status) in NMEA 4.1.

---

### NMEA 0183 v4.30 (December 2023)

Latest version, replaces v4.11 (2018). New sentences for modern multi-GNSS use cases:

| Sentence | Purpose |
|----------|---------|
| GIR | GNSS integrity information |
| GRP | High-accuracy positioning |
| GGC | Autonomous platform guidance (course) |
| GCF | Autonomous platform guidance (fix) |
| GSN | SBAS status and correction data |
| SMV | SafetyNet maritime distress messaging |

The standard is proprietary ($1,150-$10,000) so field-level details for v4.30-specific sentences are not publicly available.

---

## Reference Files

| File | Contents |
|---|---|
| [sentence-fields.md](references/sentence-fields.md) | Full GGA quality table with use cases, complete FAA mode indicator table with version history, GGA-to-FAA mapping, satellite ID ranges with GLONASS/BeiDou dual-numbering details, RTK quality progression |
| [multi-gnss-extensions.md](references/multi-gnss-extensions.md) | GSA System ID field with parsing implications, GSV Signal ID field with GPS signal table, RMC Nav Status field with version history, v4.30 new sentence summary |
