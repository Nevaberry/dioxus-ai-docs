# Time Service

### Minimal time-service build profile
`timeservice=yes` is a constrained SCons profile: it forces nowait operation, requires PPS support at configure time, and builds `cgps` and `ntpshmmon` unless all clients are disabled. Most receiver drivers are omitted while NMEA remains mandatory, so enable the required binary protocol explicitly.

```sh
scons -c
scons timeservice=yes ublox=yes
```

### Linux kernel PPS prerequisites
Kernel-timestamped serial PPS needs the RFC 2783 core and line-discipline client; a GPIO pulse additionally needs the GPIO client and sysfs GPIO support. Built-in (`y`) and modular (`m`) configurations both work, and `pps-tools` supplies the associated user-space tools and `timepps.h`.

```text
CONFIG_PPS=y
CONFIG_PPS_CLIENT_LDISC=y
CONFIG_PPS_CLIENT_GPIO=y
CONFIG_GPIO_SYSFS=y
```

### PPS wiring and diagnostics
GPSD accepts a serial pulse on either Carrier Detect or Ring Indicator, so the cable must carry handshake lines rather than only TXD, RXD, and ground. Confirm `PPS` markers and the PPS offset in `gpsmon`, fall back to `ppscheck`, and use debug level 5 to distinguish missing privileges (`KPPS cannot set PPS line discipline`) from a driver without the required wait ioctl (`PPS ioctl(TIOCMIWAIT) failed`).

```sh
gpsmon /dev/ttyS0
ppscheck
gpsd -D 5 /dev/ttyS0
```

### Pulse and report epoch ordering
GPSD assumes a receiver asserts PPS for an epoch before sending that epoch's time sentences, with the sentence burst ending before the next pulse. A receiver that reverses this order appears to report future time and needs a negative fudge; very long 4800-baud bursts can also spill into the following epoch.

### NTP SHM privilege boundary
NTP units 0 and 1 are private segments (mode `0600`), whereas units 2 and above are normally public (`0666`); GPSD therefore normally attaches NTP0/NTP1 when privileged and NTP2/NTP3 otherwise. A public unit lets any local user inject clock samples, so the GPSD privilege level, refclock unit numbers, and local threat model must agree.

The System V keys are `0x4e545030 + unit`; inspect attachment and ownership with `ipcs -m` or `/proc/sysvipc/shm` when a refclock has zero reach.

### NTPsec and classic ntpd SHM configuration
NTPsec can name the SHM driver and unit directly; classic ntpd selects the same units through pseudo-addresses `127.127.28.<unit>`. Keep the coarse serial clock available for epoch information or monitoring and prefer the PPS clock when it is present.

```text
# NTPsec
refclock shm unit 0 refid GPS
refclock shm unit 1 prefer refid PPS

# Classic ntpd
server 127.127.28.0 noselect
fudge 127.127.28.0 refid GPS
server 127.127.28.1 prefer
fudge 127.127.28.1 refid PPS
```

### Chrony socket and SHM consumption
For SOCK transport, chronyd must start before GPSD creates or connects to the receiver-specific sockets; GPSD tries its run directory first and `/tmp` as a fallback. SHM is an alternative, but chronyd does not obtain PPS precision from the SHM structure, so the PPS source needs an explicit `precision 1e-7`.

```text
refclock SHM 0 refid GPS precision 1e-1 delay 0.2 noselect
refclock SHM 1 refid PPS precision 1e-7
```

### In-band offset calibration
The frequently shown `offset 0.9999` or `time1 0.9999` is only a bring-up placeholder and must not be deployed as a calibration. With chrony, monitor the coarse source unselected for at least four hours, read its stable offset from `chronyc sourcestats`, then configure that measured value; with ntpd, a positive observed offset means reducing `time1` by that amount.

```text
refclock SHM 0 poll 8 filter 1000 noselect
```

```sh
chronyc sourcestats
```

### Native NTPsec GPSD refclock
NTPsec's `gpsd` driver connects to the local daemon over its JSON protocol, watches the selected receiver, and consumes `VERSION`, `WATCH`, `TPV`, `PPS`, and `TOFF`; protocol 3.10 or later supplies `TOFF`, whose absence worsens in-band jitter and offset. A failed connection is retried after 10 seconds with exponential backoff up to about 10 minutes, and `path` overrides the receiver selected by the unit's default device name.

```text
refclock gpsd mode 1 path /dev/ttyS0
```

### Native driver operating modes
For the native NTPsec driver, `mode 0` uses in-band time only, `mode 1` is strict and emits samples only from a valid PPS-plus-in-band pair, and experimental `mode 2` falls back to in-band-only after 120 seconds without valid combined samples and returns to strict mode after 40 seconds of stable PPS. Switching in mode 2 changes offset and jitter, so it is suitable only when continued coarse synchronization is preferable to losing the refclock.

### NTPsec PPS tandem units
Native GPSD units 128 and above are PPS-only secondaries for primary unit `unit % 128`; the primary remains required because it owns transport and decoding. A secondary accepts PPS only after the host is synchronized and both system and phase offsets are within 400 ms; its PPS calibration is its own `time1`, and `flag1` should advertise it as a PPS peer only when the pulse is trustworthy.

```text
server gpsd unit 0 minpoll 4 maxpoll 4 noselect
server gpsd unit 128 minpoll 4 maxpoll 4
```

### Inspecting exported samples
`ntpshmmon` can run alongside the time daemon without consuming its samples. It needs root to see private NTP0/NTP1, an ordinary user normally sees only public units, `-o` reports `Clock - Real` instead of collection time, and `-n` or `-t` bounds a capture by count or seconds.

```sh
sudo ntpshmmon -o -n 20
```

### Deliberate GPS-only NTPsec service
NTPsec normally requires three sane sources before serving time, so a truly offline single-GPS deployment needs an explicit quorum reduction. This removes source-consensus protection and is discouraged when fallback servers are available.

```text
tos minclock 1 minsane 1
```

### Coexisting with PTP SHM producers
When `ptp4l` or `phc2sys` exports through `ntpshm`, allocate a unit that GPSD is not using; on a privileged GPSD master, NTP2 is the usual next unit after GPS and PPS. Configure the time daemon to consume that same unit, or the producers will overwrite one another's samples.

```text
[global]
clock_servo ntpshm
ntpshm_segment 2
```

