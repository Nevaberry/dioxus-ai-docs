# NMEA and Application Framing

## Active AgIO dispatch

AgIO 6.8.5 actively dispatches both `GP` and `GN` forms of GGA, VTG, and HDT.
It also dispatches:

- `$PAOGI` and `$PANDA`;
- `$KSXT`;
- `$GPHPD`;
- `$GNTRA` and `$GPTRA`;
- `$PSTI` subtypes 032, 035, and 036;
- `$PTNL` AVR.

RMC parser code exists, but it is not reachable from the active dispatch path.
An RMC-only receiver stream is therefore insufficient. Configure the receiver
for a sentence set the active dispatcher actually consumes.

## Release-specific `$KS` checksum behavior

Normally, a sentence is accepted only when its computed NMEA XOR checksum
matches. In 6.8.5, input beginning with `$KS` can pass when the expected
checksum-length test fails.

Treat this as pinned application compatibility behavior. Do not reproduce it
in a general NMEA parser, and do not infer that every consumed sentence passed
the same validation path.

## Binary application boundary

After parsing, AgIO sends its current navigation values to AgOpenGPS and,
optionally, network modules in binary AgOpenGPS framing with PGN byte `0xD6`.
This is not ASCII NMEA and not an SAE J1939 PGN.

Keep the three data classes explicit in bridges and monitors:

```text
receiver -> ASCII NMEA/proprietary sentences -> AgIO
caster   -> binary RTCM corrections          -> receiver
AgIO     -> binary AgOpenGPS PGN 0xD6         -> application/modules
```

Log and decode each segment using its own framing rules. A valid sentence at
the receiver input does not by itself prove that the corresponding `0xD6`
application frame reached its destination.
