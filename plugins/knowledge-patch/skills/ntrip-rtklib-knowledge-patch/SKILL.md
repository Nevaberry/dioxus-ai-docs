---
name: ntrip-rtklib-knowledge-patch
description: NTRIP / RTKLIB current compatibility guidance. Use for NTRIP / RTKLIB work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# NTRIP / RTKLIB Knowledge Patch

Baseline: NTRIP through 2.0 and RTKLIB through 2.4.2. Coverage extends through BNC 2.13, RINEX 3.04, RTKLIB 2.4.2 patch releases and 2.4.3 b34, and current Demo5 behavior documented by this patch.

## Use this patch

1. Identify the exact NTRIP revision, RTKLIB branch, patch level, application, receiver format, and transport before choosing syntax or defaults.
2. Read the reference file matching the task; branch-specific behavior in upstream RTKLIB, Demo5, and BNC is not interchangeable.
3. Preserve byte streams unless conversion is intentional. RTKLIB's converter decodes and re-encodes selected messages rather than mixing generated messages with untouched input.
4. Validate outputs semantically: inspect RTCM message inventory, RINEX epoch and navigation counts, reference-station coordinates, solution status, and trace warnings.
5. Treat configuration samples as starting points. Confirm option spelling and availability against the actual binary or source tree.

## Reference index

| Reference | Topics |
|---|---|
| [ntrip-casters-and-vrs.md](references/ntrip-casters-and-vrs.md) | Rev1/Rev2 interoperability, sourcetables, GGA/VRS behavior, BKG caster deployment, TLS, ACLs, authorization, RTK2go, Centipede, Emlid |
| [bnc-client.md](references/bnc-client.md) | BNC runtime and configuration, transports, TLS, RINEX, record/replay, engine feeds, PPP, correction combination, RTNET, SSR uploads |
| [rinex-and-conversion.md](references/rinex-and-conversion.md) | RINEX 3.04 grammar and semantics, RTKCONV/CONVBIN, decoder controls, observation priorities, conversion defects and compatibility |
| [rtklib-core-and-support.md](references/rtklib-core-and-support.md) | Source layout, compile-time capabilities, format boundaries, embedding APIs, patch-level limits, correctness fixes, licensing |
| [applications-and-streaming.md](references/applications-and-streaming.md) | RTKNAVI, RTKRCV, RTKPOST, RNX2RTKP, STR2STR, RTKGET, replay, stream slots, downloads, command-line operation |
| [positioning-and-ambiguity.md](references/positioning-and-ambiguity.md) | Position modes, PPP/SSR, RAIM, base and antenna configuration, Demo5 filtering and AR, branch-aware post-processing |
| [diagnostics-and-platforms.md](references/diagnostics-and-platforms.md) | Solution/status records, trace diagnosis, RTKPLOT, converter isolation, Linux/Qt/Raspberry Pi builds, serial integration |

## Breaking changes and compatibility boundaries

### Separate NTRIP rover and source behavior

- Expect upstream RTKLIB's NTRIP client to speak Rev1 only.
- Let a Rev2 rover accept a Rev1 response, but do not extend that fallback to source uploads.
- Use Rev1 `SOURCE` plus `Source-Agent` for legacy uploads; Rev2 changes uploads to `POST` and deprecates `Source-Agent`.
- Parse both Rev1 sourcetable-style failures and Rev2 HTTP 4xx failures.
- Send rover GGA only after the mountpoint request succeeds.

### Treat VRS sessions as bidirectional and per-rover

- Read the sourcetable from `/`; honor case-sensitive mountpoints, `NMEA=1`, and the `N`/`B`/`D` authentication flags.
- Send a usable GGA immediately after connection and then at the service interval; strict casters may reject stale time, zero satellites, or invalid fix status.
- Do not fan out one VRS stream to several rovers. Each rover needs its own GGA feedback and position-dependent correction session.
- Verify whether a `VRS` mountpoint is synthetic by decoding RTCM 1005/1006 ECEF coordinates and comparing them with the requested rover location.

