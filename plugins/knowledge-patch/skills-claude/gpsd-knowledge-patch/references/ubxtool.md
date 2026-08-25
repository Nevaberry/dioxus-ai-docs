# ubxtool

### Protocol version is part of command selection
`ubxtool` must be told the receiver's actual UBX protocol version with `-P`; its default is version 10, and a wrong value can make newer receivers fail silently or behave oddly. Poll `MON-VER` first and put the result in `UBXOPTS`, which is processed before command-line options.

```sh
ubxtool -p MON-VER
export UBXOPTS="-P 27 -v 2"  # replace 27 with the reported PROTVER
```

### Daemon, device, file, and capture modes
By default the tool uses the local GPSD, while `-f` opens a regular file read-only or a character device read/write unless `-r` is also set; direct serial access requires pyserial and device permission, but normal daemon use needs neither root nor `sudo`. `-s` selects the host-side serial speed, `-S` changes the receiver's speed, `-R` records received raw serial data, and `-w 0` keeps reading indefinitely.

```sh
ubxtool -r -f ublox-neo-m8n.log
ubxtool -S 230400 -f /dev/ttyAMA0
ubxtool -R receiver.ubx -w 0
```

### Raw commands, presets, and discoverability
`-c` takes comma-separated hexadecimal class, ID, and payload bytes and adds the UBX header, length, and checksum; `-p` sends a named poll or preset, multiple presets can be queued, and `-e`/`-d` expose a smaller set of canned feature switches. Verbose help level 2 lists every preset and switch, while level 3 additionally dumps the configuration-item database.

```sh
ubxtool -p MON-VER -p CFG-GNSS -w 4 -v 2
ubxtool -h -v 3
```

### Reset ordering and unreliable acknowledgements
`-p RESET` may leave flash-backed configuration intact; after a reset, enable binary output before disabling NMEA so the receiver never goes silent, and enable informational messages when rejection details are needed. A NAK proves the request was invalid, but an ACK does not prove it took effect and some valid requests produce no ACK, so always poll or read back the changed setting.

```sh
ubxtool -p RESET
ubxtool -e BINARY
ubxtool -d NMEA
ubxtool -e INFMSG
```

### Traditional versus configuration-item generations
Pre-Gen9 receivers use compound `UBX-CFG-*` messages, Gen9 straddles both schemes with firmware-dependent and undocumented differences, and Gen10 onward uses configuration items only. The item interface requires protocol version 27 or later and avoids overwriting unrelated fields in a compound configuration message.

### Configuration-item layers and deletion
`-g ITEM,LAYER` uses layer indexes 0 RAM, 1 BBR, 2 flash, and 7 firmware default, whereas the optional layer operand to `-z`/`-x` is a bitmap with bits 1 RAM, 2 BBR, and 4 flash; use explicit masks when persistence matters. Deleting a BBR/flash override restores its default for a future load but does not alter the live RAM value, and a NAK while reading BBR or flash can simply mean that no override exists there.

```sh
ubxtool -g CFG-NAVSPG-DYNMODEL,0
ubxtool -z CFG-NAVSPG-DYNMODEL,6,7
ubxtool -x CFG-NAVSPG-DYNMODEL,6
```

### Group reads and paginated configuration dumps
An item-group prefix such as `CFG-TP` retrieves the group's keys, and `-g ITEM,LAYER,POSITION,END` can walk large results that the receiver returns 64 pairs at a time; omitting the layer asks for RAM, BBR, flash, and default. A `CFG` group dump also reveals keys unknown to `ubxtool`, while `-h -v 3` lists the names it can decode.

```sh
ubxtool -g CFG-TP,0
ubxtool -g CFG,0,0,1200 | fgrep 'item CFG-'
```

### Message rates became explicitly port-specific
On older receivers, `CFG-MSG,class,id[,rate]` polls all six port rates or sets the current port; newer receivers require a `CFG-MSGOUT-*_<port>` item, and `ubxtool` cannot discover the receiver-side current port or poll all ports at once. Choose the key matching the physical interface, such as `_USB`, `_UART1`, or `_SPI`, and use verbosity 2 when the output being tested is NMEA.

```sh
ubxtool -p CFG-MSG,1,6,2
ubxtool -g CFG-MSGOUT-UBX_NAV_TIMELS_USB,0
ubxtool -z CFG-MSGOUT-UBX_NAV_TIMELS_USB,1,7
```

### Dynamic platform and navigation-rate controls
The dynamic platform model changes the receiver's motion filtering, so the usual portable default can be unsuitable in a car or aircraft and supported model numbers must be checked against the exact firmware. Measurement rate is expressed in milliseconds and navigation rate in measurement cycles; not every receiver supports rates above 1 Hz.

```sh
# Compound-message receivers
ubxtool -p CFG-NAV5
ubxtool -p MODEL,4
ubxtool -p CFG-RATE,100

# Configuration-item receivers
ubxtool -z CFG-NAVSPG-DYNMODEL,4,7
ubxtool -z CFG-RATE-MEAS,100,7 -z CFG-RATE-NAV,1,7
```

### Persistence differs by generation and hardware
The live configuration is in RAM and disappears on power loss, reset, load, or replacement; legacy `-p SAVE` tries BBR, flash, EEPROM, and SPI flash, but `UBX-CFG-CFG` is deprecated from protocol 23.01 and newer receivers should write explicit configuration-item layers. `MON-VER` showing `EXT CORE` establishes that firmware was loaded from flash, while `ROM CORE` means no firmware flash; other storage types generally have to be tested directly.

