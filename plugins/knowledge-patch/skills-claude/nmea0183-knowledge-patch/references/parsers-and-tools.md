# Parsers and Tools

Use this reference when selecting a parser, handling invalid or null navigation data, filtering mixed streams, or building the Hazer toolchain.

## Contents

- [Rust nmea0183 0.6.0](#rust-nmea0183-060)
- [Hazer C parser](#hazer-c-parser)
- [gpstool stream processing](#gpstool-stream-processing)
- [Building Hazer locally](#building-hazer-locally)

## Rust `nmea0183` 0.6.0

### Streaming API

The crate is heap-free and depends only on `core`, so it can parse an unframed byte stream on embedded targets.

`parse_from_byte` returns `None` until a complete sentence is available, then returns `Some(Result<ParseResult, &str>)`. `parse_from_bytes` accepts a chunk or log and returns an iterator of results.

```rust
use nmea0183::{ParseResult, Parser};

let mut parser = Parser::new();
for result in parser.parse_from_bytes(b"$GPGGA,,,,,,,,,,,,,,*56\r\n") {
    match result {
        Ok(ParseResult::GGA(Some(fix))) => { /* valid fix */ }
        Ok(ParseResult::GGA(None)) => { /* receiver has no solution */ }
        Ok(_) => {}
        Err(message) => { /* checksum, source, type, or format error */ }
    }
}
```

### Null navigation data

A successfully framed sentence whose navigation data is null or invalid returns the matching `ParseResult` variant containing `None`. Treat this as a working receiver without a solution, not as malformed input.

### Errors and recovery

Documented error strings are:

```text
Unsupported sentence type.
Checksum error!
Source is not supported!
NMEA format error!
```

Rarer protocol errors may return other strings. Errors are `&str`, not typed variants. The parser survives errors without reinitialization; a format error discards accumulated data and resumes searching for a new sentence.

### Filters and sentence length

Builder filters accept bitwise sentence and source masks. The Galileo source variant is spelled `Source::Gallileo` in this API.

With the `strict` feature active, `MAX_SENTENCE_LENGTH` is 79 characters. Disabling `strict` permits sentences up to 120 characters.

```rust
use nmea0183::{Parser, Sentence, Source};

let gps_fixes = Parser::new()
    .source_only(Source::GPS)
    .sentence_filter(Sentence::RMC | Sentence::GGA);
let gps_or_galileo = Parser::new()
    .source_filter(Source::GPS | Source::Gallileo);
```

### Advertised coverage

The public API lists structures for `GGA`, `GLL`, `GSA`, `GSV`, `RMC`, `VTG`, and `ZDA`. The same 0.6.0 landing page still describes GSA and GSV parsing as planned. Do not infer decoder support merely from the presence of a structure.

## Hazer C parser

### Project scope and sentence coverage

Hazer is the C NMEA stack in a repository that also provides Yodel for UBX, Tumbleweed for RTCM, and Calico for Garmin CPO.

Its NMEA decoder processes `GGA`, `GLL`, `GSA`, `GSV`, `RMC`, `TXT`, `VTG`, and `ZDA`, plus u-blox `PUBX,00`, `PUBX,03`, and `PUBX,04`. `PAIR`, `PGRM`, `PMTK`, `PSRF`, and other `PUBX` sentences are recognized and logged rather than decoded.

### Talkers and constellation identity

Hazer recognizes observed talkers `GA`, `GB`, `GI`, `GL`, `GN`, `GP`, and `GQ`. `BD` and `QZ` are implemented but only unit-tested.

For GSA constellation identity, prefer the NMEA 4.10 System ID because satellite identifiers can overlap. Hazer falls back to identifier ranges for older receivers.

### Results and errno

Parsing functions return a nonnegative value when input is valid and the supplied position/navigation/time structures were updated.

On a negative return:

- `errno == 0`: the sentence is valid but reports no valid solution; structures remain unchanged.
- `EINVAL`: invalid field character.
- `EIO`: checksum/CRC or other end-matter error.
- `ENODATA`: insufficient length or too few fields.
- `ENOMSG`: invalid start matter or identifiers.
- `ERANGE`: out-of-range value.

Distinguish the zero-`errno` no-solution case from rejection.

### Stream resynchronization

`gpstool` reports `Sync Start` after an NMEA, UBX, or RTCM state machine validates a complete frame, including its checksum or CRC.

- `Sync Lost`: the next frame has no recognized start; restart all three state machines.
- `Sync Stop`: all three state machines gave up; restart them.
- `-z`: terminate the process on `Sync Stop` instead of continuing.

## `gpstool` stream processing

### Input and output routing

Consume input from standard input, a serial-like device with `-D`, a file or FIFO with `-S`, or a local UDP port with `-G :PORT`.

Route output independently:

- `-C`: catenate raw input;
- `-Q`: write validated frames only;
- `-L`: create a pretty listing;
- `-R`, `-E`, or `-H`: produce reports; and
- `-T`: record a PVT trace.

```text
gpstool -S capture.nmea -R -Q validated.nmea -T trace.csv
```

Datagram, device-sink, and validation-queue masks use `NMEA=1`, `UBX=2`, `RTCM=4`, and `CPO=8`; `15` is the default all-formats mask.

`-W STRING` collapses a command, appends NMEA end matter, and writes it to the configured device.

### Trace selection

The `-T` CSV trace records one PVT solution per second by default. It prefers:

1. u-blox `UBX-NAV-HPPOSLLH`;
2. an ensemble solution;
3. GPS;
4. GLONASS;
5. Galileo; then
6. BeiDou.

Unavailable fields are serialized as `0.` instead of empty fields. Do not interpret them as measured zero without consulting fix and source fields.

## Building Hazer locally

Build without installing:

```text
make pristine
make depend
make all
```

`gpstool` requires the separately built Diminuto project; `libhazer` itself does not.

If artifacts remain in the build tree, source `out/host/bin/setup` to add binaries and shared libraries to `PATH` and `LD_LIBRARY_PATH`.
