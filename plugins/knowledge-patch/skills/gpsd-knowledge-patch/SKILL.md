---
name: gpsd-knowledge-patch
description: gpsd 3.27 compatibility. Use for gpsd work.
license: MIT
version: "3.27"
metadata:
  author: Nevaberry
---

# gpsd Knowledge Patch

Baseline: gpsd through 3.25; covers later releases through the latest documented state, including the 3.27.6 development stream.

Use this skill for daemon deployment, protocol consumers, libgps clients, receiver configuration, PPS/NTP/chrony integration, capture and replay, and post-processing. Read the task-specific reference before relying on defaults or wire formats.

## Reference index

| Reference | Topics |
|---|---|
| [Daemon architecture](references/daemon-architecture.md) | Device lifecycle, hotplug protocol, sniffing and drivers, normalized state, exporters, privilege boundaries |
| [Daemon operation](references/daemon-operation.md) | Source URLs, serial framing, passive/nowait modes, control socket, D-Bus, time sources, client timeouts |
| [Installation and building](references/installation-and-building.md) | SCons, dependencies, install layout, minimal and cross builds, permissions, udev, tests |
| [JSON protocol](references/json-protocol.md) | Framing, VERSION/WATCH/POLL/DEVICE, TPV/SKY/GST/ATT/IMU/PPS, RTCM, AIS, SUBFRAME |
| [Client programming](references/client-programming.md) | libgps C API, buffering, shared memory, gpsmm, Python binding, endpoints, units |
| [Receiver hardware and control](references/receiver-hardware-and-control.md) | gpsctl, direct access, binary commands, PPS transport, firmware and device-specific setup |
| [ubxtool](references/ubxtool.md) | Protocol versions, configuration layers, persistence, logging, survey-in, RTCM3, signals, timepulse |
| [Time service](references/time-service.md) | Kernel PPS, SHM security, ntpd/NTPsec/chrony, calibration, native GPSD refclock, PTP coexistence |
| [Precise point positioning](references/precise-point-positioning.md) | Raw observations, gpsprof averaging, u-blox/GREIS setup, RINEX acquisition, PPP services |
| [NMEA protocols](references/nmea-protocols.md) | GGA/GNS/GSA/GSV/RMC/VTG semantics, versioned fields, error sentences, proprietary forms |
| [Troubleshooting](references/troubleshooting.md) | udev, systemd activation, remote sockets, reproducible captures, clock lag, stable device paths |
| [Release compatibility and security](references/release-compatibility-and-security.md) | CVEs, API corrections, deprecations, protocol/receiver changes, hotplug and development changes |
| [Monitoring and profiling tools](references/monitoring-and-profiling-tools.md) | cgps, gpsmon, gpsprof, packet views, PPS diagnostics, latency plots |
| [Data pipeline tools](references/data-pipeline-tools.md) | gpscat, gpspipe, gps2udp, gpsdecode, gpsfake, gpsrinex, offline processing |

## Critical compatibility and security

- Use 3.27.1 or later for untrusted input. It fixes CVE-2025-67268 in NMEA2000 parsing and CVE-2025-67269 in NovAtel parsing.
- Do not infer API compatibility from the 3.27 release number alone. Version values were corrected in 3.27.3, changed to 16.1 in 3.27.4, and corrected again in 3.27.5.
- C clients must check `GPSD_API_MAJOR_VERSION` and `GPSD_API_MINOR_VERSION`; reject an unknown major version at build time.
- Keep the daemon, command-line clients, and libraries on the same GPSD version. Remove an old installation completely before switching between packages and source builds.
- The package named `gpsd` on PyPI is unrelated and obsolete; obtain GPSD from a distribution or its source tree.
- `gps_send()` is deprecated; use `gps_stream()` for watch policy. The older request/response `gps_query()` is removed, and the current streaming read API is `gps_read()`.
- The `Lexer()` FFI interface was deprecated in October 2025. `gpsmon` is officially deprecated since 3.26, although it remains useful for low-level diagnostics.
- TPV `alt` is deprecated and undefined. Use `altHAE` or `altMSL`.
- GPSD's RTCM3 JSON dump is incomplete and buggy; never treat it as a production decoding interface.
- Since 3.26, u-blox, RTCM104v2, and RTCM104v3 drivers are unconditional. RTCM3.2 and chunked NTRIPv2 input are supported; SPARTNv2 is initial and disabled by default.

## Daemon lifecycle and safe operation

