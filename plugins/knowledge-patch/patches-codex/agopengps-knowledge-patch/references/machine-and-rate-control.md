# Machine and Rate Control

## Pin classic machine firmware by source

The official classic machine-board path uses an Arduino Nano over Ethernet or
USB. Its primary sketch is:

```text
ArduinoModules/UDP/Machine_UDP_v5
```

That is a source path on the moving `Boards` main branch, not a firmware
release. “Machine v5” does not pin later sketch or Ethernet-library changes.
Record the board wiring and revision plus the exact source commit.

## Machine-specific custom PGNs

The documented message set assigns:

```text
239  normal machine and section data
238  machine configuration
236  relay configuration
235  machine and tool dimensions
229  extended control: 64-bit section state and tool speeds
228  rate-control exchange
```

Use a protocol document matched to the application and controller firmware for
framing, offsets, byte order, scaling, and checksum. Support for 64 equal
sections in the application does not mean a controller has 64 physical
outputs.

## Rate-controller families

The board families are not pin-compatible or configuration-compatible.

### Nano `RC12-3`

- one or two rate channels;
- ENC28J60 Ethernet shield;
- on-board Cytron interface;
- external relay-module connectivity;
- work and pressure-switch inputs;
- through-hole construction.

### Teensy 4.1 `RC11-2`

- two rates and eight sections;
- eight 12 V SPDT relay outputs;
- filtered pressure input;
- two optically isolated pulse inputs;
- work switch and CAN;
- 3.3 V I2C/Qwiic expansion.

### ESP32 `RC15`

- two rates and 7-14 section outputs;
- reversible motor drivers;
- four 5 V analog inputs or two differential inputs;
- two optically isolated pulse inputs;
- RS-485 and 3.3 V I2C;
- optional W5500 Ethernet.

These hardware trees obtain firmware from `SK21/AOG_RC`. Preserve a compatible
firmware commit with the PCB revision. Never reuse RC11, RC12, or RC15 pin
meanings or configuration constants across families.

## Select one output owner

ISOBUS and relay boards are alternative owners of physical outputs. When the
Task Controller owns section control, diagnose its process-data exchange, CAN
adapter, implement object and process data, and logs. Do not treat it as an
Arduino relay path.

A zero-section state can intentionally mean no implement is connected. Never
enable two physical control paths to command the same outputs.
