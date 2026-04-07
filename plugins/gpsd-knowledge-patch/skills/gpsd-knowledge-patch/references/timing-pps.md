# TOFF and PPS Reports for Precise Timing

gpsd provides two timing report classes for applications that need precise time synchronization (NTP servers, time-stamping systems).

## Enabling Timing Reports

Both TOFF and PPS must be explicitly enabled in the WATCH command:

```json
?WATCH={"enable":true,"json":true,"pps":true}
```

The `"pps":true` flag enables both TOFF and PPS output.

## TOFF — Time Offset from Serial Data

TOFF reports derive timing from the serial data stream (NMEA sentences or binary protocol messages). Each report carries two timestamps:

| Field | Description |
|-------|-------------|
| `real_sec` | GPS time — seconds |
| `real_nsec` | GPS time — nanoseconds |
| `clock_sec` | System clock time — seconds |
| `clock_nsec` | System clock time — nanoseconds |

The offset between GPS time and system time is: `(real_sec + real_nsec/1e9) - (clock_sec + clock_nsec/1e9)`.

TOFF precision is limited by serial port latency (typically milliseconds).

## PPS — Pulse Per Second

PPS reports come from the hardware 1PPS pulse that many GPS receivers output. This is **much more precise** than TOFF — typically sub-microsecond.

PPS carries the same `real_sec`/`real_nsec` and `clock_sec`/`clock_nsec` fields as TOFF, plus:

| Field | Description |
|-------|-------------|
| `precision` | Log2 of the pulse precision in seconds (e.g., -20 ≈ 1 µs) |
| `shm` | Shared memory segment number used for NTP SHM driver |
| `qErr` | Quantization error / sawtooth correction in **picoseconds** |

### Sawtooth Correction (qErr)

Many GPS receivers' 1PPS output has a quantization error (sawtooth jitter) because the pulse is aligned to the receiver's internal clock, not the true GPS second boundary. The `qErr` field provides the correction in picoseconds. Subtract this from the measured PPS offset for higher accuracy:

```
corrected_offset = measured_offset - (qErr / 1e12)
```

## TOFF vs PPS Summary

| Property | TOFF | PPS |
|----------|------|-----|
| Source | Serial data stream | Hardware 1PPS pulse |
| Typical precision | ~1–10 ms | ~0.1–1 µs |
| Requires hardware PPS | No | Yes |
| Extra fields | — | `precision`, `shm`, `qErr` |
| NTP use case | Coarse time-of-day | Precise second boundary |
