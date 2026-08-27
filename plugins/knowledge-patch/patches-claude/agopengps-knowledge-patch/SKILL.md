---
name: agopengps-knowledge-patch
description: AgOpenGPS
version: "6.8.5"
license: MIT
metadata:
  author: Nevaberry
---


# AgOpenGPS Knowledge Patch

Use this skill when designing, extending, deploying, or diagnosing AgOpenGPS,
AgIO, AgValoniaGPS, AgOpenWeb, GNSS correction paths, autosteer hardware, or
machine-control hardware. Start by identifying the exact application release,
codebase, board revision, firmware source commit, and operating mode.

Treat application behavior, field data, profiles, wire protocols, and hardware
pinouts as separate compatibility surfaces. Shared ancestry or a familiar board
name does not make any of those surfaces interchangeable.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/architecture-profiles-and-releases.md](references/architecture-profiles-and-releases.md) | WinForms modernization, profiles, section timing, Task Controller, Easy Drive, release selection, field-data fixes |
| [references/desktop-operation-and-networking.md](references/desktop-operation-and-networking.md) | Safety, portable installation, section capacity, layered AgIO diagnosis, Ethernet conventions |
| [references/cross-platform-hosts.md](references/cross-platform-hosts.md) | AgValoniaGPS archival, AgOpenWeb architecture, execution modes, artifacts, migration boundaries |
| [references/ntrip-and-correction-routing.md](references/ntrip-and-correction-routing.md) | AgIO NTRIP requests, GGA, correction outputs, Serial NTRIP, caster pinning |
| [references/rtcm-base-and-rtkbase.md](references/rtcm-base-and-rtkbase.md) | F9P base messages, MSM coherence, correction freshness, RTKBase relays, receiver profiles |
| [references/nmea-and-application-protocol.md](references/nmea-and-application-protocol.md) | Active sentence dispatch, checksum exception, NMEA/RTCM/custom-PGN boundaries |
| [references/autosteer-hardware.md](references/autosteer-hardware.md) | Hardware levels, AIO revisions, Teensy requirements, steering interfaces, antennas, IMU and WAS setup |
| [references/machine-and-rate-control.md](references/machine-and-rate-control.md) | Machine firmware identity, PGNs, rate-controller families, ISOBUS ownership |

## Breaking architecture and deployment changes

### Identify the product line first

- Keep classic WinForms AgOpenGPS plus AgIO distinct from AgValoniaGPS and
  AgOpenWeb.
- Use an official unprefixed tag for classic deployments, not a moving branch.
- Do not compare date-like AgValoniaGPS or AgOpenWeb versions as if they were
  classic `6.8.x` releases.
- Revalidate profiles, field files, custom PGNs, ports, GNSS sentences, and
  board firmware whenever crossing codebases.

### Account for the classic project-layout transition

- The classic 6.7 line remains WinForms and retains the AgIO/application split.
- Its projects use SDK style, no longer build for x86, move shared facilities
  into `AgLibrary`, and centralize logging.
- Review extensions that depend on 6.6.x project paths or internals.
- Prefer 6.7.1 over 6.7.0 when a deployment must remain on the 6.7 line.
- Treat 6.8 as 64-bit only.

### Do not assume one combined vehicle file

- From 6.8.2, select vehicle and implement profiles independently.
- Store steering, IMU, GPS, and hardware-brand settings in the vehicle profile.
- Store sections, tramlines, relays, Arduino Machine settings, and nudge step in
  the tool profile.
- Keep display, sound, and window-position settings in the environment profile.
- Legacy conversion reads `Vehicles/` and may proceed without a tool profile.
- Profile switching saves the current profile before loading another profile.

### Update section-control assumptions

- Section control is switch-based in the 6.7 architecture.
- Machine nudge uses custom PGN 222.
- From 6.8.1, section processing runs at a fixed 10 Hz; never derive its timing
  or diagnosis from render-frame rate.
- The desktop application can model either 16 individually sized sections or
  64 equal sections, but controller output counts remain hardware-dependent.

### Respect maintenance and successor status

- Classic WinForms became maintenance-only after feature work moved toward the
  cross-platform rewrite, but critical fixes still landed after that shift.
- Prefer 6.8.5 for a classic 6.8 deployment.
- AgValoniaGPS is archived read-only and points to AgOpenWeb.
- AgOpenWeb is an independent fork and its browser UI does not prove that GNSS,
  corrections, hardware UDP, or control output works.

## Safety boundary

AgOpenGPS is described as a demonstration/simulator system and supplies no
built-in safety limits. Provide an independent means to stop automatic control,
keep people clear, and validate the complete physical system. RTK fix, coverage
painting, GNSS reception, and a responsive steering loop are not safety proof.

## High-value operator workflows

### Install a classic desktop release

1. Unblock the Windows ZIP if required.
2. Extract the complete archive to a normal writable directory.
3. Run `AgOpenGPS.exe` from the extracted tree, never from inside the archive.
4. Launch AgIO separately when isolating communications from guidance behavior.

