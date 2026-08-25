# RTCM Base and Receiver Profiles

## Coherent stationary-base message set

For the documented stationary ZED-F9P pairing with default constellations, the
base message set is:

```text
1005                  # reference antenna reference point; may run slower
1074 1084 1094 1124   # GPS, GLONASS, Galileo, BeiDou MSM4 observations
1230                  # GLONASS code-phase biases
```

A rover needs `1005` or `1006` plus MSM4 or MSM7 observations. `1006` is an
accepted rover input but is not part of this receiver's base-output list.
MSM7 replaces MSM4 for a constellation; do not transmit both families for the
same constellation.

Treat proprietary `4072.0` and `4072.1` reference or moving-base messages as
firmware-specific additions, not generic interoperable RTCM messages.

## Observation and station coherence

Send all constellation observations at the same rate and use one MSM class
across them. Mixing MSM4 and MSM7 can create an incorrect multiple-message
indication.

The station ID in `1005` or `1006` must equal the station ID in MSM messages.
Keep RTCM settings consistent across all enabled receiver ports.

For the documented firmware, transmit `1230` or its recognized `1033`
alternative to resolve GLONASS ambiguities. Without one, GLONASS can remain
float even while other parts of the solution report fixed.

Corrections expire after 60 seconds by default, and the timeout is
configurable. Monitor correction age instead of treating an open caster
connection as proof of usable RTK input.

## RTKBase relay stages

RTKBase uses a main RTKLIB `str2str` instance to read the receiver and expose a
local TCP stream. Separate service instances then relay or convert that stream
to NTRIP, TCP, serial, or files.

Check the receiver-facing main stream first, then walk each downstream service
in order. Receiver detection and caster connectivity do not establish precise
base coordinates; surveyed or fixed coordinates remain a separate input.

## Match profiles, roles, and firmware

The AgOpenGPS guide provides Config-O-Matic profiles for:

- a single-antenna role;
- a dual-heading role;
- a radio-base role.

Manual u-center configuration is the alternative. The documented workflow
uses `460800` baud and requires saving the applied configuration to receiver
memory.

Known-good documented pairings use HPG 1.32 for the single-receiver profile
and HPG 1.13 for the dual setup. The dual-heading profile has a warning under
1.32. These are profile-specific combinations, not a general rejection of
newer firmware. Match the named profile to the board role, receiver hardware,
and firmware.
