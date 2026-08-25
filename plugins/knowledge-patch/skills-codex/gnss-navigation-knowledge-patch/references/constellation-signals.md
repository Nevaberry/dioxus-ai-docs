# Constellation Signals and Broadcast Systems

## GPS signals

### L2C CM/CL multiplexing and selectable data rates

GPS L2C time-division multiplexes the 511.5-kchip/s CM code (10,230 chips over 20 ms) and CL code (767,250 chips over 1.5 s) into a 1.023-Mchip/s composite; CM carries navigation data while CL is dataless. On Block IIR-M, the ground can select either 50-bit/s uncoded data or 25-bit/s data encoded by a rate-1/2 convolutional code to 50 symbols/s, so a decoder cannot assume a single CM data mode.

### CHIMERA authentication on L1C

CHIMERA (Chips Message Robust Authentication) is a proposed L1C enhancement that inserts encrypted watermarks into the signal. It is intended both to expose spoofed signals and to let another party authenticate a receiver's location; treat it as an enhancement under study, not an inherent property of every L1C broadcast.

## Galileo signals

### Carrier frequencies and receiver reference bandwidths

Galileo transmits RHCP CDMA signals on E1 at 1575.420 MHz, E6 at 1278.750 MHz, and composite E5 at 1191.795 MHz; E5 separates into E5a at 1176.450 MHz and E5b at 1207.140 MHz. The corresponding receiver reference bandwidths for E1, E6, E5, E5a, and E5b are 24.552, 40.920, 51.150, 20.460, and 20.460 MHz.

### E1 Open Service data and pilot channels

E1 Open Service uses CBOC, an MBOC(6,1,1/11) implementation that assigns an average 1/11 of its power to the BOC(6,1) component and the remainder to BOC(1,1). E1-B carries the I/NAV data stream and ranging code, while E1-C is a dataless pilot with a secondary code.

### E5 navigation-message mapping and narrowband reception

E5a-I carries F/NAV and E5b-I carries I/NAV, while E5a-Q and E5b-Q are dataless pilots; all four use unencrypted ranging codes. Composite E5 uses AltBOC(15,10), with a 10.23 MHz code rate and 15.345 MHz subcarrier, but a receiver that cannot acquire the full wideband main lobes can correlate it using a QPSK(10) replica.

### E6 data and pilot split

E6 uses BPSK(5) at 1278.75 MHz; its E6-B 448-bit/s data component and E6-C pilot share the carrier at equal power. E6-B is the signal-in-space transport for current High Accuracy Service correction data.

## GLONASS signals and navigation data

### Legacy open-message schedule and orbit representation

The 50-bit/s FDMA open message is a 150-second superframe of five 30-second frames, each containing fifteen 100-bit, two-second strings. Strings 1–4 repeat the transmitting satellite's ephemeris, clock and frequency offsets, and health in every frame; strings 5–15 distribute almanacs for five satellites in frames I–IV and the remaining four in frame V.

Broadcast ephemerides use ECEF Cartesian position and velocity plus lunisolar acceleration and are refreshed every 30 minutes, whereas the daily almanac uses modified orbital elements. A decoder therefore cannot process GLONASS broadcast ephemerides as GPS-style Keplerian ephemerides.

### L1OC data and pilot structure

L1OC is centered at 1600.995 MHz and has equal-power data and pilot components whose PRNs are chip-by-chip time-division multiplexed. L1OCd combines a 0.5115-Mchip/s PRN, a 500-symbol/s overlay code, and a 250-symbol/s convolutional-encoder stream; its navigation payload is 125 bit/s in normal 250-bit, two-second strings, with one- and three-second anomalous strings around time corrections.

L1OCp combines a 0.5115-Mchip/s PRN with a 2.046-MHz `0101` meander to form a BOC(1,1) pilot. The open L1OC signal is in phase quadrature with the restricted L1SC signal.

### L2OC is pilot-only

The open CDMA signal at 1248.06 MHz is L2OCp: it carries ranging but no navigation message. Its 0.5115-Mchip/s PRN is combined with a 50-symbol/s overlay code and a 2.046-MHz meander to form BOC(1,1), and it is chip-by-chip multiplexed with the restricted L2 signal.

### L3OC quadrature data and pilot

L3OC is centered at 1202.025 MHz and places equal-power BPSK(10) data and pilot components in quadrature, both using 10.23-Mchip/s ranging codes. L3OCd adds a five-symbol Barker code at 1,000 symbols/s and a convolutional-encoder stream at 200 symbols/s; its 100-bit/s message normally uses 300-bit, three-second strings, with two- and four-second anomalous strings for time correction.

L3OCp is the dataless quadrature component and applies a ten-symbol Neuman–Hofman overlay at 1,000 symbols/s. Tracking implementations must therefore use different secondary-code replicas for the L3 data and pilot channels.

### Extensible CDMA navigation strings

