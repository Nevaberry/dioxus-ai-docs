# GNSS Observation Equations

## Pseudorange Observation

The fundamental GNSS measurement. Pseudorange `R` is the apparent distance from receiver to satellite, contaminated by clock errors, atmospheric delays, and noise:

```
R = ρ + c(dt_r - dt^s) + T + (40.3e16/f²)·STEC + M + ε
```

| Symbol | Meaning |
|--------|---------|
| `ρ` | True geometric range (receiver to satellite) |
| `c` | Speed of light |
| `dt_r` | Receiver clock error |
| `dt^s` | Satellite clock error |
| `T` | Tropospheric delay (~2.3 m zenith, scales with elevation) |
| `(40.3e16/f²)·STEC` | Ionospheric delay (frequency-dependent, ~1–50 m) |
| `M` | Multipath (signal reflections, ~0.5–1 m) |
| `ε` | Receiver noise + unmodeled errors |

## Carrier Phase Observation

More precise than pseudorange (~mm-level noise vs ~m-level), but contains an unknown integer ambiguity:

```
Φ = ρ + c(dt_r - dt^s) + T - (40.3e16/f²)·STEC + λN + ε
```

**Key differences from pseudorange:**
- Ionosphere sign is **negative** (carrier advance vs code delay)
- `λN` = wavelength × integer ambiguity (unknown number of whole cycles between receiver and satellite)
- Ambiguity is constant while signal is tracked — **lost on cycle slip** (signal lock loss)
- Resolving integer ambiguity is the core challenge of RTK and PPP-AR

## Ionosphere-Free Linear Combination

Combines two frequencies to eliminate ~99.9% of first-order ionospheric delay. Standard technique for PPP:

```
P_IF  = (f1²·P1 - f2²·P2) / (f1² - f2²)
Φ_IF  = (f1²·Φ1 - f2²·Φ2) / (f1² - f2²)
```

**Trade-off**: Eliminates iono but amplifies noise by ~3×. Higher-order iono terms (0.1% residual) remain.

## Common GPS Frequencies

| Signal | Frequency (MHz) | Wavelength (cm) |
|--------|-----------------|------------------|
| L1 C/A | 1575.42 | 19.0 |
| L2C | 1227.60 | 24.4 |
| L5 | 1176.45 | 25.5 |

## Error Budget (Single-Frequency, No Corrections)

| Source | Typical magnitude |
|--------|------------------|
| Satellite clock | ~2 m (removed with broadcast ephemeris) |
| Satellite orbit | ~2 m (removed with broadcast ephemeris) |
| Ionosphere | 1–50 m (worst at solar max, low elevation) |
| Troposphere | ~2.3 m zenith (higher at low elevation) |
| Multipath | 0.5–1 m code, mm carrier |
| Receiver noise | ~0.3 m code, ~2 mm carrier |
