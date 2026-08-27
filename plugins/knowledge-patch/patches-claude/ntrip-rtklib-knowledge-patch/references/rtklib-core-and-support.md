# RTKLIB Core, APIs, and Patch-Level Support

## Contents

- [Architecture and build-time capabilities](#architecture-and-build-time-capabilities)
  - [Portable core and platform boundary](#portable-core-and-platform-boundary)
  - [Compile-time capability selection](#compile-time-capability-selection)
  - [Position-mode names that are easy to misread](#position-mode-names-that-are-easy-to-misread)
  - [Directional and partial format support](#directional-and-partial-format-support)
  - [STRSVR receiver-to-RTCM conversion](#strsvr-receiver-to-rtcm-conversion)
  - [str2str TTY-as-file input](#str2str-tty-as-file-input)
  - [RTKRCV lifecycle hooks](#rtkrcv-lifecycle-hooks)
  - [rtklib-py RINEX object model](#rtklib-py-rinex-object-model)
- [Patch-level limits and correctness](#patch-level-limits-and-correctness)
  - [Demo5 GNSS/IMU code revisions](#demo5-gnssimu-code-revisions)
  - [RTCM MSM cell-mask ceiling](#rtcm-msm-cell-mask-ceiling)
  - [Constellation support depends on patch level](#constellation-support-depends-on-patch-level)
  - [Combined rover/base observation ceiling](#combined-roverbase-observation-ceiling)
  - [2.4.2 PPP and SSR correctness floors](#242-ppp-and-ssr-correctness-floors)
- [Embedding and 2.4.1 API changes](#embedding-and-241-api-changes)
  - [Library documentation boundary](#library-documentation-boundary)
  - [Core embedding entry points](#core-embedding-entry-points)
  - [APIs added in 2.4.1](#apis-added-in-241)
  - [APIs marked modified in 2.4.1](#apis-marked-modified-in-241)
- [License, toolchain, and 2.4.2 API changes](#license-toolchain-and-242-api-changes)
  - [License and Windows toolchain boundary](#license-and-windows-toolchain-boundary)
  - [APIs added in 2.4.2](#apis-added-in-242)
  - [APIs marked modified in 2.4.2](#apis-marked-modified-in-242)

## Architecture and build-time capabilities

### Portable core and platform boundary

The upstream 2.4.x library and command-line applications are ANSI C89. `-DWIN32` selects Winsock and Win32 threads; Unix-like builds use standard sockets and pthreads without that define. The GUI applications are C++ programs built around Embarcadero/Borland VCL, so the supplied GUI projects are Windows-oriented while other platforms are expected to build the command-line applications.

Core sources live in `src/`, receiver-specific decoders in `src/rcv/`, and each application has its own directory under `app/`; console builds provide a `gcc` subdirectory:

```sh
cd RTKLIB/app/rnx2rtkp/gcc
make
```

### Compile-time capability selection

Constellation support is selected with `ENAGLO`, `ENAQZS`, `ENAGAL`, and `ENACMP`; `NFREQ=n` controls the number of frequencies, `NEXOBS=n` the extra observation types, and `TRACE` enables debug tracing. The documented defaults for `NFREQ` and `NEXOBS` are both 3.

Add the selected definitions to a Unix makefile's `OPTS`, or to `BCC_Defines` in a Windows `.cbproj`; choose `-DLAPACK` or `-DMKL` to replace the internal matrix path with that backend:

```text
-DENAGLO -DENAQZS -DENAGAL -DENACMP -DNFREQ=3 -DNEXOBS=3 -DTRACE -DLAPACK
```

### Position-mode names that are easy to misread

`Single` uses code measurements with broadcast ephemerides and clocks and, in the documented 2.4.2 behavior, does not use carrier-phase smoothing. `Moving-Baseline` estimates the base position with `Single` and solves the rover-to-base separation without requiring the base's absolute position. `Fixed` and `PPP-Fixed` are residual-analysis modes, not names for ordinary RTK after integer ambiguities have fixed.

### Directional and partial format support

The 2.4.2 format boundary is asymmetric: BINEX is input-only and partial, NMEA 0183 is output-only, and SP3-c, IONEX, and EMS 2.0 are input-only. ANTEX 1.4 and NGS PCV are partial inputs, with antenna corrections limited to a hard-coded 5-degree elevation step; a listed format therefore must not be assumed to support round trips.

### STRSVR receiver-to-RTCM conversion

STRSVR can take a receiver's proprietary binary stream, convert it to RTCM 3, and publish it through an `NTRIP Server` output. Its message list uses `TYPE(interval)` entries, for example:

```text
1002(1),1019(1)
```

### `str2str` TTY-as-file input

When a Unix serial device is opened through a `file://` endpoint, configure the TTY externally; the stream suffix selects the receiver decoder. This example reads raw UBX and serves it on a local TCP port:

```sh
stty -F /dev/ttyUSB1 clocal raw speed 115200
str2str -in file:///dev/ttyUSB1#ubx -out tcpsvr://:22101
```

### RTKRCV lifecycle hooks

`misc-startcmd` and `misc-stopcmd` run shell hooks around RTKRCV operation, and the referenced scripts must have executable permission:

```text
misc-startcmd =../rtkstart.sh
misc-stopcmd  =../rtkshut.sh
```

### `rtklib-py` RINEX object model

The separate `rtklibexplorer/rtklib-py` implementation stores an observation epoch in `Obs` (`t`, `P`, `L`, `D`, `S`, and `sat`) and navigation state in `Nav`, whose `eph` collection holds GPS/Galileo/QZSS `Eph` records while `geph` holds GLONASS `Geph` records. Its `rnx_decode` class exposes `decode_nav()`, `decode_obsh()`, and `decode_obs()` for navigation, observation headers, and epochs; `next_obs()` advances and synchronizes base and rover observations even when their sampling rates differ.

## Patch-level limits and correctness

### Demo5 GNSS/IMU code revisions

The Demo5/rtklibexplorer `GNSS_IMU` work adds loosely coupled GNSS/IMU sensor fusion. Results published with the original code were revised again on 2025-12-18 after additional implementation errors were found, so use the latest code rather than the initially published version.

### RTCM MSM cell-mask ceiling

An MSM cell mask is limited to 64 entries, so `number_of_satellites * number_of_signals` must not exceed 64 in one message. STRSVR/STR2STR before 2.4.3 b31 could emit invalid MSM at larger products; even with later application fixes, callers of `gen_rtcm3()` must split such observations themselves and invoke the encoder multiple times.

### Constellation support depends on patch level

The original 2.4.2 could convert and plot BeiDou but could not use it in real-time or post-processed solutions; patch p7 added solution support. Version 2.4.2 p13 still accepts only BeiDou C01-C35 and Galileo E01-E30, whereas 2.4.3 b34 accepts BeiDou C01-C63 and Galileo E01-E36.

### Combined rover/base observation ceiling

In 2.4.2 p7 baseline modes, `MAXOBS=64` limits the sum of visible satellites from rover and base, not each receiver independently; surplus observations are discarded, so two sites seeing more than about 32 satellites each can lose usable data. Patch p8 addresses this restriction.

### 2.4.2 PPP and SSR correctness floors

Several patch levels change solution correctness: p4 fixes satellite antenna PCV being evaluated only at zero nadir; p7 fixes omission of the final satellite field in some RTCM SSR messages and incorrect ionosphere-free satellite antenna offsets; p11 fixes GLONASS/BeiDou ionosphere scaling in Single and PPP modes; and p13 fixes false orbit/clock IOD rejection with `Broadcast+SSR APC` or `Broadcast+SSR CoM`. On the last issue, the trace contains `inconsist ssr correction`.

## Embedding and 2.4.1 API changes

### Library documentation boundary

The manual's API appendix explicitly says it was not updated for 2.4.1, so `rtklib.h` and each implementation's header comment are authoritative for signatures, parameters, and return values. An embedded application includes `rtklib.h`, adds `-I rtklib_2.4.1/src`, and compiles or links the required RTKLIB source modules rather than relying on the appendix alone.

### Core embedding entry points

The solver lifecycle is `pntpos()` for standard positioning, `rtkinit()`/`rtkpos()`/`rtkfree()` for precise relative or PPP processing, and `postpos()` for file-oriented post-processing. Raw and RTCM streams use `init_raw()`/`input_raw()`/`free_raw()` and `init_rtcm()`/`input_rtcm2()` or `input_rtcm3()`/`free_rtcm()`, while resident applications are built on the `strsvr*` and `rtksvr*` lifecycle families and configuration is bridged with `loadopts()`, `getsysopts()`, and `setsysopts()`.

### APIs added in 2.4.1

The appendix marks these as additions: time screening and cleanup with `screent()` and `freenav()`; ionosphere/troposphere support with `ionppp()`, `ionmapf()`, `iontec()`, `readtec()`, `ionocorr()`, and `tropcorr()`; RINEX GEO/QZSS headers and body with `outrnxhnavh()`, `outrnxlnavh()`, and `outrnxhnavb()`; and almanac positioning with `alm2pos()`.

It also marks new Furuno/JAVAD stream and file decoders (`input_gw10()`, `input_gw10f()`, `input_javad()`, `input_javadf()`), solution-status cleanup via `freesolstatbuf()`, and stream proxy configuration via `strsetproxy()`.

### APIs marked modified in 2.4.1

Callers upgrading into 2.4.1 must recheck source declarations for the functions marked modified: `readrnx()`, `readrnxt()`, `outrnxnavh()`, `outrnxgnavh()`, `satpos()`, `satposs()`, and `decode_frame()`. The same warning applies to server lifecycle/status entry points `strsvrstart()`, `strsvrstop()`, `rtksvrstart()`, `rtksvrstop()`, `rtksvrostat()`, and `rtksvrsstat()`; the appendix identifies the change but does not describe its signature or compatibility.

## License, toolchain, and 2.4.2 API changes

### License and Windows toolchain boundary

Version 2.4.2 changes the package license from GPLv3 to the BSD 2-clause license plus the package's additional clauses, so consumers should review the supplied text rather than assume an unmodified stock BSD grant. The Windows projects now target Embarcadero C++ Builder XE2/XE3; Turbo C++ 2006 is no longer supported because its GUI string types are incompatible with 2.4.2.

### APIs added in 2.4.2

The appendix marks new signal/time helpers `satexclude()`, `testsnr()`, `setcodepri()`, `getcodepri()`, `bdt2time()`, `time2bdt()`, `gpst2bdt()`, `bdt2gpst()`, and `utc2gmst()`, plus encoder primitives `setbitu()`, `setbits()`, and `crc16()`.

RINEX and orbit additions are `outrnxcnavh()`, `init_rnxctr()`, `free_rnxctr()`, `open_rnxctr()`, `input_rnxctr()`, `tle_read()`, `tle_name_read()`, and `tle_pos()`. Receiver/message additions are `input_nvs()`, `input_nvsf()`, `input_binex()`, `input_binexf()`, `gen_nvs()`, `gen_rtcm2()`, and `gen_rtcm3()`.

PPP additions are `pppos()`, `pppnx()`, `pppoutsolstat()`, `windupcorr()`, and `pppamb()`; stream conversion adds `strconvnew()` and `strconvfree()`. Download support adds `dl_readurls()`, `dl_readstas()`, `dl_exec()`, and `dl_test()`, while QZSS LEX adds `lexupdatecorr()`, `lexreadmsg()`, `lexoutmsg()`, `lexconvbin()`, `lexeph2pos()`, and `lexioncorr()`.

### APIs marked modified in 2.4.2

Recheck declarations and callers for `obs2code()`, `code2obs()`, `eci2ecef()`, `antmodel()`, `sunmoonpos()`, `readrnx()`, `readrnxt()`, `outrnxobsh()`, `readsp3()`, and `strsvrstart()`. The appendix marks them modified but leaves exact signatures and compatibility to `rtklib.h` and the implementation header comments.

