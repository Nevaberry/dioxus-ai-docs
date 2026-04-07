# str2str Usage & Build Guide

## str2str Stream Path Syntax

str2str uses URI-scheme paths in `-in` and `-out` flags:

```
ntrip://[user[:passwd]@]addr[:port][/mntpnt]       # NTRIP client (input)
ntrips://[:passwd@]addr[:port][/mntpnt[:str]]       # NTRIP server (output only)
serial://port[:brate[:bsize[:parity[:stopb[:fctr]]]]]
tcpsvr://:port
tcpcli://addr[:port]
file://path[::T][::+start][::xspeed][::S=swap]
```

## Relay Examples

### Serial Receiver → NTRIP Server (Base Station)

Relay u-blox raw data from serial to NTRIP caster as RTCM3:

```bash
str2str -in serial://ttyACM0:115200#ubx \
        -out ntrips://:password@rtk2go.com:2101/MY_MOUNT#rtcm3 \
        -msg 1077(1),1087(1),1097(1),1127(1),1005(10),1033(10) \
        -p 60.1234 24.5678 45.0
```

### NTRIP Client → File (Log Corrections)

```bash
str2str -in ntrip://user:pass@caster.example.com:2101/MOUNT \
        -out file:///tmp/rtcm_%Y%m%d%h%M.rtcm3
```

### The `-msg` Flag

Specifies RTCM output messages and intervals in seconds:
- `1077(1)` — GPS MSM7 every 1 second
- `1005(10)` — Station coordinates every 10 seconds
- `1033(10)` — Antenna descriptor every 10 seconds

### The `-p` Flag

Sets the station position (latitude, longitude, height) for RTCM 1005/1006 messages.

## Building Demo5 on Linux

Build from `rtklibexplorer/RTKLIB`, not `tomojitakasu/RTKLIB`.

### CUI Apps (Raspberry Pi / Ubuntu)

```bash
git clone https://github.com/rtklibexplorer/RTKLIB.git
cd RTKLIB/app/rtkrcv/gcc && make    # single app
# or: cd RTKLIB/app && make          # all CUI apps
```

### Qt GUI Apps (Ubuntu)

```bash
sudo apt install build-essential libpng-dev qt5-default libqt5serialport5-dev
cd RTKLIB/app/qtapp && qmake && make && ./install_qtapp
```
