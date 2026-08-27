# Autosteer Hardware

## Separate hardware levels

A Windows tablet plus GNSS can provide lightbar guidance without steering
hardware. Standard autosteer additionally requires a controller, actuator,
feedback and switching, and the suitable power or CAN interface. Section and
rate control use a separate machine-control hardware and firmware path.

Diagnose and document guidance, steering, and machine control separately.

## AIO identity and source pinning

All-In-One v4.5 is a recommended board baseline, not a firmware tag. Standard
v4 and Micro v4 PCB artifacts live in separate repositories; the central
`Boards` repository carries firmware and additional layouts without a release
series.

Identify an installation by:

- exact PCB revision and populated options;
- schematic or Gerber commit;
- `Boards` source commit and firmware folder;
- generated Config-O-Matic configuration.

## Teensy and firmware paths

Current AIO designs require Teensy 4.1, including its Ethernet hardware and
pinout. Teensy 3.2 and 4.0 are not drop-in substitutes.

In the central repository, `TeensyModules` is the current AIO path.
`ArduinoModules` contains older Nano steering and machine firmware plus the
retired external-IMU path. Preserve generated configuration together with the
source commit.

## Choose the actuator chain first

The documented steering interfaces are:

- steer-ready CAN through a dedicated vehicle-specific board;
- Keya steering wheel;
- DIY electric wheel motor;
- added PWM hydraulic valve;
- Danfoss integrated valve.

PWM motor and valve builds commonly combine an AIO 4.x, Cytron driver, WAS,
and BNO085. Keya does not need the separate Cytron. CAN installations require
vehicle-specific messages; do not copy another actuator path's pinout or
output mode.

## Receiver form factor and antenna geometry

The SimpleRTK2B path calls for a ZED-F9P rather than an F9R. Standard and Micro
receiver modules must match the PCB's physical interface.

For the documented dual-receiver setup:

- keep at least 150 cm between antennas;
- make physical left/right or heading/position placement match receiver
  profiles and software settings;
- give an ANN-MB-style antenna a metal ground plane.

## Attitude and wheel-angle setup

The usual single-antenna setup uses a BNO085. The documented dual-antenna setup
derives attitude from its antennas and needs no separate IMU. TM171 remains
under testing and is not the default replacement.

Mount a BNO085 upright with X or Y along vehicle travel. Select the matching
0, 90, 180, or 270-degree orientation and inversion. Before enabling steering
output, verify WAS sign, center, range, smoothness, and full mechanical travel.

## Revision-specific connector limits

AIO v2 uses pins 18 and 19 for a second CAN channel. On v4, pin 18 is the
Cytron supply input and pin 19 is unconnected.

Fuse battery input, keep the board's 12 V auxiliary output at or below 1 A,
and treat direct Teensy A12-A14 connections as unprotected. They are not
generic 12 V inputs or outputs.
