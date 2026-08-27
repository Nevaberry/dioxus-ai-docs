# Platform and Installation

## Platform requirements

RTKBase 2.7.0 supports Debian 13 (Trixie). Updates require Debian 12,
Ubuntu 24.04, or newer. Python versions earlier than 3.11 are deprecated.

## Ready-to-flash images and first boot

RTKBase publishes ready-to-flash Armbian images for 64-bit Raspberry Pi and
Orange Pi Zero, Zero 2, and Zero 3 boards. Flash the downloaded image archive to
microSD, connect Ethernet and the GNSS receiver, and allow at least about five
minutes for the first boot. Then browse to `http://basegnss.local` or the board's
IP address. The initial web password is `admin`.

SSH is available as `basegnss@basegnss.local` with password `basegnss!`. The
image's first-boot configuration can optionally enable Wi-Fi and a serial port
before the board starts.

## Release installer

The normal installer fetches dependencies and RTKBase, deploys services, detects
the receiver, and configures supported U-Blox ZED-F9P, Septentrio Mosaic-X5, and
Unicore UM980/UM982 receivers as base stations:

```bash
cd ~
wget https://raw.githubusercontent.com/Stefal/rtkbase/master/tools/install.sh -O install.sh
chmod +x install.sh
sudo ./install.sh --all release
```

The source passed after `--all` may be `release`, `repo`, `url`, or `bundled`.
Repository installs add `--rtkbase-repo <branch>`, custom downloads add
`--rtkbase-custom-source <url>`, and `--user=<name>` selects both the service user
and the `/home/<name>/rtkbase` installation path.

An unsupported receiver must be configured manually to emit raw or RTCM3 data.
Select its port afterward in the Settings page.

## Staged installation and receiver access

The installation can be split into these flags:

- `--dependencies`
- `--rtklib`
- `--rtkbase-release`
- `--unit-files`
- `--gpsd-chrony`
- `--detect-gnss`
- `--configure-gnss`
- `--start-services`

`--no-write-port` makes detection report the receiver without updating
`settings.conf`. Detection and configuration can be combined:

```bash
sudo ./install.sh --detect-gnss --configure-gnss
```

To use a receiver configuration tool from another machine, temporarily expose
the serial port over TCP. Adjust the device and baud rate for the receiver:

```bash
sudo socat tcp-listen:128,reuseaddr /dev/ttyS1,b115200,raw,echo=0
```

The remote tool connects to TCP port 128. Stop `socat` after configuration so the
receiver is not left exposed.

## Service topology

`str2str_tcp.service` is the primary RTKLIB instance. It reads the receiver and
publishes its raw stream for other services. Separate `run_cast.sh` instances
consume that stream for:

- upstream NTRIP A and B;
- a local NTRIP caster;
- RTCM TCP and UDP server or client output;
- serial RTCM output; and
- file logging.

The web UI runs as `rtkbase_web`. `rtkbase_archive.timer` runs raw-data archival
and cleanup. The installer can deploy and start these units.

For a manual deployment, copy units to `/etc/systemd/system`, replace their
`{user}` placeholder, run `systemctl daemon-reload`, and enable the required
units.

## Core `settings.conf` fields

`settings.conf` is a sectioned, shell-style configuration read by `run_cast.sh`.
A core configuration resembles:

```ini
[main]
position='47.0983869 -1.2655108 36.40'
com_port='/dev/ttyACM0'
com_port_settings='38400:8:n:1'
antenna_info='ADVNULLANTENNA'
tcp_port='5015'
```

Important field rules:

- `position` is ordered latitude, longitude, height.
- Serial parameters use `baud:data-bits:parity:stop-bits`.
- `antenna_info` must contain no spaces.
- Raw TCP defaults to port 5015. Changing it also requires changing gpsd's
  `DEVICES` value.
- `ext_tcp_source` and `ext_tcp_port` can substitute another base's raw stream
  during development.
- `gnss_rcv_web_ip` and `gnss_rcv_web_proxy_port` expose a receiver-integrated
  UI through the Flask proxy.
- `nmea_port` selects the raw-to-NMEA service port.

The `[general]` section has several operationally important settings:

- `new_web_password` is a one-shot value erased at the next web-server start.
- `prerelease=True` opts into beta updates.
- `cpu_temp_offset` corrects board temperature readings.
- `maptiler_key` enables the aerial map layer.

## Local data retention

Local logging defaults to `$BASEDIR/data`, 24-hour files, zero overlap, and a
500 MB minimum-free-space threshold. The 2.7.0 configuration archives the
previous day's data and removes archives older than 60 days. Enabling
`rtkbase_archive.timer` schedules archive-and-clean daily at 04:00.

## GNSS-backed system time

The gpsd/chrony installer feeds gpsd from RTKBase's primary raw TCP stream and
orders gpsd after `str2str_tcp.service`. Chrony consumes gpsd's shared-memory
clock. Essential gpsd settings are:

```ini
DEVICES="tcp://localhost:5015"
GPSD_OPTIONS="-n -b"
```

When gpsd cannot decode a non-U-Blox receiver's raw format, enable
`rtkbase_raw2nmea`. It converts the primary receiver stream onto `nmea_port` for
gpsd and chrony:

```bash
sudo systemctl enable --now rtkbase_raw2nmea
```

## PPS time service

A receiver timepulse can make the station a stratum-1 NTP source. On Raspberry
Pi, configure `dtoverlay=pps-gpio,gpiopin=18` and load `pps-gpio`. On Orange Pi,
add `pps-gpio` to the overlays and set `param_pps_pin` to the selected input.

Lock the PPS source to the GNSS clock in chrony:

```ini
refclock SHM 0 refid GPS precision 1e-1 offset 0 delay 0.2 noselect
refclock PPS /dev/pps0 refid PPS lock GPS
```

## ELT_RTKBase installation variant

ELT_RTKBase is a separate Raspberry Pi OS-compatible fork for Unicore UM98x,
Bynav M2x, Septentrio Mosaic-X5, and U-Blox ZED-X20P receivers. Install it in one
pass, or in two phases when the receiver cannot initially be connected:

```bash
wget https://github.com/GNSSOEM/ELT_RTKBase/raw/main/install.sh
chmod +x install.sh
./install.sh          # one pass
./install.sh -1       # install without receiver
./install.sh -2       # finish after connecting receiver
```

The fork is available locally as `rtkbase.local`. It writes the configured base
position and changed baud rate back to supported receivers. Setting both mount
name and password to `TCP` requests a TCP client instead of an NTRIP server.

Additional capabilities include static-IP and WPS Wi-Fi setup, Tailscale,
supported USB 4G/5G networking, radio-modem output, NTRIP 2.0, and configuration
for five NTRIP servers.
