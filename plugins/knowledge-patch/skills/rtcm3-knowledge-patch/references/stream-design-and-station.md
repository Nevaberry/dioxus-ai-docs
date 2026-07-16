# Stream design and station messages

## Separate legacy and MSM streams

An RTK base stream needs at least one observation message and station or antenna information. Do not combine legacy observations (`1001`–`1004`, `1009`–`1012`) with MSM observations in one stream: the mixture can cause remote-rover problems. Serve separate streams when supporting both populations.

## Reach-to-Reach profile

For a Reach base and Reach rover, use station coordinates at a low rate, MSM4 observations every second for each supported constellation, and GLONASS code-phase biases. Type 1006 is mandatory, and at least GPS MSM4 type 1074 must remain enabled.

```text
1006  0.1 Hz  antenna-reference-point station coordinates
1074  1 Hz    GPS MSM4
1084  1 Hz    GLONASS MSM4
1094  1 Hz    Galileo MSM4
1124  1 Hz    BeiDou MSM4
1230  1 Hz    GLONASS code-phase biases
```

## Reach profile for legacy third-party rovers

For a legacy third-party receiver, use extended GPS and GLONASS observations at 1 Hz and antenna/receiver identification at 0.1 Hz. This is a different observation profile from the Reach-to-Reach MSM4 stream.

```text
1004  1 Hz    extended L1/L2 GPS observables
1008  0.1 Hz  antenna descriptor and serial number
1012  1 Hz    extended L1/L2 GLONASS observables
1033  0.1 Hz  receiver and antenna descriptors
```

## Legacy observation variants

The less common legacy variants form parallel GPS and GLONASS families. An extended variant adds C/N0.

```text
GPS      1001 L1 basic | 1002 L1 extended | 1003 L1/L2 basic
GLONASS  1009 L1 basic | 1010 L1 extended | 1011 L1/L2 basic
```

Types 1001, 1003, 1009, and 1011 are generally unsupported. Types 1002 and 1010 are mainly useful on bandwidth-limited, L1-only links. The commonly deployed extended L1/L2 variants are 1004 and 1012.

## Coordinates, offsets, and descriptors

Type 1005 carries the ECEF position of the antenna reference point, not its phase center, and its datum field is undefined. Type 1006 adds antenna height. Type 1032 identifies the physical reference-station antenna position.

On OEM7, select antenna phase-center offsets with `THISANTENNAPCO` or `THISANTENNATYPE`. Otherwise, 1005 and 1006 carry the position passed to `FIX`. OEM7 always writes zero to the 1006 antenna-height field.

```text
thisantennatype NOV702
fix position 51.1136 -114.0435 1059.4
log com2 rtcm1006 ontime 10
```

Type 1033 carries receiver type and firmware version as well as antenna information. A rover can use it to select phase-bias calibration and improve GLONASS ambiguity fixing. OEM7 fills 1033 automatically and recommends sending 1006 plus 1033. Its type 1008 antenna-serial field is always null.

## Type 1013 stream catalog

Type 1013 predates Ntrip and carries the transmitted message-type/rate table plus the current leap-second count, though few devices send it. In an Ntrip caster-table entry, `1004(1),1005(10)` advertises type 1004 every second and type 1005 every ten seconds. Parenthesized rates are optional.

## Ephemeris scheduling

Broadcast-orbit types are `1019` GPS, `1020` GLONASS, `1042` BeiDou, `1044` QZSS, `1045` Galileo F/NAV, and `1046` Galileo I/NAV. Ordinary RTK usually receives ephemerides from satellites, so these messages are optional. A separate ephemeris stream, often named `RTCM3EPH`, can reduce startup time.

On OEM7, scheduling a non-`ASYNC` ephemeris log `ONTIME` emits one satellite per interval and cycles numerically. Scheduling the corresponding `ASYNC` log `ONCHANGED` emits new or changed ephemerides as soon as they are available.

```text
log rtcm1019 ontime 10
log rtcm1019async onchanged
```

## Receiver-dependent type 1230

GLONASS code-phase-bias type 1230 is not universally required. u-blox F9P and Topcon AGI-4 rovers have operated without it, and one NovAtel base could not emit it. On constrained links, omit it only for receiver combinations known to interpret the biases as zero; otherwise retain it for interoperability.
