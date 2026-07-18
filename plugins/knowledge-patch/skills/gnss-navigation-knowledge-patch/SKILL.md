---
name: gnss-navigation-knowledge-patch
description: GNSS
license: MIT
version: null
metadata:
  author: Nevaberry
---

# GNSS Navigation Knowledge Patch

Baseline and covered range: GNSS navigation fundamentals through mid-2024, including GPS, Galileo, GLONASS, BeiDou, SBAS, RTK, and PPP; covers the included operational and specification updates through 2026-07-11.

## Reference index

| Reference | Topics |
| --- | --- |
| [constellation-signals.md](references/constellation-signals.md) | GPS L2C/L1C, Galileo E1/E5/E6, GLONASS FDMA/CDMA, BeiDou B1/B2/B3 signal structures |
| [galileo-services-and-osnma.md](references/galileo-services-and-osnma.md) | Galileo HAS, time offsets, SAR return link, OSNMA trust bootstrap, transport, status, availability, TTFF, and events |
| [augmentation-corrections-and-products.md](references/augmentation-corrections-and-products.md) | SBAS, GBAS, DGNSS, WARTK, RTCM, RTK bases, RINEX 4, SSR, SPARTN, and IGS products |
| [atmosphere-and-multipath.md](references/atmosphere-and-multipath.md) | Ionosphere-free PPP, second-order ionosphere, troposphere states and mappings, multipath bounds and diagnostics |
| [zed-f9p-operations.md](references/zed-f9p-operations.md) | ZED-F9P variants, ports, configuration, correction inputs, moving base, integrity, timing, OSNMA, raw data, and IMX integration |
| [receiver-software-and-timing.md](references/receiver-software-and-timing.md) | Linux serial/PPS timing, Android raw GNSS, antenna corrections, SUPL, logging, GNSS Analysis, and GNSS-SDR |

## Breaking boundaries and deprecations

### Pin data formats to exact revisions

- RTCM Version 3 is not wire-compatible with Version 2.x.
- RINEX 4 is not one fixed capability set: 4.01 adds GPS Block IIIF and NavIC observation codes; 4.02 adds picosecond time tags and new NavIC, GLONASS CDMA, QZSS, and NavIC navigation records.
- SPARTN 2.0.3, dated November 2025 in the included material, is the current available specification; all earlier listed versions are deprecated.
- ZED-F9P firmware consumes a receiver-specific SPARTN 2.0.1 subset, even when the ecosystem supports newer SPARTN features.
- Bias-SINEX 1.00 has two validity-interval encodings: the February 2016 definition uses two-digit years and the December 2016 definition uses four-digit years.

### Update IGS product discovery

- Operational products from GPS week 2238 and repro3 products use long filenames.
- Do not rely only on legacy constructors such as `igswwwwd.sp3.Z`, `igrwwwwd.clk.Z`, or `iguwwwwd_hh.sp3.Z`.
- Combined long names encode producer/version/project, solution class, start epoch, span, sample interval, content, and exchange format.
- Archived `igc`/`igt` real-time-derived products remain distinct from live caster corrections and have a separately postponed filename transition.

### Respect receiver and firmware boundaries

- ZED-F9P `-15B` is the L1/L5 variant; the `-01B/-02B/-04B/-05B` family uses the documented L1/L2-oriented default set.
- HPG L1L5 1.40 excludes moving base, legacy GPS/GLONASS RTCM observations, and proprietary message 4072.0.
- Moving base on HPG 1.12 requires MSM7 plus 4072.1; HPG 1.13 and later use 4072.0 and may use MSM4.
- HPG 1.13 supports navigation rates through 10 Hz, while the documented HPG 1.51 path is limited to 8 Hz and adds newer correction functionality.
- Classic u-center with the Generation 9 configuration format is the documented path for F9 receivers.

## Galileo OSNMA quick reference

### Service boundary

- OSNMA Initial Service has been operational since 24 July 2025.
- It authenticates the origin and integrity of Open Service I/NAV data after delayed key disclosure.
- It does not authenticate the ranging signal and does not by itself prove that a PVT solution is authentic.
- It is a free, worldwide, non-safety-critical service without a service guarantee.
- Continue to apply ordinary Open Service signal health and status rules independently of OSNMA status.