GPSD is demand-driven unless `-n`/`--nowait` is used. A watch opens a pooled sensor; without nowait, an idle sensor is closed but stays available for later activation. Use nowait for reference-clock service.

There is no receiver-type or serial-settings configuration file. GPSD sniffs checksummed packets and hunts serial parameters. Driver selection can change packet by packet, and multiple protocols can share one wire.

Use `-b` when automatic baud changes or wake-up strings might wedge fragile hardware. `-p` suppresses automatic receiver configuration but still permits explicit changes; receiver settings changed by GPSD may persist after exit and generally cannot be restored automatically.

Useful startup and inspection commands:

```sh
gpsd -l
gpsd -D 5 -N -n /dev/ttyUSB0
gpsd -f 8O1 -s 115200 /dev/ttyUSB0
```

The local control socket processes one operation per line:

```text
+/dev/ttyUSB0
-/dev/ttyUSB0
!/dev/ttyUSB0=<control-string>
&/dev/ttyUSB0=<paired-hex-digits>
```

Each operation returns `OK` or `ERROR`. `+` and `-` alter the device pool, `!` writes a textual control string, and `&` writes hexadecimal binary data. A startup with no source requires `-F`; otherwise it fails.

`SIGHUP` closes all device and client connections, reconnects pooled devices, and resumes service. Clients must reconnect. Nonreading clients are detached; unassigned clients time out after 60 seconds, polling clients after 15 minutes, while watchers and raw clients have no inactivity timeout.

## Data sources and hotplug

GPSD accepts serial/USB paths, `/dev/ppsN` alongside a local GPS, `tcp://`, listening `udp://`, authenticated `ntrip://`, `dgpsip://`, remote `gpsd://`, and Linux `nmea2000://` SocketCAN sources. Configure CAN before starting GPSD.

The device hook is called on demand-driven transitions:

```text
/etc/gpsd/device-hook <device> ACTIVATE
/etc/gpsd/device-hook <device> DEACTIVATE
```

With systemd socket activation, stopping `gpsd.service` is not enough; `gpsd.socket` can restart it. Stop both for manual debugging. If systemd owns port 2947, `-G` alone does not expose it remotely—change the socket listener and firewall as well.

## JSON protocol essentials

Requests are US-ASCII, begin with `?`, and are limited to 80 characters excluding newline. Responses end in CR-LF. The default maximum response is 10,240 characters including the terminator; reject a truncated response as invalid JSON.

```text
?VERSION;?DEVICES;
?WATCH={"enable":true,"json":true,"device":"/dev/ttyUSB0"};
```

Every connection receives `VERSION`; validate both `proto_major` and `proto_minor`. Bare `?WATCH;` reports policy. A WATCH change is followed by `DEVICES`; `enable` defaults true and `json` false.

Treat reports as incremental, presence-gated state:

- `TPV.mode` is always present, but several progressively populated TPVs can describe one epoch. Require a 2D/3D fix and initially three consecutive 3D fixes before trusting time.
- `libgps` uses `NAN` for unknown floating values; use `isfinite()`.
- `status` refines rather than replaces `mode`. Gate every optional TPV field on presence.
- `SKY.nSat` counts array entries; `uSat` counts satellites used. Prefer `gnssid` plus `svid` over ambiguous NMEA-style PRNs.
- `ATT` is GNSS-epoch synchronized; `IMU` is emitted promptly and may have arbitrary or out-of-order device timestamps.
- `TOFF` and `PPS` pair source and host timestamps. PPS also carries precision, SHM key, and optional quantization error.
- `POLL` is cached, requires an active WATCH, and can expose a partially accumulated NMEA epoch or data one cycle stale.
- Raw level 1 passes NMEA/AIVDM and hex-dumps binary; level 2 emits binary verbatim. Neither raw mode dumps RTCM2/3.

## Client implementation pattern

```c
#include <gps.h>

struct gps_data_t gpsdata;
if (gps_open("localhost", DEFAULT_GPSD_PORT, &gpsdata) != 0) {
    /* inspect errno */
}
gps_stream(&gpsdata, WATCH_ENABLE | WATCH_JSON | WATCH_DEVICE,
           "/dev/ttyUSB0");
```

Link with `-lgps`; adding `-lm` is safe and is required on systems that do not propagate libgps's math dependency. Call `gps_close()` only after a successful open.

`gps_read()` can receive fragments, one object, or multiple objects plus a tail. libgps retains incomplete input and accumulates decoded fields in one `gps_data_t` blackboard. `PACKET_SET` only means at least one complete response arrived; compare timestamps and clear state deliberately when per-read semantics matter.

