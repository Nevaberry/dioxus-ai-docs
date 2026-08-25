# BNC Client and Correction Services

## Contents

- [Runtime, streams, and operations](#runtime-streams-and-operations)
  - [Runtime and build requirements](#runtime-and-build-requirements)
  - [Stream inputs and transport selectors](#stream-inputs-and-transport-selectors)
  - [Decoder override and byte-preserving modes](#decoder-override-and-byte-preserving-modes)
  - [Configuration precedence and headless operation](#configuration-precedence-and-headless-operation)
  - [Active configuration and live rereads](#active-configuration-and-live-rereads)
  - [TLS certificate layout](#tls-certificate-layout)
  - [Outage alarms and stream diagnostics](#outage-alarms-and-stream-diagnostics)
  - [BNC correction-file interchange](#bnc-correction-file-interchange)
- [RINEX, recording, and file processing](#rinex-recording-and-file-processing)
  - [Output overwrite and record/replay semantics](#output-overwrite-and-recordreplay-semantics)
  - [RTCM-to-RINEX conversion guardrails](#rtcm-to-rinex-conversion-guardrails)
  - [RINEX skeleton selection](#rinex-skeleton-selection)
  - [RINEX file rotation and version mapping](#rinex-file-rotation-and-version-mapping)
  - [RINEX editing and quality control](#rinex-editing-and-quality-control)
  - [SP3 comparison behavior](#sp3-comparison-behavior)
- [Engine feeds and rover feedback](#engine-feeds-and-rover-feedback)
  - [Synchronized and immediate engine feeds](#synchronized-and-immediate-engine-feeds)
  - [Serial rover output and VRS GGA](#serial-rover-output-and-vrs-gga)
- [PPP and correction products](#ppp-and-correction-products)
  - [PPP input contract and fallback](#ppp-input-contract-and-fallback)
  - [PPP replay, coordinates, and antenna corrections](#ppp-replay-coordinates-and-antenna-corrections)
  - [PPP observation and timing controls](#ppp-observation-and-timing-controls)
  - [PPP ambiguity resolution and multi-station output](#ppp-ambiguity-resolution-and-multi-station-output)
  - [Correction combination limits](#correction-combination-limits)
  - [Internal validation of a combination](#internal-validation-of-a-combination)
  - [RTNET engine bridge](#rtnet-engine-bridge)
  - [SSR upload sampling and product references](#ssr-upload-sampling-and-product-references)
  - [Ephemeris and raw-stream uploads](#ephemeris-and-raw-stream-uploads)

## Runtime, streams, and operations

### Runtime and build requirements

BNC 2.13 uses Qt 5; a source build is produced with `qmake bnc.pro` followed by `make`. Static builds cannot provide OpenStreetMap tracks because that feature needs `QtWebEngineWidgets` from a shared Qt build, and Linux batch jobs that generate plots still need graphics support such as Xvfb plus `--display`/`--platform offscreen`.

### Stream inputs and transport selectors

BNC can ingest NTRIP, direct TCP, local UDP, and serial streams. Its NTRIP selector values are `1` (Rev1/TCP), `2` (Rev2/TCP), `2s` (Rev2/TLS), `R` (Rev2 RTSP/RTP), and `U` (Rev2 UDP); the last two may slightly reduce latency but do not work through proxies and may lose data.

Direct TCP, UDP, and serial inputs appear in the stream table with protocol markers `N`, `UN`, and `S`. The `mountPoints` CLI key accepts a semicolon-separated stream list, so a headless job can be configured without first creating a GUI file:

```sh
bnc --nw --conf /dev/null --key mountPoints \
  "//user:pass@caster.example:2101/MOUNT RTCM_3.3 XXX 50.09 8.66 no 2"
```

### Decoder override and byte-preserving modes

BNC normally chooses `RTCM_2.x`, `RTCM_3.x`, or `RTNET` from sourcetable metadata, but the decoder field is editable when that metadata is wrong. `ZERO` bypasses decoding for raw forwarding, while `ZERO2FILE` both forwards and writes daily files named from the mountpoint and date; these modes are also required when an otherwise unrecognized format is sent to a local TCP port or re-uploaded.

### Configuration precedence and headless operation

The default Unix/macOS configuration is `${HOME}/.config/BKG/BNC.bnc`. `--conf FILE` selects another file, `--nw` runs without a window, and repeated `--key NAME VALUE` options override the file without modifying it; PPP keys require the `PPP/` prefix, and values containing spaces or semicolon-separated lists must be quoted.

Using `--conf /dev/null` starts from defaults for an all-CLI job. `--file RAW` replays a BNC raw recording and implicitly enables no-window mode, while separate `--conf` files allow several BNC jobs to run concurrently.

### Active configuration and live rereads

GUI fields, the active running configuration, and the configuration file are separate layers: editing the GUI or disk file does not generally alter a running job. A periodic `onTheFlyInterval` rereads only `mountPoints`, `outWait`, `outSampl`, and `outFile`, allowing stream selection and synchronized-engine output settings to change without stopping unrelated threads.

### TLS certificate layout

`sslCaCertPath` names a directory whose `.crt` and `.pem` files become BNC's CA database. Mutual TLS client material in `sslClientCertPath` must be named `<hostname>.<port>.crt` and `<hostname>.<port>.key`; password-protected private keys are unsupported, and `sslIgnoreErrors=2` disables authorization-error enforcement.

### Outage alarms and stream diagnostics

BNC treats 20 seconds without bytes as a broken connection and retries after 1, 2, 4, and successively doubled delays capped at 256 seconds. Explicit failure/corruption alarms require `adviseObsRate`; zero failure or recovery thresholds report immediately, and `adviseScript` receives mountpoint, `Begin_Outage`/`End_Outage` or `Begin_Corrupted`/`End_Corrupted`, and timestamps.

`miscScanRTCM=2` logs message numbers and sizes, ARP/APC coordinates, antenna metadata, and RINEX 3 observation types. `miscIntr` adds mean latency and gap statistics, but meaningful latency requires the host clock to be synchronized.

### BNC correction-file interchange

BNC's own plain-ASCII correction format uses GPS-timed blocks named `ORBIT`, `CLOCK`, `CODE_BIAS`, `PHASE_BIAS`, and `VTEC`; each epoch record includes the SSR update-interval indicator, record count, and source mountpoint. `corrPath` rotates these into `.ssr` files and `corrPort` serves the same synchronized representation locally; this is also the correction-file format accepted by BNC's offline PPP mode.

## RINEX, recording, and file processing

### Output overwrite and record/replay semantics

Starting BNC creates fresh outputs and overwrites same-named files unless the global `rnxAppend=2` option is set, which affects every file type rather than only RINEX. Output directories must already exist; BNC generally does not create missing ones.

`rawOutFile` records all streams in received order in one daily file, prefixing each binary block with reception time, mountpoint, format, and byte count. This is BNC's record/replay format for reproducing a real-time PPP situation with `--file`; it is not a RINEX-like post-processing format.

### RTCM-to-RINEX conversion guardrails

For RTCM 3 MSM observations, BNC needs the prospective observation types before it can write a complete RINEX 3/4 header. GLONASS MSM4 message 1084 lacks channel numbers, so conversion requires message 1020 or extended channel information from MSM5/7; RTCM 2 types 20/21 likewise require GPS/GLONASS broadcast ephemeris from 1019/1020.

RTCM 3 legacy messages 1001, 1003, 1009, and 1011 without an ambiguity field produce invalid RINEX values modulo 299792.458. BNC always labels RINEX 3 observation files as mixed, and forcing RTCM 2 into RINEX 3/4 is discouraged because RTCM 2 lacks tracking-mode attributes.

### RINEX skeleton selection

At startup and midnight BNC can fetch a public header skeleton from NET field 7 of the caster table. A personal skeleton named from the mountpoint's first nine characters for RINEX 3/4 or first four for RINEX 2 overrides the public one completely; `rnxSkelPath` changes its lookup directory and `rnxOnlyWithSKL=2` suppresses output when none is available.

Without a skeleton, RINEX 3/4 MSM conversion writes only BNC's default observation-type selection. A personal skeleton must omit `TIME OF FIRST OBS`; it should include `RINEX VERSION / TYPE` and `END OF HEADER` and normally provide the station, receiver, antenna, coordinates, eccentricity, and `SYS / # / OBS TYPES` records.

### RINEX file rotation and version mapping

`rnxIntr` controls file duration, `rnxSampl` controls epoch sampling, and zero sampling stores every received epoch. `rnxScript` runs when an interval closes—or on reconnection after an outage—and receives the completed path as `$1` on Unix or `%1` on Windows.

When producing RINEX 2, `rnxV2Priority` resolves the many RINEX 3/4 tracking attributes to one signal per band, with system/frequency forms such as `G:12&PWCSLX G:5&IQX`. The reverse conversion is not standards-clean: unknown RINEX 2 tracking attributes are left blank in RINEX 3/4.

### RINEX editing and quality control

The `Edit/Concatenate` action can merge observation or navigation files, reconcile differing observation-type headers, resample, trim, select signals, and conditionally replace marker, antenna, or receiver metadata. `Analyze` produces multipath, SNR, availability, elevation, and PDOP results; signal selectors use forms such as `G:1C&5X C:2I&6I`.

```sh
bnc --nw --conf /dev/null \
  --key reqcAction Edit/Concatenate \
  --key reqcObsFile 'Input/*.rnx' \
  --key reqcOutObsFile Output/hour.rnx \
  --key reqcSampling '30 sec'
```

### SP3 comparison behavior

BNC compares only epochs present in both SP3 files and never interpolates missing orbit epochs. It reports radial, along-track, and out-of-plane differences, reduces clock differences by the radial orbit component, and computes clock RMS after both per-epoch all-satellite and per-satellite all-epoch offsets; exclusions accept entries such as `G05,G31,R`.

## Engine feeds and rover feedback

### Synchronized and immediate engine feeds

`outPort` serves synchronized plain-ASCII observations on `127.0.0.1`; each epoch is keyed by GPS week/seconds and contains RINEX-style code, phase, Doppler, strength, and slip fields grouped by mountpoint. `outWait` bounds how long BNC collects an epoch, and observations arriving later are dropped from this feed but are still retained in RINEX files.

`outUPort` instead forwards each decoded observation immediately and puts the GPS time tag in every record. `outSampl` applies to synchronized output, while `outFile` saves that same format and is one of the few paths that can be rotated by a live configuration reread.

### Serial rover output and VRS GGA

For serial output, `serialAutoNMEA=Auto` forwards GGA from the connected rover, while `Manual GPGGA` or `Manual GNGGA` synthesizes it from the stream-table latitude/longitude plus `serialHeightNMEA`. These modes operate only when the stream has `nmea=yes`; a manual sampling value of `0` sends one initialization GGA, whereas many VRS services require a recurring interval.

## PPP and correction products

### PPP input contract and fallback

Real-time PPP requires RTCM 3 observations/navigation plus RTCM-SSR or IGS-SSR orbit/clock corrections referenced to the satellite antenna phase center, not center of mass. If corrections are absent BNC silently performs SPP; separately selected bias or VTEC streams override those topics from the main correction stream, otherwise the main stream is used when it carries them.

BNC supports uncombined and ionosphere-free PPP for GPS, GLONASS, Galileo, and BDS, and PPP ambiguity resolution for GPS, Galileo, and BDS. Wrong or outdated ephemerides are rejected, unhealthy ones remain usable with a log warning, and an IOD-SSR change causes PPP to reset all ambiguities.

### PPP replay, coordinates, and antenna corrections

Post-processing PPP accepts RINEX 2/3/4 observation and navigation files plus BNC-format correction, bias, and ionosphere files; the raw `--file` path instead replays a previously recorded real-time job for debugging. A coordinates-file row is keyed by the real-time mountpoint or the RINEX station's first nine/four characters; zero XYZ marks an unknown/mobile position, and supplied NEU eccentricities make output refer to the marker rather than the antenna reference point.

ANTEX corrections require both `PPP/antexFile` and the coordinates row's fixed-width 20-character antenna/radome name. Receiver type is otherwise optional but is required when writing SINEX troposphere output.

### PPP observation and timing controls

Per-constellation observation modes include uncombined `Pi&Li`, single-frequency `P1&L1`, and ionosphere-free `P3&L3`; editable forms such as `P125&L125` select explicit bands, while station-specific signal priorities choose tracking attributes. `PPP/corrWaitTime` can buffer epochs until sufficiently recent clock corrections arrive—half the correction update interval is suggested—trading added latency for less high-frequency noise and lower computation.

`PPP/seedingTime` fixes a known stationary coordinate during startup for Quick-Start convergence. The same setting bridges any solution gap longer than the hard-wired 60-second limit by fixing the latest solution for the seeding period, so it is unsuitable for a rover that may move during the gap.

### PPP ambiguity resolution and multi-station output

PPP-AR uses Best Integer Equivariant ambiguities and can gate fixing by minimum epochs, minimum satellites, maximum fractional distance, and maximum BIE sigma; `PPP/arUseYaw=2` takes satellite yaw from SSR phase-bias messages instead of the standard attitude model. `PPP/staTable` runs multiple station filters in one job and assigns each station its coordinate/troposphere noise, local NMEA port, and signal priorities.

PPP results can be written as daily per-station `.ppp` logs (`normal`, `debug`, or `all` detail), paired GPGGA/GPRMC `.nmea` streams/files, and SINEX TRO files. SINEX TRO output additionally needs interval, sampling, three-character analysis center, one-character solution ID, and receiver metadata from the coordinates file.

### Correction combination limits

All inputs to `cmbStreams` must be APC-referenced and real-time broadcast ephemeris must also be available. BNC combines only clocks: the orbit is copied from one input and its source can switch on outage; corrections arriving later than one combination sampling interval are ignored. Provider, Solution, or IOD changes reset that center's satellite-clock offsets in the Kalman adjustment.

`Filter` (Kalman) and `Single-Epoch` methods are available. A stream weight above `1` enlarges its pseudo-observation sigma and down-weights it, while clock-residual and orbit-displacement thresholds reject outliers; a single correction input is a supported merge-with-ephemeris mode for producing SP3/Clock RINEX rather than a combination.

### Internal validation of a combination

Setting the PPP correction source to `INTERNAL` feeds the not-yet-uploaded combined correction product directly into BNC's PPP engine for live spatial validation. When using a single correction stream only to create SP3/clock products, BNC warns against also pulling an equivalent backup correction stream because only one such source is allowed in that mode.

### RTNET engine bridge

To generate SSR from an external network engine, BNC accepts an `RTNET` ASCII stream of precise IGS20 ECEF orbits and clocks on an IP input. Epochs begin with `*`, satellite records carry counted key/value groups such as `APC`, `CoM`, `Clk`, `Vel`, `CodeBias`, `PhaseBias`, and yaw, and `EOE` terminates the epoch; unknown counted keys are skipped for forward compatibility.

The RTNET sampling interval should not exceed 15 seconds to avoid streaming timeouts. BNC combines the precise state with live broadcast ephemeris, deliberately waits 60 seconds before adopting a newly received ephemeris set so rovers can obtain the same IOD, then encodes RTCM-SSR or IGS-SSR for upload.

### SSR upload sampling and product references

Uploaded corrections default to APC but can be marked as CoM, may target IGS20 or configured regional/custom Helmert frames, and carry explicit SSR Provider, Solution, and IOD identifiers. `uploadSamplRtcmEphCorr=0 sec` emits combined orbit-and-clock messages at every incoming epoch; a nonzero value emits separate orbit and clock messages, with clocks retaining the incoming rate.

SP3 output is supposed to be CoM-referenced, so an ANTEX path is required to convert an APC correction product; without it BNC writes APC-referenced positions instead. SP3 and Clock RINEX clocks omit the conventional periodic relativistic correction, SP3 files include epoch headers even through outages, and their first-header epoch count may require repair before post-processing.

### Ephemeris and raw-stream uploads

BNC can aggregate received navigation messages into a selected-system RTCM 3 ephemeris stream (`G`, `GRE`, or `ALL`) with a default five-second full-set repetition; it rejects ephemerides outside constellation-specific age windows or failed plausibility checks but retains unhealthy data with a warning. Its raw-upload table separately provides NtripServer-style byte-for-byte forwarding from any selected input, using `ZERO` or `ZERO2FILE` when no recognized decoder applies.

