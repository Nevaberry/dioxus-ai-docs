---
name: gnss-navigation-knowledge-patch
description: "GNSS navigation since training cutoff (latest: latest) — RTK/RTCM 3.x, SPARTN v2.0.3 PPP, Galileo HAS/OSNMA, u-blox F9P UBX protocol, IGS products, Android GnssMeasurement API. Load before working with GNSS."
version: "latest"
license: MIT
metadata:
  author: Nevaberry
---

# GNSS Navigation Knowledge Patch

Claude's baseline covers basic GPS/GNSS concepts, WGS84, and satellite constellations (GPS/GLONASS/Galileo/BeiDou). This skill provides the practical implementation details needed to write GNSS positioning code: observation equations, correction protocols, receiver configuration, and platform APIs.

## Index

| Topic | Reference | Key content |
|---|---|---|
| Observation equations | [references/observation-equations.md](references/observation-equations.md) | Pseudorange/carrier phase models, ionosphere-free combination, error budget |
| RTK & RTCM corrections | [references/rtk-rtcm.md](references/rtk-rtcm.md) | RTCM 3.x message types, MSM4/MSM7, base station output config |
| SPARTN & PPP corrections | [references/spartn-ppp.md](references/spartn-ppp.md) | SPARTN format v2.0.3, SSR corrections, atmosphere models, encryption |
| Galileo services | [references/galileo-services.md](references/galileo-services.md) | HAS (free PPP corrections), OSNMA (navigation authentication) |
| u-blox F9P & UBX protocol | [references/ublox-f9p.md](references/ublox-f9p.md) | CFG keys, NAV/RXM messages, RTK activation, SPARTN input |
| IGS products & formats | [references/igs-products.md](references/igs-products.md) | SP3 orbits, Clock RINEX, IONEX, ANTEX, product tiers and latencies |
| Android raw GNSS | [references/android-gnss.md](references/android-gnss.md) | GnssMeasurement API, carrier phase, antenna info, dual-frequency |

---

## GNSS Signal Frequencies — Quick Reference (inline)

| Constellation | Signal | Frequency (MHz) | Wavelength (cm) | Notes |
|---------------|--------|-----------------|------------------|-------|
| GPS | L1 C/A | 1575.42 | 19.0 | Legacy civil signal |
| GPS | L2C | 1227.60 | 24.4 | Modernized civil |
| GPS | L5 | 1176.45 | 25.5 | Safety-of-life, highest precision |
| Galileo | E1 | 1575.42 | 19.0 | Same center freq as L1 |
| Galileo | E5a | 1176.45 | 25.5 | Same center freq as L5 |
| Galileo | E5b | 1207.14 | 24.8 | |
| Galileo | E6 | 1278.75 | 23.4 | HAS corrections on E6-B |
| GLONASS | L1 | ~1602 | ~18.7 | FDMA: per-satellite freq |
| GLONASS | L2 | ~1246 | ~24.1 | FDMA: per-satellite freq |
| GLONASS | L3 | 1202.025 | 24.9 | CDMA (modernized) |
| BeiDou | B1I | 1561.098 | 19.2 | Legacy |
| BeiDou | B1C | 1575.42 | 19.0 | Modernized, interoperable |
| BeiDou | B2a | 1176.45 | 25.5 | Interoperable with L5/E5a |

---

## Observation Equations — Quick Reference (inline)

Pseudorange:

```
R = ρ + c(dt_r - dt^s) + T + (40.3e16/f²)·STEC + M + ε
```

Carrier phase:

```
Φ = ρ + c(dt_r - dt^s) + T - (40.3e16/f²)·STEC + λN + ε
```

Where: `ρ` = geometric range, `c` = speed of light, `dt_r`/`dt^s` = receiver/satellite clock errors, `T` = troposphere, `STEC` = slant total electron content, `M` = multipath, `λN` = integer ambiguity (carrier only), `ε` = noise.

**Critical**: Ionosphere sign flips — code delay (+), carrier advance (−). `λN` is an unknown integer number of cycles, lost on signal lock loss (cycle slip).

Ionosphere-free combination (eliminates ~99.9% first-order iono, standard for PPP):

```
P_IF  = (f1²·P1 - f2²·P2) / (f1² - f2²)
Φ_IF  = (f1²·Φ1 - f2²·Φ2) / (f1² - f2²)
```

---

## RTCM 3.x Message Types — Quick Reference (inline)

