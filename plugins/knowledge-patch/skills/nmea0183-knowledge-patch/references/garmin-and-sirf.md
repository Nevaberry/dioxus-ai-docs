# Garmin and SiRF Extensions

Use this reference when configuring Garmin or SiRF receivers, selecting sentence output, interpreting proprietary telemetry, or issuing resets. Preserve exact field positions, nulls, checksums, and CRLF.

## Contents

- [Garmin output and telemetry](#garmin-output-selection-and-timing)
- [Garmin configuration](#garmin-initialization-and-pgrmc-configuration)
- [Garmin waypoint, aviation, and beacon data](#garmin-waypoint-aviation-and-beacon-data)
- [SiRF sentence and command behavior](#sirf-standard-sentence-differences)
- [SiRF configuration and resets](#sirf-serial-and-correction-port-configuration)

## Garmin output selection and timing

### PGRMO selection

`PGRMO` selects a target formatter or the whole output stream:

- mode `0`: disable the target formatter;
- mode `1`: enable the target formatter;
- mode `2`: disable all output;
- mode `3`: enable all output except `GPALM`;
- mode `4`: restore factory-default output; and
- mode `G`: switch the port to Garmin Data Transfer format until power cycle.

```text
$PGRMO,GPGSV,0*22\r\n
$PGRMO,,4*hh
$PGRMO,GPALM,1*hh
$PGRMO,,G*hh
```

Enabling `GPALM` temporarily suspends every other sentence while the stored almanac is sent.

Enabled sentences are emitted contiguously in each record, normally once per second at the factory 4800-baud setting. `PGRMT` remains once per minute.

On products with PPS, after at least four seconds of valid, accurate positioning, the rising edge is within one microsecond of the UTC boundary. Each burst describes the pulse immediately preceding `GPRMC`, or the first enabled sentence if `GPRMC` is disabled.

## Garmin position, motion, and receiver telemetry

- `PGRME` reports horizontal, vertical, and spherical position error in metres.
- `PGRMV` reports true east, north, and up velocity in metres per second.
- `PGRMZ` reports altitude in feet and fix dimension `2` for user altitude or `3` for GPS altitude.
- `PGRMF` combines GPS week and time-of-week, UTC date/time, leap seconds, position, automatic/manual mode, fix type `0`/`1`/`2`, speed in km/h, true course, PDOP, and TDOP.
- `PGRMM` names the active horizontal datum.

```text
$PGRME,hpe,M,vpe,M,spherical_error,M*hh
$PGRMV,east_mps,north_mps,up_mps*hh
$PGRMZ,altitude,f,fix_dimension*hh
$PGRMM,WGS-84*0B\r\n
```

### PGRMT health report

`PGRMT` uses `P`/`F` for ROM, receiver, and oscillator checks; `R`/`L` for stored data, clock, and configuration retention; and `C` or null for data collection.

## Garmin initialization and PGRMC configuration

### PGRMI initialization

`PGRMI` reports or sets initialization latitude, longitude, UTC date, and UTC time. Receiving it restarts satellite acquisition. Its final receiver-command field is `A` for Auto Locate or `R` for unit reset. Query stored initialization defaults with `PGRMIE`.

```text
$PGRMI,ddmm.mmm,N,dddmm.mmm,E,ddmmyy,hhmmss*hh
$PGRMI,,,,,,,A*hh
$PGRMI,,,,,,,R*hh
```

### Shared configuration behavior

Garmin configuration sentences accept null fields as “no change,” persist accepted values, and echo a successful command. On an error, they echo current defaults.

### PGRMC fields

`PGRMC` supports:

- fix mode `A` automatic, `2` 2D with host-supplied altitude, or `3` 3D;
- altitude;
- datum index and optional user-datum ellipsoid plus `dx/dy/dz`;
- differential mode `A` automatic or `D` differential-only;
- baud codes `1`/`2`/`3`/`4` for 1200/2400/4800/9600 and `5`/`6`/`7` for 19200/300/600;
- velocity filter `0` off, `1` automatic, or `2`–`255` seconds;
- PPS mode `1` off or `2` at 1 Hz; and
- a 1–30 second dead-reckoning-valid time in field 14.

User-datum parameters must be null unless datum index `96` is selected. Only a baud change waits for reset or power cycle. Query defaults with `PGRMCE`.

```text
$PGRMC,A,altitude,datum,semi_major,inverse_flattening,dx,dy,dz,differential_mode,baud_code,2,pps_mode*hh
```

## Garmin PGRMC1 configuration

`PGRMC1` configures:

- a 1–900 second NMEA output period;
- binary-phase output;
- automatic stopped-position averaging;
- NMEA 2.30 mode indication;
- WAAS-only or disabled DGPS mode;
- normal or power-save operation;
- adaptive transmission;
- automatic power-off; and
- power-on with an external charger.

Boolean fields use `1` for off and `2` for on. Fields 4–6 have no effect. Query defaults with `PGRMC1E`. Every change except binary-phase output applies immediately.

```text
$PGRMC1,period,binary,stopped_average,,,,v230,W|N,P|N,adaptive,auto_off,charger_on*hh
```

To recover a receiver already in binary mode, send bytes `10 0A 02 26 00 CE 10 03`, then send a `PGRMC1` command that disables binary-phase output. The binary-phase setting takes effect on reset or power cycle.

## Garmin waypoint, aviation, and beacon data

### PGRMW waypoint updates

`PGRMW` modifies altitude in metres, a hexadecimal symbol number up to `FFFF`, and the comment of an existing waypoint. The identifier must match exactly or the update is ignored. Overlong comments are truncated to the unit's capacity, and not every unit implements the command.

```text
$PGRMW,waypoint_id,altitude_m,symbol_hex,comment*hh
```

### PGRMH aviation and VNAV

`PGRMH` reports status (`A` valid or `v` unusable), signed vertical speed, signed VNAV profile error, vertical speeds required for the VNAV target and next waypoint, terrain clearance rounded down to 100 feet, desired true track, and the true course of the route leg after the active waypoint.

Vertical rates are feet per minute; the remaining vertical quantities are feet.

```text
$PGRMH,status,vertical_fpm,profile_error_ft,target_fpm,waypoint_fpm,terrain_ft,desired_track,next_leg_course*hh
```

### PGRMB beacon telemetry

`PGRMB` reports beacon frequency, bit rate, SNR, data quality, distance in kilometres, receiver state, correction source, and DGPS mode.

Receiver states `0`–`4` mean check wiring, no signal, tuning, receiving, and scanning. Source is `R` RTCM, `W` WAAS, or `N` non-DGPS. Mode is `A` automatic, `W` WAAS-only, `R` RTCM-only, or `N` disabled. Garmin units with SiRF chipsets do not support this sentence.

```text
$PGRMB,frequency_khz,bit_rate,snr,quality,distance_km,K,receiver_state,source,dgps_mode*hh
```

### PSLIB beacon control

`PSLIB` tunes or queries a differential-GPS beacon receiver using frequency and bit rate. Request `J` asks for status, `K` asks for configuration, and an empty request field performs tuning.

```text
$PSLIB,frequency,bit_rate,request*hh
```

## SiRF standard-sentence differences

SiRF uses GGA fix indicator `6` for a valid dead-reckoning fix and does not support indicators `3` through `5`.

Its versioned `GLL`, `RMC`, and `VTG` forms use trailing mode `A` autonomous, `D` differential, or `E` dead reckoning. SiRF does not supply magnetic declination, so RMC magnetic variation and VTG magnetic course may be empty.

SiRF `ZDA` timestamps the PPS pulse that just occurred, fixes local-zone fields at `00,00`, and supports years 1980 through 2079.

## SiRF command envelope

SiRF receivers ignore NMEA input commands unless already operating in NMEA mode. Every field and checksum is required in the `$PSRF<MID>,...*hh\r\n` envelope. Missing termination also prevents command processing.

## SiRF serial and correction-port configuration

`PSRF100` sets protocol (`0` SiRF binary, `1` NMEA), baud, data bits, stop bits, and parity (`0` none, `1` odd, `2` even). SiRF binary requires 8 data bits, one stop bit, and no parity. Accepted settings are saved before restart.

`PSRF102` applies the serial tuple, without the protocol field, to the RTCM correction port and also saves it across restart. GSW3 and GSWLT3 do not apply DGPS parameters from this message.

```text
$PSRF100,0,9600,8,1,0*0C\r\n
$PSRF102,9600,8,1,0*12\r\n
```

## SiRF output query and rate control

`PSRF103` has `message,mode,rate,checksum-enable` fields:

- mode `0` sets periodic output;
- mode `1` polls once;
- rate `0` disables output;
- rates `1` through `255` set the interval; and
- final `0`/`1` disables/enables output checksums.

Message IDs `0`–`5` select `GGA`, `GLL`, `GSA`, `GSV`, `RMC`, and `VTG`; `6` selects `MSS` when an internal beacon is supported; and `8` selects `ZDA` when PPS is supported. In TricklePower mode, rate counts power cycles rather than seconds.

```text
$PSRF103,00,01,00,01*25\r\n
```

## SiRF initialization and reset modes

`PSRF101` initializes using ECEF `X/Y/Z`, receiver clock offset, GPS time-of-week, GPS week, channel count, and reset configuration. `PSRF104` uses latitude, longitude, and altitude instead.

GSW3, GSWLT3, and SiRFXTrac ignore supplied position/time, making warm-start initialization ineffective on those platforms.

```text
$PSRF101,-2686700,-4304200,3851624,96000,497260,921,12,3*2F\r\n
$PSRF104,37.3875111,-121.97232,0,96000,237759,1946,12,1*06\r\n
```

On non-SiRFLoc platforms, reset values mean:

| Value | Action |
| ---: | --- |
| `1` | hot |
| `2` | warm with ephemeris cleared |
| `3` | warm with initialization |
| `4` | cold with memory cleared |
| `8` | factory reset |

SiRFLoc instead uses:

| Value | Action |
| ---: | --- |
| `0` | hot without initialization |
| `1` | initialization start |
| `2` | no-init warm |
| `3` | initialized warm |
| `4` | cold |
| `8` | factory reset |

## SiRF diagnostics and datum selection

`PSRF105,1` enables rejection diagnostics for failures such as bad checksums or out-of-range parameters; `PSRF105,0` disables them.

`PSRF106` selects a coordinate-conversion datum by numeric ID, including `21` for WGS 84 and `178` for Tokyo Mean.

```text
$PSRF105,1*3E\r\n
$PSRF106,178*32\r\n
```

## SiRF trickle-power and beacon messages

`PSRF150` reports whether a trickle-power receiver is awake (`1`) and safe to command or asleep (`0`).

`$GPMSK` independently selects beacon frequency and bit rate as automatic or manual and sets the MSS status interval. Poll or schedule MSS only through this message. GSW3/GSWLT3 emit it empty because they do not support the beacon.

```text
$PSRF150,1*3E\r\n
$GPMSK,318.0,A,100,M,2*45\r\n
```
