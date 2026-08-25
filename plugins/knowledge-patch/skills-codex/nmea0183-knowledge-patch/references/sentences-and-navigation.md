# Sentences and Navigation Semantics

Use this reference when parsing addresses, reconstructing routes, driving an autopilot, interpreting signed motion, or validating navigation status.

## Contents

- [Addresses and queries](#addresses-null-fields-and-queries)
- [Autopilot and route sentences](#apb-autopilot-steering-data)
- [Transducer and motion values](#repeating-xdr-transducer-groups)
- [Legacy route and source data](#legacy-route-and-source-identification)
- [RMB and NMEA 2.3 status](#rmb-closing-velocity-and-mode)

## Addresses, null fields, and queries

A standard address contains a two-character talker ID followed by a three-character sentence formatter. Leave unavailable fields empty while retaining their delimiting commas.

Proprietary sentences begin with `$P` plus a three-character manufacturer ID. A query combines the requester and target talker IDs, `Q`, and the requested formatter.

```text
$ttsss,d1,,d3*hh\r\n
$Pmmm,data*hh\r\n
$CCGPQ,GGA*2B\r\n
```

## APB autopilot steering data

`APB` carries:

1. two navigation-status fields;
2. cross-track error and left/right steering direction;
3. arrival-circle and perpendicular-passed flags;
4. origin-to-destination bearing;
5. destination waypoint ID;
6. present-position-to-destination bearing; and
7. heading to steer.

Each bearing or heading is followed by `T` for true or `M` for magnetic reference.

```text
$--APB,status1,status2,xte,steer_dir,N,arrival,perpendicular,bearing_od,bearing_ref,waypoint,bearing_pd,bearing_ref,heading,heading_ref*hh
```

Some autopilots, particularly Robertson units, interpret APB's origin-to-destination bearing as a present-position-to-destination bearing, which is the APA meaning. This mismatch can cause poor steering when the vessel is well off the route leg. Confirm the receiving autopilot's interpretation.

## Multi-sentence routes

`RTE` begins with total-message and current-message numbers, then mode `c` for a complete route or `w` for a working route, followed by as many waypoint IDs as fit.

A working route begins with the waypoint just left, then the destination, then the remaining route.

```text
$--RTE,total,index,mode,waypoint1,waypoint2,...*hh
```

Reassemble messages by route identity and index; do not treat each fragment as an independent route.

## Repeating XDR transducer groups

`XDR` has one or more repeating `type,value,unit,name` groups. Iterate to the end of the sentence rather than assuming one measurement.

```text
$--XDR,type,value,unit,name,type,value,unit,name,...*hh
```

## Signed motion conventions

Interpret signs according to the formatter:

- Negative `ROT` means a turn to port.
- Negative `RPM` pitch means astern.
- Negative `RSA` rudder angle means port.
- Negative `VBW` longitudinal speed means astern; negative transverse speed means port.
- Negative `VPW` speed means downwind.

The accompanying `A` fields in `ROT`, `RPM`, `RSA`, and `VBW` indicate data validity. Do not use a value solely because it parsed successfully.

## Fixed waypoint bearing in BOD

`BOD` reports waypoint-to-waypoint bearing, not the changing bearing from the present position. In GOTO mode, its bearing is fixed when the destination is selected. With an active route, it remains the origin-to-destination leg bearing until advancing to the next leg.

## Legacy route and source identification

`R00` lists waypoint IDs in the active route and alternates with a cycle of `WPL` waypoint sentences.

`STN` is sent immediately before another sentence when a listener must distinguish data sources. Its only data field is a source ID from `00` through `99`; apply it to the following sentence.

```text
$GPR00,waypoint1,waypoint2,...*hh
$--STN,source_id*hh
```

## RMB closing velocity and mode

`RMB` combines cross-track error and steering direction with origin/destination IDs, destination coordinates, range, true bearing, closing velocity, and arrival status. Closing velocity is waypoint VMG:

```text
closing velocity = SOG * cos(COG - bearing)
```

It is not raw speed over ground. NMEA 2.3 adds the final mode field.

```text
$--RMB,status,xte,L|R,from,to,lat,N|S,lon,E|W,range_nm,bearing_true,closing_kn,A|V,mode*hh
```

## NMEA 2.3 mode validation

The NMEA 2.3 mode character is appended to `RMC`, `RMB`, `VTG`, and `GLL`, and may also appear on `BWC` and `XTE`.

- `A`: autonomous, active and reliable.
- `D`: differential, active and reliable.
- `E`: estimated, not active/reliable for the covered navigation behavior.
- `N`: not valid.
- `S`: simulator, not active/reliable.
- null: not active/reliable.

Validate both the sentence's ordinary status fields and this mode when present.
