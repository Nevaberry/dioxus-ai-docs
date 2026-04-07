# Sentence Field Reference

Detailed field values for NMEA 0183 sentences that are commonly needed when writing parsers or validators. Covers quality indicators, mode flags, and satellite numbering that go beyond the basic A/V status fields.

## GGA Quality Indicator (Field 6)

The full range of GPS quality values. Values 0-2 are widely known; values 3-8 are critical for RTK and precision applications:

| Value | Meaning | Typical use case |
|-------|---------|-----------------|
| 0 | No fix | Receiver searching |
| 1 | GPS (SPS) fix | Standard autonomous positioning |
| 2 | DGPS fix | Differential corrections applied (SBAS/WAAS) |
| 3 | PPS fix | Precise Positioning Service (military) |
| 4 | Real Time Kinematic (fixed) | cm-level accuracy, integer ambiguity resolved |
| 5 | Float RTK | dm-level accuracy, ambiguity not fully resolved |
| 6 | Estimated (dead reckoning) | IMU/wheel sensor extrapolation, no satellite fix |
| 7 | Manual input | Position entered manually |
| 8 | Simulation | Testing/demo mode |

### RTK quality progression

In RTK applications, the typical fix progression is:

```
0 (no fix) → 1 (autonomous) → 5 (float RTK) → 4 (fixed RTK)
```

A receiver may oscillate between 4 and 5 in challenging environments (urban canyons, tree canopy). Quality 4 (fixed) is required for survey-grade work.

## FAA Mode Indicator

Added in NMEA 2.3 as the last field (before checksum) on RMC, VTG, GLL, BWC, XTE, and other sentences. Common values (A, D, E, M, N, S) are well-known. Less common values for precision applications:

| Value | Meaning | Added in |
|-------|---------|----------|
| A | Autonomous | NMEA 2.3 |
| D | Differential (DGPS) | NMEA 2.3 |
| E | Estimated (dead reckoning) | NMEA 2.3 |
| F | RTK Float mode | NMEA 2.3 |
| M | Manual input | NMEA 2.3 |
| N | No fix / not valid | NMEA 2.3 |
| P | Precise (no degradation) | NMEA 4.00 |
| R | RTK Integer mode (fixed) | NMEA 2.3 |
| S | Simulator | NMEA 2.3 |

### Mapping between GGA quality and FAA mode

| GGA quality | FAA mode |
|-------------|----------|
| 0 | N |
| 1 | A |
| 2 | D |
| 4 | R |
| 5 | F |
| 6 | E |
| 7 | M |
| 8 | S |

## Satellite ID Ranges (Multi-constellation)

Parsers handling multi-constellation GSV sentences need these ID boundaries to map satellite numbers to constellations:

| ID Range | System | Notes |
|----------|--------|-------|
| 1-32 | GPS | PRN number |
| 33-54 | SBAS | WAAS, EGNOS, MSAS, GAGAN |
| 65-88 | GLONASS | 64 + slot number |
| 173-182 | IMES | Indoor Messaging System |
| 193-197 | QZSS | Quasi-Zenith Satellite System |
| 201-235 | BeiDou | u-blox non-standard mapping |
| 301-336 | Galileo | Standard NMEA mapping |
| 401-437 | BeiDou | NMEA standard mapping |

### GLONASS dual ID behavior

GLONASS satellite IDs differ based on the talker ID:

- **`$GL` talker** (GLONASS-only sentence): IDs are 1-32 (slot number). Add 64 to get the global ID.
- **`$GN` talker** (multi-constellation sentence): IDs are already 65-96 (global numbering).

Parsers must check the talker ID before mapping GLONASS satellite numbers.

### BeiDou dual range

BeiDou has two valid ID ranges:
- **201-235**: Used by u-blox receivers (non-standard, widely deployed)
- **401-437**: NMEA standard range

Accept both ranges when parsing BeiDou satellites. Some receivers may use either depending on firmware version.
