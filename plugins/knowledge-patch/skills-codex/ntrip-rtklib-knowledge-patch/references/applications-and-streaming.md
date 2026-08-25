# RTKLIB Applications and Streaming

## Contents

- [NTRIP upload and stream compatibility](#ntrip-upload-and-stream-compatibility)
  - [str2str base-station upload](#str2str-base-station-upload)
  - [str2str standard streams and format suffixes](#str2str-standard-streams-and-format-suffixes)
  - [2.4.2 stream recovery and fan-out](#242-stream-recovery-and-fan-out)
- [RTKNAVI, streams, and GUI operation](#rtknavi-streams-and-gui-operation)
  - [Per-instance GUI state](#per-instance-gui-state)
  - [Receiver startup and shutdown scripts](#receiver-startup-and-shutdown-scripts)
  - [RTKNAVI stream-role constraints](#rtknavi-stream-role-constraints)
  - [Time-tagged replay and rotating files](#time-tagged-replay-and-rotating-files)
  - [Scheduled precise-correction downloads](#scheduled-precise-correction-downloads)
  - [NRTK feedback and navigation-source selection](#nrtk-feedback-and-navigation-source-selection)
  - [RTKNAVI monitor service](#rtknavi-monitor-service)
- [Post-processing and conversion applications](#post-processing-and-conversion-applications)
  - [RTKPOST input discovery](#rtkpost-input-discovery)
  - [Multi-session path expansion](#multi-session-path-expansion)
  - [RTKCONV batch overwrite boundary](#rtkconv-batch-overwrite-boundary)
- [Command-line tools](#command-line-tools)
  - [RTKRCV process and console lifecycle](#rtkrcv-process-and-console-lifecycle)
  - [RNX2RTKP input order and precedence](#rnx2rtkp-input-order-and-precedence)
  - [STR2STR fan-out controls](#str2str-fan-out-controls)
- [GUI and receiver-command updates](#gui-and-receiver-command-updates)
  - [GUI state migration and launcher](#gui-state-migration-and-launcher)
  - [NVS receiver command scripts](#nvs-receiver-command-scripts)
- [Product downloads](#product-downloads)
  - [RTKGET URL-list grammar](#rtkget-url-list-grammar)
  - [RTKGET selection and diagnostics](#rtkget-selection-and-diagnostics)
- [Demo5 stream and console extensions](#demo5-stream-and-console-extensions)
  - [Current caster and UDP endpoint grammar](#current-caster-and-udp-endpoint-grammar)
  - [str2str feedback and per-output controls](#str2str-feedback-and-per-output-controls)
  - [RTKRCV headless and diagnostic controls](#rtkrcv-headless-and-diagnostic-controls)
- [Stream conversion preservation](#stream-conversion-preservation)
  - [RTCM message 1230 is not preserved by stream conversion](#rtcm-message-1230-is-not-preserved-by-stream-conversion)
- [RTKRCV and str2str configuration](#rtkrcv-and-str2str-configuration)
  - [RTKRCV stream-slot configuration](#rtkrcv-stream-slot-configuration)
  - [Console option matching and persistence](#console-option-matching-and-persistence)
  - [Time-tagged file replay and rotation](#time-tagged-file-replay-and-rotation)
  - [Scheduled FTP and HTTP inputs](#scheduled-ftp-and-http-inputs)
  - [str2str connection defaults](#str2str-connection-defaults)

## NTRIP upload and stream compatibility

### `str2str` base-station upload

An RTKLIB source upload uses the `ntrips://` output scheme; the empty username before the colon is intentional for RTK2go's mountpoint-password authentication. Quote the URL when credentials or the mountpoint contain shell metacharacters:

```sh
str2str -in serial://ttyACM0:115200:8:n:1:off \
  -out 'ntrips://:PASSWORD@rtk2go.com:2101/MOUNTPOINT'
```

Configure the receiver's USB output as RTCM 3 only: interleaved NMEA can make RTK2go report that the stream is not parsed. Message 1084 alone does not convey the base position; include 1005 and the other messages required by the rover.

### `str2str` standard streams and format suffixes

Patch 2.4.2 p10 added stdin/stdout operation when `-in` or `-out` is omitted. That patch misparses an explicitly supplied endpoint containing `#format`; use p11 or later when selecting a decoder with forms such as `file://path#ubx`.

### 2.4.2 stream recovery and fan-out

Before patch p7, an NTRIP inactive-timeout followed by a temporary DNS failure can leave the connection permanently stuck until the application is restarted. Separately, 2.4.2 p13 can lose one `strwrite()` message to all remaining TCP-server clients immediately after any one client disconnects; that fan-out defect is fixed in 2.4.3 b34.

## RTKNAVI, streams, and GUI operation

### Per-instance GUI state

RTKNAVI, RTKPOST, RTKCONV, and STRSVR accept `-i <file>.ini` to keep independent option sets and `-t <title>` to distinguish their windows. These applications do not use the Windows registry; without `-i`, their INI state is normally placed under `C:\Windows`, and the MKL-linked RTKNAVI/RTKPOST binaries use `OMP_NUM_THREADS` to select matrix-computation thread count.

```bat
rtknavi.exe -i rover-a.ini -t "Rover A"
set OMP_NUM_THREADS=4
rtknavi_mkl.exe -i rover-b.ini -t "Rover B"
```

### Receiver startup and shutdown scripts

A serial receiver command file contains startup commands, then a line beginning with `@`, then shutdown commands; ordinary lines are sent as text, while `!UBX` and `!STQ` generate supported u-blox and SkyTraq binary commands and `!WAIT time` pauses for `time` milliseconds. Startup and shutdown transmission must each be enabled by the caller, so merely loading the file does not send both sets.

```text
!UBX CFG-RATE 1000 1 1
!WAIT 500
@
```

### RTKNAVI stream-role constraints

Rover and base inputs can use serial, TCP client/server, NTRIP client, or files; FTP and HTTP are correction-only inputs, and in 2.4.1 their usable correction format is SP3. RTKNAVI provides two solution outputs and three byte-preserving input logs; output transports are serial, TCP client/server, NTRIP server, or file, TCP servers admit multiple clients, a blank NTRIP-client port means `2101`, and a blank NTRIP-server port means `80`.

### Time-tagged replay and rotating files

File replay speed and start offset work only when the raw log has its companion time-tag file; enabling `Time-Tag` while logging creates `<log-path>.tag`. A periodically swapped output path must contain a replaceable time keyword, and `File Swap Margin` overlaps old and new files—`0` disables overlap—to avoid losing data at the boundary.

### Scheduled precise-correction downloads

An FTP/HTTP correction address is written as `<server>/<path>` and may contain GPST-derived path substitutions such as `%W` (GPS week), `%D` (day of week), and `%hb` (six-hour block). Download interval, schedule offset, retry interval, a separate time offset used for path expansion, credentials for FTP, and the local download directory are independently configurable; for example, interval `6H` and offset `2H` attempts downloads at 02:00, 08:00, 14:00, and 20:00 GPST.

### NRTK feedback and navigation-source selection

For a base/NRTK input, `inpstr2-nmeareq` selects no GGA, a configured latitude/longitude, or RTKNAVI's current single-point position, while `misc-nmeacycle` controls the transmission period. `misc-navmsgsel` can accept navigation messages from all streams or restrict them to rover, base, or correction input, which prevents an unwanted duplicate source from driving the solution.

```text
inpstr2-nmeareq =latlon
inpstr2-nmealat =60.1699
inpstr2-nmealon =24.9384
misc-nmeacycle  =5000
misc-navmsgsel  =base
```

### RTKNAVI monitor service

The monitor port is a TCP server used by RTKPLOT and external monitors; its documented default is `52001`, following port numbers are chosen for additional RTKNAVI instances, and `0` disables it. Multiple monitor clients are allowed, while the separate solution buffer/log size controls how much trajectory can later be saved or displayed.

## Post-processing and conversion applications

### RTKPOST input discovery

RTKPOST accepts gzip, Unix-compress, and Hatanaka-compressed observation files and expands wildcards to multiple files; the first observation input is the rover and the second is the base in relative modes. If navigation fields are blank, an `.obs` path is retried with `.*nav`, while a `.yyO` path is retried as `.yyN`, `.yyG`, `.yyH`, `.yyQ`, and `.yyP`; additional correction inputs may be SP3-c, RINEX CLK, IONEX, an RTKLIB SBAS log, or EMS 2.0.

### Multi-session path expansion

With both start and end times set, RTKPOST can split work into hour-sized sessions, but the output path must contain a session-dependent keyword to avoid overwriting every result. Batch paths recognize `%Y`, `%y`, `%m`, `%d`, `%n`, `%W`, `%D`, `%h`, `%H`, `%r`, and `%b`; `%r` and `%b` expand entries from rover and base lists, whose comment lines begin with `#`.

### RTKCONV batch overwrite boundary

In multi-session conversion, RTKCONV does not ask before overwriting an existing output, so every generated path needs a distinguishing time keyword. It can create the selected output directory when absent, but only if that directory's parent already exists.

## Command-line tools

### RTKRCV process and console lifecycle

`rtkrcv` uses stdin/stdout as its console by default; `-p` opens a Telnet console, `-m` opens a monitor stream, `-d` selects a terminal device, `-s` starts the server immediately, `-o` replaces `rtkrcv.conf`, `-r` selects status detail, and `-t` selects trace level. `set` and `load` changes take effect only after `restart`; `exit` logs out without stopping positioning, `shutdown` stops the server and process, and `USR2` also shuts the process down.

```sh
rtkrcv -s -p 2105 -m 52001 -o rover.conf -r 2 -t 3
```

The console's `solution`, `status`, `satellite`, `observ`, `navidata`, and `stream` commands accept an optional display cycle and stop cyclic output with Ctrl-C; `!command` runs a non-interactive shell command. Command prefixes may be abbreviated as long as their leading characters distinguish them.

### RNX2RTKP input order and precedence

The first observation file passed to `rnx2rtkp` is the rover, the second is the base for a relative solution, and at least one navigation file is required; SP3 input must end in `.sp3` or `.eph`, and application-expanded wildcards should be quoted against shell expansion. `-k` loads a configuration file, but explicit CLI switches override it; mode numbers are `0` single, `1` DGPS, `2` kinematic, `3` static, `4` moving-base, `5` fixed, `6` PPP-kinematic, and `7` PPP-static.

```sh
rnx2rtkp -k rover.conf -p 2 -c -ts 2026/7/12 08:00:00 \
  -te 2026/7/12 10:00:00 -ti 1 -o rover.pos \
  rover.obs base.obs '*.nav'
```

`-b` requests backward processing, `-c` forward/backward combination, `-i` instantaneous AR, `-h` Fix-and-Hold, `-y` solution-status level, and `-x` trace level. Reference coordinates can be supplied as ECEF with `-r x y z` or latitude/longitude/height with `-l lat lon hgt`; otherwise the base defaults to an average single-point position.

### STR2STR fan-out controls

The 2.4.1 `str2str` is a resident byte-stream fan-out and accepts repeated `-out` endpoints; serial paths encode bitrate, byte size, parity, stop bits, and flow control, while TCP server/client and file paths use `tcpsvr://:port`, `tcpcli://address[:port]`, and `file://path`. `-s` and `-r` set timeout and reconnect milliseconds, `-d` controls status-display interval, `-f` sets file-swap overlap, `-c` supplies the receiver command file, `-n` and `-p` set the GGA cycle and fixed position, and `-x` supplies the HTTP/NTRIP proxy.

```sh
str2str -in serial://ttyS0:115200:8:n:1:off \
  -out file://base.rtcm3 -out tcpsvr://:22101 \
  -d 5000 -s 10000 -r 10000 -f 30
```

## GUI and receiver-command updates

### GUI state migration and launcher

Default GUI INI files move from `C:\Windows` to `<install-dir>\rtklib_2.4.2\bin`; copy the old files there when preserving 2.4.1 settings. The new `rtklaunch.exe` accepts `-mkl` to launch the MKL variants of RTKNAVI/RTKPOST and `-tray` to start as a task-tray icon; RTKGET joins the applications that accept `-i <file>.ini` and `-t <title>`.

### NVS receiver command scripts

Serial/TCP startup and shutdown scripts can now generate NVS NV08C commands with `!NVS CFG-PVTRATE`, `!NVS CFG-RAWRATE`, `!NVS CFG-SMOOTH`, or raw hexadecimal `!NVS CFG-BINR xx ...`. Loading a script still does not transmit a section unless the corresponding startup or shutdown checkbox is enabled.

## Product downloads

### RTKGET URL-list grammar

The new RTKGET reads one whitespace-separated record per product: data-type ID, `ftp://` or `http://` URL, and default local directory; `#` starts a comment, and underscores in the ID form category separators. A blank URL-list setting uses `data\URL_LIST.txt` from the installation.

```text
PRODUCT_EPH ftp://host/products/%W/product%W%D_%h.sp3.Z C:\products\%W
```

Paths expand calendar fields `%Y`, `%y`, `%m`, `%d`, and `%M`; `%h` is hour `00`–`23`, `%H` is hour code `a`–`x`, `%n` is day of year, `%W`/`%D` are GPS week/day, and `%N` is a sequence number. `%s` lowercases a station name, `%S` uppercases it, `%r` inserts the station token, and `%{env}` inserts an environment variable; the same expansion applies to the default or overridden local directory.

### RTKGET selection and diagnostics

RTKGET expands its catalog over a GPST start/end/interval, station selections, and a `%N` sequence whose GUI field accepts ranges such as `1-99`; it can skip existing files and unpack downloaded archives. Enabling detailed error retention writes `<downloaded-file>.err`, retaining the remote directory listing writes `.listing` in the current directory, and Abort cannot cancel the transfer already in progress.

## Demo5 stream and console extensions

### Current caster and UDP endpoint grammar

The Demo5 A.5 command reference spells local caster output as `ntripc://[user:passwd@][:port]/mountpoint[:srctbl]`; it also adds directional UDP endpoints, with `udpsvr://:port` input-only and `udpcli://address:port` output-only.

```sh
str2str -in serial://ttyUSB1:115200 -out 'ntripc://:12345/BASE'
str2str -in udpsvr://:3000 -out udpcli://192.0.2.10:3001
```

### `str2str` feedback and per-output controls

`-b str_no` relays messages received from a selected output stream back to the common input, and `-c1` through `-c4` attach receiver-command files to individual outputs while `-c` remains the input command file. Generated RTCM metadata can be supplied with `-px x y z`, `-a antinfo`, `-i rcvinfo`, and `-o e n u`; the manual spells the background-detachment flag `--deamon`, with `-t`/`-fl` selecting trace level and file.

### RTKRCV headless and diagnostic controls

`rtkrcv -nc` starts the RTK server without a console, `-w` sets the remote-console password, `-sta` supplies the station name used for receiver DCB handling, and `--deamon` detaches. New console-visible operations include `ssr [cycle]`, `error`, `log [file|off]`, and `help path` for stream-path syntax.

```sh
rtkrcv -nc -o rover.conf --deamon
```

## Stream conversion preservation

### RTCM message 1230 is not preserved by stream conversion

Enabling RTKLIB's RTCM conversion path decodes and re-encodes the selected output rather than mixing generated messages with untouched input. The discussed converter can generate legacy 1004/1012 observations from an incoming MSM stream but cannot generate 1230, so even an input 1230 disappears from the converted output; use byte-for-byte relay when the existing 1230 must be retained.

## RTKRCV and str2str configuration

### RTKRCV stream-slot configuration

An RTKRCV options file has three input slots: `inpstr1-*` is normally the rover, `inpstr2-*` the base, and `inpstr3-*` an additional correction source. Each has `type`, `path`, `format`, and receiver-specific `rcvopt` settings; the file also provides two solution outputs (`outstr1-*`/`outstr2-*`), three input logs (`logstr1-*` through `logstr3-*`), and one receiver command file per input (`cmdfile1` through `cmdfile3`).

```text
inpstr1-type   =serial
inpstr1-path   =ttyACM0:115200:8:n:1:off
inpstr1-format =ubx
inpstr2-type   =ntripcli
inpstr2-path   =user:passwd@caster.example:2101/MOUNT
inpstr2-format =rtcm3
```

### Console option matching and persistence

The interactive `option` command lists every processing option when called alone and pattern-matches names when given an argument. `set name` without a value prompts for one, while `load` and `save` use `rtkrcv.conf` when their filename is omitted; for a remote Telnet console, an empty `-w` value explicitly means no login password.

```text
rtkrcv> option inpstr
rtkrcv> set inpstr1-path
rtkrcv> save field.conf
```

### Time-tagged file replay and rotation

A file input can use `file://path::T::+start::xspeed`: `::T` selects the time-tagged recording, `::+start` chooses its replay offset, and `::xspeed` sets the replay-speed factor. The file grammar also accepts `::S=swap` for swapping, while `str2str -f sec` sets the overlap margin at a swap boundary and defaults to 30 seconds.

```sh
str2str -in 'file://capture.ubx::T::+60::x2' -out tcpsvr://:22101
```

### Scheduled FTP and HTTP inputs

RTKRCV's stream-path grammar accepts scheduled correction downloads as `user:passwd@addr/path::T=poff,tint,off,rint` for FTP and `addr/path::T=poff,tint,off,rint` for HTTP. In `str2str`, `-l local_dir` selects the local directory for FTP/HTTP downloads.

### `str2str` connection defaults

The default stream timeout and reconnect interval are both 10000 ms (`-s` and `-r`). The NMEA request cycle (`-n`) defaults to `0`, so periodic rover-position requests must be enabled explicitly when the correction service needs them.

