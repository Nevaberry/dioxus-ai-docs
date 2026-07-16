# Augmentation, Corrections, and Precise Products

## SBAS, GBAS, and DGNSS

### SBAS correction and ranging boundary

An SBAS GEO satellite can contribute a ranging measurement as well as relay wide-area correction and integrity data. The broadcast covers satellite orbit, clock, and ionospheric-delay errors, but the user must apply a tropospheric-delay model, including its integrity treatment, rather than expect a tropospheric correction from SBAS.

### GBAS local broadcast envelope

GBAS derives local pseudorange corrections and integrity parameters from two or more surveyed receivers, then broadcasts them with WGS-84-referenced Final Approach Segment data over VHF Data Broadcast. Corrections are emitted at 2 Hz within 23 nmi (43 km), and one installation can support as many as 48 approaches.

### DGNSS spatial decorrelation and integrity

Classical DGNSS improves accuracy but does not itself assure integrity; the rover and reference station also need common satellite visibility because ephemeris and atmospheric errors decorrelate spatially. A cited rule of thumb is about 1 m (1 sigma) within a few tens of kilometres, with error growing roughly 1 m per 150 km of separation.

### Wide-area RTK reference spacing

As a rule of thumb, conventional RTK or network RTK baselines should remain within about 15 km when differential ionospheric delay must stay small. WARTK instead supplies explicit ionospheric corrections, allowing reference-station spacing of roughly 500–900 km.

### System-specific SBAS reception constraints

MSAS moved its SBAS transmission from MTSAT to the QZS-3 GEO satellite through the QZSS transmission service in April 2020, while GAGAN broadcasts SBAS data on L1 and had its L5 broadcast under development. SDCM was conceived to augment both GPS and GLONASS rather than the GPS-only scope described for the other contemporary SBAS initiatives.

## RTCM format boundaries and mapping

### Legacy RTCM version boundary

RTCM SC-104 correction streams are binary, and Version 3 is not wire-compatible with Version 2.x; RTCM 10403.1 adds GPS network corrections and GPS/GLONASS orbital parameters for faster acquisition. Ntrip is separately standardized as RTCM 10410.0 for streaming GNSS data over IP, while RTCM 10401.2 specifies reference-station and integrity-monitor performance.

### RTCM 2.3 RTK message mapping

In RTCM 10402.3, types 1, 2, and 3 carry differential GPS corrections, delta corrections, and reference-station parameters. The RTK extension uses type 18 for uncorrected carrier phase, 19 for uncorrected pseudorange, 20 for carrier-phase corrections, and 21 for pseudorange corrections; Version 2.3 uses 30-bit words.

## RTK base configuration

### ZED-F9P multi-constellation RTCM3 output

A ZED-F9P base configuration can emit reference-station position message 1005; the MSM4/MSM7 pairs 1074/1077 for GPS, 1084/1087 for GLONASS, 1094/1097 for Galileo, and 1124/1127 for BeiDou; and GLONASS code-phase-bias message 1230. Enable each message for the intended interface under `UBX-CFG-MSG`, then set that interface's `UBX-CFG-PRT` output protocol to RTCM3 or UBX+NMEA+RTCM3.

### Survey-in and fixed base coordinates

`UBX-CFG-TMODE3` survey-in forms a weighted mean of valid 3D fixes and completes only when both its minimum observation time and required position-accuracy thresholds are met; only then does the receiver enter time mode and begin outputting RTCM3 message 1005. For a permanent base, fixed mode instead accepts either ECEF coordinates or latitude, longitude, and ellipsoid height—not mean-sea-level height—and any base-coordinate error transfers directly to the rover's absolute position.

### Independent ports and persistent configuration

On a NEO-M8P, USB, I2C, SPI, and UART are independent interfaces: USB can inspect or configure the receiver while another interface ingests RTCM3 or carries navigation output. Message enablement is per interface, port protocol enablement is separate, and applied settings must finally be written with `UBX-CFG-CFG` “Save current configuration” to the desired nonvolatile devices if they must survive reconnection.

## Exchange and correction formats

### RINEX 4 navigation and observation changes

RINEX 4.00 modernizes navigation files to carry new constellation-specific navigation messages and system-data records such as ionospheric corrections, Earth-orientation parameters, and system-time offsets. Observation and meteorological records retain their prior structure apart from added signal codes and optional FAIR-data header lines; RINEX 4.01 adds GPS Block IIIF RMP/M-code L1/L2 observation codes and NavIC L1 observation codes.

RINEX 4.02 adds picosecond-resolution observation time tags, NavIC L1 and GLONASS L1/L3 CDMA navigation messages, and navigation-message subtypes for the dual ionosphere models broadcast by QZSS and NavIC. Parser capabilities should therefore be keyed to the exact RINEX minor version rather than to “RINEX 4” as a single feature set.

### IGS SSR v1 correction envelope

IGS SSR v1 is an open real-time, multi-GNSS state-space format whose baseline messages carry orbit, clock, differential-code-bias, phase-bias, and ionospheric-delay corrections. Satellite attitude, phase-center offsets and variations, and group-delay variations are listed as planned extensions rather than baseline v1 content.

### Current SPARTN feature baseline

