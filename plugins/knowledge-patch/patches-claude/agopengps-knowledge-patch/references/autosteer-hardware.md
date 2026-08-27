# Autosteer Hardware Compatibility

## Separate hardware levels

A Windows tablet plus GNSS can provide lightbar guidance without steering
hardware. Standard autosteer additionally needs a controller, actuator,
feedback and switching, and a suitable power or CAN interface. Section and rate
control use a separate machine-control hardware and firmware path.

## Reproducible AIO identity

All-In-One v4.5 is a board baseline, not a firmware tag. Standard v4 and Micro
v4 PCB artifacts reside in separate repositories. The central `Boards`
repository carries firmware and more layouts but has no release series.

Record exact PCB revision and population options, schematic or Gerber commit,
`Boards` commit, and firmware folder. “AIO v4.5” or “latest firmware” alone does
not identify a reproducible installation.

## Teensy and firmware families

Current AIO designs specifically require Teensy 4.1, including its Ethernet
hardware and pins. Teensy 3.2 and 4.0 are not drop-in substitutes.

In the central repository, `TeensyModules` is the current AIO path.
`ArduinoModules` holds older Nano steering and machine firmware and the retired
external-IMU path. Preserve the Config-O-Matic-generated configuration with its
source commit.

## Steering output chains

Documented actuator paths include steer-ready CAN through a dedicated
vehicle-specific board, Keya steering wheel, DIY electric wheel motor, added
PWM hydraulic valve, and Danfoss integrated valve.

PWM motor or valve installations commonly combine AIO 4.x, a Cytron driver,
WAS, and BNO085. Keya does not require the separate Cytron. CAN installations
must implement the vehicle-specific messages and must not borrow another
actuator path's pinout or output mode.

## Receivers and antenna geometry

The SimpleRTK2B path calls for ZED-F9P rather than F9R. Standard and Micro
receiver modules must match the PCB's physical interface.

For the documented dual-receiver arrangement, maintain at least 150 cm between
antennas. Physical left/right or heading/position placement must agree with the
receiver profiles and software settings. An ANN-MB-style antenna needs a metal
ground plane.

## Attitude and wheel-angle setup

The usual single-antenna system uses a BNO085. The documented dual-antenna
system derives attitude from the antennas and does not require a separate IMU.
TM171 remains under testing rather than being the default replacement.

Mount BNO085 upright with X or Y aligned to vehicle travel. Select the matching
0/90/180/270-degree orientation and inversion. Before enabling steering output,
verify WAS sign, center, range, smoothness, and full mechanical travel.

## Revision-specific electrical limits

AIO v2 uses pins 18/19 for a second CAN channel. On v4, pin 18 is the Cytron
supply input and pin 19 is unconnected. Fuse battery input and keep the board's
12 V auxiliary output at or below 1 A. Direct Teensy A12-A14 connections are
unprotected and are not generic 12 V I/O.

