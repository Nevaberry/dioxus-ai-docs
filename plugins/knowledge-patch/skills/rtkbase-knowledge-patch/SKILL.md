---
name: rtkbase-knowledge-patch
description: RTKBase 2.7.0 compatibility. Use for RTKBase work.
license: MIT
version: "2.7.0"
metadata:
  author: Nevaberry
---

# RTKBase Knowledge Patch

Baseline: RTKBase through 2.6.3; covers RTKBase 2.7.0 and current installation, hardware, surveying, streaming, and RTKLIB operational guidance.

## How to use this skill

Use the quick reference for common decisions and failure-prone operations. Open the
topic reference that matches the work before changing installer flags, service
units, receiver output, coordinates, correction streams, or RTKLIB configuration.

## Reference index

| Reference | Topics |
| --- | --- |
| [platform-and-installation.md](references/platform-and-installation.md) | Platform requirements, ready-to-flash images, installer modes, systemd topology, `settings.conf`, retention, GNSS/chrony/PPS time, ELT_RTKBase |
| [receivers-and-antennas.md](references/receivers-and-antennas.md) | Mosaic-X5, ZED-F9P, Unicore, receiver access, antennas, baselines, raw observations, diagnostics, RTK2GO credentials |
| [surveying-and-position.md](references/surveying-and-position.md) | Permanent coordinates, PPP, ELT coordinate behavior, WinRtkBaseUtils, full-day recording, RINEX and final products |
| [ntrip-and-rtcm.md](references/ntrip-and-rtcm.md) | NTRIP endpoints, RTCM selection, direct caster push, SNIP metadata, TCP/UDP/serial correction services |
| [rtklib-and-raspberry-pi.md](references/rtklib-and-raspberry-pi.md) | RTKLIB 2.5.0-EX, console and Qt builds, U-Blox preparation, `str2str`, VRS GGA, `rtkrcv` |

## Breaking changes and deprecations

### Update prerequisites

- RTKBase 2.7.0 supports Debian 13 (Trixie).
- Updating requires Debian 12, Ubuntu 24.04, or newer.
- Python versions earlier than 3.11 are deprecated.

Check the host OS and Python before attempting an in-place update. For a fresh
single-board-computer deployment, a published Armbian image is often the shortest
path to a known service layout.

### Coordinate changes stop services

In ELT_RTKBase, saving changed base coordinates stops every service. Main restarts
automatically only if it was running before the change; all other services remain
stopped and must be restarted explicitly. Changing coordinates or any other Main
setting also restarts built-in PPP refinement from the beginning.

### External receiver reconfiguration is hazardous

WinRtkBaseUtils `RTK.bat` and `HAS.bat` require **Rtcm tcp service**. Enable it only
for the operation and disable it afterward because it permits external receiver
reconfiguration. A failed or interrupted run can leave the receiver reconfigured;
reapply its base configuration before resuming service.

## RTKBase 2.7.0 changes

- Bundled RTKLIB is v2.5.0-EX.
- Septentrio Mosaic-X5 firmware 4.15 is supported. Its default credentials are
  login `basegnss` and password `basegnss!`.
- The Settings GUI TCP host address controls whether the GNSS receiver is exposed
  externally or blocked from external access.
- The NRCAN RINEX preset includes Galileo observations.
- ZED-F9P configuration sets the receiver dynamic model to static.
- The daily archive configuration archives the previous day's data and deletes
  archives older than 60 days.

## Fast installation paths

### Ready-to-flash images

RTKBase publishes 64-bit Armbian images for Raspberry Pi and Orange Pi Zero,
Zero 2, and Zero 3 boards. Flash the downloaded archive, attach Ethernet and the
GNSS receiver, wait at least about five minutes on first boot, then open:

```text
http://basegnss.local
```

The initial web password is `admin`. SSH uses `basegnss@basegnss.local` with
password `basegnss!`. Wi-Fi and serial can be enabled in the image's first-boot
configuration before the board starts.

### Release installer

```bash
cd ~
wget https://raw.githubusercontent.com/Stefal/rtkbase/master/tools/install.sh -O install.sh
chmod +x install.sh
sudo ./install.sh --all release
```

The installer fetches dependencies, installs RTKBase and services, detects the
receiver, and configures supported ZED-F9P, Mosaic-X5, and UM980/UM982 receivers
as bases. Unsupported receivers must be configured manually to emit raw or RTCM3,
then selected by port in Settings.

Useful source and targeting forms:

```bash
sudo ./install.sh --all repo --rtkbase-repo <branch>
sudo ./install.sh --all url --rtkbase-custom-source <url>
sudo ./install.sh --all bundled --user=<name>
sudo ./install.sh --detect-gnss --configure-gnss
```

