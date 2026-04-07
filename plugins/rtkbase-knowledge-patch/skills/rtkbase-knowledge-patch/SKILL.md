---
name: rtkbase-knowledge-patch
description: "RTKBase changes since training cutoff (latest: 2.7.0) — str2str service chain, settings.conf structure, F9P/Mosaic-X5/UM980 receivers, install.sh flags, systemd units. Load before working with RTKBase."
version: "2.7.0"
license: MIT
metadata:
  author: Nevaberry
---

# RTKBase Knowledge Patch

RTKBase is a web-managed GNSS base station built on RTKLIB `str2str`. It runs multiple `str2str` instances as systemd services, with a Flask/Gunicorn web GUI for configuration.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Architecture | [references/architecture.md](references/architecture.md) | str2str service chain, service topology, systemd units |
| Configuration | [references/configuration.md](references/configuration.md) | settings.conf INI structure, all sections and keys, RTCM message syntax |
| Installation & Receivers | [references/installation-and-receivers.md](references/installation-and-receivers.md) | install.sh flags, supported receivers (F9P, Mosaic-X5, UM980), requirements |

---

## Quick Reference: Service Chain

```
str2str_tcp.service          # Main: receiver -> TCP (raw data on port 5015)
  +-- str2str_ntrip_A        # TCP -> NTRIP caster A (raw->rtcm conversion)
  +-- str2str_ntrip_B        # TCP -> NTRIP caster B
  +-- str2str_local_ntrip_caster  # TCP -> local NTRIP caster (self-hosted)
  +-- str2str_rtcm_svr       # TCP -> RTCM TCP server for clients
  +-- str2str_rtcm_serial    # TCP -> serial port (radio link)
  +-- str2str_file           # TCP -> raw data log files
  +-- rtkbase_raw2nmea       # Optional: raw->NMEA for gpsd (non-UBX receivers)

rtkbase_web.service          # Flask/Gunicorn web GUI (default port 80)
rtkbase_archive.timer        # Daily archive+cleanup of raw logs
```

The main `str2str_tcp` connects to the GNSS receiver and broadcasts raw data on TCP. All other services consume from it. Services are configured via `run_cast.sh` reading `settings.conf` (INI format).

## Quick Reference: Supported Receivers

| Receiver | Detection | Raw Format | Notes |
|----------|-----------|-----------|-------|
| u-blox ZED-F9P | USB + UART | `ubx` | Full support. `-TADJ=1` recommended. Dynamic model set to static. |
| Septentrio Mosaic-X5 | USB | `rtcm3` (SBF for logging) | Reverse proxy to receiver web UI. Default creds: `basegnss/basegnss!` |
| Unicore UM980/UM982 | Auto-detect | `rtcm3` only | No raw binary in RTKLIB -> no PPP/rtkrcv solution. RTCM3 streaming works. |

## Quick Reference: settings.conf Key Sections

```ini
[general]
version=2.7.0
web_port=80
web_authentification=true
new_web_password=           # Set once, hashed on next web server start
maptiler_key=               # Optional: aerial imagery layer

[main]
position='47.0983 -1.2655 36.40'   # lat lon height
com_port=''                         # /dev/ttyGNSS0, /dev/ttyUSB0, etc.
com_port_settings='38400:8:n:1'
receiver='unknown'                  # u-blox_zed-f9p, mosaic-x5, unicorecomm
receiver_format=''                  # ubx, rtcm3, oem3, etc.
antenna_info='ADVNULLANTENNA'
tcp_host_addr='127.0.0.1'          # Bind addr; 0.0.0.0 for external access
tcp_port='5015'
gnss_rcv_web_ip=192.168.3.1        # Mosaic-X5 web interface IP
gnss_rcv_web_proxy_port=9090        # Flask reverse proxy port for receiver UI
nmea_port='5014'                    # raw2nmea output port

[local_storage]
datadir=$BASEDIR/data
file_name='%Y-%m-%d_%h-%M-%S_GNSS-1'
file_rotate_time='24'               # Hours
archive_rotate='60'                 # Days before deletion
min_free_space='500'                # MB

[ntrip_A]                           # (ntrip_B has identical structure)
svr_addr_a='caster.centipede.fr'
svr_port_a='2101'
svr_pwd_a=''
mnt_name_a='Your_mount_name'
rtcm_msg_a='1004,1005(10),1006,1008(10),1012,1019,1020,1033(10),1042,1045,1046,1077,1087,1097,1107,1127,1230'
ntrip_a_receiver_options=''         # e.g. '-TADJ=1' for u-blox

[local_ntrip_caster]
local_ntripc_user=''
local_ntripc_pwd=''
local_ntripc_port='2101'
local_ntripc_mnt_name=''

[rtcm_svr]                          # Also: [rtcm_client], [rtcm_serial]
rtcm_svr_port='5016'                # [rtcm_udp_svr], [rtcm_udp_client]

[log]
level=0                             # str2str trace level

[network]
modem_at_port=''                    # 4G Simcom A76XX modem AT port
```

RTCM message rate syntax: `1005(10)` = send msg 1005 every 10th epoch. No suffix = every epoch.

## Quick Reference: install.sh

```bash
sudo ./install.sh --all release          # Full install from latest release
sudo ./install.sh --all repo --rtkbase-repo dev  # Install from git branch
sudo ./install.sh --detect-gnss          # Detect receiver model and port
sudo ./install.sh --detect-gnss --configure-gnss  # Detect + configure
sudo ./install.sh --dependencies         # Install apt packages only
sudo ./install.sh --rtklib               # Compile RTKLib (v2.5.0-EX)
sudo ./install.sh --unit-files           # Deploy systemd services
sudo ./install.sh --gpsd-chrony          # Setup time sync
sudo ./install.sh --start-services       # Start all services
sudo ./install.sh --user=john            # Install as specific user
```

`--all` combines: `--dependencies --rtklib --unit-files --gpsd-chrony --detect-gnss --configure-gnss --start-services`.

## REST API

```
GET /api/v1/infos   # Base station info (position, receiver, mount name)
```

## Requirements

- Debian >= 12 (Bookworm) / Ubuntu >= 24.04
- Python >= 3.11
- RTKLib v2.5.0-EX (from rtklibexplorer)
- Default web password: `admin`
- Armbian images: `basegnss.local`, SSH: `basegnss/basegnss!`

## Reference Files

| File | Contents |
|---|---|
| [architecture.md](references/architecture.md) | str2str service chain topology, systemd service details, service dependencies |
| [configuration.md](references/configuration.md) | Complete settings.conf reference — all sections, keys, and defaults |
| [installation-and-receivers.md](references/installation-and-receivers.md) | install.sh flags, receiver detection/configuration, supported hardware, requirements |
