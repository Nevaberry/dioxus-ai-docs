---
name: ntrip-rtklib-knowledge-patch
description: "NTRIP & RTKLIB reference (latest: 0.1.0) — str2str/rtkrcv stream path syntax, NTRIP v1/v2 wire format, rtkrcv.conf parameters, demo5 fork setup, RTK2go connections. Load before working with RTKLIB or NTRIP clients."
license: MIT
version: "0.1.0"
metadata:
  author: Nevaberry
---

# NTRIP & RTKLIB Knowledge Patch

Covers NTRIP protocol internals and RTKLIB configuration details that are easy to get wrong: stream path formats differ between tools, parameter names are non-obvious, and NTRIP v1 quirks break standard HTTP libraries.

## Reference Files

| File | Contents |
|------|----------|
| `ntrip-protocol.md` | NTRIP v1/v2 wire format, GGA requirement for VRS, RTK2go connection details |
| `rtkrcv-config.md` | Full rtkrcv.conf parameters, demo5-specific tuning for u-blox receivers |
| `str2str-usage.md` | str2str relay examples, building demo5 on Linux |

## Stream Path Syntax

Stream URLs differ between str2str CLI and rtkrcv.conf — getting these wrong silently fails.

**str2str CLI (`-in`/`-out` flags):**
```
ntrip://[user[:passwd]@]addr[:port][/mntpnt]
ntrips://[:passwd@]addr[:port][/mntpnt[:str]]
serial://port[:brate[:bsize[:parity[:stopb[:fctr]]]]]
tcpsvr://:port
tcpcli://addr[:port]
file://path[::T][::+start][::xspeed][::S=swap]
```

**rtkrcv.conf path format** (no URI scheme — type set separately):
```
ntripcli : user:passwd@addr:port/mntpnt
ntripsvr : [passwd@]addr:port/mntpnt[:str]
ntripcas : user:passwd@:[port]/mpoint[:srctbl]
tcpsvr   : :port
tcpcli   : addr:port
serial   : port[:bit_rate[:byte[:parity(n|o|e)[:stopb[:fctr]]]]]
file     : path[::T[::+offset][::xspeed]]
```

See `references/rtkrcv-config.md` for full rtkrcv.conf parameter reference.

## rtkrcv.conf Quick Reference

Key parameter names for stream setup (easy to guess wrong):

```conf
# Input streams (1=rover, 2=base, 3=corrections)
inpstr1-type       = serial        # serial|tcpcli|tcpsvr|ntripcli|file|off
inpstr1-path       = /dev/ttyACM0:115200:8:n:1:off
inpstr1-format     = ubx           # ubx|rtcm3|rtcm2|nov|oem3|...
inpstr2-type       = ntripcli
inpstr2-path       = user:passwd@caster.example.com:2101/MOUNTPT
inpstr2-format     = rtcm3

# Output streams
outstr1-type       = file
outstr1-path       = /tmp/solution_%Y%m%d%h%M.pos
outstr1-format     = llh           # llh|xyz|enu|nmea|...

# Log streams (raw data logging)
logstr1-type       = file
logstr1-path       = /tmp/rover_%Y%m%d%h%M.ubx
```

## RTCM MSM Message Numbering

MSM types 1–7 repeat per constellation in blocks of 10:

| Constellation | Range |
|---------------|-------|
| GPS | 1071–1077 |
| GLONASS | 1081–1087 |
| Galileo | 1091–1097 |
| SBAS | 1101–1107 |
| QZSS | 1111–1117 |
| BeiDou | 1121–1127 |

MSM4 = pseudorange + phase + CNR (no Doppler). MSM7 = full resolution + Doppler. **MSM7 is preferred** (1077, 1087, 1097, 1127). Legacy: 1004 (GPS L1+L2), 1012 (GLONASS L1+L2).

See `references/str2str-usage.md` for `-msg` flag examples.

## NTRIP v1 Wire Protocol (Quick Reference)

