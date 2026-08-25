# Machine and Rate Control

## Machine-board firmware identity

The official classic machine-board path uses an Arduino Nano over Ethernet or
USB. Its primary sketch is `ArduinoModules/UDP/Machine_UDP_v5` on the moving
`Boards` main branch.

`Machine_UDP_v5` is a source path, not a firmware release. “Machine v5” does not
pin subsequent sketch or Ethernet-library changes. Record board wiring and
revision plus the exact source commit.

## Custom machine PGNs

The documented machine-control set is:

```text
239  normal machine/section data
238  machine configuration
236  relay configuration
235  machine/tool dimensions
229  extended control: 64-bit section state and tool speeds
228  rate-control exchange
```

Use a protocol document matched to both application and controller firmware for
framing, offsets, byte order, scaling, and checksum. Application support for 64
equal sections does not imply that a controller has 64 physical outputs.

## Rate-controller board families

Board families are not interchangeable:

- Nano `RC12-3` provides one or two rate channels, an ENC28J60 Ethernet shield,
  an onboard Cytron interface, external relay-module connectivity, and work and
  pressure switch inputs. It is a through-hole design.
- Teensy 4.1 `RC11-2` provides two rates, eight sections, eight 12 V SPDT relay
  outputs, filtered pressure input, two optically isolated pulse inputs, a work
  switch, CAN, and 3.3 V I2C/Qwiic expansion.
- ESP32 `RC15` provides two rates, 7-14 section outputs, reversible motor
  drivers, four 5 V analog inputs or two differential inputs, two optically
  isolated pulse inputs, RS-485, and 3.3 V I2C. W5500 Ethernet is optional.

These hardware trees receive firmware from `SK21/AOG_RC`. Preserve a compatible
firmware commit with the PCB revision. Never reuse RC11, RC12, or RC15 pin
meanings or configuration constants across families.

## Output ownership and ISOBUS

ISOBUS Task Controller and relay boards are alternative output owners. When the
Task Controller owns section control, diagnose its process-data exchange, CAN
adapter, implement object and process data, and logs rather than treating it as
an Arduino relay path.

A zero-section state can deliberately indicate that no implement is connected.
Never enable two physical control paths to command the same outputs.