### Diagnose AgIO from upstream to downstream

1. Confirm incoming NMEA and inspect position and fix status.
2. Confirm the NTRIP session and that correction bytes are moving.
3. Check the chosen serial or UDP correction output.
4. Check module status and the traffic reaching the hardware.
5. Only then investigate application guidance or steering.

Use AgIO's serial and UDP monitors to filter and log traffic. A working browser,
Wi-Fi connection, caster session, or receiver detection proves only that one
stage is alive.

### Keep the three navigation transports separate

```text
receiver -> ASCII NMEA/proprietary sentences -> AgIO
caster   -> binary RTCM corrections          -> receiver
AgIO     -> binary custom PGN 0xD6            -> application/modules
```

The final frame is AgOpenGPS protocol, not ASCII NMEA and not SAE J1939.

### Configure NTRIP deliberately

- Select HTTP/1.0 or HTTP/1.1 request form and Basic authorization as required.
- Use **Verify** for reachability and **Get Source Table** to discover the real
  mountpoint.
- Choose fixed or live GGA; interval `0` disables GGA transmission.
- Route received RTCM to serial, UDP, or use **Serial NTRIP** for locally
  received corrections.
- Pin AgOpen Ntripcaster by commit or image and test source upload syntax.

### Build a coherent F9P correction stream

- Emit `1005`, MSM4 `1074/1084/1094/1124`, and `1230` for the documented
  default-constellation stationary base setup.
- Use one MSM class and one observation rate for every constellation.
- Make the `1005` or `1006` station ID match every MSM station ID.
- Replace MSM4 with MSM7 when choosing MSM7; do not emit both families.
- Monitor correction age because an open link does not imply fresh corrections.

### Diagnose RTKBase hop by hop

Start with the main RTKLIB `str2str` receiver input and local TCP stream. Then
inspect each NTRIP, TCP, serial, conversion, or file service independently.
Surveyed or fixed base coordinates are a separate requirement from receiver
detection and caster connectivity.

## Hardware compatibility checkpoints

### Record immutable identities

For an installation, record:

- exact application tag and product line;
- PCB family, revision, and population options;
- schematic or Gerber commit;
- `Boards` commit and firmware folder;
- generated Config-O-Matic configuration;
- receiver role, hardware, profile, and firmware;
- host platform, browser-client platform, execution mode, and architecture.

Names such as AIO v4.5, Machine v5, or “latest firmware” are not enough to
reproduce a system.

### Keep control levels and output owners distinct

- Lightbar guidance needs a Windows tablet and GNSS, not steering hardware.
- Autosteer additionally needs a controller, actuator, feedback, switching, and
  suitable power or CAN integration.
- Section and rate control use a separate machine-control firmware path.
- Do not let ISOBUS Task Controller and a relay controller command the same
  physical outputs.

### Match the AIO design, actuator, and feedback chain

- Current AIO designs specifically require Teensy 4.1; 3.2 and 4.0 are not
  drop-in substitutes.
- Select the correct steer-ready CAN, Keya, DIY motor, PWM hydraulic, or Danfoss
  path; vehicle CAN messages, drivers, pinouts, and output modes differ.
- A PWM motor or valve commonly uses AIO 4.x, Cytron, WAS, and BNO085; Keya does
  not need the separate Cytron.
- Verify BNO085 orientation and inversion, then WAS sign, center, range,
  smoothness, and full travel before steering output is enabled.

### Treat board pinouts as revision-specific

On AIO v2, pins 18/19 are a second CAN channel. On v4, pin 18 is Cytron supply
input and pin 19 is unconnected. Fuse battery input, limit the 12 V auxiliary
output to 1 A, and treat direct Teensy A12-A14 connections as unprotected.

## Data and feature semantics

### Easy Drive is temporary

Easy Drive provides quick guidance with a rigid single-section tool and no
field creation. It disables field-dependent features, writes no session data,
and restores the original vehicle and tool settings on exit.

### Task Controller uses the existing AgIO path

The ISOBUS Task Controller launches through AgIO and uses the existing UDP and
custom-PGN channel to communicate with the application. Follow the repository's
protocol; do not invent a separate application transport.

### Preserve local field state

AgShare downloads preserve local sections, flags, headland, and contour data.
Cancelling an already-triggered U-turn restores the original path, and Drive In
distance accepts comma-decimal locales.

## Validation discipline

- Verify the active NMEA dispatch set rather than assuming parser presence means
  a sentence is accepted; an RMC-only feed is insufficient.
- Treat the `$KS` checksum exception as release-specific compatibility behavior,
  not a general parser rule.
- Match custom-PGN framing, offsets, byte order, scaling, and checksum to both
  application and controller firmware.
- Match rate-controller configuration and pin meanings to RC11-2, RC12-3, or
  RC15; never transpose them between families.
- Test physical stop behavior and output ownership before field operation.

