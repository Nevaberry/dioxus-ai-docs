# Daemon Operation

### Passive and persistent receiver configuration
`-p`/`--passive` suppresses automatic receiver configuration but still permits manual configuration changes. GPSD may change a receiver's sentence or packet emission settings and cannot generally restore their original values when it exits.

### Fixed serial framing and speed
`-f`/`--framing` accepts `[78][ENO][012]` framing such as `8N1` or `8O1`; `-s`/`--speed` accepts 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, or 921600 baud. Both default to detection, but fixing the speed can avoid Trimble autobaud delays of 20 seconds or more, and integrated USB receivers may ignore the requested speed.

```sh
gpsd -f 8O1 -s 115200 /dev/ttyUSB0
```

### Runtime driver inventory
`gpsd -l` lists the drivers compiled into that binary and exits; the letters printed to the left of each driver identify the GPSD control commands it supports.

### Data-source forms
Besides local serial/USB paths, GPSD accepts a `/dev/ppsN` source when a local serial/USB GPS is also present, outbound `tcp://host:port` feeds, listening `udp://address:port` feeds, authenticated `ntrip://user:password@caster:port/stream` correction feeds, `dgpsip://host[:port]` feeds whose port defaults to 2101, remote `gpsd://host[:port][:device]` feeds, and Linux SocketCAN `nmea2000://interface` feeds. A CAN interface must already be configured; if several units provide positions, GPSD selects the first one from which it sees a GPS message.

```sh
gpsd tcp://data.example:4006
gpsd udp://127.0.0.1:5000
gpsd ntrip://user:password@caster.example:80/stream
gpsd gpsd://remote.example:2947:/dev/ttyAMA0
gpsd nmea2000://can0
```

### MAGIC_HAT PPS aliases
In a binary built with `MAGIC_HAT`, using `/dev/ttyAMA0` or `/dev/gpsd0` also opens `/dev/pps0` for RFC 2783 PPS; if that node is the fake `ktimer` PPS, GPSD uses `/dev/pps1` instead.

### Hotplug-only startup and device hooks
Startup fails when neither an initial source nor a `-F` control socket is supplied. A hotplug-only daemon that has seen devices later exits once it has neither connected devices nor subscribers, and `/etc/gpsd/device-hook` is invoked on demand-driven activation and deactivation with the device path followed by `ACTIVATE` or `DEACTIVATE`.

```text
/etc/gpsd/device-hook <device> ACTIVATE
/etc/gpsd/device-hook <device> DEACTIVATE
```

### Binary control-socket writes
The control socket's `&` operation sends binary data to a device, with the payload encoded as paired hexadecimal digits.

```text
&/dev/ttyUSB0=<paired-hex-digits>
```

### SIGHUP reset semantics
`SIGHUP` closes every GPS and client connection, then reconnects the devices still in the pool and resumes accepting clients; it can therefore reset a receiver that recovers when DTR is dropped, but connected clients must reconnect too.

### D-Bus fix signal contract
When D-Bus support is built in, each fix is emitted as signal `fix` on path `/org/gpsd` and interface `org.gpsd`. Its ordered payload is time, mode, time uncertainty, latitude, longitude, horizontal uncertainty, MSL altitude, altitude uncertainty, course, course uncertainty, speed, speed uncertainty, climb, climb uncertainty, and device name; all but the 32-bit mode and final string are doubles.

### Host-clock dependence and no-fix time
GPSD uses the daemon's startup time to disambiguate GPS week rollovers, and an NMEA-only receiver without an early GPZDA sentence relies on the host clock for the current century. `-r`/`--badtime` allows GPS time to be used without a current fix when the receiver has a trustworthy battery-backed RTC, but can otherwise publish bad time.

### NTP and chrony channels
Run with `-n`/`--nowait` when GPSD is a reference clock so it polls without a watching client. Local time sources consume NTP shared-memory pairs in command-line order (`NTP0`/`NTP1`, then `NTP2`/`NTP3`, through `NTP6`/`NTP7`), observable with `ntpshmmon`; GPSD also looks in its run directory for `chrony.<device>.sock` for PPS and `chrony.clk.<device>.sock` for serial-derived time.

### Late-added PPS limitation
On systems other than Linux, a PPS-capable device added through the control socket may be too late for GPSD to set its PPS line discipline because root privileges have already been dropped. Put such timing devices on the original command line; Linux retains the required capability after the drop.

### Exact client timeout classes
A client that has not requested a channel is timed out after 60 seconds, while an assigned device in polling mode has a 15-minute timeout. Watcher and raw-mode clients have no inactivity timeout, though they are still removed if they stop reading until the outbound socket buffer fills.

### File capabilities for unprivileged startup
A capabilities-enabled build can start as a normal user with reduced functionality when the executable has `CAP_FOWNER` for `chmod()`, `CAP_SETGID` for group changes, and `CAP_SETUID` for user changes.

```sh
export CAPS='cap_fowner=ep cap_setgid=ep cap_setuid=ep'
setcap "$CAPS" /path/to/gpsd
getcap /path/to/gpsd
```

### Shared-memory test isolation
Set `GPSD_SHM_KEY` to choose the key of the shared-memory segment used by client libraries, allowing a test daemon's segment to be isolated from production.

### Mixed NMEA talkers
When several NMEA talkers feed one serial stream, a `TPV` report can combine altitude from one talker's GGA sentence with latitude and longitude from another talker's RMC or GLL sentence; do not treat such a multiplexed stream as source-isolated.

### RTCM2 decoding coverage
GPSD fully recognizes RTCM 2.1 message types 1, 3-7, 9, and 16; of RTCM 2.3 it recognizes and reports types 13, 14, and 31, while the other listed RTCM2 message types are unsupported.

