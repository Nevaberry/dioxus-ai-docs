# Inertial, Attitude, and Motion Output

Use this reference when configuring Advanced Navigation or SBG outputs and when decoding fused position, attitude, heave, DVL, pressure, or compatibility sentences.

## Contents

- [Advanced Navigation](#advanced-navigation-gnss-compass-behavior)
- [sbgECom classes and fused quality](#sbgecom-nmea-classes-and-ids)
- [Standard and direct inertial output](#standard-vbw-dpt-and-rot-output)
- [SBG attitude and combined motion](#psbga-attitude-and-filter-mode)
- [Compatibility sentence layouts](#pashr-layouts)
- [System and ship-motion output](#phinf-system-status)
- [Navigation state and GGK](#indyn-navigation-state)

## Advanced Navigation GNSS Compass behavior

The GC2-SER emits NMEA 4.10 on its auxiliary serial port. By default, it enables only `GPHDT` and `GPRMC`, both at 8 Hz.

The GC2-POE multicasts to `239.192.0.4`. It normally enables its listed messages at 1 Hz, except `GPHDT`/`GPRMC` at 8 Hz and `GPHBT` every 60 seconds. `TSS1` is disabled by default. It also supports `PASHR` and `PFEC` attitude/heave extensions. Configurable rates are 1–50 Hz except for the documented `GPHBT`/`TSS1` minima.

## sbgECom NMEA classes and IDs

Standard NMEA 4.1 outputs use class `SBG_ECOM_CLASS_LOG_NMEA_0` (`0x02`). Proprietary and third-party NMEA-like outputs use `SBG_ECOM_CLASS_LOG_NMEA_1` (`0x03`). Use the class and message ID when configuring logs.

```text
0x02: 00 GGA, 01 RMC, 02 ZDA, 03 HDT, 04 GST, 05 VBW, 07 DPT, 08 VTG, 09 ROT, 10 GSV
0x03: 00 PRDID, 01 PSBGI, 02 PASHR, 04 PSBGB, 05 PHINF, 06 PHTRO, 07 PHLIN,
      08 PHOCT, 09 INDYN, 10 GGK, 12 WASSP, 13 PSBGA
```

## Fused-solution quality

SBG standard output describes the fused AHRS/INS solution, not the aiding GNSS receiver. Even RTK GNSS input produces invalid GGA until the INS aligns.

GGA/GGK quality, RMC/VTG mode, and RMC navigation status derive from INS horizontal-position standard deviation:

```text
>100 m: GGA/GGK 0/0, mode/status N/V
<100 m: GGA/GGK 6/1, mode/status E/C
 <10 m: GGA/GGK 1/4, mode/status A/S
<1.2 m: GGA/GGK 2/2, mode/status D/S
<0.30 m: GGA/GGK 5/3, mode/status F/S
<0.10 m: GGA/GGK 4/2, mode/status R/S
```

DOP is synthesized from north/east position standard deviations rather than satellite geometry.

SBG GGA uses eight fractional minute digits and reports MSL altitude plus WGS-84 geoid separation. GST reports the fused solution's error ellipse and latitude/longitude/altitude one-sigma errors; its pseudorange-residual field is always empty.

## Talker and GSV behavior

Configure the talker ID independently per output interface. This setting is ignored when parsing NMEA aiding input.

`GSV` is always separated by constellation as `GP`, `GL`, `GA`, `GB`, `GI`, or `GQ`; it is never emitted as `GNGSV`. A tracked satellite with unknown SNR is reported as `60`; an untracked satellite has an empty SNR.

## Standard VBW, DPT, and ROT output

SBG `VBW` expresses longitudinal and transverse water/ground velocity in the INS body frame. It is valid only when bottom- and water-tracking DVL data are available.

`DPT` passes through positive-down depth from an external pressure sensor and always leaves offset and range-scale empty.

`ROT` is the true-heading derivative in clockwise-positive degrees per minute, not the IMU Z gyro.

```text
$--DPT,depth_m,,*hh
$--ROT,heading_rate_deg_per_min,A|V*hh
```

## PSBGI direct inertial measurements

`PSBGI` carries millisecond UTC, body-frame X/Y/Z rotation rates in degrees per second, and X/Y/Z acceleration in metres per second squared. These are direct IMU measurements, not corrected for sensor bias, Earth rotation, or gravity.

```text
$PSBGI,hhmmss.sss,gyro_x,gyro_y,gyro_z,accel_x,accel_y,accel_z*hh
```

## PSBGA attitude and filter mode

`PSBGA` carries UTC, roll (port up), pitch (bow up), true heading, each angle's standard deviation, a smart-solution code, and roll/pitch and heading validity.

UTC status is:

- `i`: invalid;
- `v`: valid with a known leap second; or
- `d`: valid with an unknown leap second.

The UTC status is uppercased when synchronized to PPS. Attitude status is `i` invalid or `v` optimal.

The solution code is lowercase before INS alignment and uppercase afterward:

| Code | State | Code | State |
| --- | --- | --- | --- |
| `a` | uninitialized | `j` | USBL |
| `b` | vertical gyro | `k` | unknown GNSS position |
| `c` | AHRS | `l` | single point |
| `d` | inertial navigation | `m` | DGPS |
| `e` | vehicle constraints | `n` | SBAS |
| `f` | odometer | `o` | RTK float |
| `g` | ZUPT | `p` | RTK fixed |
| `h` | DVL | `q` | PPP float |
| `i` | GNSS velocity | `r` | PPP fixed |

```text
$PSBGA,time,utc_status,roll,pitch,heading,roll_sd,pitch_sd,heading_sd,solution,rp_status,heading_status*hh
```

## PSBGB combined motion solution

Version-1 `PSBGB` combines UTC, attitude and standard deviations, heave, compensated body angular rates, body X/Y/Z velocities, velocity uncertainty, and per-group statuses.

UTC states are:

| State | Meaning |
| ---: | --- |
| `0` | invalid |
| `1` | valid/PPS |
| `2` | valid/no-PPS |
| `3` | unknown leap/PPS |
| `4` | unknown leap/no-PPS |

Attitude and velocity states are `0` invalid, `1` optimal, or `2` degraded during alignment. Heave state is `0` invalid/initializing, `1` velocity-aided, or `2` standalone.

Heave is positive down and its reported standard deviation is fixed at 0.05 m. Body velocity is positive forward, starboard, and down. Angular rates are positive port-up, bow-up, and clockwise.

```text
$PSBGB,1,time,utc,roll,pitch,heading,roll_sd,pitch_sd,heading_sd,rp_status,heading_status,heave,heave_sd,heave_status,rate_x,rate_y,rate_z,vel_x,vel_y,vel_z,vel_sd,vel_status*hh
```

## PASHR layouts

Normal SBG `PASHR` reports UTC, true heading, roll, pitch, positive-down heave, angle standard deviations, position status, and IMU status. Invalid time or motion fields are left empty.

Position status is `0` no position, `1` any non-RTK-fixed position, or `2` RTK fixed. IMU status is `0` healthy or `1` sensor error.

The WASSP-compatible log uses the same `$PASHR` address and field order, but changes heave to positive up and prints it with three fractional digits. Determine the configured log externally; the address does not distinguish these layouts.

```text
$PASHR,time,heading,T,roll,pitch,heave,roll_sd,pitch_sd,heading_sd,position_status,imu_status*hh
```

## Compact RDI and iXblue attitude forms

The RDI-compatible `PRDID` orders signed bow-up pitch, signed port-up roll, and true heading.

The iXblue-compatible `PHTRO` uses unsigned magnitudes with sign letters. Pitch `M` is bow up and `P` is bow down; roll `B` is port down and `T` is port up.

```text
$PRDID,pitch,roll,true_heading*hh
$PHTRO,pitch,M|P,roll,B|T*hh
```

## PHINF system status

`PHINF` encodes a 32-bit status word as eight hexadecimal digits:

- bits `0`/`1`/`2`: invalid heading/roll/pitch;
- bit `3`: heave initialization;
- bit `5`: alignment;
- bit `7`: CPU overload;
- bits `8`–`10`: gyro-axis self-test failures;
- bit `11`: a gyro out of range;
- bits `12`–`14`: accelerometer-axis failures;
- bit `15`: any sensor failure;
- bits `16`–`18`: serial-input A–C errors;
- bit `19`: any output overload;
- bits `20`–`22`: full serial outputs A–C; and
- bit `27`: any invalid heading/roll/pitch component.

```text
$PHINF,hhhhhhhh*hh
```

## iXblue ship-motion forms

`PHLIN` reports surge positive forward, sway positive left, and heave positive up. The sway and heave signs are reversed from SBG's native convention.

`PHOCT` adds UTC and status, true heading, roll, bow-down-positive pitch, primary and lever-arm heave, lever-arm surge/sway, their speeds, and clockwise-positive heading rate. Its latency field is fixed at zero. Value statuses are `T` valid, `E` invalid, or `I` initializing; UTC uses only `T`/`E`.

```text
$PHLIN,surge_m,sway_m,heave_m*hh
$PHOCT,01,time,utc_status,00,heading,h_status,roll,r_status,pitch,p_status,primary_heave,motion_status,heave,surge,sway,heave_speed,surge_speed,sway_speed,heading_rate*hh
```

## INDYN navigation state

`INDYN` uses decimal-degree latitude/longitude and MSL altitude, followed by true heading, port-up roll, bow-down pitch, heading/roll/pitch rates, and forward horizontal speed. The attitude rates are angle derivatives, not raw body-frame gyroscope measurements.

```text
$INDYN,latitude_deg,longitude_deg,msl_altitude_m,heading,roll,pitch,heading_rate,roll_rate,pitch_rate,ground_speed_mps*hh
```

## Trimble-compatible GGK

SBG `$PTNL,GGK` uses `mmddyy` date order, eight fractional minute digits for position, and an ellipsoidal-height field prefixed by `EHT`. Position quality and HDOP derive from INS standard deviation, while satellite count comes from the latest received GNSS fix.

```text
$PTNL,GGK,hhmmss.ss,mmddyy,ddmm.mmmmmmmm,N,dddmm.mmmmmmmm,E,quality,sv,hdop,EHTheight_m,M*hh
```
