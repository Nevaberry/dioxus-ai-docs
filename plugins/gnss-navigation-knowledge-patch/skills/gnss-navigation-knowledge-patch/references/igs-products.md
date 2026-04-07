# IGS Products & Formats

## International GNSS Service (IGS) Product Tiers

| Tier | Orbit accuracy | Clock accuracy | Latency | File naming |
|------|---------------|----------------|---------|-------------|
| **Final** | ~2.5 cm | ~20 ps | 13 days | `igsWWWWD.sp3` |
| **Rapid** | ~2.5 cm | ~40 ps | 17 hours | `igrWWWWD.sp3` |
| **Ultra-Rapid** | ~3–5 cm | ~30 ps | 3 hours | `iguWWWWD_HH.sp3` |

`WWWW` = GPS week number, `D` = day of week (0=Sunday), `HH` = hour (Ultra-Rapid only).

Real-time products available via NTRIP caster at CDDIS (Crustal Dynamics Data Information System).

## Key Formats

| Format | Extension | Content |
|--------|-----------|---------|
| **SP3** | `.sp3` | Precise satellite orbits (position + optional velocity, 15-min epochs) |
| **Clock RINEX** | `.clk` | Precise satellite and station clock offsets (5-min or 30-s epochs) |
| **IONEX** | `.ionex` / `.??i` | Global ionospheric TEC maps (2-hour grids) |
| **ANTEX** | `.atx` | Antenna phase center offsets (PCO) and variations (PCV) per frequency |
| **Bias-SINEX** | `.bsx` | Differential code biases (DCBs) and observable-specific signal biases (OSBs) |

## RINEX (Receiver Independent Exchange Format)

Current version: **RINEX 4.02**

Key features of v4:
- Pico-second timing resolution
- Full multi-GNSS support (GPS, GLONASS, Galileo, BeiDou, QZSS, IRNSS/NavIC, SBAS)
- Unified observation codes across constellations

RINEX file types:
- **Observation** (`.obs` / `.??o`): Pseudorange, carrier phase, Doppler, SNR per satellite
- **Navigation** (`.nav` / `.??n`): Broadcast ephemeris
- **Meteorological** (`.met` / `.??m`): Pressure, temperature, humidity for troposphere modeling

## Typical PPP Workflow with IGS Products

1. Collect raw observations (RINEX or proprietary) on dual-frequency receiver
2. Download IGS precise orbits (SP3) and clocks (Clock RINEX)
3. Apply antenna corrections (ANTEX) for both satellite and receiver antennas
4. Apply ionosphere-free combination or use IONEX maps (single-frequency fallback)
5. Process with PPP software (e.g., RTKLIB, GipsyX, Bernese)