```sh
ubxtool -p SAVE
ubxtool -g CFG-NAVSPG-DYNMODEL,1
ubxtool -g CFG-NAVSPG-DYNMODEL,2
```

### Receiver-resident flash logging
UBX logging needs protocol 15 or later plus external SQI flash with a valid Flash Information Structure; `LOG-INFO` returning no response means unsupported, while a zero `filestoreCapacity` means firmware support without usable storage. The destructive setup is erase, create, enable, then later disable and retrieve; erase and recreate the log before enabling it for another run.

```sh
ubxtool -p LOG-INFO
ubxtool -p LOG-ERASE
ubxtool -p LOG-CREATE
ubxtool -e LOG
ubxtool -p LOG-INFO -v 2
ubxtool -d LOG
ubxtool -p LOG-RETRIEVE -v 2
```

### RAM batching
Batching stores fixes in receiver RAM rather than flash and requires a Gen8, Gen9, or Gen10 receiver at protocol 23.01 or later with batching memory; Gen20 does not support it. Probe with `MON-BATCH`, use the legacy switch on Gen8 or `CFG-BATCH` configuration items on Gen9/10, and retrieve accumulated fixes through `LOG-RETRIEVEBATCH`.

```sh
ubxtool -p MON-BATCH
ubxtool -e BATCH
ubxtool -p LOG-RETRIEVEBATCH -v 2
ubxtool -d BATCH
```

### Survey-in and fixed-base mode
Timing and high-precision products expose survey state through `TIM-SVIN` or `NAV-SVIN`; `active 1` means convergence is in progress, `valid 1` means it completed, and an over-strict accuracy limit may prevent completion forever. Legacy-capable firmware uses `SURVEYIN`/`SURVEYIN3`, while configuration-item firmware sets the minimum duration, accuracy limit, and `CFG-TMODE-MODE=1`; the calculated position must be read from the SVIN report rather than polled from `CFG-TMODE-LAT_HP`.

```sh
ubxtool -p NAV-SVIN -P 27
ubxtool -e SURVEYIN3,60,200000 -P 27
ubxtool -p NAV-SVIN -P 27
ubxtool -d SURVEYIN3

ubxtool -z CFG-TMODE-SVIN_MIN_DUR,30
ubxtool -z CFG-TMODE-SVIN_ACC_LIMIT,1000000
ubxtool -z CFG-TMODE-MODE,1
ubxtool -z CFG-TMODE-MODE,0
```

### RTCM3 correction output
Some protocol-20-or-later timing and high-precision receivers can act as bases and emit RTCM3, but none emit RTCM2; the documented `RTCM3` preset targets the USB port of compatible Gen9 devices and enables a very high-volume set of messages. Disable it again before ordinary interactive work.

```sh
ubxtool -e RTCM3 -P 27 -v 2
ubxtool -d RTCM3 -P 27 -v 2
```

### Constellation and signal constraints
Older receivers expose capabilities and simultaneous-constellation limits through `MON-GNSS` and detailed enablement through `CFG-GNSS`; if a receiver permits only two constellations, disable one before enabling another because an illegal third choice may not be reported reliably. Later firmware drops those interfaces in favor of the per-constellation and per-band `CFG-SIGNAL` group, and some models require a saved configuration plus cold boot after a valid change.

```sh
ubxtool -p MON-GNSS -p CFG-GNSS -v 2
ubxtool -g CFG-SIGNAL,0
ubxtool -z CFG-SIGNAL-BDS_B2_ENA,1,7
```

### ADR/UDR inertial and high-rate output
ADR/UDR firmware at protocol 19.20 or later adds `UBX-ESF-*` and `UBX-HNR-*`; the legacy ESF/HNR presets omit the flood-volume `ESF-MEAS` and `ESF-RAW` streams, whose `timeTag` can jump backward and whose `sTtag` uses a separate timebase. Gen9 cannot reliably use those presets because the required port discovery disappeared, so configure the desired `CFG-MSGOUT-*_<port>` item instead.

```sh
ubxtool -P 19 -p CFG-MSG,0x10,2,1
ubxtool -P 19 -p CFG-MSG,0x10,3,1
ubxtool -P 27 -z CFG-MSGOUT-UBX_ESF_MEAS_USB,15,7
```

### Timepulse syntax changed with configuration items
Legacy `CFG-TP5` controls pulse period or frequency, unlocked/locked pulse length or duty cycle, polarity, and delays; periods and lengths are microseconds, while duty cycle in frequency form is a fraction of `2^32-1`, and `-e PPS`/`-d PPS` are shortcuts differing only in the enable flag. New-style receivers do not use `CFG-TP5`, so inspect and set the `CFG-TP` group instead.

```sh
# 1 Hz/100 ms unlocked, 4 Hz/25 ms locked, on TIMEPULSE 0
ubxtool -p CFG-TP5,0,,,1000000,250000,100000,25000,,0x77

ubxtool -g CFG-TP,7
ubxtool -z CFG-TP-PERIOD_TP1,1000000,7 \
  -z CFG-TP-LEN_TP1,100000,7 \
  -z CFG-TP-TP1_ENA,1,7
```

### MON-SPAN antenna spectrum scans
Gen9/Gen10 receivers around protocol 27 add `MON-SPAN`, which turns the receiver into a simple spectrum analyzer for checking whether an antenna passes the enabled GNSS bands; enable every signal band under test before scanning. It works through GPSD, or directly when GPSD is stopped, and verbosity 3 exposes the numeric scan data for plotting.

```sh
ubxtool -p MON-SPAN -P 27 -v 3 |
  grep -E '^     1[[:digit:]]{9}, [[:digit:]]{1,3}' > ant.dat
```

