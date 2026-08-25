# GNSS and Receiver Output

Use this reference when updating NMEA 0183 4.30 tables or consuming receiver-specific GNSS output.

## Contents

- [NMEA 0183 4.30 GNSS support](#nmea-0183-430-gnss-support)
- [Emlid Reach output](#emlid-reach-output)
- [Fixposition GGA profiles](#fixposition-gga-profiles)
- [NovAtel OEM7 output](#novatel-oem7-output)
- [Trimble Alloy output](#trimble-alloy-output)

## NMEA 0183 4.30 GNSS support

NMEA 0183 4.30 was published in December 2023 as the replacement for 4.11. It updates the full GNSS sentence suite for GPS, GLONASS, Galileo, BDS, QZSS, and NavIC.

### Receiver identifiers and observation codes

Version 4.30 adds Navigation Satellite System Receiver talker identifiers and sentence formatters. It also expands the GNSS Identification Table with RINEX observation codes. Replace fixed 4.11 lookup tables in parsers and emitters so new identifiers, formatters, and observation codes are accepted.

### Added and expanded sentences

- `GIR` provides enhanced GNSS integrity information.
- `GRP` provides high-accuracy positioning information.
- `GGC` and `GCF` improve GNSS support for autonomous platforms.
- `GSN` provides comprehensive Satellite Based Augmentation System support.
- `RLM` receives improved GNSS search-and-rescue support.
- `SMV` carries SafetyNet vessel-in-distress information.

Do not reject these formatters solely because they are absent from a 4.11 table.

## Emlid Reach output

### Default stream and talkers

Reach RS2/RS2+ defaults `GGA` to 5 Hz and `GSA`, `GST`, `GSV`, `RMC`, `VTG`, `ZDA`, and `EBP` to 1 Hz.

`GGA`/`GST`/`RMC`/`VTG`/`ZDA`/`EBP` normally use the `GN` talker. `GSA` and `GSV` emit successive `GP`, `GL`, `GA`, and `GB` sentences. Selecting `GP` restricts output to GPS. Do not configure an output rate higher than the GNSS update rate.

### EBP base position

Emlid's custom `EBP` sentence carries RTK base latitude, longitude, and ellipsoidal altitude in metres.

```text
$GNEBP,ddmm.mmmmmmm,N,dddmm.mmmmmmm,E,ellipsoid_altitude,M*hh
```

## Fixposition GGA profiles

### Solution-specific variants

`NMEA-GN-GGA_GNSS` averages the time and position from GNSS1 and GNSS2, uses fix type, satellite count, and DOP from the better receiver, and is valid only when both receivers have a valid fix.

`NMEA-GN-GGA_FUSION` uses Fusion time and position but retains GNSS-derived satellite and DOP data. Its quality follows the best GNSS state while GNSS is used; otherwise it reports dead reckoning or invalid according to Fusion state.

The GNSS, GNSS1, GNSS2, and Fusion variants are indistinguishable on the wire. Enable no more than one on a port.

### Top-of-second and NTRIP forms

`NMEA-GN-GGA_GNSS1TOS` is a strict-NMEA, 1 Hz top-of-second GNSS1 sentence intended to pair with PPS for consumers such as gpsd or chrony. High-precision mode does not affect it.

`NMEA-GN-GGA_NTRIP` is also strict. It uses system time and the most recent position from GNSS1, then GNSS2, then Fusion. It retains an old position for no more than 30 seconds.

The NTRIP form deliberately synthesizes quality fields:

| Position | Quality | Satellites | DOP |
| --- | ---: | ---: | ---: |
| unavailable | `0` | `0` | `99.99` |
| available | `1` | `10` | `02.00` |

Differential-age and station fields are null. This sentence is only a VRS-caster position report; never use it for navigation.

### High-precision non-standard fields

Optional high precision expands:

- UTC from two to four fractional digits;
- latitude/longitude from five to seven fractional minute digits;
- altitude from one to four decimals; and
- the satellite-count range from `00`–`12` to `00`–`99`.

Unlike conventional GGA interpretation, altitude is above the ellipsoid and both geoid-separation fields are always null. Differential age approximates time since the last GPS MSM correction.

```text
$GNGGA,hhmmss.ssss,ddmm.mmmmmmm,N,dddmm.mmmmmmm,E,q,sv,hdop,ellipsoid_altitude,M,,,diff_age,station*hh
```

## NovAtel OEM7 output

### UTC before almanac and selected datum

OEM7 emits `GPGGA` and `GPRMC` before it has a valid almanac. It derives UTC from default parameters and marks the separate `TIME` log as `WARNING`. Once almanac parameters are available, `TIME` becomes `VALID`.

Both position sentences use the receiver's selected datum, which is not necessarily WGS 84.

### GGA quality extensions

NovAtel overloads the GGA quality indicator for correction services:

- `1`: single point or converging TerraStar-L.
- `2`: pseudorange differential, converged TerraStar-L, or converging TerraStar-C PRO/X.
- `4`: RTK fixed.
- `5`: RTK float or converged TerraStar-C PRO/X.
- `6`: dead reckoning.
- `7`: fixed manual input.
- `8`: simulator.
- `9`: WAAS.

Use `BESTPOS` to disambiguate overloaded values. Correction age is capped at 99 seconds.

On SPAN receivers, GGA position comes from the GNSS+INS `BESTPOS` solution, while DOP values update only at 1 Hz.

### NMEATALKER and constellation behavior

`NMEATALKER` defaults to `GP`. That setting limits affected sentences to GPS information even when the receiver tracks other constellations.

```text
NMEATALKER auto
```

`AUTO` selects a single-constellation talker—`GP`, `GL`, `GA`, configurable `GB`/`BD`, `GI`, or `GQ`—and uses `GN` for a multi-constellation solution.

In a multi-constellation solution, `GSV` is the exception: it emits separate sentences under each constellation's talker rather than one `GN` sentence.

The command affects `HDT`, `GLL`, `GRS`, `GSA`, `GST`, `GSV`, `RMC`, and `VTG`, but not `GGA` or `ZDA`. With SPAN enabled, affected talkers become `IN`, except `GSA`/`GRS`/`HDT` remain `GN` and `GSV` remains per-constellation.

## Trimble Alloy output

Trimble Alloy output conforms to NMEA 0183 3.01. Enable it by sending a Configuration Toolbox application file containing NMEA output settings.

Alongside common GNSS sentences, Alloy supports:

- `DP` dynamic positioning;
- `LLQ` Leica local position/quality; and
- `PTNL` extensions: `AVR` moving-baseline attitude, `BPQ` base position/quality, `DG` L-band/beacon status, `EVT` event markers, `GGK`/`PJK` position and DOP, `PJT` projection type, `VGK` locator vectors, and `VHD` heading.