### Trust and verification

1. Provision the Merkle-tree root from the Galileo Service Centre Internet interface; it is never broadcast by the signal.
2. Verify the TESLA root-key signature using an OSNMA public key.
3. Verify each disclosed TESLA key against the root key.
4. Recompute and compare the MAC over the navigation data.
5. Protect stored cryptographic material from modification; confidentiality is not required.
6. Maintain Galileo System Time synchronization within the applicable 30-to-300-second mode requirement.

### Transport and page handling

- Each nominal E1-B I/NAV odd page dedicates 40 reserved bits to OSNMA.
- HKROOT uses 8 bits per page portion; MACK uses 32 bits.
- Fifteen portions over a 30-second subframe form 120-bit HKROOT and 480-bit MACK messages.
- Reject affected navigation data after a navigation-message CRC failure.
- Discard OSNMA fields from I/NAV Dummy Messages and I/NAV Alert Pages.
- Forty zero bits mean that the satellite is not currently distributing OSNMA.
- Distributor satellites may cross-authenticate other satellites; E14 and E18 may distribute authentication data but are not authenticated themselves.

### Status and alert actions

- `Operational` is the only global OSNMA status with the stated performance commitment.
- `Test` has no operational guarantee.
- `Don't use` forbids authentication with the broadcast data.
- An authenticated OSNMA Alert Message requires stopping OSNMA use and retrieving recovery instructions.
- Do not confuse an OSNMA Alert Message with an I/NAV Alert Page.
- Monitor both NAGUs and registered-user Internet notifications because they cover different delivery paths.

### Availability and startup expectations

- Initial Service requires at least 40 equivalent verified tag bits for a navigation data set.
- ADKD0 covers I/NAV Word Types 1–5 and targets four satellites within 30 seconds at 95% minimum availability.
- ADKD12 is the lower-time-synchronization mode and targets four satellites within 240 seconds at 95%.
- ADKD4 authenticates GST-UTC and GST-GPS conversion parameters and targets one satellite within 60 seconds at 97%.
- The stated 95% ADKD0 TTFF-AD values are 130 seconds hot, 300 seconds warm, and at most 6 hours cold.
- ADKD12 values are 460 seconds hot, 520 seconds warm, and at most 6 hours cold.
- The cold bound follows the six-hour public-key message schedule; the Merkle root still requires separate provisioning.

## Galileo HAS quick reference

- HAS Initial Service was declared on 24 January 2023.
- It supplies real-time orbit, clock, and satellite-bias corrections to broadcast ephemerides.
- Apply the corrections in a PPP algorithm; HAS corrections alone are not a position solution.
- Supported signals include Galileo E1/E5a/E5b/E6 and GPS L1/L2C.
- Receive the same correction service over E6-B or the registered Ntrip-based Internet Data Distribution interface.
- Initial Service is Phase 1, Service Level 1, with reduced coverage and performance.
- Do not assume phase-bias products or Service Level 2 availability yet.

## Signal-selection quick reference

### GPS

- L2C time-division multiplexes CM and CL into a 1.023-Mchip/s composite.
- CM carries navigation data; CL is dataless.
- Block IIR-M may use either 50-bit/s uncoded data or 25-bit/s data convolutionally encoded to 50 symbols/s.
- CHIMERA is a proposed L1C encrypted-watermark enhancement, not an inherent property of every L1C broadcast.

### Galileo

- E1-B carries I/NAV data and ranging; E1-C is the dataless pilot.
- E5a-I carries F/NAV and E5b-I carries I/NAV; both Q channels are dataless pilots.
- Full E5 uses AltBOC(15,10), while a narrowband receiver may correlate with a QPSK(10) replica.
- E6-B carries 448-bit/s data, including HAS, and E6-C is the equal-power pilot.

### GLONASS

- Legacy FDMA broadcast ephemerides are ECEF position, velocity, and lunisolar acceleration, not GPS-style Keplerian elements.
- L2OC is pilot-only.
- L1OC and L3OC use different data/pilot structures and secondary codes.
- CDMA availability depends on spacecraft generation; do not infer L1/L2 CDMA support from L3OC reception.
- Broadcast coordinates use PZ-90.11 and require the defined transformation in precise mixed-constellation work.

