---
name: agopengps-knowledge-patch
description: AgOpenGPS
version: 6.8.5
license: MIT
metadata:
  author: Nevaberry
---


# AgOpenGPS Knowledge Patch

Use this skill when maintaining, deploying, integrating, or diagnosing
AgOpenGPS, AgIO, their successor applications, or the associated GNSS and
machine-control hardware.

## How to use this patch

1. Identify the exact application line: classic WinForms AgOpenGPS,
   historical AgValoniaGPS, or AgOpenWeb.
2. Record the application tag or commit, controller source commit, PCB
   revision, receiver role, receiver firmware, and generated configuration.
3. Keep position input, correction transport, application framing, steering,
   and machine output as separate interfaces while diagnosing a system.
4. Apply only the guidance that matches the selected application line and
   hardware family.
5. Revalidate files, messages, ports, and firmware whenever crossing an
   application or board-family boundary.

## Reference index

| Reference | Topics |
| --- | --- |
| [Application evolution and profiles](references/application-evolution-and-profiles.md) | WinForms architecture, deployment changes, profiles, Easy Drive, Task Controller, maintenance fixes |
| [Desktop operation and networking](references/desktop-operation-and-networking.md) | Safety, portable releases, section capacities, AgIO diagnostics, Ethernet setup |
| [Cross-platform hosts](references/cross-platform-hosts.md) | AgValoniaGPS archive status, AgOpenWeb architecture, modes, artifacts, migration boundaries |
| [NTRIP and correction routing](references/ntrip-and-correction-routing.md) | AgIO caster requests, GGA, RTCM routes, Serial NTRIP, AgOpen Ntripcaster |
| [RTCM base and receiver profiles](references/rtcm-base-and-receiver-profiles.md) | Coherent RTCM sets, station IDs, correction age, RTKBase stages, ZED-F9P profiles |
| [NMEA and application framing](references/nmea-and-application-framing.md) | Active sentence dispatch, checksum behavior, binary `0xD6` boundary |
| [Autosteer hardware](references/autosteer-hardware.md) | Hardware levels, AIO identity, Teensy requirements, actuator paths, antenna and sensor setup, connector limits |
| [Machine and rate control](references/machine-and-rate-control.md) | Firmware pinning, custom PGNs, rate-controller families, ISOBUS ownership |

## Safety boundary

Automatic control has no built-in safety boundary. Treat the software as a
demonstration and simulator system, provide an independent way to stop control,
and keep people clear of moving equipment.

Do not use any of these as evidence that operation is safe:

- valid GNSS reception;
- an RTK fixed solution;
- correct coverage painting;
- a responsive steering loop;
- an accessible browser or caster connection.

Verify wheel-angle sign, center, range, smoothness, and full mechanical travel
before enabling steering output. See
[Autosteer hardware](references/autosteer-hardware.md).

## Breaking application changes

### Recheck extensions after the 6.7 modernization

The 6.7 line retained the AgIO/application split but moved projects to SDK
style, removed x86 builds, moved shared facilities to `AgLibrary`, and
centralized logging. Review extensions that depend on 6.6.x project layout or
internals. The WPF example did not replace the production WinForms direction.

Use 6.7.1 rather than 6.7.0 when a deployment must remain on the 6.7 line,
because 6.7.1 corrects several initial behaviors.

### Do not time section control from rendering

Section control became switch-based in 6.7, and machine nudge uses custom PGN
222. Since 6.8.1, section processing runs at a fixed 10 Hz. Render-frame rate
is therefore the wrong clock for section timing or diagnosis.

### Treat profile domains independently

Starting in 6.8.2, vehicle, tool, and environment settings have separate
storage and lifecycles:

```text
VehicleProfiles/{name}.xml
ToolProfiles/{name}.xml
Environment/environment.xml
```

Do not assume a vehicle selection also selects an implement. Profile switching
saves the current profile first in 6.8.3, and nudge step size belongs to the
tool. See
[Application evolution and profiles](references/application-evolution-and-profiles.md).

### Keep Task Controller on the existing transport

The ISOBUS Task Controller introduced in 6.8.2 launches through AgIO and uses
the existing UDP/custom-PGN channel to reach AgOpenGPS. Do not invent a second
Task Controller transport or diagnose it as an Arduino relay path.

### Preserve temporary Easy Drive semantics

