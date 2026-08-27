# Message catalog

## OEM7 log IDs versus RTCM types

The OEM7 log catalog's `Message ID` is an internal log identifier. Use the log name and separate RTCM-type column to identify the message carried on the stream.

```text
RTCM1004       log ID 770   -> RTCM type 1004
RTCM1074       log ID 1475  -> RTCM type 1074
RTCM1019ASYNC  log ID 2088  -> RTCM type 1019
```

## Network RTK correction families

```text
1014             auxiliary-station count and positions relative to the master
1015/1016/1017   GPS ionospheric / geometric / combined correction differences
1037/1038/1039   GLONASS ionospheric / geometric / combined correction differences
1030/1031        GPS / GLONASS per-SV non-dispersive interpolation residuals
1034/1035        GPS / GLONASS localized horizontal FKP gradients
1303/1304        BeiDou / Galileo per-SV non-dispersive interpolation residuals
```

## Coordinate transformation and CRS messages

Types 1021–1027 describe transformations, residual grids, and projections rather than observations:

```text
1021       seven-parameter Helmert or abridged Molodenski transformation
1022       Molodenski-Badekas transformation about an arbitrary point
1023/1024  residual grid in ellipsoidal / plane coordinates
1025       projections other than Lambert Conic Conformal
1026       Lambert Conic Conformal with two standard parallels (LCC2SP)
1027       Oblique Mercator projection
```

Type 1300 names the service CRS and associates it with transformation messages. Type 1301 provides a time-dependent 15-parameter transformation between named plate-fixed frames. Type 1302 links the stream to external CRS databases. These messages are uncommon in ordinary RTK streams.

## Broadcast ephemerides

```text
1019  GPS, Kepler form       1020  GLONASS, Cartesian form
1042  BeiDou                 1044  QZSS, Kepler form
1045  Galileo F/NAV          1046  Galileo I/NAV
```

See [stream-design-and-station.md](stream-design-and-station.md) for delivery and OEM7 scheduling behavior.

## Text and reserved ranges

Type 1029 carries a short human-readable Unicode string with space for roughly 128 UTF-8 encoded characters.

Types 1–100 are temporary experimental assignments and should not be deployed as stable formats. Types 4001–4095 are proprietary; interpret their layouts according to the registered assignee, not a generic common payload definition.

## Common proprietary assignments

Within the proprietary range, the message number identifies the registered format owner and therefore which private decoder is needed. Common receiver and correction-provider assignments include:

```text
4072 u-blox       4074 Unicore       4076 IGS
4077 Hemisphere   4078 ComNav        4089 Septentrio
4090 Geo++        4091 Topcon        4092 Leica
4093 NovAtel      4094 Trimble       4095 Ashtech
```
