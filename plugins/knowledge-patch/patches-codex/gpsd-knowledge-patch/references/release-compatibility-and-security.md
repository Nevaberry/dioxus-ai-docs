# Release Compatibility and Security

## Security

### Malicious-packet fixes in 3.27.1
Release 3.27.1 fixes two parsing vulnerabilities: CVE-2025-67268, a heap-based out-of-bounds write in NMEA2000 handling, and CVE-2025-67269, an integer underflow in NovAtel handling. Deployments that can receive untrusted packets need 3.27.1 or later.

## API and client compatibility

### Corrected 3.27 API versioning
Release 3.27.3 corrected an API-major value from 0 to 3; 3.27.4 then bumped the API version to 16.1, and 3.27.5 corrected that bump and made `cgps` check for a matching API version.

### Newer signal IDs in 3.27 clients
Release 3.27 improves handling of newer L1, L2, and L5 signal IDs; `xgps` displays signal-ID names, while `gpsrinex` supports the new IDs and adds `-g` and `--gnss` options.

### Client-interface and desktop compatibility
The `Lexer()` FFI interface was deprecated in October 2025. Release 3.27 also makes `xgps` and `xgpsspeed` work under Wayland and adds Qt6 support.

## Corrections and protocol coverage

### Initial SPARTNv2 support
Release 3.27 adds initial SPARTNv2 support, but it is disabled by default; do not assume a default installation can consume SPARTNv2 corrections.

### Chunked NTRIPv2 transport
Release 3.26 accepts NTRIPv2 data delivered in chunks, allowing correction streams from casters that use chunked transfer.

### Unconditional protocol drivers
Beginning with 3.26, the u-blox, RTCM104v2, and RTCM104v3 drivers are always built rather than selected as optional build features. The same release adds RTCM3.2 support.

### Receiver-protocol coverage changes
Release 3.26 adds partial Allystar support, minimal Unicore, CASIC, and Inertial Sense support, and handling for new BeiDou PRNs and subframes. It removes Oceanserver IMU support.

## Tooling and system integration

### Tool lifecycle changes
The `ntploggps` utility moved from NTPsec into GPSD and was renamed `gpslogntp` in 3.26. That release also officially deprecated `gpsmon`, with 3.26.1 making the deprecation more visible.

### Linux GNSS-subsystem hotplug
Release 3.26 adds a `SUBSYSTEM=gnss` rule to `gpsd.rules`, bringing Linux GNSS-subsystem devices into the udev hotplug path.

### Development-only 3.27.6 changes
The unreleased 3.27.6 development stream adds Oncore M12 and Erickson GRU 04 support, plus `gpsdctl -l` to log to standard error instead of syslog.