`--user=<name>` installs under `/home/<name>/rtkbase`. Use `--no-write-port` with
detection to avoid updating `settings.conf`. See the installation reference for
all staged flags and temporary TCP serial access.

## Service and configuration map

```text
GNSS receiver
    |
    v
str2str_tcp.service  -- raw TCP, normally :5015
    |
    +-- NTRIP A / NTRIP B
    +-- local caster
    +-- RTCM TCP/UDP server or client
    +-- serial RTCM output
    +-- file logging and archive timer
    +-- gpsd -> chrony
    +-- raw2nmea -> gpsd, when native raw is undecodable
```

`str2str_tcp.service` is the primary reader. Separate `run_cast.sh` instances
consume its raw stream. The UI is `rtkbase_web`; `rtkbase_archive.timer` schedules
archival and cleanup.

Core `settings.conf` invariants:

- Position order is latitude, longitude, height.
- Serial format is `baud:data-bits:parity:stop-bits`.
- Antenna text cannot contain spaces.
- Raw TCP defaults to 5015. If changed, update gpsd `DEVICES` too.
- `new_web_password` is consumed and erased at the next web-server start.
- `prerelease=True` opts into beta updates.

## Choosing receiver input and output

- Prefer a receiver-native raw stream when RTKLIB decodes it.
- For UM980-class hardware whose native format is not decoded, emit RTCM3 MSM,
  constellation navigation messages, and `GPRMC` over the USB-connected port;
  select `rtcm3` as input.
- Preserve TCP 5015 if gpsd/chrony uses the default primary stream.
- For U-Blox raw logging, enable both `UBX-RXM-RAWX` and `UBX-RXM-SFRBX`, verify
  constellations and rate, and save with `CFG`.
- Use 1 Hz for PPP recordings. Faster observations are often ignored or decimated,
  and a 24-hour 1 Hz UBX capture is already about 300 MB.
- Add `-TADJ=1` to the applicable U-Blox receiver-options field to avoid
  non-rounded-second tags in RTCM and NTRIP output.

## Permanent-coordinate workflow

1. Record an uninterrupted 12- or preferably 24-hour raw observation instead of
   accepting survey-in as the permanent answer.
2. Convert the archive to RINEX from Logs or with the receiver-specific tool.
3. Submit RINEX to a precise-point-positioning service or process it with RTKLIB.
4. Enter the solved latitude, longitude, and height as the fixed base position.
5. Restart every correction and logging service that remained stopped after save.

For CSRS-PPP, select **ITRF** and **Static**. Waiting about 15 days allows final
orbit and clock products to replace ultra-rapid products. A complete UTC-day file
must not be interrupted by stopping the device, Main, or File Service.

## NTRIP and RTCM quick reference

An NTRIP Server URI puts the source password after an empty username:

```bash
str2str \
  -in serial://ttyAMA2:57600:8:n:1:off \
  -out ntrips://:secret@caster.example:2101/BASE
```

For a VRS mount point, relay receiver GGA with `-b 1`, or synthesize it with
`-p <lat> <lon> <height> -n 1`. Specify full serial settings to avoid baud
mismatches. An NTRIP caster-table string is optional; omit it rather than sending
malformed semicolon-delimited metadata. Do not include the mount point inside the
metadata string.

## GNSS-backed time

gpsd normally reads `tcp://localhost:5015` with `GPSD_OPTIONS="-n -b"`, ordered
after `str2str_tcp.service`; chrony reads its shared-memory clock. If gpsd cannot
decode a receiver's raw format, enable the converter:

```bash
sudo systemctl enable --now rtkbase_raw2nmea
```

For stratum-1 service, expose the receiver timepulse as `/dev/pps0` and lock a
chrony PPS refclock to the GNSS refclock. Raspberry Pi commonly uses GPIO 18;
Orange Pi requires the `pps-gpio` overlay and selected input pin.

## Operational checks

- After install: verify receiver detection, `str2str_tcp.service`, web access, and
  nonzero raw-stream transfer counts.
- After coordinate save: verify Main and explicitly restart every other service.
- Before full-day logging: verify storage, file growth, UTC-day boundaries, and
  that neither the board nor Main/File Service will restart.
- Before VRS use: verify GGA reaches the caster and RTCM returns to the receiver.
- For reception failures: capture base and rover NMEA plus `UBX-RXM-RTCM`,
  `UBX-MON-COMMS`, `UBX-NAV-CLOCK`, and `UBX-NAV-PVT`.
- For `rtkrcv`: confirm a base-position message such as RTCM 1005 arrives before
  evaluating fix behavior; use trace level 3 for deeper diagnosis.
