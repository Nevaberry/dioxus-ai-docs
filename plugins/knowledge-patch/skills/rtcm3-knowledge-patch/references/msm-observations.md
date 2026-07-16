# MSM observations

## Rollout across RTCM 3.x

RTCM 3.2 introduced MSM observation families for GPS, GLONASS, Galileo, QZSS, and BeiDou together with GLONASS bias type 1230. RTCM 3.3 added the SBAS MSM family. Check the claimed RTCM revision when deciding which constellations two receivers can exchange.

## Constellation and subtype numbering

The first three digits encode the constellation and the final digit is the MSM subtype from 1 through 7.

```text
1071–1077  GPS       1081–1087  GLONASS
1091–1097  Galileo   1101–1107  SBAS
1111–1117  QZSS      1121–1127  BeiDou
1131–1137  IRNSS
```

For example, 1127 is BeiDou MSM7 and 1104 is SBAS MSM4.

## Multiple-signal design

Legacy GPS types 1001–1004 and GLONASS types 1009–1012 are limited to L1/L2 and one signal per frequency band. MSM uses a constellation-independent layout that carries multiple signals and additional bands, avoiding proprietary observation formats or a RINEX 3 conversion step in real-time interchange.

## Precision tiers and field sets

MSM1–MSM5 use standard-precision fields. MSM6 and MSM7 carry the same respective field sets as MSM4 and MSM5 at higher resolution. MSM2 contains only phase-range observations. A constrained base can send MSM2 frequently, then interleave MSM3 less often to refresh pseudorange or MSM4 to refresh pseudorange and carrier-to-noise data.

MSM5 and MSM7 include Doppler; MSM4 and MSM6 omit it. Avoid describing all MSM variants as carrying Doppler.

## Onocoy ingest profile

Onocoy processes MSM4 and higher but ignores MSM1–MSM3 and the complete SBAS family, including types 1104 and 1107. Send only one MSM tier for each supported constellation. Prefer MSM7 (`1077`, `1087`, `1097`, `1117`, `1127`, `1137`) or use the matching MSM4 set as fallback. Sending MSM4 and MSM7 together is redundant, and the lower-quality tier is filtered.
