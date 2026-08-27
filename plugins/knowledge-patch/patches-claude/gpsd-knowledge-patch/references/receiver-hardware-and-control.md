# Receiver Hardware and Control

### Daemon-mediated and direct receiver access
With GPSD running and only one receiver attached, `gpsctl` can omit the device and let the daemon select it, and this daemon-mediated path is available to an ordinary user. `-f` forces direct access, which requires an explicit device and write permission as root or through the device-owning group; with no change option, `gpsctl` identifies the selected receiver and exits after an eight-second default sampling timeout, adjustable with `-T`.

```sh
gpsctl
gpsctl -f -T 12 /dev/ttyUSB0
```

### Ordered changes and standalone reset
Combined requests run in a fixed order: binary/NMEA mode (`-b`/`-n`), baud (`-s`), cycle time in seconds (`-c`), then control strings (`-x`). Reset (`-r`) must be used alone with both a device path and forced type, and mode or baud changes are reliable in direct mode but not through the daemon client path.

```sh
gpsctl -f -n -s 9600 /dev/ttyUSB0
gpsctl -f -r -t TYPE /dev/ttyUSB0
```

### Driver forcing semantics
The `-t TYPE` argument must be a substring unique to one driver name from `gpsctl -l`, which also shows which control switches each receiver type supports. Through GPSD it only verifies that the daemon-selected receiver matches and otherwise exits with a warning; in direct mode it replaces a `Generic NMEA` identification with the selected driver, allowing control of known receivers that do not answer probes.

### SiRF identification side effect
A SiRF receiver emitting NMEA can be identified only by successfully attempting to switch it into SiRF binary mode. Consequently, even an identification probe can change that receiver's output mode.

### Control-string framing
`gpsctl -x` decodes C-style escapes, including `\xNN` and `\e`, and an NMEA string must include its leading `$`. Through GPSD the decoded bytes are forwarded unchanged, so the caller must supply the complete header, checksum, and suffix; direct mode instead adds the framing and checksum required by the forced or detected driver.

```sh
gpsctl -x '\xb5\x62\x0a\x04\x00\x00\x0e\x34'
```

### Direct-mode binary payload rules
For UBX, Allystar, and CASIC, the first two `-x` bytes are the message class and type; for Navcom NCT and Trimble TSIP, the first byte is the command ID; for Zodiac, the first two bytes are a little-endian short message ID and the remaining byte pairs are little-endian shorts. Other supported binary protocols, including SiRF, treat the entire string as payload; `-e` writes the resulting packet as raw bytes to standard output and can be combined with `-t` without opening a device.

### Shared-memory export cleanup
`gpsctl -R` removes the selected GPSD shared-memory export segment, providing an explicit cleanup operation for test or stale SHM instances.

```sh
gpsctl -R
```

### PPS transport accuracy tiers
A receiver's USB data connection alone does not carry hardware PPS: the documented serial paths are direct RS-232 or a serial-to-USB adapter with the receiver's 1PPS wired to DCD. Typical reported NTP stability is on the order of 1 microsecond over RS-232 versus 1 millisecond over such USB adapters, while a native-USB receiver without PPS yields serial-derived time accurate only to about 250 milliseconds.

### Firmware-dependent raw measurements
Raw observables are exposed only when both firmware and protocol allow them: SiRFstar1 uses message 5, SiRFstar2 message 28, and SiRFstar3 message 28 without carrier phase; u-blox uses `RXM-RAW`, available on all Antaris chips, only timing Antaris4 variants, and premium-raw u-blox 5 firmware. NovAtel SuperStarII uses message 23 only with carrier-phase firmware, while Fastrax `PSEUDO`, Trimble packet `0x5a`, and Thales AC12 `PASHR,MCA` provide raw measurements; NavSync requires unavailable custom firmware.

### Manual setup for newer u-blox timing hardware
The MAX-M10Q and MAX-M10S breakouts and the EVK-F10T cannot be autoconfigured by GPSD, so their receiver output must be configured manually. The EVK-F10T, EVK-F9T-20-00, and EVK-M9DR-0 do not carry PPS over USB; use their separate UART or RS-232 PPS path for time service.

### Decoding does not imply configuration support
The HI-303S works in NMEA but ignores the `$PSRF100` mode-switch command and does not provide working SiRF binary control on its normal port. Likewise, WBT-200 iTalk and WBT-201 UBX data can be decoded even though protocol switching and device configuration are unsupported.

### Garmin interface prerequisites
The Foretrex 201 and GPS 76 must be placed in NMEA output mode in their device settings; the GPS 76's serial adapter does not require the Linux `garmin_gps` module, whereas the GPS-18 USB requires the kernel `garmin_usb` driver. A GPS-15 must receive `$PGRMI,,,,,,,R` before PPS works and can then take about five minutes before GPSD detects the pulse correctly.

### Garmin binary-data limitations
The GPS-16 does not return DGPS information in GPGGA; its binary mode omits satellite azimuth/elevation and magnetic variation, and its signal quality uses a nonstandard 16-bit SNR scale. `PGRMC1` can switch it to NMEA 3.0; the GPS-18 USB similarly lacks native DOP and magnetic variation, so GPSD approximates DOP from EPE and must interpret Garmin's nonstandard SNR representation.

### eXplorist USB mode selection
An eXplorist 210 must be put in USB `NMEA Data Comm` mode to expose `/dev/ttyACM0`, then configured for NMEA v2.1 GSA. Its APA and XTE extensions choke GPSD, while its other USB modes expose file storage or power only rather than live navigation data.

### Receivers that require preactivation
The Thales AC12 may start silent and needs `ashctl` to enable a default message set; the CH-4711 needs its vendor tool configured to report 2D fixes if they are wanted. An RGM-3800 must have GPS-mouse output enabled before GPSD starts.

```sh
rgm3800.py -d /dev/ttyUSB0 gmouse on
```

### Enabling GST on a LEA-5Q
The LEA-5Q does not emit GPGST by default; enable it by sending its complete checksummed `PUBX,40` control sentence.

```sh
gpsctl -x '$PUBX,40,GST,1,1,1,0*5A\n'
```

### CPIT GP-27 persistent controls
The CPIT GP-27 stores settings in battery-backed flash across connections and power cycles, but its Bluetooth interface does not support baud changes through `PNMRX100`. Do not send that sentence to change its baud rate.

