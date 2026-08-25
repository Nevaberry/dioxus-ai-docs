# Monitoring and Profiling Tools

### cgps display modes and live controls
`cgps -i` replaces the fix and satellite panes with IMU data, `-l d|m|s` selects decimal degrees, degrees and decimal minutes, or degrees/minutes/seconds, `-s` hides raw daemon data, and `-m` displays calculated magnetic rather than true track. Invoke it as the ordinary user rather than through `sudo`, which the manual warns loses functionality.

While it is running, `d` changes coordinate format, `i`/`m`/`n` select imperial, metric, or nautical units, `s` toggles raw JSON, `t` toggles true/magnetic track, `c` clears the lower window, and `q` exits.

### gpsmon is a packet monitor, not a navigation decoder
`gpsmon` displays receiver packets with only enough decoding for diagnostic checks; it does not use the daemon's normalized decoding and does not interpolate climb, model errors, or reject altitude solely because fix quality is low. It may therefore show data differently from `cgps`, and it does not cover every raw packet type understood by the daemon.

Apart from device wakeups, it sends no probe or control strings unless explicitly commanded. It can synchronize to a binary packet stream, but a binary-capable receiver emitting extended NMEA may remain identified as generic NMEA until a type is forced or probing is enabled.

### gpsmon daemon and direct modes
An argument containing slashes but no colons selects direct serial access; this mode hunts for the baud rate but does not probe the device subtype automatically. In daemon mode, `-n` requests NMEA0183 rather than the raw stream, while `-t TYPE` supplies a uniquely prefixed fallback driver for mode, speed, and rate controls when the packet-selected driver lacks them.

```sh
gpsmon /dev/ttyUSB0
gpsmon -n localhost:2947:/dev/ttyUSB0
```

### gpsmon direct-control grammar
In direct mode, `i1` enables subtype probes and reselects the driver, while `i0` disables them; probing can switch a SiRF receiver into binary mode. Other controls are `cSECONDS` for cycle time, `n0`/`n1` for NMEA/native mode, `sBPS[:FRAMING]` for host and receiver serial settings, and `tTYPE` to force a uniquely matching monitor driver.

The `xHEX` command treats the bytes as a payload and adds driver-specific framing, trailers, and checksums; uppercase `XHEX` writes the bytes unchanged. Serial changes can wedge USB or Bluetooth receivers whose adapters and receiver UARTs do not change framing or speed together, potentially requiring a power cycle.

### gpsmon logging and PPS limitations
`gpsmon -l FILE` begins packet logging immediately on device open, allowing receiver startup and firmware banners to be captured; interactive `lFILE` toggles append-mode logging of complete packets. `-L` lists built-in monitor types and their generic controls, but omits type-specific commands.

The PPS Offset display is useful only in direct mode: in daemon-client mode it never updates even when PPS events appear in the packet window. `Ctrl-S` and `Ctrl-Q` freeze and resume the display without stopping collection.

### SiRF-specific gpsmon views
Only the SiRF monitor has additional chipset commands: in direct mode, `A` toggles 50-bps subframe reporting, and `P` switches between the normal display and selected MID 19 navigation parameters. The NMEA and u-blox monitors have no type-specific commands beyond whichever generic controls their drivers advertise.

### gpsprof skyview and timing plots
Besides its spatial scatterplot, `gpsprof -f polar` maps reported SNR by azimuth and elevation; `polarused` and `polarunused` restrict that view to satellites used or rejected for fixes. The `time` formatter plots system-clock minus GPS time from PPS reports, while `instrumented` and `uninstrumented` expose decomposed and total fix-delivery latency.

```sh
gpsprof -f polar | gnuplot -p
```

### Instrumented latency boundaries
The instrumented plot separates GPS-time-to-start-of-reporting-cycle fix latency, calculated serial transmission time, daemon analysis time (`EORC - SORC - serial time`), and daemon-to-client reception time. Detecting the start from an inter-cycle quiet gap requires a device running at 9,600 bps or faster; initial serial buffering can also create spuriously large startup latencies.

The uninstrumented plot is a distortion check rather than a breakdown. It plots only reports containing fixes, so intervening no-fix reports can appear as staircase artifacts.

### Reusing gpsprof captures
`--dumpfile FILE` writes plot data without the generated gnuplot program, whereas `--logfile FILE` saves the collected raw JSON. `--redo` reads such JSON from standard input, ignores collection-duration and logfile options, and permits several plots to be generated from one observation run.

```sh
gpsprof -f polar --logfile sky.json | gnuplot -p
gpsprof -f polarused --redo < sky.json | gnuplot -p
gpsprof -f polarunused --redo < sky.json | gnuplot -p
```

### Profiling progress signal
The first number in `gpsprof`'s startup message is its process ID. Sending that process `SIGUSR1` makes it write a completion message to standard error and continue processing.

