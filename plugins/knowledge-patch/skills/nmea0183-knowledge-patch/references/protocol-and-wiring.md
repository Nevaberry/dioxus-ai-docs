# Protocol and Wiring

Use this reference when wiring devices, selecting adapters, configuring serial ports, validating frames, or bridging marine networks.

## Differential electrical contract

NMEA 0183 v2.x and later use an EIA-422-A differential `A`/`B` pair. A conforming listener:

- is optically isolated;
- recognizes a 2.0 V differential signal while drawing no more than 2.0 mA; and
- tolerates the legacy +/-15 V range.

Use shielded twisted-pair cable and bond the shield only to the talker chassis.

At idle (`STOP`, logical 1), `A` is negative with respect to `B`; with no load, typical values are 0 V on `A` and 5 V on `B`. The `START`/logical-0 state reverses that polarity. `A`/`B` may instead be labeled `Data+`/`Data-`, but connector assignments and wire colors are not standardized. Follow the device pinout.

## Legacy single-ended interoperability

Version 1.x talkers are RS-232-like single-ended outputs with one data wire referenced to ground and signaling as high as +/-15 V. Some devices emit v2-format sentences from a 5 V single-ended output, so neither sentence syntax nor product labeling establishes electrical compliance.

For the common direct connection cases:

```text
differential talker -> single-ended listener: A/+ -> Data In; Ground -> Ground; leave B/- open
single-ended talker -> differential listener: Data Out -> A/+; Ground -> B/-
```

Never connect a conventional differential talker's driven `B/-` output to ground. Doing so can overload or damage the driver.

## Talkers, listeners, buffers, and multiplexers

An NMEA 0183 pair has one continuously driving talker and may feed multiple listeners. Do not place two talkers on one pair: their unsynchronized outputs contend.

- Use a multiplexer to combine several talkers into one output stream.
- Use a buffer to fan one talker out as separately isolated outputs when its driver cannot supply every listener.

## Serial modes and character range

The normal asynchronous link is `4800 8N1`. NMEA 0183 v3 added `38400 8N1` as NMEA 0183-HS for higher-volume ARPA and AIS traffic. Some equipment also supports 115200 baud for PC-oriented high-rate use. Configure both endpoints identically.

Sentence data uses printable ASCII `0x20` through `0x7e`, with the high data bit clear.

## Delimiters, termination, and checksums

Sentences start with `$` or `!` and end with CRLF. Version 2.0 and later require a two-hex-digit checksum; it was optional in version 1.5.

Calculate the checksum as the 8-bit XOR of every byte, including commas, between but excluding the opening delimiter and `*`:

```text
$yyXXX,fields*HH\r\n
HH = XOR(bytes after '$' and before '*')
```

For `!` sentences, apply the same rule after `!`. Preserve empty fields and their delimiting commas because each comma participates in both field position and checksum calculation.

## Isolated computer connections

A direct NMEA-to-PC serial connection may appear to work while exposing the computer to induced voltage spikes and destructive ground-loop current. Use an optically isolated NMEA-to-RS-232/RS-422 adapter or an isolated NMEA-to-USB gateway. A TTL-level USB serial cable is not an electrical substitute.

## Protocol gateways

NMEA 0183-HS remains the same serial protocol at a higher bit rate. It is unrelated to NMEA 2000's 250 kbps CAN network and binary PGNs. Do not mix the wires.

Use a gateway that maps sentences to PGNs and vice versa. A multiplexer or electrical adapter alone does not perform protocol conversion. Older NMEA 0180 and 0182 links are likewise transmission-incompatible with NMEA 0183.
