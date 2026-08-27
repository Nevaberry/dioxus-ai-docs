# RTCM Base Streams and RTKBase

## Coherent ZED-F9P stationary-base output

For the documented default-constellation ZED-F9P stationary base pairing, use:

```text
1005                  # reference ARP; may run slower
1074 1084 1094 1124   # GPS, GLONASS, Galileo, BeiDou MSM4
1230                  # GLONASS code-phase biases
```

A rover needs `1005` or `1006` plus MSM4 or MSM7 observations. `1006` is
accepted as rover input but does not appear in the receiver's documented base
output list. When selecting MSM7, replace MSM4 for a constellation rather than
emitting both.

Treat proprietary `4072.0` and `4072.1` reference or moving-base messages as
firmware-specific additions, not generic interoperable RTCM messages.

## Coherence and freshness

Send every constellation's observations at the same rate and use the same MSM
class. Mixing MSM4 and MSM7 can set an incorrect multiple-message indication.
The station ID in `1005` or `1006` must match the station ID in the MSM messages,
and RTCM configuration must remain consistent across enabled receiver ports.

The documented firmware needs `1230` or its recognized `1033` alternative to
resolve GLONASS ambiguities. Without it, GLONASS can remain float while other
parts of the solution report fixed.

Corrections expire after 60 seconds by default, with a configurable timeout.
Monitor correction age; an open caster connection is not proof of usable RTK
input.

## RTKBase relay diagnosis

RTKBase runs a main RTKLIB `str2str` process that reads the receiver and exposes
a local TCP stream. Separate service instances relay or convert that stream to
NTRIP, TCP, serial, or files.

Inspect the receiver-facing main stream first, then follow each downstream hop
in order. Receiver detection and caster connectivity do not establish precise
base coordinates; surveyed or fixed-coordinate input is a separate concern.

## Receiver roles, profiles, and firmware

The AgOpenGPS guide supplies Config-O-Matic profiles for single-antenna,
dual-heading, and radio-base roles, with manual u-center setup as an alternative.
Its workflow uses `460800` baud and requires saving the applied configuration to
receiver memory.

Documented known-good combinations are HPG 1.32 for the single-receiver profile
and HPG 1.13 for the dual setup, with a dual-heading warning under 1.32. These
are profile-specific combinations, not a general rejection of newer firmware.
Match board role, receiver hardware, named firmware, and profile together.

