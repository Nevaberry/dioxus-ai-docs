# RINEX and Data Conversion

## Contents

- [RINEX 3.04 format](#rinex-304-format)
  - [Long filename grammar](#long-filename-grammar)
  - [Header and record parsing](#header-and-record-parsing)
  - [System-specific observation declarations](#system-specific-observation-declarations)
  - [GLONASS CDMA observation codes](#glonass-cdma-observation-codes)
  - [QZSS Block II coding and satellite IDs](#qzss-block-ii-coding-and-satellite-ids)
  - [BeiDou-3 observation codes](#beidou-3-observation-codes)
  - [Mandatory carrier-phase alignment](#mandatory-carrier-phase-alignment)
  - [Mandatory GLONASS metadata](#mandatory-glonass-metadata)
  - [Epoch, event, LLI, and SSI fields](#epoch-event-lli-and-ssi-fields)
  - [Receiver clock correction contract](#receiver-clock-correction-contract)
  - [Scale factors and signal strength](#scale-factors-and-signal-strength)
  - [Moving and virtual markers](#moving-and-virtual-markers)
  - [Ionosphere and receiver-channel pseudo-observables](#ionosphere-and-receiver-channel-pseudo-observables)
  - [Mixed-file time systems and leap-second normalization](#mixed-file-time-systems-and-leap-second-normalization)
  - [Navigation time-correction headers](#navigation-time-correction-headers)
  - [Mixed navigation blocks and Galileo duplicates](#mixed-navigation-blocks-and-galileo-duplicates)
  - [Navigation conversion edge cases](#navigation-conversion-edge-cases)
- [Recording and convbin basics](#recording-and-convbin-basics)
  - [Recording convertible ZED-F9P logs](#recording-convertible-zed-f9p-logs)
  - [RTKCONV signal selection and diagnostics](#rtkconv-signal-selection-and-diagnostics)
  - [convbin decoder and time selection](#convbin-decoder-and-time-selection)
  - [convbin RINEX content controls](#convbin-rinex-content-controls)
  - [convbin headers and output routing](#convbin-headers-and-output-routing)
- [RTKLIB conversion compatibility and fixes](#rtklib-conversion-compatibility-and-fixes)
  - [ZED-F9P Galileo I/NAV in 2.4.3 b34](#zed-f9p-galileo-inav-in-243-b34)
  - [High-rate BINEX time tags in 2.4.3 b34](#high-rate-binex-time-tags-in-243-b34)
  - [SP3-d files above 99 satellites](#sp3-d-files-above-99-satellites)
  - [Leading null receiver observations](#leading-null-receiver-observations)
  - [GLONASS phase from MSM4 and MSM6](#glonass-phase-from-msm4-and-msm6)
  - [RINEX 2 extension boundary](#rinex-2-extension-boundary)
- [Interchange formats](#interchange-formats)
  - [SBAS log framing](#sbas-log-framing)
- [RTKLIB conversion and decoder controls](#rtklib-conversion-and-decoder-controls)
  - [RINEX version conversion and header scan](#rinex-version-conversion-and-header-scan)
  - [Per-signal selection and phase shifts](#per-signal-selection-and-phase-shifts)
  - [Default multiple-signal priorities](#default-multiple-signal-priorities)
  - [Decoder-specific input controls](#decoder-specific-input-controls)
  - [RTCM encode/decode boundary](#rtcm-encodedecode-boundary)
  - [RTCM stream conversion contract](#rtcm-stream-conversion-contract)
- [Demo5 conversion and signal handling](#demo5-conversion-and-signal-handling)
  - [Additional raw stream decoders](#additional-raw-stream-decoders)
  - [CONVBIN decoder and output additions](#convbin-decoder-and-output-additions)
  - [u-blox observation-quality decoder options](#u-blox-observation-quality-decoder-options)
  - [Navigation-family selection at decode time](#navigation-family-selection-at-decode-time)
  - [Demo5 multiple-signal priorities](#demo5-multiple-signal-priorities)
  - [Support-matrix inconsistencies](#support-matrix-inconsistencies)

## RINEX 3.04 format

### Long filename grammar

The recommended observation filename is `<site9>_<source>_<YYYYDDDHHMM>_<period>_<rate>_<type>.rnx[.<compression>]`; navigation names omit the rate. The nine-character site is normally `XXXXMRCCC`, source is `R` (receiver), `S` (stream), or `U`, the start uses the file's time system, and `MO`/`MN` identify mixed observation/navigation data.

```text
ALGO00CAN_R_20121601000_01H_05Z_MO.rnx.gz
ALGO00CAN_S_20121600000_01D_MN.rnx.gz
```

All main-body fields are fixed-width, zero-padded ASCII capitals or digits; `.rnx`, Hatanaka `.crx`, and compression suffixes are lowercase. Rate units include `C` for 100 Hz, `Z` for Hz, then `S`, `M`, `H`, `D`, or `U`.

### Header and record parsing

Header labels occupy columns 61–80 exactly. `RINEX VERSION / TYPE` is first and `END OF HEADER` last; otherwise records are freely ordered, except `SYS / # / OBS TYPES` precedes related DCB and scale-factor records and `# OF SATELLITES` is immediately followed by its `PRN / # OF OBS` records.

Readers should buffer whole variable-length records, tolerate truncated trailing blank fields, trim leading blanks in character fields, and skip or report unknown header, observation, and event types. Missing header values default to blank/zero and every supplied value remains valid until an event changes it; observation records are not limited to 80 characters, normal epochs must increase in time, and duplicate time tags are allowed only for events.

### System-specific observation declarations

Each constellation has its own `SYS / # / OBS TYPES` list, whose order defines every satellite record. A normal code is `tna`: type `C`, `L`, `D`, or `S`; band `1`–`9`; and a defined tracking attribute—RINEX 3.04 does not permit an omitted or invented tracking mode.

```text
G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES
R    2 C1C L1C                                              SYS / # / OBS TYPES
```

### GLONASS CDMA observation codes

RINEX 3.04 adds G1a at 1600.995 MHz as band 4 and G2a at 1248.06 MHz as band 6. For every available measurement type, data, pilot, and combined tracking use `4A/4B/4X` and `6A/6B/6X` respectively; the legacy FDMA G1, G2, and CDMA G3 codes remain on bands 1, 2, and 3.

```text
C4A L4A D4A S4A   C4B L4B D4B S4B   C4X L4X D4X S4X
C6A L6A D6A S6A   C6B L6B D6B S6B   C6X L6X D6X S6X
```

### QZSS Block II coding and satellite IDs

All QZSS observations use `J01`–`J09` in 3.04; the alternative `Sxx` identity is dropped. Standard PNT PRNs map by subtracting 192, L1S PRNs by subtracting 182, L6E PRNs by subtracting 202, and L5S PRNs 196, 200, and 197 map specially to `J02`, `J03`, and `J07`.

Block II L5S uses suffixes `5D`, `5P`, and `5Z`; its L6 data, second data, and combined channels use `6S`, `6E`, and `6Z`. In older Block I data, `1Z` can mean L1-SAIF rather than L1S, while `6S`, `6L`, and `6X` denote LEX data, pilot, and combined tracking.

### BeiDou-3 observation codes

BeiDou-3 B1 uses `1D/1P/1X`, B1A uses `1A`, B2a uses `5D/5P/5X`, B2b uses `7D/7P/7Z`, combined B2a+B2b uses `8D/8P/8X`, and B3A uses `6A`; the prefix remains `C`, `L`, `D`, or `S`. B1 codeless tracking has `L1N`, `D1N`, and `S1N` but no pseudorange code.

BeiDou-2 B1-2 remains band 2 (`2I/2Q/2X`), B2b remains band 7 (`7I/7Q/7X`), and B3 remains band 6 (`6I/6Q/6X`). A 3.02 reader must accept both band-1 and band-2 spellings for B1 and treat them as the band-2 convention used by 3.03/3.04.

### Mandatory carrier-phase alignment

Before writing RINEX 3.0x, every phase must be aligned to its constellation/frequency reference signal even when that reference was not tracked, and each system needs `SYS / PHASE SHIFT`. Its sign is `phase_RINEX = phase_original + correction`; a zero reports that the receiver or input format already supplied aligned data, a reference-only system has the observation code with the remaining fields blank, and unknown alignment is an exceptional blank-record case rather than publishable normal data.

For 3.04 signals, QZSS Block II `L1S`, `L1L`, and `L1X` require `+0.25` cycle relative to `L1C` (Block I `L1S` requires zero), QZSS `L5P` requires `-0.25` relative to `L5D`, and the new QZSS L6 and GLONASS CDMA signals require no shift. BeiDou-3 pilot phases on B1, B2a, B2b, and combined B2 require the specification's preliminary `+0.25` cycle, with combined phases aligned to the corresponding data signal.

### Mandatory GLONASS metadata

An observation file containing GLONASS needs `GLONASS SLOT / FRQ #` entries mapping each `Rnn` slot to FDMA channel `-7`…`+6`. It also needs `GLONASS COD/PHS/BIS` with metre-valued `C1C`, `C1P`, `C2C`, and `C2P` code-phase biases; an already aligned receiver reports zeros, while an exceptional unknown alignment leaves all four fields blank rather than omitting the record.

Apply a nonzero bias before output as `aligned_phase_cycles = observed_phase_cycles + bias_metres / wavelength`. The header retains the applied values so the receiver observations can be reconstructed.

### Epoch, event, LLI, and SSI fields

An epoch begins with `>` and flag `0` means normal, `1` means a power failure since the prior epoch, `2` starts a moving antenna, `3` starts a new static occupation and requires at least `MARKER NAME`, `4` introduces header updates, `5` is an external event, and `6` introduces cycle-slip records. For flags 0/1 the count is satellites and ordinary observation records follow; for flags 2–5 it is the number of special records.

Each observation is `F14.3` plus one LLI and one SSI character; missing values are zero or blank. LLI applies only to phase: bit 0 marks loss of lock/cycle-slip risk, bit 1 a possible half-cycle ambiguity, and bit 2 experimental Galileo BOC tracking of MBOC; a phase overflowing `F14.3` is shifted by `10^9` cycles into range and gets bit 0 set. Distinct half-wavelength signals use their own codes but are still stored in full cycles.

### Receiver clock correction contract

If epoch records carry a receiver clock offset, `RCV CLOCK OFFS APPL` is required: `0` means the observations are uncorrected and `1` means epoch, pseudorange, and phase were all corrected. Applying offset `dT` must preserve their consistency as `time' = time - dT`, `P' = P - c*dT`, and `L' = L - f*dT`.

### Scale factors and signal strength

`SYS / SCALE FACTOR` is a reader operation: divide each listed stored observation by the declared factor (`1`, `10`, `100`, or `1000`), defaulting to one when absent. The one-character SSI is `clamp(INT(dBHz/6), 1, 9)`; preferably store the actual carrier-to-noise value as an `Sna` observation and declare `DBHZ` in `SIGNAL STRENGTH UNIT`.

### Moving and virtual markers

`MARKER TYPE` is required except for the default `GEODETIC` and `NON_GEODETIC` cases; `NON_PHYSICAL` identifies a network-generated site, while vehicle/air/water/space types tell a processor that the receiver moves. Fixed stations express the ARP as `ANTENNA: DELTA H/E/N`, whereas vehicles use body-fixed `ANTENNA: DELTA X/Y/Z` and express boresight, zero direction, phase center, and center of mass in that same body frame; attitude remains an external input.

### Ionosphere and receiver-channel pseudo-observables

An `In` observation with blank attribute stores at most one ionospheric phase delay per satellite in cycles: add it to same-band raw phase, subtract `delay*c/f` from pseudorange, and scale it to another band by `(fi/fk)^2`. Use the normative Section 5.13 spelling `X1` with blank attribute for the receiver-channel pseudo-observable. Its value packs up to five right-justified two-digit channels into `F14.3`, so channels 9 and 10 become `0910.000`.

### Mixed-file time systems and leap-second normalization

`TIME OF FIRST OBS` is compulsory in a mixed observation file; pure files default respectively to `GPS`, `GLO`, `GAL`, `QZS`, `BDT`, or `IRN`. The `GLO` scale is UTC(SU)-linked and uses UTC hours rather than UTC+3, while GPS/QZSS, Galileo, and BDS use their own continuous scales.

When one receiver clock serves mixed systems, remove whole leap-second offsets from code observations before writing: with a GLONASS clock add `c*ΔtLS` to GPS/Galileo and `c*ΔtLS_BDS` to BDS; with a GPS/Galileo clock subtract `c*ΔtLS` from GLONASS; with a BDS clock subtract `c*ΔtLS_BDS` from GLONASS and add `c*(ΔtLS-ΔtLS_BDS)` to GPS. Known fractional inter-system receiver-clock biases likewise require matching code and phase corrections, while realization differences are left for post-processing.

### Navigation time-correction headers

`TIME SYSTEM CORR` stores the fractional, leap-second-excluded difference as `Δt = a0 + a1*(t-tref)` and uses continuous reference weeks; GLONASS has zero `T/W`, and BDS weeks start at 2006-01-01 rather than 1980-01-06. RINEX 3.04 renames Galileo-minus-GPS from `GPGA` to `GAGP` without changing its sign or value.

For BDS `IONOSPHERIC CORR`, both the hour letter `A`–`X` and broadcasting satellite ID are mandatory; multiple records are allowed, with GEO parameters preferred over IGSO and then MEO. In `LEAP SECONDS`, only `GPS` and `BDS` are valid system identifiers; BDS-only files use the BDS week epoch and day numbers 0–6, whereas GPS-family fields use continuous GPS weeks and days 1–7.

### Mixed navigation blocks and Galileo duplicates

A mixed navigation file repeats system-dependent headers and prefixes every block with its constellation and satellite ID, which determines that block's record count; all navigation time tags remain in the satellite system's own time scale. Floating fields accept `E`, `e`, `D`, or `d` but require zero-padded two-digit exponents; when both are decoded, Galileo writers emit separate F/NAV and I/NAV blocks, and readers must accept both with the same IOD as well as multiple same-IOD blocks whose validity or other fields changed independently.

### Navigation conversion edge cases

GLONASS navigation epochs are UTC, and broadcast clock values are stored with the GPS-like sign convention `-TauN`, `+GammaN`, and `-TauC`. GPS, Galileo, BDS, and IRNSS transmission times are adjusted by `±604800` to the reported ephemeris week and use `0.9999E9` when unknown; QZSS permits the necessary `-604800` adjustment, while SBAS permits either sign to reach the ephemeris week.

The GPS fit-interval field is the actual interval in hours derived from IODC and the broadcast flag, but QZSS stores `0` for two hours, `1` for more than two hours, or blank if unknown. BDS navigation weeks are continuous from 2006-01-01, Galileo weeks are continuous and aligned to GPS weeks, and an SBAS payload is identified as `Snn` with `nn = PRN - 100` and defaults to GPS time.

## Recording and convbin basics

### Recording convertible ZED-F9P logs

For a simpleRTK2B/ZED-F9P log, enable the required constellations and signals in u-center and write them to both RAM and Flash, disable NMEA child messages, and enable `UBX-RXM-RAWX` observations plus `UBX-RXM-SFRBX` navigation messages. Verify both message types in Packet Console before recording each rover and base log; both observation and navigation data are needed for the resulting RINEX pair.

### RTKCONV signal selection and diagnostics

RTKCONV proposes observation (`.obs`) and navigation (`.nav`) outputs for the selected raw log; its options must match what was recorded, such as GPS/GLO/GAL/BDS with L1 and L2/E5b for the tutorial's dual-frequency workflow. In its observation plot, green is dual-frequency, yellow is single-frequency, and red ticks are cycle slips; all-gray satellites usually mean the navigation file is missing, while a few gray satellites may simply be below the elevation threshold.

### `convbin` decoder and time selection

Force an input decoder with `-r` and one of `rtcm2`, `rtcm3`, `nov`, `oem3`, `ubx`, `ss2`, `hemis`, `stq`, `javad`, `nvs`, `binex`, `rt17`, `sbf`, or `rinex`; otherwise recognized extensions such as `.rtcm3`, `.ubx`, `.sbf`, and `.obs` select it automatically. `-ts`/`-te` bound the time range, `-tr` supplies approximate time for RTCM, `-ti` sets the observation interval, and `-span` limits the span in hours.

```sh
convbin -r ubx -ts 2026/7/12 08:00:00 -te 2026/7/12 10:00:00 \
  -ti 1 -f 2 -od -os rover.ubx
```

### `convbin` RINEX content controls

The defaults are RINEX 2.11, two frequencies, and no Doppler, SNR, ionosphere correction, time correction, or leap-second header data; change these with `-v`, `-f`, `-od`, `-os`, `-oi`, `-ot`, and `-ol`. Signal filtering uses `-mask`/`-nomask`, `-x` excludes a satellite, and `-y` excludes whole systems using `G`, `R`, `E`, `J`, `S`, or `C`.

### `convbin` headers and output routing

Header switches set comment (`-hc`), marker name/number/type (`-hm`/`-hn`/`-ht`), observer and agency (`-ho`), receiver (`-hr`), antenna (`-ha`), approximate XYZ (`-hp`), and antenna H/E/N delta (`-hd`); slash-separate the compound values. Use `-d` for the output directory, `-c` for station-ID filename convention, and `-o`/`-n`/`-g`/`-h`/`-q`/`-l`/`-s` for OBS, NAV, GNAV, HNAV, QNAV, LNAV, and SBAS paths; the documented default suffixes are `.obs`, `.nav`, `.gnav`, `.hnav`, `.qnav`, `.lnav`, and `.sbs`.

## RTKLIB conversion compatibility and fixes

### ZED-F9P Galileo I/NAV in 2.4.3 b34

Affected ZED-F9P firmware produces E5b I/NAV `UBX-RXM-SFRBX` frames that 2.4.3 b34 rejects, leaving RTKCONV/CONVBIN RINEX navigation output without Galileo ephemerides and preventing RTKNAVI/RTKRCV from using them. The documented source workaround is:

```diff
-if (raw->len<44+off) return 0; /* E5b I/NAV */
+if (raw->len<40+off) return 0; /* E5b I/NAV */
```

Apply it in `src/rcv/ublox.c` and rebuild the affected applications.

### High-rate BINEX time tags in 2.4.3 b34

RTKCONV/CONVBIN can introduce plus-or-minus 100 ns errors when converting high-rate BINEX observations because the minute and millisecond offsets are combined in one floating-point addition. In `src/rcv/binex.c`, preserve the millisecond resolution with two additions:

```diff
-raw->time=timeadd(epoch2time(gpst0),min*60.0+msec*0.001);
+raw->time=timeadd(epoch2time(gpst0),min*60.0);
+raw->time=timeadd(raw->time,msec*0.001);
```

### SP3-d files above 99 satellites

RTKPOST and RNX2RTKP 2.4.3 b34 misread the three-column SP3-d satellite count and cannot ingest files containing more than 99 satellites. The `src/preceph.c` header parse must read three characters beginning at offset 3:

```diff
-ns=(int)str2num(buff,4,2);
+ns=(int)str2num(buff,3,3);
```

### Leading null receiver observations

In 2.4.3 b34, a receiver log beginning with null observation records can make RTKCONV or CONVBIN write only the final observation record, even though its navigation file converts normally. Validate the observation epoch count instead of treating a successful navigation conversion as proof that both outputs are complete.

### GLONASS phase from MSM4 and MSM6

RTKCONV 2.4.3 b34 can supply the missing GLONASS frequency-channel numbers for MSM4/MSM6 from an enabled FCN table in its conversion options. CONVBIN has no equivalent FCN-table facility, so an FCN-less stream that RTKCONV can convert with this option still cannot be converted the same way by CONVBIN.

### RINEX 2 extension boundary

RTKLIB 2.4.2 does not properly read TEQC's "RINEX 2.11 extended" format, the non-standard RINEX 2.11 Galileo/QZSS/BeiDou navigation extensions, or the RINEX 2.12 BeiDou navigation extension. Its one supported non-standard RINEX 2 extension is JAXA's RINEX 2.12 QZSS format.

## Interchange formats

### SBAS log framing

RTKCONV's SBAS text log stores one frame as `GPS-week TOW PRN message-type : hex`; the hexadecimal payload is the 226-bit SBAS message without its 24-bit parity field, zero-padded at the tail to a byte boundary. This is also the SBAS-log input format accepted by RTKLIB post-processing.

```text
1471 349007 137 25 : C666A0A7F1FE6000027F80000003468000000000000000000000000000
```

## RTKLIB conversion and decoder controls

### RINEX version conversion and header scan

RTKCONV can take RINEX as input to convert version 2 to 3 or version 3 to 2 while filtering time, interval, satellites, and signals. For RINEX 3 output, enable `Scan Obs Types`: RTKCONV first scans the input for the actual observation-type set, then writes it on a second pass; without it, the header is built from format defaults and the signal mask.

RINEX 2 writes separate GNAV/HNAV/QNAV/LNAV navigation files, whereas RINEX 3 sends all selected constellations to one mixed NAV file.

### Per-signal selection and phase shifts

RTKPOST's `misc-rnxopt1` and `misc-rnxopt2` accept space-separated `-GLss`, `-RLss`, `-ELss`, `-JLss`, `-CLss`, and `-SLss` selectors for rover and base data. Appending `=+n.nn` applies that many cycles to the chosen carrier phase; without a selector, RTKLIB uses its system/frequency priority table.

```text
misc-rnxopt1 =-GL1X -RL1C
misc-rnxopt2 =-GL1X -RL1C
```

### Default multiple-signal priorities

When no selector is supplied, priority decreases from left to right in these sequences; the preference is not simply the first signal encountered in the stream:

```text
GPS:     L1 1C>1P>1Y>1W>1M>1N>1S>1L; L2 2P>2Y>2W>2C>2M>2N>2D>2S>2L>2X; L5 5I>5Q>5X
GLONASS: G1 1P>1C; G2 2P>2C; G3 3I>3Q>3X
Galileo: E1 1C>1A>1B>1X>1Z; E5a 5I>5Q>5X; E5b 7I>7Q>7X; E5a+E5b 8I>8Q>8X; E6 6A>6B>6C>6X>6Z
QZSS:    L1 1C>1S>1L>1X>1Z; L2 2S>2L>2X; L5 5I>5Q>5X; LEX 6S>6L>6X
BeiDou:  B1 2I>2Q>2X; B2 7I>7Q>7X; B3 6I>6Q>6X
SBAS:    L1 1C; L5 5I>5Q>5X
```

### Decoder-specific input controls

RTCM 3 input accepts `-STA=nnn` to keep one station ID, `-EPHALL` to retain all ephemerides, and the per-system signal selectors; BINEX supports the ephemeris and signal selectors as well. Receiver-specific controls include `-INVCP` for u-blox and SkyTraq carrier-phase polarity, `-TADJ=tint` for u-blox and NVS time-tag alignment, and JAVAD's `-NOET` to discard `ET (::)` epoch-time messages.

### RTCM encode/decode boundary

The support table marks legacy compact observations 1001/1003/1009/1011 and MSM1–MSM3 as encode-only; full legacy observations 1002/1004/1010/1012 and MSM4–MSM7 are the bidirectional choices. RTCM 2 types 1 and 9 can be read, but their DGPS corrections are not supported.

SSR orbit, clock, code-bias, combined, URA, and high-rate-clock messages are supported as GPS 1057–1062 and GLONASS 1063–1068; the corresponding Galileo 1240–1245 and QZSS 1246–1251 definitions are marked draft.

### RTCM stream conversion contract

The new STRSVR converter accepts RTCM 2/3, supported receiver formats, and BINEX but generates RTCM 3 only. Its message list is `type(interval)`; omitting the interval follows the input message interval, and generated antenna-information messages take their station and antenna fields from STRSVR Options.

For `str2str`, conversion is enabled only when both endpoints carry format suffixes. `-msg` selects generated messages and rates, `-sta` sets the station ID, and `-opt` passes decoder options:

```sh
str2str -in serial://ttyS0:115200:8:n:1:off#ubx \
  -out tcpsvr://:22101#rtcm3 \
  -msg '1005(10),1074(1),1019(5)' -sta 1
```

## Demo5 conversion and signal handling

### Additional raw stream decoders

Demo5's `str2str` format suffixes include input-only `swiftnav`, `unc` (Unicore), and `sbf` (Septentrio), and its `ubx` entry covers generations 8 and 9 in addition to the older receivers. These are decoder suffixes after `#format`, not stream URL schemes.

### CONVBIN decoder and output additions

`convbin -r unc` and `-r sbp` select Unicore and Swift Navigation SBP input; `.unc` is auto-recognized, but no SBP filename suffix is listed for autodetection. `-tt` sets epoch tolerance, `-halfc` enables half-cycle ambiguity correction, `-b` and `-i` route RINEX CNAV and INAV output, and `-trace` enables tracing.

```sh
convbin -r sbp -tt 0.005 -halfc -b rover.cnav -i rover.inav rover.sbp
```

### u-blox observation-quality decoder options

For u-blox input, `-MULTICODE` preserves multiple codes on one frequency, `-RCVSTDS` stores receiver standard deviations in otherwise unused RINEX fields, and `-STD_SLIP=n` turns large phase standard deviation into a cycle-slip indication. `-MAX_STD_CP=n` rejects carrier phase above the receiver-reported standard-deviation limit; its documented generation-specific defaults are 5 for M8T/M8P and 8 for F9P.

### Navigation-family selection at decode time

RTCM 3, BINEX, and several proprietary decoders accept `-GALINAV` or `-GALFNAV` to retain only Galileo I/NAV or F/NAV ephemerides rather than the default of accepting both. RTCM 3 also accepts `-INVPRR` for phase-range-rate polarity, `-STA=nnn` for one station ID, `-ILss` for an IRNSS MSM signal, and `-RT_INP` for real-time input handling.

### Demo5 multiple-signal priorities

Demo5 changes several defaults rather than merely adding signals: GPS L2 now prefers `2C`, GLONASS prefers C/A before P and includes CDMA choices, and QZSS prefers L before S. The changed/expanded priority rows are:

```text
GPS L2:  2C>2P>2Y>2W>2M>2N>2D>2L>2S>2X
GLO G1:  1C>1P>1A>1B>1X; G2: 2C>2P>2A>2B>2X
QZSS L1: 1C>1L>1S>1X>1Z; L2: 2L>2S>2X
QZSS L5: 5I>5Q>5X>5D>5P>5Z; LEX: 6L>6S>6X>6E>6Z
BDS B1:  2I>2Q>2X>2D>2P>2A>2N; B2: 7I>7Q>7X>7D>7P>7Z
```

### Support-matrix inconsistencies

Treat the command references as evidence that Unicore, SwiftNav, and Septentrio decoder entry points exist even though Appendix D.2 omits them from its receiver-message table. Likewise, IRNSS is selectable in the positioning UI, `rnx2rtkp -sys I`, RTCM's `-ILss`, and CONVBIN signal masks. The overview, supported-signal table, and CONVBIN `-y` list do not establish complete end-to-end support, so verify the exact application and path in use.
