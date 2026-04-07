---
name: gpsd-knowledge-patch
description: "gpsd changes since training cutoff (latest: latest) — altHAE/altMSL, ECEF/NED fields, TOFF/PPS timing, gps_mainloop(), shared-memory API. Load before working with gpsd."
version: "latest"
license: MIT
metadata:
  author: Nevaberry
---

# gpsd Knowledge Patch

Covers gpsd JSON protocol fields, libgps C client API, and timing interfaces. Claude knows gpsd daemon basics, gpspipe, cgps, and JSON protocol fundamentals, but is **unaware** of the specific field semantics, deprecations, and API patterns below.

## Index

| Topic | Reference | Key content |
|---|---|---|
| TPV message fields | [references/tpv-message.md](references/tpv-message.md) | altHAE/altMSL, status codes, ECEF/NED, float validity |
| Timing & PPS | [references/timing-pps.md](references/timing-pps.md) | TOFF/PPS reports, sawtooth correction, NTP integration |
| Client API (libgps) | [references/client-api.md](references/client-api.md) | gps_mainloop(), shared-memory interface, usage patterns |

---

## Essential Quick Reference

### ECEF and NED Velocity/Position Fields

TPV can include ECEF (Earth-Centered, Earth-Fixed) coordinates and NED (North-East-Down) components:

```json
{
  "class": "TPV",
  "ecefx": 3981234.56,
  "ecefy": 123456.78,
  "ecefz": 4966789.01,
  "ecefpAcc": 2.5,
  "ecefvx": 0.12,
  "ecefvy": -0.05,
  "ecefvz": 0.03,
  "ecefvAcc": 0.1,
  "velN": 0.12,
  "velE": -0.05,
  "velD": -0.03,
  "relN": 1.234,
  "relE": -0.567,
  "relD": 0.089
}
```

`relN`/`relE`/`relD` are RTK baseline vectors relative to a base station (meters). Only populated when the receiver reports RTK baseline data.

### TPV Key Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `altHAE` | float | meters | Height Above Ellipsoid (WGS84) — raw GPS altitude |
| `altMSL` | float | meters | Mean Sea Level altitude — what maps show |
| `geoidSep` | float | meters | Geoid separation: `altHAE - altMSL` |
| `status` | int | — | Fix quality: 2=DGPS, 3=RTK Fixed, 4=RTK Float, 5=DR |
| `ecefx/y/z` | float | meters | ECEF position from Earth center |
| `ecefpAcc` | float | meters | ECEF 3D position accuracy |
| `velN/E/D` | float | m/s | North/East/Down velocity components |
| `relN/E/D` | float | meters | RTK baseline relative to base station |

### Altitude — "alt" Is Deprecated

The `alt` field in TPV is **deprecated and undefined**. Always use `altHAE` or `altMSL`:

```json
{
  "class": "TPV",
  "altHAE": 120.345,
  "altMSL": 85.678,
  "geoidSep": 34.667
}
```

`altMSL` is what most users want (matches map elevations). `altHAE` is the raw GPS measurement.

### Float Validity — Use isfinite(), Not isnan()

Unknown/invalid floats in gpsd are NaN. **Always** check with `isfinite()`:

```c
// WRONG: misses infinity
if (!isnan(gpsdata->fix.speed)) { ... }

// CORRECT: catches NaN AND infinity
if (isfinite(gpsdata->fix.speed)) { ... }
```

### TPV Status Field Values

The `status` field modifies `mode` (not a replacement). Values 0 (Unknown) and 1 (Normal) are **omitted from JSON output** — if absent, assume Normal:

| Value | Meaning | Accuracy |
|-------|---------|----------|
| 2 | DGPS | Sub-meter |
| 3 | RTK Fixed | Centimeter |
| 4 | RTK Floating | Decimeter |
| 5 | DR | Dead Reckoning |
| 6 | GNSSDR | GNSS + DR combined |
| 7 | Time (surveyed) | Time-only mode |
| 8 | Simulated | Test data |
| 9 | P(Y) | Military code |

---

## Timing — Enable TOFF/PPS

```json
?WATCH={"enable":true,"json":true,"pps":true}
```

Both TOFF and PPS carry `real_sec`/`real_nsec` (GPS time) and `clock_sec`/`clock_nsec` (system time).

| Report | Source | Precision | Extra fields |
|--------|--------|-----------|--------------|
| TOFF | Serial data stream | ~1–10 ms | — |
| PPS | Hardware 1PPS pulse | ~0.1–1 µs | `precision`, `shm`, `qErr` |

PPS `qErr` is the sawtooth correction in **picoseconds** — subtract from measured offset for higher accuracy.

---

## Client API Patterns

### gps_mainloop() — Simple Event Loop

```c
int gps_mainloop(struct gps_data_t *gpsdata, int timeout,
                 void (*hook)(struct gps_data_t *gpsdata));
```

`timeout` is in **microseconds**. Returns -1 on timeout or error. Calls `hook` on each data arrival.

```c
#include <gps.h>
#include <math.h>

void on_gps(struct gps_data_t *gpsdata) {
    if (gpsdata->fix.mode >= MODE_2D && isfinite(gpsdata->fix.latitude))
        printf("%.6f, %.6f\n", gpsdata->fix.latitude, gpsdata->fix.longitude);
}

int main(void) {
    struct gps_data_t gpsdata;
    gps_open("localhost", "2947", &gpsdata);
    gps_stream(&gpsdata, WATCH_ENABLE | WATCH_JSON, NULL);
    gps_mainloop(&gpsdata, 5000000, on_gps);  /* 5s timeout */
    gps_stream(&gpsdata, WATCH_DISABLE, NULL);
    gps_close(&gpsdata);
}
```

### Shared-Memory Interface

Pass `GPSD_SHARED_MEMORY` as host for fast local-only access. **Cannot** use `gps_stream()`, `gps_send()`, `gps_waiting()`, or `gps_data()`. `gps_read()` always returns current snapshot; `gps_fd` is always -1.

```c
struct gps_data_t gpsdata;
gps_open(GPSD_SHARED_MEMORY, NULL, &gpsdata);
if (gps_read(&gpsdata, NULL, 0) > 0) {
    if (isfinite(gpsdata.fix.latitude))
        printf("%.6f, %.6f\n", gpsdata.fix.latitude, gpsdata.fix.longitude);
}
gps_close(&gpsdata);
```

**Use for:** embedded systems, simple pollers, monitoring scripts (local only).
**Avoid when:** you need streaming (`gps_stream`), device filtering, `gps_waiting()`, or remote access.

### Shared Memory vs TCP Socket

| Feature | TCP Socket | Shared Memory |
|---------|-----------|---------------|
| `gps_stream()` | Yes | **No** |
| `gps_send()` | Yes | **No** |
| `gps_waiting()` | Yes | **No** |
| Device filtering | Yes | **No** |
| `gps_read()` behavior | Blocks for new data | Returns current snapshot |
| `gps_fd` | Socket fd | Always -1 |
| Remote access | Yes | **No** (local only) |
