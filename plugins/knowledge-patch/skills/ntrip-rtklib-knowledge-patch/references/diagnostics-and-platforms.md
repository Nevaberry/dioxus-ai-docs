# Diagnostics, Output, and Platforms

## Contents

- [GUI availability](#gui-availability)
  - [Qt-based Linux GUI](#qt-based-linux-gui)
- [Solution output and plotting](#solution-output-and-plotting)
  - [Positioning-solution record semantics](#positioning-solution-record-semantics)
  - [Solution-status diagnostics](#solution-status-diagnostics)
  - [RTKPLOT comparison and live diagnostics](#rtkplot-comparison-and-live-diagnostics)
  - [POS2KML filtering](#pos2kml-filtering)
- [Visibility analysis](#visibility-analysis)
  - [TLE-based visibility analysis](#tle-based-visibility-analysis)
- [Converter isolation](#converter-isolation)
  - [Isolate conversion from solving in 2.4.3 b33 diagnostics](#isolate-conversion-from-solving-in-243-b33-diagnostics)
- [Trace and failure diagnosis](#trace-and-failure-diagnosis)
  - [Trace levels and record severity](#trace-levels-and-record-severity)
  - [RTKNAVI base-position and navigation state](#rtknavi-base-position-and-navigation-state)
  - [Distinguishing missing observations from a zero base position](#distinguishing-missing-observations-from-a-zero-base-position)
  - [Q=0 input-mismatch signatures](#q0-input-mismatch-signatures)
  - [Q=2 with immediate all-satellite outliers](#q2-with-immediate-all-satellite-outliers)
  - [Demo5 chi-square behavior](#demo5-chi-square-behavior)
  - [RTKPLOT plot prerequisites](#rtkplot-plot-prerequisites)
  - [Inspecting Demo5 SNR values in code](#inspecting-demo5-snr-values-in-code)
- [Build and device integration](#build-and-device-integration)
  - [Demo5 console-app layout on Raspberry Pi](#demo5-console-app-layout-on-raspberry-pi)
  - [Branch-specific Qt build files](#branch-specific-qt-build-files)
  - [u-blox UART settings can throttle USB](#u-blox-uart-settings-can-throttle-usb)
  - [Sharing an exclusively owned receiver port](#sharing-an-exclusively-owned-receiver-port)
  - [Timestamped raw logging without a file URL](#timestamped-raw-logging-without-a-file-url)
  - [Single-position fallback output](#single-position-fallback-output)

## GUI availability

### Qt-based Linux GUI

A Qt-based RTKLIB GUI is now available with particular emphasis on Linux, providing a GUI path separate from the Windows-oriented VCL applications.

## Solution output and plotting

### Positioning-solution record semantics

The `%` field-indicator line defines the body layout and must not be deleted; solution time is true signal-reception time, not the receiver-clock reading. Quality is `1` fixed, `2` float, `3` reserved, `4` DGPS or SBAS-corrected, and `5` single; `sdne`, `sdeu`, and `sdun` store the signed square roots of absolute covariance terms, so each covariance is reconstructed as `sign(v) * v^2`, and the reported ratio is second-best divided by best squared ambiguity residual.

### Solution-status diagnostics

Status level `1` selects filter states and level `2` selects measurement residuals; RTKNAVI places this file in its current directory and RTKPOST beside its solution output. Parsers should recognize the record families and field order below, especially `$SAT`'s ambiguity state (`0` no data, `1` float, `2` fixed, `3` hold), slip/parity flags, and cumulative outage, slip, and rejection counts.

```text
$POS,week,tow,stat,posx,posy,posz,posxf,posyf,poszf
$VELACC,week,tow,stat,vele,veln,velu,acce,accn,accu,velef,velnf,veluf,accef,accnf,accuf
$ION,week,tow,stat,sat,az,el,ion,ion-fixed
$TROP,week,tow,stat,rcv,ztd,ztdf
$HWBIAS,week,tow,stat,frq,bias,biasf
$SAT,week,tow,sat,frq,az,el,resp,resc,vsat,snr,fix,slip,lock,outc,slipc,rejc
```

### RTKPLOT comparison and live diagnostics

RTKPLOT can open two solution streams and plot `solution-1 - solution-2`; an NMEA solution input must contain both GPRMC and GPGGA, and a remote RTKNAVI monitor is reached as a TCP client. Carrier-phase residual plots mark cycle slips in red and parity-unknown intervals in gray, while observation QC invokes the configured external command—TEQC options are the default—and that executable must be on `PATH` or beside the RTKLIB binaries.

### POS2KML filtering

`pos2kml` can select a quality flag with `-q`, decimate by seconds with `-i`, apply north/east/height offsets with `-f`, emit altitude with `-a` or geodetic altitude with `-ag`, and timestamp tracks in GPST or UTC with `-tg` or `-tu`. Input comment lines may start with `%`, `#`, or `;`.

```sh
pos2kml -tu -ag -i 1 -q 1 -f 0 0 1.5 -o fixed.kml rover.pos
```

## Visibility analysis

### TLE-based visibility analysis

RTKPLOT 2.4.2 adds predicted satellite-visibility analysis from NORAD two- or three-line TLE data. It requires a separate satellite-number file mapping TLE catalog numbers to GNSS IDs and a configured `Lat/Lon/Hgt` receiver position; the mapping may need maintenance when constellation assignments change, and TLE positions can also backfill skyplots when broadcast ephemerides are absent.

## Converter isolation

### Isolate conversion from solving in 2.4.3 b33 diagnostics

In the supplied nine-data-set M8T benchmark, RINEX generated by official 2.4.3 b33 caused sharply lower fix rates in eight cases, while 2.4.2-generated RINEX passed to the same 2.4.3 solver restored the expected results. Compare converter versions and inspect cycle-slip indications before blaming the solver; loss of slip flags while filtering low-quality observations was the suspected cause, not a confirmed diagnosis.

## Trace and failure diagnosis

### Trace levels and record severity

In the GUI, start with `Output Debug Trace` level 2 for input and configuration failures, use level 3 for solution and ambiguity-resolution detail, and reserve level 4 for communication streams; level 5 includes large solution matrices, while level 1 merely repeats the Error/Warning view. Trace records beginning with `1` are errors and those beginning with `2` are warnings, so both must be inspected when the displayed error is generic.

### RTKNAVI base-position and navigation state

Selecting `RTCM Position` for a base stream that contains no RTCM position message can leave RTKNAVI running without a solution; its Error/Warning monitor reports `initial base station position error`. RTKNAVI also retains previously received navigation messages across stream changes, so colored satellite bars after changing mountpoints do not prove that the new stream carries ephemerides—use the monitor's `Nav Data` view to confirm fresh messages.

### Distinguishing missing observations from a zero base position

A missing rover observation file and a base RINEX header whose approximate XYZ is all zero can lead to the same immediate top-level failure. The trace distinguishes them: failure to open an observation file is a level-2 warning, whereas the later inability to establish the base position is the level-1 error; RTKCONV normally derives header coordinates from the initial observations plus navigation data unless a position is supplied explicitly, so missing navigation can produce the zero header.

### Q=0 input-mismatch signatures

If rover and base observation periods do not overlap, processing can run to completion at Q=0; the trace's `age of differential` exposes the time separation to the nearest base epoch. A wrong navigation file can produce the same Q=0 outcome but instead reports `no common satellites`.

### Q=2 with immediate all-satellite outliers

When every satellite has extremely large residuals from the first epoch and the solution remains float at Q=2, recheck the explicitly supplied base coordinates before tuning ambiguity resolution. This signature usually means coordinates from a different data set or base were reused.

### Demo5 chi-square behavior

`point pos error (chi-square error ...)` indicates poor single-position residual consistency. In Demo5 this check was changed from a fatal error to a warning so a low-quality value can still be returned; improving the raw observations is the corrective action rather than suppressing the diagnostic.

### RTKPLOT plot prerequisites

RTKPLOT can estimate multipath only when both L1 and L2 observations are present, while satellite-elevation plots require valid navigation data. A loaded but invalid navigation file therefore still leaves elevation unavailable.

### Inspecting Demo5 SNR values in code

In the discussed Demo5 layout, `ssat` SNR entries use quarter-dB-Hz units; L1 is slot 0 and an enabled L5/E5a signal such as S5Q is slot 2. Older RTKCONV UI builds label that third-frequency selection `L3`.

```c
double l1_dbhz = rtk->ssat[sat - 1].snr[0] * 0.25;
double l5_dbhz = rtk->ssat[sat - 1].snr[2] * 0.25;
```

## Build and device integration

### Demo5 console-app layout on Raspberry Pi

The Pi-oriented demo5 tree places command-line applications under `app/consapp/<app>/gcc`, rather than the upstream-style `app/<app>/gcc` layout. Build and install the two resident applications independently:

```sh
cd RTKLIB/app/consapp/str2str/gcc
make
sudo cp str2str /usr/local/bin/
cd ../../rtkrcv/gcc
make
sudo cp rtkrcv /usr/local/bin/
```

### Branch-specific Qt build files

The 2.4.3 b34 UI rewrite invalidated the older Qt makefiles; builds without the later b34 Qt port cannot use the old top-level `qmake` recipe. In the later demo5 tree that imported that port, the Ubuntu 20.04 instructions require `build-essential`, `libpng-dev`, `qt5-default`, and `libqt5serialport5-dev`, then build and install all Qt applications from one directory:

```sh
cd RTKLIB/app/qtapp
qmake
make
./install_qtapp
```

These Qt GUIs do not expose every demo5-only configuration parameter, and the source's testing found RTKPLOT only partially functional, so do not assume feature parity with the other application variants.

### u-blox UART settings can throttle USB

A low configured baud rate on either u-blox UART can limit output bandwidth on every port, including USB, even when nothing is connected to that UART. Disable unused UARTs or give them adequate rates, and save the receiver configuration to flash.

### Sharing an exclusively owned receiver port

When `str2str` owns the Pi's USB serial device to feed corrections to the receiver, append `#<port>` to that serial output to expose bytes returning from the receiver on a local TCP port. RTKRCV or another `str2str` instance can then consume the TCP stream without trying to open the same serial device:

```sh
str2str -in 'ntrip://user:pass@caster.example:2101/MOUNT' \
  -out serial://ttyACM0:115200:8:n:1#1000
```

### Timestamped raw logging without a file URL

The demo5 Pi workflow accepts a bare filename as a `str2str` output; `%m`, `%d`, `%h`, and `%M` expand to month, day, hour, and minute. This records the receiver's byte stream directly for later PPK conversion:

```sh
str2str -in serial://ttyACM0 -out rover_%m%d_%h%M.ubx
```

### Single-position fallback output

Set `out-outsingle=on` to keep RTKRCV emitting a single-point position when a relative-mode job temporarily has no usable base or NTRIP corrections. This lets downstream logic continue receiving a degraded position instead of losing output entirely.

```text
out-outsingle =on
```

