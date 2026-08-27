# NMEA and Application Protocol Boundaries

## Active sentence dispatch

AgIO 6.8.5 actively dispatches the `GP` and `GN` talker forms of GGA, VTG, and
HDT, plus these proprietary inputs:

- `$PAOGI`
- `$PANDA`
- `$KSXT`
- `$GPHPD`
- `$GNTRA` and `$GPTRA`
- `$PSTI` subtypes 032, 035, and 036
- `$PTNL` AVR

The RMC parser is not reachable from the active dispatch path. An RMC-only
receiver stream is therefore insufficient even though RMC parsing code exists.

## Checksum exception

Ordinary sentences are accepted only when the computed NMEA XOR checksum
matches. In 6.8.5, input beginning with `$KS` can pass when the expected
checksum-length test fails. This is pinned compatibility behavior. Do not copy
it into a general NMEA parser or infer that every consumed sentence received
identical checksum validation.

## Distinct transport classes

After parsing, AgIO packages its current navigation values for AgOpenGPS and,
optionally, network modules in binary AgOpenGPS framing whose PGN byte is
`0xD6`.

```text
receiver -> ASCII NMEA/proprietary sentences -> AgIO
caster   -> binary RTCM corrections          -> receiver
AgIO     -> binary AgOpenGPS PGN 0xD6         -> application/modules
```

The `0xD6` frame is neither ASCII NMEA nor an SAE J1939 PGN. Bridges and traffic
monitors must preserve the distinction between receiver navigation sentences,
caster corrections, and application/module frames.