A normal CDMA pseudo-frame has six strings: types 10, 11, and 12 form a consecutive current-satellite ephemeris and time/frequency packet, while three type-20 strings each carry another satellite's almanac. Eight pseudo-frames cover a 24-satellite almanac; strings carry version tags so older decoders can ignore newer forms while the older string types remain broadcast.

Other defined content includes type 25 for Earth-rotation parameters, ionosphere models, and the UTC(SU)–TAI model; types 31–32 for long-term motion; type 50 for a Cospas–Sarsat message on L1OC only; and type 60 for text. L1OC's normal envelope is 250 bits with a 16-bit CRC, while L3OC's is 300 bits with a 24-bit CRC; both expose satellite health, data-reliability, orientation, and leap-correction state in the header.

### Leap-second and calendar handling

CDMA headers announce whether a quarter-end UTC correction is positive, negative, absent, or unknown and separately flag execution after the current string. At the event, the final string of the day is shortened by one second for a negative leap or extended with one second of zero padding for a positive leap; receivers discard this anomalous string rather than decoding it as an ordinary payload.

The almanac day number runs from 1 through 1461 in a four-year interval beginning on 1 January of the last leap year. Its calendar treats every year divisible by 100 as a leap year, unlike the Gregorian exception, which matters for long-lived decoders at century boundaries.

### Signal support depends on spacecraft generation

Modern CDMA availability is not constellation-wide: GLONASS-K1 adds L3OC to the legacy L1/L2 FDMA signals, and GLONASS-M spacecraft produced since 2014 may also transmit L3OC for testing. GLONASS-K2 adds the L1OC/L1SC and L2OC/L2SC pairs as well as L3OC while retaining the legacy signals, so acquisition logic must use per-satellite signal capability rather than infer L1/L2 CDMA support from L3OC reception.

### PZ-90.11 broadcast reference frame

GLONASS has broadcast PZ-90.11 since 31 December 2013. It is aligned at centimetre level to ITRF2008 at epoch 2011.0, but a precise mixed-constellation solution should still perform the defined frame conversion rather than silently treating broadcast GLONASS ECEF coordinates as WGS 84.

## BeiDou signals and service payloads

### Open and authorized signal map

BeiDou band names do not by themselves identify either frequency or access class. The open signals are B1I at 1561.098 MHz, B1C at 1575.42 MHz, B2I and B2b at 1207.14 MHz, B2a at 1176.45 MHz, and B3I at 1268.52 MHz; B1Q, B1A, B2Q, B3Q, and B3A are authorized signals, while the 2492.028 MHz Bs broadcast was experimental.

### B1I, B2I, and B3I acquisition parameters

B1I and B2I use BPSK(2), a 2.046-Mchip/s rate, and 2,046-chip one-millisecond codes; each carries a 50-bit/s navigation stream. B3I uses BPSK(10), a 10.23-Mchip/s rate, and a 10,230-chip one-millisecond code at 1268.52 MHz; B3I is available from BDS-2 and BDS-3 MEO, IGSO, and GEO spacecraft.

B1I occupies a 4.092 MHz reference bandwidth and B3I occupies 20.46 MHz. Both directly modulate the ranging code and navigation data onto the carrier, rather than providing separate data and dataless-pilot components.

### B1C data and pilot components

The BDS-3 open B1C signal occupies 32.736 MHz around 1575.42 MHz and, in the ordinary signal definition, is transmitted by MEO and IGSO satellites but not GEO satellites. Its quadrature components are a 100-symbol/s data channel using sine BOC(1,1) and a dataless pilot using QMBOC(6,1,4/33); the data-to-pilot power ratio is 1:3.

### B2a data and pilot components

B2a occupies 20.46 MHz around 1176.45 MHz. It places a 200-symbol/s data component and a dataless pilot in quadrature, both using BPSK(10), with equal power allocated to the two components.

### Reference receive levels and coherence

B1I, B1C, B2a, and B3I are RHCP CDMA signals. Their listed ground receive levels are -163 dBW for B1I and B3I, -159 dBW from MEO and -161 dBW from IGSO for B1C, and -156 dBW from MEO and -158 dBW from IGSO for B2a; the B1I, B2a, and B3I figures are referenced to the output of a 0-dBi RHCP antenna above 5 degrees elevation.

B1C and B2a constrain the code-phase difference between their components to at most 10 ns and align data-symbol, primary-code, and secondary-code boundaries. For B1I, B2I, and B3I, inter-signal ranging-code phase jitter is below 1 ns (1 sigma), and ranging-code-to-carrier phase jitter is below 3 degrees (1 sigma).

### Orbit-dependent BDS-3 service payloads

The nominal BDS-3 constellation combines 24 MEO, three IGSO, and three GEO satellites, so service payloads are not uniform across spacecraft. The system overview assigns GEO payloads for SBAS on B1C, B2a, and B1A and for PPP corrections on B2b, while six MEO satellites carry MEOSAR transponders; new-generation satellites also support a short-message service.