RTKLIB only supports NTRIP v1. Key detail for custom client implementations.

**Client request:**
```
GET /mountPt HTTP/1.0\r\n
User-Agent: NTRIP theSoftware/theRevision\r\n
Authorization: Basic dXNlcjpwYXNzd29yZA==\r\n
\r\n
```

**Responses:**
```
ICY 200 OK\r\n         # success — binary RTCM follows
SOURCETABLE 200 OK\r\n  # sourcetable (also returned on error)
```

Note: Some HTTP libraries reject `ICY 200 OK` as non-standard — must handle explicitly.

See `references/ntrip-protocol.md` for v2 differences, GGA/VRS requirements, RTK2go setup.

## RTK2go Quick Reference

Free public caster at `rtk2go.com:2101` (v1+v2) or `:2102` (TLS, v2 only).

| Role | User | Password | Notes |
|------|------|----------|-------|
| Client (rover) | your email | `none` | Select mountpoint from sourcetable |
| Server (base) | — | assigned | Requires reservation at rtk2go.com |

**RTKLIB limitation:** can only connect as server with Rev1 — do not request Rev2 reservations for RTKLIB-based stations.

## Server Parameters

```conf
svrcycle           = 10            # processing cycle (ms)
timeout            = 10000         # stream timeout (ms)
reconnect          = 10000         # reconnect interval (ms)
nmeacycle          = 5000          # NMEA GGA send cycle (ms) for VRS
buffsize           = 32768         # input buffer size (bytes)
```

See `references/rtkrcv-config.md` for demo5-specific parameters.

## str2str Relay (Common Pattern)

```bash
# Serial receiver → NTRIP server (base station)
str2str -in serial://ttyACM0:115200#ubx \
        -out ntrips://:password@rtk2go.com:2101/MY_MOUNT#rtcm3 \
        -msg 1077(1),1087(1),1097(1),1127(1),1005(10),1033(10) \
        -p 60.1234 24.5678 45.0

# NTRIP client → file (log corrections)
str2str -in ntrip://user:pass@caster.example.com:2101/MOUNT \
        -out file:///tmp/rtcm_%Y%m%d%h%M.rtcm3
```

The `-msg` flag specifies RTCM output messages and intervals in seconds. The `-p` flag sets station position for 1005/1006 messages.

See `references/str2str-usage.md` for full path syntax and build instructions.

## Demo5 Key Parameters (u-blox Receivers)

Build from `rtklibexplorer/RTKLIB`, not `tomojitakasu/RTKLIB`.

```conf
# Pseudorange/carrier ratio — 300 for u-blox (default 100)
stats-eratio1      = 300
stats-eratio2      = 300

# Fix-and-hold tracking gain (higher = lower gain, avoids false holds)
pos2-varholdamb    = 0.1           # default 0.001; 0.1-1.0 recommended

# AR filter — delay new/cycle-slip sats if they degrade AR ratio
pos2-arfilter      = on

# Position variance threshold before enabling AR
pos2-arthres1      = 0.004         # 0.004-0.10 typical

# Consecutive fix samples before hold
pos2-arminfix      = 20            # 5-20× sample rate

# Min satellites for fix/hold/drop
pos2-minfixsats    = 4
pos2-minholdsats   = 5
pos2-mindropsats   = 10
```

See `references/rtkrcv-config.md` for GLONASS AR and full parameter reference.

## GGA Requirement for VRS

VRS/NEAR mountpoints require NMEA GGA sentences periodically so the caster generates position-specific corrections. In rtkrcv.conf:

```conf
nmeacycle          = 5000          # GGA send interval (ms)
ant2-postype       = single        # approximate position source
```

**Without GGA, VRS streams may send no data or stale corrections.**

## Building Demo5 on Linux

```bash
git clone https://github.com/rtklibexplorer/RTKLIB.git
cd RTKLIB/app/rtkrcv/gcc && make    # single CUI app
# or: cd RTKLIB/app && make          # all CUI apps
```
