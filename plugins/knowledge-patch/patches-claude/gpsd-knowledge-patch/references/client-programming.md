# Client Programming

### C build and API-version contract
C clients include `<gps.h>` and link with `-lgps`; adding `-lm` is always safe and is required on systems that do not propagate libgps's math-library dependency. Guard builds with `GPSD_API_MAJOR_VERSION` and `GPSD_API_MINOR_VERSION`, and fail compilation on an unrecognized major version rather than assuming `gps_data_t` and its APIs are compatible.

### Socket session lifecycle and current read API
`gps_open(server, port, &gpsdata)` initializes caller-owned storage and accepts a DNS name, IPv4 or IPv6 address; it returns 0 on success and -1 with `errno` on failure, and `gps_close()` is valid only after a successful open. The current streaming entry point is `gps_read()`—pre-v5 bindings called it `poll()`, while the old request/response-oriented `gps_query()` has been removed.

`gps_stream()` may be called repeatedly to change policy. To select one source, pass its path as the third argument together with `WATCH_DEVICE`:

```c
gps_stream(&gpsdata, WATCH_ENABLE | WATCH_JSON | WATCH_DEVICE,
           "/dev/ttyUSB0");
```

### Buffered reads and accumulated state
A socket `gps_read()` may obtain part of one JSON object, one object, or several objects plus a fragment; libgps retains an incomplete tail and unpacks every complete object into the same `gps_data_t` blackboard. `PACKET_SET` means at least one complete response arrived on that read, but data and validity state accumulate across reads, so clients that need per-read state must clear it deliberately and must compare the fix and sentence timestamps; replacement TPV data is written atomically rather than field by field.

### Waiting, return values, and drain cadence
`gps_waiting()` takes a maximum wait in microseconds, clears `errno` on entry, and returns false for either timeout or error, so inspect `errno` when the distinction matters. Use a wait of at least twice the receiver cycle to avoid treating a normal reporting gap as failure, while still draining the socket more often than one report cycle; AIS consumers should read more often than every two seconds so a later message of the same type cannot overwrite an earlier one in the blackboard.

On success `gps_read()` returns the byte count, returns 0 when no data is available, and returns -1 with `errno` set for a Unix read error. A -1 without a newly set `errno` denotes a daemon-side socket close or an unavailable shared-memory segment.

### Raw buffers and caller-managed I/O
Passing a buffer and size to `gps_read()` exposes the raw daemon response, while `gps_data()` returns the library's client buffer; under `WATCH_RAW`, neither is guaranteed to be NUL-terminated. `gps_unpack()` parses JSON supplied by the caller for applications that manage their own socket I/O, and `gps_mainloop()` instead drives a callback until its microsecond timeout or an error produces a negative return.

### Shared-memory client mode
Passing `GPSD_SHARED_MEMORY` as the `gps_open()` host selects the local shared-memory export. It supplies immediate snapshots with `gps_fd == -1` and `PACKET_SET` asserted, but cannot filter by device or deliver activation, deactivation, or packet-traffic notices; `gps_stream()` is unavailable, `gps_send()` does nothing, and `gps_data()` returns NULL. Because `gps_waiting()` has a race with the following nonblocking shared-memory read, prefer a simple `gps_read()` loop in this mode.

### Explicit-command union hazard
If legacy `gps_send()` is unavoidable, account for response fields that share union storage inside `gps_data_t`: closely sequenced VERSION, DEVICELIST, RTCM2, RTCM3, SUBFRAME, AIS, GST, or ERROR responses can overwrite one another, and that list is not guaranteed exhaustive.

### C++ binding ownership model
`gpsmm` is a thin RAII wrapper over libgps: constructing `gpsmm(host, port)` opens the session, destruction closes it, and `read()` returns access to the underlying C `gps_data_t` blackboard rather than an independent value. It has no `unpack()` method; `libQgpsmm` supplies the related Qt wrapper.

### Python session model
The `gps.gps` constructor opens a session and the other C operations become methods. Iteration is a shim over `read()` and cannot pass its options; after an explicit read, `session.response` holds the received text and JSON is decoded into `session.data`, which supports both key and attribute access, while `session.bresponse` exposes bytes.

```python
import gps

session = gps.gps(host="localhost", port="2947")
session.stream(flags=gps.WATCH_JSON)
for report in session:
    print(report)
```

### Common client endpoint and unit conventions
Daemon-connected command-line clients default to `localhost:2947` and accept `[server[:port[:device]]]`; bracket an IPv6 literal before adding port or device suffixes, and use an empty port field to select a device on the default port, as in `localhost::/dev/ttyS1`.

When no command-line unit system is selected, `GPSD_UNITS` accepts `i`/`imperial`, `m`/`metric`, or `n`/`nautical`. Otherwise clients consult `LC_MEASUREMENT` and then `LANG`; `C`, `POSIX`, and `en_US...` select imperial, with metric as the final default.

### Bundled conversion and administration clients
Purpose-built data clients include `gpscsv` for JSON-to-CSV conversion, `gpspipe` for retrieving sentences, `gpsrinex` for RINEX3 output, `gpssubframe` for subframe dumps, `gpxlogger` for GPX output, and `gps2udp` for forwarding data to aggregation sites; `gegps` and `lcdgps` provide Google Earth and LCD front ends.

Additional helpers include `gpscat` for dumping a receiver's output, `gpsdctl` for control-socket operations, `gpsdebuginfo` for a host debug dump, and `gpsinit` for initializing the CAN kernel modules used by GPSD.

