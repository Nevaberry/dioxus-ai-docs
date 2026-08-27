# JSON Protocol

### Request framing and truncation
A request line starts with `?`, may contain multiple commands, and encodes each command as an identifier followed by `;` or by `=` and a JSON object. Requests must be US-ASCII and at most 80 characters excluding the trailing newline; responses end in CR-LF and default to a compile-time `GPS_JSON_RESPONSE_MAX` cap of 10,240 characters including that terminator, so an oversized response can be truncated into invalid JSON and must be rejected as an incomplete frame.

```text
?VERSION;?DEVICES;
?WATCH={"enable":true,"json":true};
```

### Version greeting and protocol compatibility
Every new connection receives a `VERSION` object without requesting one; `?VERSION;` requests it explicitly. Check both `proto_major` and `proto_minor` against the client’s expected protocol, alongside `release` and `rev`; an optional `remote` identifies a relayed daemon.

### Incremental TPV fixes
`TPV.mode` is always present and means 0 unknown, 1 no fix, 2 2D, or 3 3D, but a TPV is not necessarily a complete epoch snapshot: receivers that dribble fields can cause several progressively populated TPVs for one measurement epoch. Optional `status` modifies rather than replaces `mode`; values 0 and 1 are omitted, while 2 is DGPS, 3/4 are RTK fixed/floating, 5/6 are DR/GNSSDR, 7 is surveyed time, 8 simulated, and 9 P(Y).

### TPV time and numeric validity
A TPV timestamp may be absent outside a 2D/3D fix or present but invalid without a fix; require three consecutive 3D fixes before initially trusting it as UTC. `libgps` represents invalid or unknown floating-point fields as `NAN`, so validate them with `isfinite()` rather than merely `isnan()`.

### Altitude and error semantics
The legacy `alt` field is deprecated and undefined; use ellipsoidal `altHAE` or mean-sea-level `altMSL`, where `altMSL = altHAE - geoidSep`. If the receiver omits the geoid, GPSD interpolates `geoidSep` from a 5-by-5-degree EGM2008 table, usually within one meter but sometimes off by as much as 12 meters; TPV error fields also have unspecified confidence in many receivers and are safest as relative quality indicators.

### Extended TPV measurements
TPV can carry ECEF position and velocity (`ecefx/y/z`, `ecefvx/y/z` plus accuracy fields), relative-baseline components (`relN/E/D`), GNSS clock bias in nanoseconds and drift in nanoseconds per second, antenna and antenna-power state, DGPS age/station, jamming level, and current leap seconds. Marine and environmental drivers may additionally populate depth, wind angles and speeds, and water or receiver temperature, so consumers should gate every such field on presence.

### SKY completeness and DOP calculation
When no sky view is available, only `class` is reliable; `nSat` counts entries in `satellites`, while `uSat` counts satellites used in the navigation solution. Satellite entries always have `PRN` and `used`, with geometry, signal, health, constellation, and signal identifiers optional; GPSD passes receiver DOPs through and tries to calculate missing ones from the sky-view covariance matrix, but singular geometry can still leave them absent.

### Constellation, satellite, and signal identifiers
NMEA-style `PRN` values are vendor-dependent across constellations; use GPSD’s `gnssid` plus native `svid` when identity matters. GPSD assigns `gnssid` 0 GPS, 1 SBAS, 2 Galileo, 3 BeiDou, 4 IMES, 5 QZSS, 6 GLONASS, and 7 NavIC; a multi-band satellite can report separate signals distinguished by receiver-specific `sigid`, which must be interpreted with the receiver documentation.

### GST error reports
`GST` is a pseudorange-noise report rather than another position fix. Its optional fields include range-input RMS, the major/minor axes and orientation of the horizontal error ellipse, latitude/longitude/altitude standard deviations, and east/north/up velocity-error standard deviations.

### Synchronous ATT versus asynchronous IMU
`ATT` and `IMU` expose the same attitude, magnetic-field, acceleration, gyroscope, depth, and temperature fields. `ATT` is synchronized to the GNSS epoch, whereas `IMU` is emitted as soon as possible and may carry arbitrary or out-of-order device time tags; the two classes can be interleaved.

