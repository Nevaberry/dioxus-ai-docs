# SSR and observation conversion

## RTCM SSR correction groups

State-space representation separates satellite orbit, clock, signal bias, ionosphere, and troposphere errors instead of embedding their combined effect in user-specific observation-space corrections.

- Phase 1 groups orbit, clock, and code bias.
- Phase 2 adds phase bias and vertical ionosphere.
- Phase 3 adds slant ionosphere and troposphere.

A global stream containing only earlier groups can support dual-frequency static PPP. Without detailed regional atmospheric corrections, it does not replace a VRS-style service for single-frequency or kinematic users.

## SSR message-number families

RTCM assigns parallel six-message SSR blocks for orbit, clock, code bias, combined orbit/clock, URA, and high-rate clock corrections:

```text
1057–1062  GPS       1063–1068  GLONASS
1240–1245  Galileo   1246–1251  QZSS
1252–1257  SBAS      1258–1263  BeiDou
1264       spherical-harmonic ionosphere correction
1265–1270  phase bias for GPS, GLONASS, Galileo, QZSS, SBAS, BeiDou
```

## RTKLIB SSR PPP inputs and reference point

Combine receiver observations with the SSR correction stream and, for post-processing, navigation data. Use `pos1-sateph=brdc+ssrapc` for corrections referenced to the satellite antenna phase center. Select Broadcast+SSR CoM for center-of-mass corrections. A reference-point mismatch misapplies the orbit correction.

```text
solution mode       PPP-Static
pos1-sateph         brdc+ssrapc
ionosphere          dual-freq
troposphere         est-ztd
```

Classic RTKLIB PPP does not resolve ambiguities, so ambiguity-resolution settings are ignored. Enable GUI option `DBCorr`, or `pos1-posopt6` in a configuration file, to correct SSR PPP anomalies at the day boundary.

## Loss in legacy observation conversion

Conversion to legacy 1002/1010 is not lossless. Pseudorange is quantized to 0.02 m, carrier phase to 0.5 mm, and epochs to 1 ms. Doppler and the half-cycle-invalid indication are absent. MSM5/MSM7 can preserve Doppler and MSM can preserve half-cycle state, but MSM epoch resolution is still 1 ms.

## Consistent epoch rounding

An off-grid u-blox `RXM-RAWX` epoch such as `50.999584` can round to `51.000` in RTCM and prevent RTKLIB from fixing when observables remain unchanged. Shift the time tag, pseudorange, and carrier phase consistently. Classic RTKLIB's `-TADJ` path covered `RXM-RAW`, not `RXM-RAWX`.

The round-number timestamps in `TRK_MEAS` avoid that quantization case, but these measurements lack GLONASS inter-channel frequency-delay compensation and are not a drop-in replacement for `RXM-RAWX`.

## Bridge an SSL-only Ntrip stream

When RTKLIB cannot directly consume an SSL Ntrip caster, use BKG BNC to fetch it and republish the raw RTCM 3 stream on a local TCP port. Configure RTKNAVI's correction input as a TCP server at `localhost:<port>`. Verify decoded corrections in the `RTCM SSR/(3) Corrections` monitor.