### BeiDou

- Band names do not uniquely imply frequency or access class.
- B1C uses a 1:3 data-to-pilot power ratio; B2a uses equal-power data and pilot.
- BDS-3 services are orbit-dependent: GEO payloads include SBAS and B2b PPP, while selected MEO spacecraft carry MEOSAR.
- Validate GEO/MEO/IGSO signal availability instead of assuming a uniform constellation payload.

## Corrections and positioning quick reference

### Integrity and geometry

- SBAS provides orbit, clock, ionosphere, integrity, and possibly GEO ranging; it does not broadcast a troposphere correction.
- Classical DGNSS improves accuracy but does not itself assure integrity.
- Conventional/network RTK generally needs short baselines when differential ionosphere matters; the included rule of thumb is about 15 km.
- WARTK supplies explicit ionosphere corrections and permits roughly 500–900 km reference spacing.
- A base-coordinate error transfers directly into rover absolute position.
- Fixed-base height is ellipsoidal height, not mean-sea-level height.

### ZED-F9P base and rover essentials

- A base typically emits 1005, one MSM4 or MSM7 family consistently across constellations, and GLONASS 1230 where needed.
- Survey-in must satisfy both minimum duration and accuracy thresholds before time mode and message 1005 begin.
- Rover ambiguity fixing needs matching MSM4/MSM7 observations and 1005/1006 with consistent station IDs.
- GLONASS fixing also needs 1230 or 1033.
- Corrections older than 60 seconds are rejected by default.
- All observation messages must use one rate, one observation type per constellation, and the same MSM family.
- Save persistent settings explicitly; interface message enablement and protocol enablement are separate controls.

### PPP observation conventions

- Use `X_IF = (f1² X1 - f2² X2) / (f1² - f2²)` for the first-order ionosphere-free combination.
- If the satellite clock is referenced to that ionosphere-free code combination, Timing Group Delays cancel and must not be applied again.
- Tropospheric delay is non-dispersive and must be modeled or estimated rather than removed by dual-frequency combination.
- Estimate the fast-changing wet zenith delay as a filter state for precise positioning.

## Time, frame, and integrity checks

- Treat Galileo System Time, UTC, and GPS Time as distinct; use broadcast offsets.
- Normalize signed `nano` before interpreting ZED-F9P UTC calendar fields.
- Use `iTOW` only to group same-epoch messages unless time validity is established.
- Check `gnssFixOK` or NMEA validity, not `fixType` alone.
- Use protection levels only when their validity and frame indicators are set, then compare each axis with its application alert limit.
- RTK/PPP-RTK coordinates remain in the correction provider's reference frame.
- For precision height, use ellipsoidal height with an external high-resolution geoid rather than the receiver's limited-resolution EGM96 output.

## Receiver data and software checks

- Android raw-measurement support does not guarantee every field, dual frequency, or carrier phase; inspect actual measurement availability.
- Android 11/API 30 exposes model-level phase-center and signal-gain corrections through `GnssAntennaInfo`.
- Use `UBX-RXM-RAWX` and `UBX-RXM-SFRBX`, not the 1 Hz rounded flash log, for PPK observation logging.
- `UBX-RXM-SFRBX` has already passed receiver parity checks; select framing by `gnssId` and `sigId` and ignore padding.
- GNSS-SDR configuration defines the complete GNU Radio receiver graph and can consume live or recorded samples.
- GNSS-SDR can write RINEX, stream RTCM 3.2, and store navigation results as KML and GeoJSON.
- For Linux timing with `gpsd` and classic `ntpd`, use SHM unit 0 for coarse serial time and unit 1 for optional PPS.

## Implementation checklist

1. Identify constellation, signal, spacecraft generation, and access class.
2. Pin the exact message, format, receiver firmware, and minor revision.
3. Separate correction content from its transport and from the positioning algorithm that consumes it.
4. Track coordinate frame, height datum, and time scale explicitly.
5. Keep signal health, correction freshness, authentication status, and solution integrity as separate states.
6. Validate interface protocol enablement, message rates, station IDs, and persistent configuration independently.
7. Test cold/warm/hot startup and correction-loss behavior, not only steady state.
8. Route to the indexed reference for full limits, formulas, message mappings, and firmware exceptions.
