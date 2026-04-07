# RTKBase Architecture: str2str Service Chain

RTKBase runs multiple RTKLIB `str2str` instances as systemd services. The main instance connects to the GNSS receiver and broadcasts raw data on TCP; all other services consume from it.

## Service Topology

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

## Service Details

### str2str_tcp (Main Service)

The core service. Connects to the GNSS receiver via serial/USB and serves raw observation data on a local TCP port (default 5015). All downstream services connect to this TCP stream.

- Bind address configured via `tcp_host_addr` in `settings.conf` (default `127.0.0.1`, use `0.0.0.0` for external access)
- Port configured via `tcp_port` (default `5015`)

### NTRIP Services (ntrip_A, ntrip_B)

Read from the main TCP stream, convert raw receiver data to RTCM3 format, and push to an external NTRIP caster. Two independent slots (A and B) allow simultaneous streaming to different casters.

- Receiver-specific options supported (e.g., `-TADJ=1` for u-blox)
- RTCM message selection and rate control per-caster

### Local NTRIP Caster

Self-hosted NTRIP caster running on the base station itself (default port 2101). Allows rover connections without an external caster.

### RTCM Server/Client/Serial/UDP

Additional output modes for RTCM data:
- `rtcm_svr`: TCP server (default port 5016) for direct client connections
- `rtcm_serial`: Output to serial port for radio links
- `rtcm_udp_svr` / `rtcm_udp_client`: UDP transport options

### File Logging (str2str_file)

Logs raw receiver data to files. Configured via `[local_storage]` section:
- File rotation by time (default 24 hours)
- Archive rotation (default 60 days before deletion)
- Minimum free space check (default 500 MB)

### rtkbase_raw2nmea

Optional service for non-UBX receivers. Converts raw data to NMEA sentences and serves on a TCP port (default 5014) for consumption by gpsd.

### rtkbase_web

Flask/Gunicorn web application providing the configuration GUI. Default port 80, configurable via `web_port` in `settings.conf`.

### rtkbase_archive.timer

Systemd timer that runs daily to compress raw log files and clean up archives older than `archive_rotate` days.

## Configuration Flow

All services are configured via `run_cast.sh` which reads `settings.conf` (INI format). The web GUI modifies `settings.conf` and restarts the relevant services.
