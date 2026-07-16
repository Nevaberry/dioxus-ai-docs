# NMEA Protocols

### Fix dimension and solution quality are separate
`GSA` mode is `1` for no fix, `2` for 2D, and `3` for 3D, while `GGA` quality describes the solution source: `0` no fix, `1` GPS, `2` DGPS, `3` PPS, `4` RTK fixed, `5` RTK float, `6` estimated/dead reckoning, `7` manual, and `8` simulated. A raw decoder needs both concepts rather than deriving fix dimension from GGA quality.

### GNS reports mode per constellation
The `GNS` mode field is a one-to-four-character vector rather than one aggregate flag; its first two positions describe GPS and GLONASS, with `A` autonomous, `D` differential, `E` estimated, `F` RTK float, `M` manual, `N` unused or no valid fix, `P` precise, `R` RTK integer, and `S` simulated. Thus `AN` means an autonomous GPS solution with GLONASS unused.

```text
$GPGNS,112257.00,3844.24011,N,00908.43828,W,AN,03,10.5,,*57
```

### Mode and status fields are versioned
NMEA 2.3 appended an optional FAA mode to GLL, RMC, VTG, and several navigation sentences; it may be empty or absent on older senders, takes precedence over the older status field, and requires decoders to allow `E` estimated, `F` RTK float, `M` manual, `N` invalid, `P` precise, `R` RTK integer, and `S` simulated alongside `A` autonomous and `D` differential, with Quectel further adding `C` caution and `U` unsafe. The NMEA 4.1x RMC form adds another navigation-status field after FAA mode, so decode by field count and do not treat its older `A`/`V` status as a pure fix-present bit: `V` can accompany a fix rejected only by an internal DOP or elevation-quality threshold.

```text
$GNRMC,001031.00,A,4404.13993,N,12118.86023,W,0.146,,100117,,,A*7B
```

### NMEA 4.x extends GSA and GSV at the tail
NMEA 4.11 GSA adds a system ID immediately before the checksum, while NMEA 4.10+ GSV adds a signal ID after its final satellite quadruple. System IDs are `1` GPS, `2` GLONASS, `3` Galileo, `4` BeiDou, `5` QZSS, and `6` NavIC; signal IDs are interpreted within that system, so fixed-field parsers must account for both optional tails.

```text
$GNGSA,A,3,80,71,73,79,69,,,,,,,,1.83,1.09,1.47,2*09
$GPGSV,1,1,01,03,45,180,40,1*5A
```

### GSV groups exceed nominal bounds
Assemble GSV using its total-message and message-number fields without assuming the historical maximum of three sentences or 12 satellite quadruples; real receivers can exceed both, and an untracked satellite can have an empty SNR. In GL-talker skyviews, GLONASS IDs 1-32 need 64 added for a globally unique NMEA ID, whereas a GN-talker multi-constellation skyview already uses 65-96; several vendors violate even these conventions.

### Error and residual sentences depend on prior context
The timestamp in GBS associates its fault/error data with a GGA or GNS fix, while GST and GRS refer to the associated GGA epoch. GRS residual positions must be matched to the satellite order in the last GSA, and its GP, GL, or GN talker identifies GPS-only, GLONASS-only, or combined residuals.

### VTG has incompatible wire shapes
Older VTG uses four unlabelled numeric fields, while the newer form interleaves the fixed unit markers `T`, `M`, `N`, and `K` and may append FAA mode; distinguish them by whether the second data field is `T`. Valid newer senders may leave both magnetic-course fields empty.

```text
$GPVTG,220.86,T,,M,2.550,N,4.724,K,A*34
```

### Jackson Labs NMEA overloads and extensions
Jackson Labs devices replace GGA's standard quality field with GPSDO status, so the normal `0`-through-`8` mapping must not be applied blindly. Their `PJLTS` report carries filtered and raw UTC offsets, captured-PPS count, lock and EFC state, frequency accuracy, holdover time, satellite count, and health; `PJLTV` carries Cartesian velocity and accuracy plus GPS time-of-week, week number, and leap-second offset.

### PASHR is producer-specific
The documented RT300 PASHR form carries UTC, true heading, roll, pitch, heave, three angular accuracy estimates, aiding status, and IMU status, but other Ashtech-originated uses of the same proprietary tag have a different layout. Select a decoder using the producer and field shape rather than the `PASHR` tag alone.

```text
$PASHR,085335.000,224.19,T,-01.26,+00.83,+00.00,0.101,0.113,0.267,1,0*06
```

