# Multi-GNSS Extensions (NMEA 4.1+)

NMEA 0183 v4.10 and later added fields to existing sentences to support multi-constellation GNSS receivers. These changes are backward-incompatible for parsers that assume a fixed field count.

## GSA — System ID Field (Field 18)

GSA gains a **System ID** field just before the checksum. Multi-constellation receivers emit one GSA sentence per constellation under a `$GN` talker:

```
$GNGSA,A,3,80,71,73,79,69,,,,,,,,1.83,1.09,1.47,1*17
                                                  ^-- System ID
```

System ID values:

| ID | System |
|----|--------|
| 1 | GPS |
| 2 | GLONASS |
| 3 | Galileo |
| 4 | BeiDou (BDS) |
| 5 | QZSS |
| 6 | NavIC (IRNSS) |

### Parsing implications

- Legacy parsers expect 17 fields in GSA. The System ID is field 18.
- When `$GP` talker is used, System ID may be omitted (GPS-only receiver).
- When `$GN` talker is used, expect multiple GSA sentences with different System IDs.

## GSV — Signal ID Field

GSV gains a **Signal ID** field just before the checksum. Signal ID values are system-specific and identify the frequency/signal type being reported.

### GPS Signal IDs

| ID | Signal |
|----|--------|
| 1 | L1 C/A |
| 5 | L2C-M |
| 6 | L2C-L |
| 7 | L5-I |
| 8 | L5-Q |

### Parsing implications

- A receiver tracking multiple signals per constellation emits separate GSV groups per Signal ID.
- The total message count in field 1 is per-signal, not per-constellation.
- Legacy parsers that count total visible satellites by summing GSV messages will double-count if they ignore Signal ID.

## RMC — Nav Status Field (Field 13)

RMC gains a **Nav Status** field after the FAA mode indicator (field 12):

```
$--RMC,hhmmss.ss,A,ddmm.mm,a,dddmm.mm,a,x.x,x.x,xxxx,x.x,a,m,s*hh
                                                                  ^-- Nav Status
```

Nav Status values:

| Value | Meaning |
|-------|---------|
| A | Autonomous |
| D | Differential |
| E | Estimated (dead reckoning) |
| M | Manual input |
| N | Not valid |
| S | Simulator |
| V | Valid (used in older specs, equivalent to A) |

### Parsing implications

- The checksum position shifts by one field.
- Parsers must check NMEA version support or count fields dynamically.
- Field 12 (FAA mode) was added in NMEA 2.3; field 13 (Nav Status) in NMEA 4.1.

## NMEA 0183 v4.30 (December 2023)

Latest version, replaces v4.11 (2018). New sentences for modern multi-GNSS use cases:

| Sentence | Purpose |
|----------|---------|
| GIR | GNSS integrity information |
| GRP | High-accuracy positioning |
| GGC | Autonomous platform guidance (course) |
| GCF | Autonomous platform guidance (fix) |
| GSN | SBAS status and correction data |
| SMV | SafetyNet maritime distress messaging |

The NMEA 0183 standard is proprietary ($1,150-$10,000 for the specification document), so field-level details for v4.30-specific sentences are not publicly available. The sentences above are known from IEC 61162-1 amendment summaries and industry publications.