Easy Drive creates no field, uses a rigid single-section tool, disables
field-dependent features, writes no session data, and restores the original
vehicle and tool settings on exit. Do not persist its temporary state as a
normal field session.

## Release and host selection

For classic WinForms deployments, use an official unprefixed release tag and
prefer the maintained 6.8.5 release over a moving branch. Maintenance-only did
not mean frozen: critical fixes continued after 6.8.3.

Do not numerically compare the classic 6.8.x line with AgValoniaGPS or
AgOpenWeb date-like releases. Those are separate codebases with independent
compatibility boundaries.

AgValoniaGPS is archived and points to AgOpenWeb. Historical nightly artifacts
need an exact nightly tag and commit because an internal version may not
identify one build uniquely.

For AgOpenWeb, select all three dimensions:

- stable or nightly channel;
- desktop, headless service, or mobile execution mode;
- operating system and CPU architecture.

Desktop, service, and Android bundles are not interchangeable. See
[Cross-platform hosts](references/cross-platform-hosts.md) for platform and
runtime prerequisites.

## Layered data-path diagnosis

Diagnose the system in transport order:

1. Confirm incoming NMEA and the current position/fix state in AgIO.
2. Confirm the NTRIP request, mountpoint, GGA behavior, and received correction
   bytes.
3. Confirm selected serial or UDP correction outputs and module status.
4. Confirm binary application messages reach AgOpenGPS or network modules.
5. Only then investigate guidance, steering, or machine behavior.

An AgIO monitor proves only the layer it observes. A browser UI proves host
reachability, and a caster socket proves connectivity, not fresh or usable
corrections.

For dedicated Ethernet modules, use unique addresses on `192.168.5.0/24` and
do not attach two PC adapters to that subnet. Working Wi-Fi does not validate
the module network. See
[Desktop operation and networking](references/desktop-operation-and-networking.md).

## Corrections and base stations

Keep NTRIP request controls, GGA feedback, and RTCM output routing distinct.
AgIO can send corrections over serial or UDP, commonly port `2233` for
All-In-One Teensy hardware, and can accept local corrections through Serial
NTRIP for onward routing.

For a stationary ZED-F9P base using the documented default constellations,
start with one coherent MSM family:

```text
1005
1074 1084 1094 1124
1230
```

Use the same observation rate and MSM class across constellations. MSM7 replaces
MSM4; it does not accompany it. Match the station ID in the reference message
and observations, keep receiver ports consistent, and monitor correction age.
See [RTCM base and receiver profiles](references/rtcm-base-and-receiver-profiles.md).

## Navigation protocol boundary

An RMC-only receiver stream is insufficient for the active AgIO dispatch path.
Configure a supported GGA/VTG/HDT or proprietary sentence set and confirm it in
the serial monitor.

Do not collapse these three formats into one protocol:

```text
receiver -> ASCII navigation sentences -> AgIO
caster   -> binary RTCM corrections     -> receiver
AgIO     -> binary AOG PGN 0xD6         -> application/modules
```

The `0xD6` frame is neither ASCII NMEA nor SAE J1939. The release-specific
`$KS` checksum exception is compatibility behavior, not a general parser rule.
See [NMEA and application framing](references/nmea-and-application-framing.md).

## Hardware identity before configuration

Never treat a board nickname as a firmware version. Record the exact PCB
revision and population, schematic or Gerber commit, firmware directory and
source commit, receiver role and firmware, and generated Config-O-Matic file.

Current AIO designs require Teensy 4.1. Teensy 3.2 and 4.0 are not substitutes.
Standard and Micro receiver modules must also match the PCB's physical socket.

Choose the output chain by steering interface: steer-ready CAN, Keya wheel,
DIY motor, PWM hydraulic valve, or Danfoss integrated valve. These paths do not
share generic pinouts or output modes.

## Machine-control ownership

Use machine-specific custom PGNs and a protocol document matched to both the
application and controller firmware. Sixty-four equal software sections do not
imply 64 physical outputs.

Do not share pin mappings or configuration constants between Nano `RC12-3`,
Teensy 4.1 `RC11-2`, and ESP32 `RC15`. Preserve the matching firmware commit
with each PCB revision.

Assign every physical output one owner. If the ISOBUS Task Controller owns
sections, do not enable a relay controller to command the same outputs. See
[Machine and rate control](references/machine-and-rate-control.md).