| Message | Content | Interval |
|---------|---------|----------|
| **1005** | Antenna Reference Point (ARP) | 2 s |
| **1074** | GPS MSM4 (code + carrier) | 1 s |
| **1084** | GLONASS MSM4 | 1 s |
| **1094** | Galileo MSM4 | 1 s |
| **1124** | BeiDou MSM4 | 1 s |
| **1230** | GLONASS code-phase biases | 10 s |

MSM7 variants (1077/1087/1097/1127) for higher precision. Typical throughput ~2 kB/s.

---

## u-blox F9P Key Config Items (inline)

| CFG Key | Purpose |
|---------|---------|
| `CFG-TMODE` | Base mode: survey-in or fixed coordinates |
| `CFG-MSGOUT-RTCM_*` | Enable RTCM output per port |
| `CFG-RATE` | Navigation rate (1–10 Hz) |
| `CFG-SPARTN` | PPP corrections input (FW 1.51+) |

Key output messages: `NAV-PVT` (position/velocity/time), `NAV-RELPOSNED` (RTK baseline), `NAV-HPPOSLLH` (high-precision LLH).

Raw logging: `RXM-RAWX` + `RXM-SFRBX` (PPK post-processing), `RXM-SPARTNKEY` (SPARTN decryption keys).

RTK auto-activates when RTCM data appears on any port. Default UART baud: 115200.

---

## IGS Product Tiers (inline)

| Tier | Orbit | Clock | Latency | File pattern |
|------|-------|-------|---------|--------------|
| Final | ~2.5 cm | ~20 ps | 13 days | `igsWWWWD.sp3` |
| Rapid | ~2.5 cm | ~40 ps | 17 hours | `igrWWWWD.sp3` |
| Ultra-Rapid | ~3–5 cm | ~30 ps | 3 hours | `iguWWWWD_HH.sp3` |

---

## PPP vs RTK — Decision Matrix (inline)

| Aspect | RTK | PPP (SPARTN/HAS) | PPP (IGS post-process) |
|--------|-----|-------------------|------------------------|
| Accuracy | 1–2 cm | 3–6 cm (converged) | ~2 cm |
| Convergence | Instant (with fix) | 30–60 s (SPARTN), minutes (HAS) | N/A (post-process) |
| Coverage | ~35 km from base | Global | Global |
| Infrastructure | Base station or NTRIP | Subscription (SPARTN) or free (HAS) | Free (IGS archives) |
| Latency | Real-time | Real-time | Hours to days |
| Frequency req. | Dual preferred | Dual required | Dual required |

---

## Galileo Services Summary (inline)

**HAS** (High Accuracy Service): Free real-time PPP corrections (initial service Jan 2023). Orbit/clock/bias for Galileo E1/E5a/E5b/E6 + GPS L1/L2C. Delivery: E6-B signal (448 bps) or NTRIP IDD (requires GSC registration). Receiver must implement PPP algorithm. ~20 cm (95%) horizontal accuracy.

**OSNMA** (Navigation Message Authentication): TESLA-based broadcast authentication on E1-B (initial service Jul 2025). Protects against spoofing. Setup: install Merkle tree root key from GSC (one-time), maintain time sync within 30–300 s of GST. Key renewal: OTAR via SIS or manual download from GSC/EUSPA.

---

## SPARTN Corrections (inline)

SSR-based PPP corrections format (current v2.0.3, Nov 2025). Content: orbit/clock/bias + atmosphere (HPAC ionosphere, BPAC troposphere). Encrypted with dynamic key management. Supports GPS/GLO/GAL/BDS/QZSS. Primary service: u-blox PointPerfect (L-band or IP delivery).

---

## Android Raw GNSS (inline)

`GnssMeasurement` (API 24+): pseudorange, ADR (carrier phase), AGC, multi-frequency. `GnssAntennaInfo` (API 30+): PCO, PCV, signal gain. Mandatory raw measurements on API 29+. L1+L5 dual-frequency on most flagships since ~2020. Log via Google's `GNSSLogger` app.

---

## Error Budget — Single Point (inline)

| Source | Pseudorange | Carrier phase |
|--------|-------------|---------------|
| Ionosphere (uncorrected) | 1–50 m | 1–50 m |
| Troposphere | ~2.3 m zenith | ~2.3 m zenith |
| Satellite orbit (broadcast) | ~2 m | ~2 m |
| Satellite clock (broadcast) | ~2 m | ~2 m |
| Multipath | 0.5–1 m | ~mm |
| Receiver noise | ~0.3 m | ~2 mm |

Iono-free combination eliminates ~99.9% of ionosphere but amplifies noise ~3×. Precise orbits/clocks (IGS) reduce orbit+clock to cm-level.
