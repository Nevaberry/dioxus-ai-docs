# Daemon Architecture

### Demand-driven device lifecycle
The daemon can keep a sensor in its device pool without holding it open: a client watch awakens the device, while non-`nowait` operation deactivates devices after an idle period with no clients but leaves them available for a later watch. Hotplug notifications add or remove pool entries, and devices that stop producing data are disabled or timed out.

### Hotplug control socket protocol
The local control socket accepts one line at a time: `+` adds a device, `-` removes one and notifies clients, and `!device=control-string` writes a device-specific command; each operation replies `OK` or `ERROR`.

```text
+/dev/ttyUSB0
-/dev/ttyUSB0
!/dev/ttyUSB0=<control-string>
```

### Autodetection and safe probing
GPSD has no daemon configuration file for sensor types or serial settings: its packet sniffer identifies protocols, and serial/USB sessions hunt through baud rate, parity, and stop-bit combinations. Run the daemon with `-b` when baud-rate changes could wedge fragile devices; probe and wake-up strings must likewise be limited to device transports that can safely receive them.

### Four-layer daemon split
The sensor path is divided into protocol drivers, a packet-sniffing state machine, a per-device core library, and the `gpsd.c` client/device multiplexer. The first three form `libgpsd`, so direct-device tools such as `gpsmon` and `gpsctl` can reuse them without the multiplexer, while `gpsdecode` can replace the multiplexer with batch log-to-JSON output.

### Packet-driven driver switching
The sniffer recognizes checksummed packet types without interpreting their payloads, then the core dispatches each complete packet to its associated driver. Driver selection is not fixed at open time: a device may switch protocols, and distinct protocols can coexist on one wire, so the active driver can change as packets arrive.

### Driver extension contract
Each driver exposes a `struct gps_type_t` capability/method table, registered through the master driver table; `driver_proto.c` is the commented skeleton for a new driver. Compile-time driver selection also removes that driver's packet states from the sniffer, allowing embedded builds to omit both unused parsers and their recognition machinery.

### Normalized report boundary
Drivers decode payloads into a per-device session structure and return a field-validity mask; a report-ready bit marks the end of a packet or packet group. Exporters consume only that normalized session state, keeping transport recognition, payload parsing, and JSON/shared-memory/DBus delivery independent.

### Core state and generated headers
`struct gps_device_t` owns one device session plus driver-private storage, `struct gps_packet_t` owns its lexer state, `struct gps_context_t` carries session-wide context, and `struct gps_type_t` represents one driver type. Internal `gpsd.h` is generated at configure time from `gpsd.h-head`, generated options, and `gpsd.h-tail`; changes belong in `gpsd.h-tail`, not in either generated `gpsd.h` or `gpsd.h-head`.

### Fixed-storage JSON and alternate exporters
Reports use a `class` member to make new object types extensible, but the daemon's static-storage JSON dialect excludes `null` and gives arrays fixed maximum lengths. The daemon deliberately avoids `malloc`/`calloc`; when daemon and client share memory, the shared-memory exporter can bypass JSON generation and parsing entirely, with DBus as another export path.

### Client-library data flow
`libgps` unmarshals daemon JSON into `struct gps_data_t` and sets its `set` mask to identify valid fields; `gps_poll()` receives and decodes updates, `gps_waiting()` checks without blocking, and `gps_stream()` controls watch policy. `gps_open_r()` uses caller-provided storage for re-entrant use, and the raw formatted-command entry point `gps_send()` is deprecated in favor of `gps_stream()`.

### Correction and precision-time paths
DGPSIP and NTRIP correction sources enter the main loop like navigation sensors, with received corrections stored in shared context and relayed to GPS devices that accept them. NTP integration allocates shared-memory segments per session; PPS delivery is withheld until several good fixes have established trust and is rejected when pulse shape or timestamp proximity fails sanity checks.

### Process and client safety boundaries
After opening privileged resources and preparing device permissions, the daemon drops to its compiled-in user (typically `nobody`) and the tty-device group. Short writes, broken sockets, persistently non-reading clients, and clients that time out without an assigned or responsive device are detached rather than allowed to stall the multiplexer.

### Replay and diagnostic tools
`gpsfake` presents one or more recorded sensor logs to the daemon as live devices and underpins reproducible bug cases and the regression suite. `gpsmon` provides low-level monitoring, `gpsprof` reports error and timing statistics, `gpsctl` changes device settings, and `gpsdecode` converts captured sensor data to readable JSON.

