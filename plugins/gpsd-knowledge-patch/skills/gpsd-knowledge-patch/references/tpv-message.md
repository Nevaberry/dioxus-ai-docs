# TPV Message Fields

The TPV (Time-Position-Velocity) message is gpsd's primary position report. This reference covers fields and conventions that differ from what you might expect.

## Altitude: altHAE and altMSL (replaces deprecated "alt")

The `alt` field in TPV is **deprecated and undefined** — do not use it. Use the explicit fields:

| Field | Meaning | Datum |
|-------|---------|-------|
| `altHAE` | Height Above Ellipsoid | WGS84 ellipsoid |
| `altMSL` | Mean Sea Level altitude | EGM2008 geoid model |
| `geoidSep` | Geoid separation | `altHAE - altMSL` |

**Relationship:** `altMSL = altHAE - geoidSep`

- `altHAE` is the raw GPS measurement (what the receiver computes directly)
- `altMSL` is what most users want (matches elevations on maps/charts)
- The difference (`geoidSep`) varies by location — up to ~100m in some regions

```json
{
  "class": "TPV",
  "altHAE": 120.345,
  "altMSL": 85.678,
  "geoidSep": 34.667
}
```

## Status Field (fix quality modifier)

The `status` field is a **modifier to `mode`**, not a replacement. The `mode` field indicates fix type (0=unknown, 1=no fix, 2=2D, 3=3D). The `status` field qualifies the fix source/quality:

| Value | Meaning | Notes |
|-------|---------|-------|
| 0 | Unknown | Omitted from JSON output |
| 1 | Normal | Omitted from JSON output |
| 2 | DGPS | Differential GPS correction applied |
| 3 | RTK Fixed | Centimeter-level accuracy |
| 4 | RTK Floating | Decimeter-level accuracy |
| 5 | DR | Dead Reckoning (no satellite fix) |
| 6 | GNSSDR | GNSS + Dead Reckoning combined |
| 7 | Time (surveyed) | Position is surveyed-in, time-only mode |
| 8 | Simulated | Simulated/test data |
| 9 | P(Y) | Military P(Y) code |

**Important:** Values 0 and 1 are omitted from JSON output. If `status` is absent, assume Normal fix.

## ECEF Position and Velocity

TPV can include Earth-Centered, Earth-Fixed coordinates:

**Position (meters from Earth center):**

| Field | Description |
|-------|-------------|
| `ecefx` | ECEF X position (meters) |
| `ecefy` | ECEF Y position (meters) |
| `ecefz` | ECEF Z position (meters) |
| `ecefpAcc` | 3D position accuracy estimate (meters) |

**Velocity (m/s):**

| Field | Description |
|-------|-------------|
| `ecefvx` | ECEF X velocity (m/s) |
| `ecefvy` | ECEF Y velocity (m/s) |
| `ecefvz` | ECEF Z velocity (m/s) |
| `ecefvAcc` | 3D velocity accuracy estimate (m/s) |

## NED Velocity and Relative Position

**Velocity components (m/s):**

| Field | Description |
|-------|-------------|
| `velN` | North velocity (m/s) |
| `velE` | East velocity (m/s) |
| `velD` | Down velocity (m/s) |

**Relative position (meters, for RTK baselines):**

| Field | Description |
|-------|-------------|
| `relN` | Relative North position from base (meters) |
| `relE` | Relative East position from base (meters) |
| `relD` | Relative Down position from base (meters) |

The `relN`/`relE`/`relD` fields are populated when the receiver reports an RTK baseline vector relative to a base station.

## Float Validity: Use isfinite(), Not isnan()

Unknown or invalid floating-point values in gpsd are set to **NaN**. Always check with `isfinite()` before using any float field:

```c
#include <math.h>

if (isfinite(gpsdata->fix.altMSL)) {
    printf("Altitude: %.1f m\n", gpsdata->fix.altMSL);
}
```

**Why not `isnan()`?** `isnan()` does not catch infinity. A value could be `INFINITY` or `-INFINITY` and pass an `isnan()` check. `isfinite()` rejects both NaN and infinity.

```c
// WRONG: misses infinity
if (!isnan(gpsdata->fix.speed)) { ... }

// CORRECT: catches NaN AND infinity
if (isfinite(gpsdata->fix.speed)) { ... }
```