SPARTN is a low-bandwidth state-space correction format designed for wide or global broadcast with reliability, integrity, encryption, and authentication support. The current available specification is 2.0.3 from November 2025; all earlier listed versions are deprecated.

The cumulative feature set covers GPS/GLONASS orbit, clock, and bias corrections; high- and basic-precision atmosphere corrections and area definitions; encryption/decryption, dynamic keys, and message authentication; Galileo, BeiDou, and QZSS; proprietary messages; BeiDou-3 code and phase biases; and Galileo E5/E6 signals. New implementations should target 2.0.3 rather than one of the deprecated intermediate versions that introduced those pieces.

## IGS orbit, clock, and frame products

### Combined orbit and clock tiers

The ultra-rapid orbit product is released at 03, 09, 15, and 21 UTC and contains a continuous 48-hour span sampled every 15 minutes: the first 24 hours are observed and the next 24 are predicted. The observed half has an initial three-hour latency; for true real-time use, the three-to-nine-hour portion of the predicted half is normally relevant. Approximate orbit accuracies are 3 cm for the observed half and 5 cm for the predicted half.

Rapid products provide roughly 2.5 cm orbits and five-minute satellite/station clocks, released daily at about 17 UTC with 17–41 hours of epoch-dependent latency. Final products provide roughly 2.5 cm orbits after 12–19 days, with 15-minute orbit samples, 30-second satellite clocks, and five-minute station clocks; final GLONASS ephemerides are approximately 3 cm. Clock accuracies are relative to the IGS timescale, aligned linearly to GPS time in one-day segments, and exclude instrumental delays that the user must calibrate separately.

### Long product filenames since GPS week 2238

Operational products from GPS week 2238 and repro3 products use long names that encode the producer/version/project and solution class, start epoch, product span, sampling interval, content, and exchange format. Representative combined-product names are:

```text
IGS0OPSFIN_yyyyddd0000_01D_15M_ORB.SP3.gz
IGS0OPSRAP_yyyyddd0000_01D_05M_CLK.CLK.gz
IGS0OPSULT_yyyydddhh00_02D_15M_ORB.SP3.gz
```

Here `yyyyddd` is year plus day of year and ultra-rapid `hh` is `00`, `06`, `12`, or `18`; the files remain organized in product directories by GPS week. Code that only constructs legacy names such as `igswwwwd.sp3.Z`, `igrwwwwd.clk.Z`, or `iguwwwwd_hh.sp3.Z` will miss the post-transition products.

### Terrestrial-frame SINEX products

IGS daily combined SINEX solutions contain station positions, daily Earth-rotation parameters, and daily apparent-geocenter coordinates. Stacking them produces a weekly solution with weekly station positions and geocenter coordinates but daily ERPs; a separate cumulative solution, now updated every eight weeks, models station motion with successive position/velocity segments and post-seismic deformation where needed.

## IGS atmosphere and bias products

### IONEX grid products

The combined final and rapid VTEC products use IONEX grids with 5-degree longitude by 2.5-degree latitude cells and two-hour epochs. Final grids have about 11 days of latency and weekly updates with stated 2–8 TECU accuracy, while rapid grids arrive in under 24 hours with daily updates and 2–9 TECU accuracy.

```text
IGS0OPSFIN_yyyyddd0000_01D_02H_GIM.INX.gz
IGS0OPSRAP_yyyyddd0000_01D_02H_GIM.INX.gz
```

### Per-site troposphere products

Current troposphere files contain daily, five-minute estimates of zenith path delay plus north and east gradient components for individual IGS sites. They depend on final orbit and Earth-orientation products and therefore arrive about three weeks after observation in TRO/SINEX-troposphere form:

```text
YYYY/IGS0OPSFIN_YYYYDOYHHMM_01D_05M_SITENAME_TRO.TRO.gz
```

`SITENAME` is the nine-character station name and `MM` is the daily file number, normally zero. Co-located pressure and temperature measurements allow precipitable water vapor to be extracted from the total zenith delay.

### Bias-SINEX differential-code-bias archive

A DCB is the systematic offset between two code observations, at either the same or different frequencies; it must be accounted for in code positioning, TEC extraction, and precise time transfer. The documented MGEX archive represents satellite and station biases in Bias-SINEX (`.BSX`): CAS rapid products are daily with two-to-three-day latency, while DLR final releases are updated every three months and contain weekly satellite-bias averages plus daily satellite and station values.

```text
CAS0MGXRAP_YYYYDDD0000_01D_01D_DCB.BSX.gz
DLR0MGXFIN_YYYY0010000_NNU_07D_DCB.BSX.gz
```

Bias-SINEX 1.00 files also have a parser trap: the February 2016 definition uses two-digit years for validity intervals, whereas the December 2016 definition uses four-digit years.

## Archived real-time-derived products

### Archived IGS real-time product boundary

The archived `igc` products are decoded from the center-of-mass-referenced IGC01 real-time stream: `igcWWWWD.sp3.Z` contains orbit and clock results at 30-second intervals, while `igcWWWWD.clk.Z` contains clocks at 10-second intervals. `igt` denotes a daily batch combination and `ritWWWWD.sum.Z` compares analysis-center and combined streams with the rapid solution; these archives are distinct from the live corrections delivered through the real-time caster, and their transition to long filenames is postponed while their continuation is under consideration.