### Pin RTKLIB branch and patch level

- Clone the `2.4.3` branch explicitly when reproducing 2.4.3; historical default branches could still yield 2.4.2.
- Do not copy Demo5 options or thresholds into upstream 2.4.2/2.4.3 without checking availability and retuning.
- Account for constellation limits: original 2.4.2 lacked BeiDou solution support, p7 added it, p13 accepts C01-C35/E01-E30, and 2.4.3 b34 accepts C01-C63/E01-E36.
- Require appropriate correctness floors: p4 for satellite antenna PCV, p7 for SSR final fields and ionosphere-free antenna offsets, p11 for GLONASS/BeiDou ionosphere scaling, and p13 for SSR IOD validation.
- Avoid the pre-p8 combined rover/base `MAXOBS=64` ceiling and the pre-b31 invalid MSM generation path when satellite-count times signal-count exceeds 64.

### Do not assume format round trips

- Treat BINEX as partial input-only, NMEA 0183 as output-only, and SP3-c, IONEX, and EMS 2.0 as input-only at the 2.4.2 boundary.
- Use full RTCM legacy observations 1002/1004/1010/1012 or MSM4-MSM7 for bidirectional encode/decode; compact legacy observations and MSM1-MSM3 are encode-only.
- Preserve RTCM 1230 with byte-for-byte relay. A conversion path that regenerates 1004/1012 cannot regenerate 1230 and drops the original.
- Split RTCM MSM observations before calling `gen_rtcm3()` whenever satellites multiplied by signals exceeds the 64-cell mask.

### Account for affected conversion defects

- Patch 2.4.3 b34 ZED-F9P E5b I/NAV length validation in `src/rcv/ublox.c` when Galileo ephemerides disappear.
- Patch high-rate BINEX time construction in `src/rcv/binex.c` to add minutes and milliseconds separately when ±100 ns errors matter.
- Patch the SP3-d header count in `src/preceph.c` to read three columns when ingesting more than 99 satellites.
- Count observation epochs after conversion; leading null receiver observations can leave only the last epoch even while navigation output looks normal.
- Use RTKCONV's FCN table for GLONASS MSM4/MSM6 without channel numbers; CONVBIN has no equivalent facility.

## High-value NTRIP and caster patterns

### Upload an RTKLIB base stream

Use `ntrips://` for a source upload. RTK2go's empty username is intentional:

```sh
str2str -in serial://ttyACM0:115200:8:n:1:off \
  -out 'ntrips://:PASSWORD@rtk2go.com:2101/MOUNTPOINT'
```

Send RTCM 3 only, include 1005 plus rover-required observations and navigation, and avoid interleaved NMEA.

### Expose a local Demo5 caster

Use the current Demo5 local-caster grammar:

```sh
str2str -in serial://ttyUSB1:115200 -out 'ntripc://:12345/BASE'
```

Use common serial, TCP, or non-position-dependent NTRIP input only; never reuse one VRS input across clients.

### Secure and authorize BKG correctly

- Terminate inbound TLS in a proxy and forward to BKG's plain listener; use this arrangement for Rev2.
- Remember `acl_policy 1` is deny-list mode and `acl_policy 0` is allow-list mode.
- Protect listeners with `users.aut`, `groups.aut`, and `clientmounts.aut`; an absent mountpoint is unprotected.
- Authorize Rev2 uploads through `users.aut`, `groups.aut`, and `sourcemounts.aut`; Rev1 uses `encoder_password`.
- Use rehash for live authorization/config reload and resync only when a disconnecting daemon restart is acceptable.

## High-value RINEX and conversion rules

### Write valid RINEX 3.04 observations

