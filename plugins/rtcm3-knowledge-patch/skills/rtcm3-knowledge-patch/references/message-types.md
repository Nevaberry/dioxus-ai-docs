# Message Types and SSR

## Version Progression

RTCM 10403.x introduced message types incrementally:

- **3.1**: GPS/GLONASS ephemeris (1019, 1020), SSR Phase 1 (1057-1068), Network RTK (1014-1017)
- **3.2**: MSM for GPS/GLO/GAL/QZSS/BDS (1071-1127), GLONASS code-phase bias (1230), Galileo F/NAV ephemeris (1045), QZSS ephemeris (1044)
- **3.3**: BDS ephemeris (1042), Galileo I/NAV ephemeris (1046), SBAS MSM (1101-1107)
- **3.4 (10403.4, Dec 2023)**: CRS messages (1300-1302), NavIC/IRNSS MSM (1131-1137), BDS/Galileo network RTK residuals (1303-1304)

## Core Message Number Ranges

| Range | Category |
|-------|----------|
| 1001-1004 | GPS L1/L2 legacy observations |
| 1009-1012 | GLONASS L1/L2 legacy observations |
| 1014-1017 | Network RTK auxiliary messages |
| 1019 | GPS ephemeris |
| 1020 | GLONASS ephemeris |
| 1042 | BDS ephemeris |
| 1044 | QZSS ephemeris |
| 1045 | Galileo F/NAV ephemeris |
| 1046 | Galileo I/NAV ephemeris |
| 1057-1068 | GPS/GLONASS SSR (Phase 1) |
| 1071-1077 | GPS MSM1-MSM7 |
| 1081-1087 | GLONASS MSM1-MSM7 |
| 1091-1097 | Galileo MSM1-MSM7 |
| 1101-1107 | SBAS MSM1-MSM7 |
| 1111-1117 | QZSS MSM1-MSM7 |
| 1121-1127 | BDS MSM1-MSM7 |
| 1131-1137 | NavIC/IRNSS MSM1-MSM7 |
| 1230 | GLONASS code-phase bias |
| 1240-1270 | Extended SSR (multi-constellation) |
| 1300-1302 | Coordinate Reference System (CRS) |
| 1303-1304 | BDS/Galileo network RTK residuals |

## MSM Subtypes

Each constellation's MSM block has 7 levels (only MSM4-7 are commonly used):

| MSM | Content |
|-----|---------|
| MSM1 | Pseudorange (compact) |
| MSM2 | Pseudorange (compact) + carrier phase (compact) |
| MSM3 | Pseudorange (compact) + carrier phase (compact) |
| MSM4 | Full pseudorange + full carrier phase + CNR |
| MSM5 | MSM4 + Doppler |
| MSM6 | Extended resolution pseudorange + carrier phase + CNR |
| MSM7 | MSM6 + Doppler |

**Practical rule**: MSM4 for corrections, MSM7 for full observables with Doppler.

## Extended SSR Messages (1240-1270)

Beyond GPS/GLONASS SSR (1057-1068), additional per-constellation SSR ranges:

| Range | Constellation | Content |
|-------|---------------|---------|
| 1240-1245 | Galileo | orbit/clock/code bias/combined/URA/high-rate clock |
| 1246-1251 | QZSS | same structure as Galileo SSR |
| 1252-1257 | SBAS | same structure |
| 1258-1263 | BDS | same structure |
| 1264 | — | SSR Ionosphere Spherical Harmonics |
| 1265-1270 | All | Satellite phase biases (GPS/GLO/GAL/QZSS/SBAS/BDS) |

## SSR Phases

- **Phase 1**: Orbit corrections + clock corrections + code bias
- **Phase 2**: Phase bias + vertical ionosphere
- **Phase 3**: Slant ionosphere + troposphere

Phase 1 is widely deployed (e.g. IGS real-time service). Phase 2/3 enable PPP-RTK but require denser reference networks.