`gps_waiting()` takes microseconds and returns false for timeout or error; inspect `errno`. Drain more often than one report cycle, especially for AIS. Under `WATCH_RAW`, returned buffers need not be NUL-terminated.

Shared-memory mode uses `GPSD_SHARED_MEMORY` as the host. It has `gps_fd == -1`, immediate snapshots, and no device filtering, stream policy, activation notices, or packet notices. Prefer a simple `gps_read()` loop because waiting then reading races.

Python sessions expose `stream()`, `read()`, iteration, text in `response`, bytes in `bresponse`, and decoded key/attribute access in `data`:

```python
import gps

session = gps.gps(host="localhost", port="2947")
session.stream(flags=gps.WATCH_JSON)
for report in session:
    print(report)
```

## Receiver changes and ubxtool

Prefer daemon-mediated `gpsctl` for ordinary access. Use `-f` for direct access, with an explicit path and device write permission. Combined changes run in mode, baud, cycle, then control-string order. Reset must be standalone and include both `-r` and a forced `-t TYPE`.

For `ubxtool`, first poll `MON-VER` and set the exact protocol version; the default is 10 and can fail silently on newer receivers:

```sh
ubxtool -p MON-VER
export UBXOPTS="-P 27 -v 2"
```

Pre-Gen9 devices use compound `UBX-CFG-*`; Gen9 varies by firmware; Gen10+ uses configuration items. Item access needs protocol 27+. `-g` layer indexes are 0 RAM, 1 BBR, 2 flash, and 7 default; `-z`/`-x` layer masks use bits 1 RAM, 2 BBR, and 4 flash.

Always read back a write: NAK proves invalidity, ACK does not prove application, and some successful writes have no ACK. Choose port-specific `CFG-MSGOUT-*_<port>` keys on newer firmware. Prefer explicit persistent layers over legacy `SAVE`, because `UBX-CFG-CFG` is deprecated from protocol 23.01.

## Precision timing

Hardware PPS over serial requires the pulse wired to DCD or RI and a handshake-capable cable. USB data alone does not carry PPS. Verify with `gpsmon`, `ppscheck`, and daemon debug level 5.

GPSD normally uses NTP SHM units 0/1 when privileged and 2/3 otherwise. Units 0/1 are private (`0600`); units 2+ are normally public (`0666`) and allow local sample injection. Match unit ownership to the threat model.

Chronyd must start before GPSD for SOCK transport. For SHM, set PPS precision explicitly because chronyd cannot obtain it from the SHM structure. Never deploy placeholder offsets such as `0.9999`; measure a stable coarse-source offset for at least four hours.

NTPsec's native GPSD refclock supports in-band mode 0, strict PPS-plus-in-band mode 1, and experimental fallback mode 2. PPS-only secondary units are 128+ and depend on primary `unit % 128`.

## Build and installation

SCons is single-phase: install can rebuild, so repeat the same feature options. Run tests before installation, and install Linux hotplug integration separately:

```sh
scons && scons check
scons install
scons udev-install
```

`minimal=yes` makes Boolean features default false, except NMEA0183 remains built. `timeservice=yes` forces nowait and PPS support but omits most receiver drivers, so explicitly enable the required binary driver.

For cross-builds, `target` is the toolchain prefix and `sysroot` supplies target headers/libraries. `includedir` changes only the install destination; use `CPPFLAGS` and `LDFLAGS` for prerequisite lookup.

Serial nodes normally need mode `0660` with a group matching compiled `gpsd_group`. Set `gpsd_user` and `gpsd_group` deliberately and ensure udev assigns the same group.

## Capture, replay, and diagnosis

Use `gpspipe -R` for byte-exact capture; `gpscat` default output escapes nonprinting bytes and adds a newline. Replay with `gpsfake`, minimize failing logs, then verify decoder failures with `gpsdecode`.

```sh
gpspipe -R -n 100 > receiver.log
gpsfake -1 -P 2948 receiver.log
gpsdecode < receiver.log
```

`gpsfake` loops by default and creates one pseudo-TTY per log. Use `-1` for one pass, `-S` for realistic pacing, and `-P` to avoid the production port. Leading `#Serial:`, `#Transport:`, `# Date:`, and `Delay-Cookie` headers control replay.

For offline RINEX, preserve raw bytes, decode to GPSD JSON, then pass the JSON file to `gpsrinex -F`. PPP collection needs supported raw observations and intact receiver configuration for the full run; 30-second epochs are the documented default cadence for long static captures.
