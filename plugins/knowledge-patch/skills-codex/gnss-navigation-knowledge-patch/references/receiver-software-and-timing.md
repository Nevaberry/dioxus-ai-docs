# Receiver Software and Timing Integration

## Linux GNSS time service

### Serial and PPS inputs with gpsd and ntpd

For classic `ntpd`, `gpsd` supplies coarse serial time through SHM refclock unit 0 (`127.127.28.0`) and optional pulse-per-second timing through unit 1 (`127.127.28.1`). Start `gpsd` with `-n` so it opens the receiver immediately; for hardware PPS, enable the kernel PPS line-discipline and GPIO clients, attach line discipline 18 to the GPIO device, and verify that `/dev/pps0` appears.

```sh
gpsd -n /dev/ttyACM0
ldattach 18 /dev/deviceNAME
```

```conf
server 127.127.28.0 minpoll 4 maxpoll 4
fudge 127.127.28.0 time1 0.0 refid GPS
server 127.127.28.1 minpoll 4 maxpoll 4
fudge 127.127.28.1 refid PPS
```

## Android measurement capabilities

### Raw support is not a complete observation contract

Raw GNSS measurements are mandatory on devices running Android 10/API 29 or later, and on Android 9 or earlier devices whose hardware year is 2016 or newer. Individual fields can still be chipset-dependent and optional—including pseudorange and pseudorange rate, navigation messages, AGC, accumulated delta range/carrier phase, and multiple frequencies—so software must test the available measurements rather than infer them from OS-level raw support.

Dual-frequency reception also does not imply carrier-phase output. The documented device landscape says most flagship phones support L1 and L5, while ADR is provided by Pixel flagships and other major flagships that do not use Qualcomm Snapdragon chipsets.

### Android exposes model-level antenna corrections

From Android 11/API 30, `GnssAntennaInfo` exposes phase-center-offset coordinates, phase-center-variation corrections, and signal-gain corrections that can be applied to raw observations. For privacy, these characteristics describe the device model, not the individual handset.

## Assistance and mobile logging

### SUPL sample requests real-time ephemeris by position

The `supl-client` sample's `SuplTester` opens a TCP connection to `supl.google.com`, submits an LPP SUPL request for a supplied latitude and longitude, and prints the server response to obtain real-time ephemeris.

### Android raw logs share a desktop-processing format

GPSTest can log NMEA, raw measurements, navigation messages, and location data in a format accepted by the GPS Measurement Tools suite; the `android_rinex` Python converter accepts the same CSV format from GPSTest or GNSSLogger and emits RINEX. The original open-source GNSSLogger is no longer maintained, although a separately distributed proprietary fork remains available.

## Desktop measurement analysis

### GNSS Analysis uses reported uncertainty and configurable truth

The desktop GNSS Analysis executable bundles MATLAB Runtime, so MATLAB itself is not required. It computes weighted-least-squares position from raw pseudoranges using each measurement's reported uncertainty, and its clock analysis can reference an automatically computed mean position, user-entered latitude/longitude/altitude, or truth PVT from an NMEA file.

Its report checks API implementation, received signal, clock behavior, and measurement accuracy against benchmarks; interactive views cover per-constellation C/N0, sky position, pseudorange and pseudorange-rate errors, receiver-clock offsets, and carrier phase. Multiple logs can also be compared side-by-side by C/N0.

## GNSS-SDR receiver construction and outputs

### Configuration defines the receiver graph

Each GNSS-SDR configuration file defines a receiver as a GNU Radio flow graph. The control plane dynamically activates and deactivates channels as satellites enter or leave availability, while the processing plane is composed from global sampling/telecommand/assistance settings, signal source and conditioning stages, acquisition, tracking, telemetry decoding, observables, PVT, and monitoring blocks.

### Live or recorded samples and live outputs

A signal source can be a USB- or Ethernet-connected RF front-end or a stored raw-sample file, and the receiver processes it through acquisition, tracking, navigation-message decoding, observables, and position. Processing output can be stored as RINEX or served in real time as RTCM 3.2 over TCP/IP, while navigation results are stored as KML and GeoJSON.
