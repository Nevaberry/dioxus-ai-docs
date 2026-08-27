# Data Pipeline Tools

### Display-safe versus packetized gpscat capture
`gpscat` reads a file or serial device directly rather than connecting to GPSD. Its default “raw” output is display-safe, not byte-preserving: nonprinting non-whitespace bytes become hexadecimal escapes and a final linefeed is added; use `gpspipe -R` when exact device bytes are required.

`gpscat -p` instead runs the GPSD packet sniffer and emits one escaped packet per line, while `-t` also prefixes its type and length. An unrecognized or non-packetized stream can be consumed without output and look hung; `-s 4800N1`-style arguments set baud, parity, and stop bits before reading a serial device.

### gpspipe stream modes
At least one stream mode is required: `-R` forwards exactly the bytes sent by the device, `-r` emits received NMEA plus any pseudo-NMEA generated from binary data, and `-w` emits GPSD JSON. `-S` requests scaled AIS and SUBFRAME JSON, `-2` keeps AIS type-24 halves separate, `-p` requests profiling JSON, and `-P` adds PPS-drift JSON alongside NMEA or raw output.

`-n COUNT` stops after that many output messages and `-x SEC` stops after elapsed seconds. `-t` timestamps records in UTC, `-T FMT` selects a `strftime` format, `-u` adds microsecond resolution, `-uu` uses `sec.usec`, and `-Z` selects ISO 8601 timestamps.

### gpspipe file, daemon, and serial delivery
`-o FILE` redirects collection to a file and is mandatory with `-d`; `-l` delays the initial daemon connection by ten seconds, and `-B` disables output buffering when latency matters. `-s DEV` together with `-r` turns a managed receiver into a serial NMEA feed, always opening the destination at 4800 8N1.

```sh
gpspipe -r -s /dev/ttyS1
gpspipe -d -l -R -o receiver.bin
```

### Filtered multi-destination UDP forwarding
`gps2udp` can send NMEA (`-n`), JSON (`-j`), or both to as many as five repeated `-u HOST:PORT` destinations. `-a` retains only AIS, `-t` retains only TPV and implies JSON, `-c COUNT` stops after that many sent sentences, and background mode (`-b`) automatically reconnects when GPSD restarts.

```sh
gps2udp -a -n -u 192.0.2.10:5000 -u 192.0.2.11:5000
```

### gpsdecode output and type filtering
The default decoder maps supported sensor packets on standard input to GPSD JSON; `-n` instead emits generated pseudo-NMEA. For AIS, `-u` suppresses scaling and text expansion to make the dump lossless, while `-s` reports type-24 halves separately.

`-t TYPES` accepts comma-separated numeric AIS, RTCM2, or RTCM3 message types and filters only packets that have such a numeric type; GPS packets and other kinds still pass unconditionally. This makes it unsuitable as a global packet-kind filter.

### AIS delimiter-separated decoding
`gpsdecode -c` emits AIS payload fields in wire order separated by `|` and forces unscaled numeric values. Dates become ISO 8601 UTC timestamps, TDMA status groups and unused regional fields are hexadecimal, and a variable-length binary field is encoded as `<bit-length>:<hex>`.

### gpsfake replay topology and pacing
`gpsfake` starts a foreground daemon with one pseudo-TTY per logfile and loops the inputs by default; multiple logs are interleaved in command-line order. Use `-1` for one pass, `-c SECONDS` for a fractional inter-sentence delay, or `-S` for realistic pacing that avoids pseudo-TTY race failures; select a nondefault daemon port with `-P` to coexist with production GPSD.

The daemon-inactivity timeout defaults to 60 seconds but typically expires about 20 seconds later because of internal delays; `-w 0` disables it. `-t` and `-u` force TCP and UDP source simulation when pseudo-TTYs are unavailable.

### gpsfake logfile control headers
Leading comments are ignored except for control headers: `#Serial:` sets the simulated serial link, `#Transport:` selects TCP or UDP instead of a pseudo-TTY, and `# Date:` gives GPSD an initial ISO date. A `Delay-Cookie` header supplies a delimiter and delay in seconds, splitting writes at that delimiter instead of packet boundaries so tests can place write boundaries inside packets.

```text
#Serial: 4800 7N2
#Transport: TCP
# Date: 2026-07-12
```

### gpsfake watcher and daemon options
`gpsfake -p` opens a watcher and writes the generated NMEA and GPSD notifications to standard output; its default initialization is `?WATCH={"enable":true,"json":true}`, replaceable with `-r STRING`. Pass daemon arguments with the required equals-sign form `-o="OPTS"`; `-n` is shorthand for `-o="-n"`.

```sh
gpsfake -1 -P 2948 -p \
  -r '?WATCH={"enable":true,"raw":1}' receiver.log
```

### Instrumented and programmable gpsfake sessions
`-m PROG` runs the test daemon inside a monitor such as Valgrind, while `-g` and `-G` select GDB and LLDB and disable the inactivity timeout for breakpointing. The underlying Python `gpsfake` module can script one daemon, multiple client sessions, and multiple fake receivers; set `GPSD_HOME` when the daemon executable is outside `PATH`.

### Offline raw-to-RINEX pipeline
`gpsrinex -F FILE` consumes previously decoded GPSD JSON rather than a live daemon, so a byte-exact receiver capture must pass through `gpsdecode` first. This separates remote acquisition from later RINEX generation.

```sh
gpspipe -x 14400 -R 10.168.1.2 > receiver.ubx
gpsdecode < receiver.ubx > receiver.json
gpsrinex -F receiver.json -f receiver.obs
```

### gpsrinex defaults, filtering, and headers
Without acquisition options, `gpsrinex` records 20 epochs at 30-second intervals and names the result `gpsrinexYYYYjjjHHMMSS.obs`; `-i` accepts millisecond-resolution seconds and `-n` changes the epoch count. `-g CODES` limits output by RINEX system code: `C` BeiDou, `E` Galileo, `G` GPS, `I` IRNSS, `J` QZSS, `R` GLONASS, and `S` SBAS.

Agency, observer, marker, receiver, antenna, and comment options only populate the RINEX header; they do not change computation. Antenna `--ant_e`, `--ant_n`, and `--ant_h` values record the east, north, and height offsets from the marker in meters.
