# Android Raw GNSS Measurements

## GnssMeasurement (API 24+)

Available since Android 7.0 (Nougat). Provides raw GNSS observables per satellite per frequency:

| Field | Description |
|-------|-------------|
| `getReceivedSvTimeNanos()` | Satellite time at signal reception — used to compute pseudorange |
| `getAccumulatedDeltaRangeMeters()` | ADR (carrier phase) in meters. State flags indicate validity. |
| `getAutomaticGainControlLevelDb()` | AGC level — useful for interference/spoofing detection |
| `getCn0DbHz()` | Carrier-to-noise density (signal strength) |
| `getCarrierFrequencyHz()` | Signal frequency — identifies L1, L2, L5, E1, E5a, etc. |
| `getMultipathIndicator()` | Multipath likelihood flag |

### Pseudorange Computation

```
pseudorange = (rxTime - svTime) * SPEED_OF_LIGHT
```

Where `rxTime` comes from `GnssClock` and `svTime` from `GnssMeasurement.getReceivedSvTimeNanos()`. Clock discontinuities must be handled via `getFullBiasNanos()` and `getBiasNanos()`.

### Carrier Phase (ADR)

`getAccumulatedDeltaRangeMeters()` provides carrier phase but check `getAccumulatedDeltaRangeState()`:
- `ADR_STATE_VALID`: Measurement is usable
- `ADR_STATE_RESET`: Cycle slip detected — ambiguity changed
- `ADR_STATE_CYCLE_SLIP`: Explicit cycle slip flag

## GnssAntennaInfo (API 30+)

Available since Android 11. Provides per-frequency antenna calibration data:

| Field | Description |
|-------|-------------|
| `getPhaseCenterOffset()` | Phase center offset (PCO) relative to device reference point |
| `getPhaseCenterVariationCorrections()` | Phase center variation (PCV) correction grid |
| `getSignalGainCorrections()` | Antenna gain pattern per azimuth/elevation |

## Platform Requirements

- **API 29+** (Android 10): Raw GNSS measurements **mandatory** for devices declaring `FEATURE_LOCATION_GPS`
- **Dual-frequency**: L1+L5 available on most flagships since ~2020 (Pixel 4+, Samsung Galaxy S10+, etc.)
- Not all devices expose carrier phase (ADR) even when measurements are mandatory

## Logging Tool

Google's **GNSSLogger** app logs raw measurements to text files for offline processing. Available on Google Play Store. Output compatible with standard GNSS processing tools.
