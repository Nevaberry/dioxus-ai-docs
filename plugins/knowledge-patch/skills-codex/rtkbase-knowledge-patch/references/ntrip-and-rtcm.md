# NTRIP and RTCM Streaming

## RTKBase endpoint configuration

The shipped configuration contains two independent upstream NTRIP sections,
both defaulting to `caster.centipede.fr:2101`. It also has sections for:

- a credentialed local caster;
- RTCM TCP server and client;
- RTCM UDP server and client; and
- serial RTCM output.

Each endpoint has its own message selector and receiver-dependent options. The
default selector is:

```ini
rtcm_msg_a='1004,1005(10),1006,1008(10),1012,1019,1020,1033(10),1042,1045,1046,1077,1087,1097,1107,1127,1230'
```

For U-Blox receivers, add `-TADJ=1` to the applicable receiver-options field to
avoid non-rounded-second time tags in RTCM and NTRIP output.

## Direct RTCM push with RTKLIB

`str2str` can send a receiver's serial RTCM stream directly to a caster. In an
NTRIP Server output URI, put the source password after an empty username and put
the mount point in the path:

```bash
str2str \
  -in serial://ttyAMA2:57600:8:n:1:off \
  -out ntrips://:secret@caster.example:2101/BASE
```

## SNIP caster-table metadata

The RTKLIB NTRIP Server's caster-table string is optional. Do not include the
mount point in it because the connection request supplies the mount point
separately.

When explicitly supplying metadata, preserve every semicolon-delimited field. An
incorrect field count makes SNIP publish a `Raw`/`Unknown` fallback entry. For an
RTCM3 stream, SNIP can infer base location and message types from roughly the
first 120 seconds of traffic, so blank metadata is better than malformed metadata.

A usable metadata string, after the separately configured mount point, is:

```text
City;RTCM 3.1;;2;GPS+GLO;SNIP;USA;34.00;-117.00;0;0;sNTRIP;None;B;N;0;
```

## VRS GGA requirements

A VRS mount point normally withholds corrections until it receives an approximate
rover position in NMEA GGA. If GGA is enabled on the receiver, `-b 1` relays the
serial data back to the NTRIP input while the output sends received corrections
to the receiver:

```bash
str2str \
  -in ntrip://username:password@caster.example:2101/VRS \
  -b 1 \
  -out serial://ttyACM0:115200:8:n:1
```

Specify the complete serial settings to avoid a baud mismatch.

Instead of relaying receiver GGA, `-p <lat> <lon> <height> -n 1` supplies a fixed
position and a GGA request cycle. Appending `#1000` to the serial output path
exposes the receiver's relayed stream on TCP port 1000 for another RTKLIB process.