- Declare observation types separately per constellation and preserve their declared order in every satellite record.
- Align every carrier phase to its constellation/frequency reference and emit `SYS / PHASE SHIFT`, including explicit zero shifts where already aligned.
- Include `GLONASS SLOT / FRQ #` and `GLONASS COD/PHS/BIS` for GLONASS observations.
- Include `TIME OF FIRST OBS` in mixed files, remove whole leap-second offsets from code observations only, and apply matching code-and-phase corrections to known fractional inter-system receiver-clock biases.
- Apply receiver clock corrections consistently to epoch time, pseudorange, and carrier phase and declare `RCV CLOCK OFFS APPL`.
- Treat `SYS / SCALE FACTOR` as a reader division operation.

### Preserve complete RTCM-to-RINEX metadata

- Know the prospective MSM observation types before writing a RINEX 3/4 header.
- Supply GLONASS channels from message 1020, MSM5/7 extension data, or RTKCONV's FCN table; MSM4 alone is insufficient.
- Use a BNC skeleton when station, receiver, antenna, coordinate, eccentricity, or observation-type metadata must be controlled.
- Enable RTKCONV `Scan Obs Types` for RINEX 3 output so the header comes from a complete first pass.
- Keep rover observations first and base observations second in RTKPOST and RNX2RTKP relative workflows.

## High-value positioning and ambiguity rules

### Configure measurement gates independently

- Set rover and base SNR masking independently and provide nine five-degree bins for every enabled frequency.
- Use `pos1-elmask` for the solution, `pos2-arelmask` for fixing, and `pos2-elmaskhold` for hold feedback.
- Keep receiver-reported uncertainty (`pos2-rcvstds`) distinct from code/phase weighting (`stats-eratio1` and `stats-eratio2`).
- Tune dynamics process noise to actual antenna motion, including vibration and bumps.

### Handle Demo5 ambiguity controls by sample count

- Interpret `pos2-arlockcnt`, `pos2-arminfix`, and `pos2-aroutcnt` as samples, not seconds.
- Use `pos2-minfixsats`, `pos2-minholdsats`, and `pos2-mindropsats` for the fix, hold, and trial-exclusion floors.
- Remember larger `pos2-varholdamb` weakens fix-and-hold feedback.
- Treat percent-fixed and AR ratio as self-referential after fix-and-hold begins; validate with independent residuals and repeatability.
- Check affected source trees for unsigned `ssat_t.lock`; make it signed before relying on the new-satellite delay.
- Treat Demo5 `PPP-AR` as unsupported even though retained documentation describes an experimental algorithm.

### Keep branch-specific frequency and rejection behavior separate

- Demo5 maps Galileo E5b differently from official 2.4.2/2.4.3 and changes multiple-signal priorities.
- Demo5 `pos2-arfilter` adaptive admission is absent from official 2.4.2 p13 and 2.4.3 b33.
- Retune `pos2-rejionno` per branch and data; equal numeric values do not produce equal outlier behavior.
- Isolate converter and solver versions when fix rates regress, and inspect cycle-slip flags before attributing the failure to the solver.

## High-value runtime and debugging rules

### Operate RTKRCV deliberately

- Configure `inpstr1` as rover, `inpstr2` as base, and `inpstr3` as correction input unless the deployment intentionally differs.
- Restart after interactive `set` or `load`; those changes do not take effect immediately.
- Distinguish console logout (`exit`) from process termination (`shutdown` or `USR2`).
- Enable periodic GGA explicitly because `str2str -n` defaults to zero.
- Enable `out-outsingle=on` only when downstream consumers should receive degraded single-position fallback during correction loss.

### Diagnose from signatures before retuning

- Use trace level 2 for input/configuration failures, level 3 for solution and AR detail, and level 4 only when communication bytes are needed.
- Read both severity-1 errors and severity-2 warnings.
- Map Q=0 plus large differential age to non-overlapping rover/base epochs; map Q=0 plus `no common satellites` to navigation mismatch.
- Map immediate all-satellite outliers at Q=2 to suspect base coordinates before changing AR settings.
- Confirm fresh navigation messages after stream changes; retained colored satellite state does not prove the new stream contains ephemerides.
- Require dual-frequency observations for RTKPLOT multipath and valid navigation for elevation plots.
