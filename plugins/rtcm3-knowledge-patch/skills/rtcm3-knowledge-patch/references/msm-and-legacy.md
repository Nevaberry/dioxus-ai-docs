# MSM vs Legacy Observations

## Resolution Comparison

When converting between formats (e.g. u-blox binary → RTCM → RINEX), resolution limits matter:

| Field | Legacy (1002/1010) | MSM (1077/1087) |
|-------|-------------------|-----------------|
| Pseudorange | 0.02 m | Higher resolution |
| Carrier phase | 0.5 mm | Higher resolution |
| Timestamp | 1 ms | 1 ms (unchanged) |
| Doppler | Not supported | Supported (MSM5/7) |
| Half-cycle invalid | Not supported | Supported |

## Timestamp Alignment Problem

The 1 ms timestamp resolution can cause RTK solution failures with receivers that don't align timestamps to round milliseconds (e.g. u-blox receivers).

**Fix**: Adjust timestamps to the nearest millisecond and compensate pseudorange and carrier phase measurements accordingly. The pseudorange/phase correction accounts for satellite motion during the time shift.

## When to Use Which Format

- **Legacy (1001-1012)**: Only for backward compatibility with old receivers/software. GPS and GLONASS only.
- **MSM4 (xx74)**: Standard for corrections — pseudorange, carrier phase, CNR. Sufficient for RTK.
- **MSM5 (xx75)**: Adds Doppler. Use when velocity information is needed.
- **MSM7 (xx77)**: Full resolution with Doppler. Use for high-precision applications or when archiving raw observations.

Legacy messages cannot represent Galileo, BDS, QZSS, SBAS, or NavIC observations — MSM is the only option for multi-constellation.