### TOFF and PPS timestamp pairs
Enabling the WATCH `pps` policy emits `TOFF` for the serial-derived start of each reporting cycle and `PPS` for each valid pulse edge. Both pair source time (`real_sec`, `real_nsec`) with the host timestamp (`clock_sec`, `clock_nsec`); PPS additionally reports NTP-style `precision`, its shared-memory key in `shm`, and optional picosecond quantization error `qErr`.

### GPS-disciplined oscillator state
An `OSC` report describes a GPS-disciplined oscillator with `running`, `reference`, and `disciplined` booleans plus `delta`, the nanosecond offset between its output pulse and the latest GPS PPS input. This distinguishes a merely powered oscillator from one that currently has a usable reference and is actively disciplined.

### WATCH policy negotiation
Bare `?WATCH;` elicits the subscriber policy; a WATCH argument changes it, and the response is followed by a `DEVICES` object. `enable` defaults to true and `json` to false; `device` restricts a watch to one source, which is especially important for raw or pseudo-NMEA output because those records are not device-tagged, and it is ignored when disabling the watch.

```text
?WATCH={"enable":true,"json":true,"device":"/dev/ttyUSB0"};
```

### Raw and auxiliary WATCH modes
With `raw:1`, NMEA/AIVDM is passed through while binary packets are hex-dumped; `raw:2` emits binary input verbatim, and neither raw level dumps RTCM2 or RTCM3. `nmea` requests pseudo-NMEA for binary packets, `scaled` applies output divisors, `split24` controls AIS type-24 aggregation, and `pps` enables the timing reports.

### POLL is cached and watch-dependent
`?POLL;` works only after WATCH has activated devices and returns `active` plus timestamped `tpv` and `sky` arrays from last-seen data. A poll during a multi-sentence NMEA epoch can expose only the fields accumulated so far or data up to one cycle stale, and clients must allow future sensor arrays to extend the response inventory.

### Device inventory events
`?DEVICES;` returns the current array of `DEVICE` descriptions, while watching clients also receive bare `DEVICE` objects when a source is added or deactivated; deactivation is represented by its path with `activated:0`. Serial sources report `bps`, `parity`, and `stopbits`, while network sources omit those fields; `flags` is a bit vector for GPS, RTCM2, RTCM3, and AIS data observed so far.

### DEVICE reconfiguration and raw writes
`?DEVICE;` reports state, while `?DEVICE=<object>` can change serial speed/framing, cycle, or `native` mode (0 NMEA, 1 alternate); `mincycle` is read-only, and `path` may be omitted only when exactly one channel is subscribed. Unsupported changes leave the old link settings in place, but failed USB or Bluetooth framing changes can wedge hardware; `hexdata` sends bare hexadecimal to a receiver and returns `ACK` on success.

```text
?DEVICE={"path":"/dev/ttyUSB2","hexdata":"b5620a0400000e34"}
```

### RTCM2 JSON framing
Each decoded RTCM2 message is one object whose header precedes its payload and contains `type`, `station_id`, GPS-time `zcount` in seconds within the hour, three-bit wrapping `seqnum`, payload-word `length`, and `station_health`; any nonzero health warns that the source data should not be used for a fix. Correction payloads use satellite subobjects such as `ident`, `udre`, ephemeris tag `iod`, pseudorange correction `prc`, and range-rate correction `rrc`; unknown message types expose parity-checked 30-bit words as hex strings in `data`, whose high two bits are ignored.

### RTCM3 dump limitation
RTCM104v3 JSON dumping is explicitly incomplete and buggy and must not be used in production. Consumers needing RTCM3 decoding must not treat the daemon’s dump format as a stable or complete interface.

### AIS scaled output
AIS support may be absent from restricted builds; each report has class `AIS`, a message `type`, source `device`, and a `scaled` flag before type-specific fields. Default scaling converts coordinates to decimal degrees, ship speeds to knots, and draught to meters; rate of turn may instead be sentinel text such as `nan`, `fastright`, or `fastleft`, so its representation is not always numeric.

### SUBFRAME report envelope
Subframe support is always compiled in, though a receiver or driver may not provide it. A `SUBFRAME` object identifies the source with `device`, constellation `gnssId`, vehicle `tSV`, and `scaled`, optionally includes `frame` and `TOW17`, and nests page-specific fields in a subobject whose names follow IS-GPS-200 conventions.

