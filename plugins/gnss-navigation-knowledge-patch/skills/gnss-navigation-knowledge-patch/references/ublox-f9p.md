# u-blox ZED-F9P & UBX Protocol

## Overview

The ZED-F9P is a multi-band (L1/L2) GNSS receiver supporting RTK and PPP. Configured and queried via the proprietary UBX binary protocol.

## Configuration (CFG Keys)

The F9P uses a key-value configuration system. Keys are set via `UBX-CFG-VALSET` and read via `UBX-CFG-VALGET`.

| CFG Key | Purpose | Notes |
|---------|---------|-------|
| `CFG-TMODE-MODE` | Base station mode | 0=disabled, 1=survey-in, 2=fixed |
| `CFG-TMODE-SVIN_MIN_DUR` | Survey-in minimum duration (seconds) | Typical: 60–300 s |
| `CFG-TMODE-SVIN_ACC_LIMIT` | Survey-in accuracy limit (0.1 mm) | Typical: 30000 (3 m) to 50000 (5 m) |
| `CFG-MSGOUT-RTCM_3X-*` | RTCM message output enable per port | One key per message type per port |
| `CFG-RATE-MEAS` | Measurement period (ms) | 1000=1 Hz, 100=10 Hz |
| `CFG-RATE-NAV` | Navigation rate (cycles per measurement) | Usually 1 |
| `CFG-SPARTN-USE_SOURCE` | SPARTN corrections source | FW 1.51+. 0=L-band, 1=IP |

Configuration layers: RAM (volatile), BBR (battery-backed), Flash (persistent).

## Output Messages

### NAV Class (Navigation Results)

| Message | Content |
|---------|---------|
| `NAV-PVT` | Position, velocity, time solution. Primary output — includes fix type, accuracy estimates, number of SVs. |
| `NAV-RELPOSNED` | Relative position (NED) from base to rover. RTK-specific — includes carrier solution flags (float/fix). |
| `NAV-HPPOSLLH` | High-precision geodetic position (lat/lon/height) with mm-level resolution fields. |
| `NAV-STATUS` | Receiver navigation status and fix type. |
| `NAV-SAT` | Per-satellite info: elevation, azimuth, CNR, health, usage flags. |

### RXM Class (Raw Measurements)

| Message | Content |
|---------|---------|
| `RXM-RAWX` | Raw measurements: pseudorange, carrier phase, Doppler, CNR per satellite per frequency. Required for PPK post-processing. |
| `RXM-SFRBX` | Raw subframe data (navigation message bits). Required for PPK with broadcast ephemeris. |
| `RXM-SPARTNKEY` | SPARTN decryption key management. Used to inject keys for PointPerfect PPP corrections. |

## RTK Operation

RTK activates automatically when valid RTCM correction data is received on **any** port (UART, SPI, I2C, USB). No explicit mode switch required.

Fix progression: `No fix` → `3D fix` → `Float RTK` → `Fixed RTK` (cm-level).

## Hardware Defaults

- Default UART baud rate: **115200**
- Default navigation rate: **1 Hz**
- Supports concurrent GPS + GLONASS + Galileo + BeiDou
- Two UART ports: UART1 (primary), UART2 (secondary, typically for RTCM input/output)
