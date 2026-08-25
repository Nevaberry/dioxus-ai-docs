# Reference Clocks, PPS, and GPS

## Driver and sampling changes

### RTC reference clock

Chrony 4.7 adds an RTC refclock driver, allowing a hardware real-time clock to be configured as a reference clock.

### PHC interface names

A PHC refclock can be identified by a network-interface name instead of requiring a PHC device path. This is useful when interface identity is more stable or clearer than a `/dev/ptpN` mapping.

### Filtering and reachability

Since 4.7, a refclock no longer needs multiple samples in each poll. This simplifies filter configuration. A refclock also remains reachable when samples are discarded for excessive delay.

Since 4.8, a refclock sample is validated before it updates reachability. An invalid sample therefore no longer makes the refclock appear reachable. Do not interpret a set reach bit as proof that every later synchronization or selection test passed.

### External PPS on current kernels

The refclock `extpps` option works on Linux 6.15 and newer with chrony 4.8. External-PPS deployments can use those kernels without disabling the option.

## gpsd-backed SOCK reference clocks

For a serial GPS receiver with PPS, gpsd can combine the inputs and feed a chrony SOCK refclock:

```conf
refclock SOCK /var/run/chrony.ttyS0.sock
```

Start gpsd after `chronyd` has created the socket. Pass `-n` so gpsd polls the receiver without waiting for a client connection:

```sh
gpsd -n /dev/ttyS0
```

## Locking PPS to a single receiver

When one receiver supplies coarse NMEA time through gpsd SHM and precise pulses through `/dev/pps0`, lock the PPS refclock to the NMEA refid and mark PPS `trust`:

```conf
refclock SHM 0 refid NMEA offset 0.000 precision 1e-3 poll 0 filter 3
refclock PPS /dev/pps0 refid PPS lock NMEA poll 3 trust
```

The trusted PPS can remain selectable when the correlated but much less accurate NMEA source is marked as a falseticker. This avoids requiring a third source solely to keep the receiver's PPS usable.

## Preventing a one-second NMEA lock error

Serial NMEA messages can arrive 900–1000 milliseconds after their pulse and associate PPS with the wrong whole second. Enable measurement statistics:

```conf
log tracking measurements statistics
```

Measure the NMEA `Est offset`, then apply the opposite correction through the refclock `offset`. If necessary, raise the serial rate or suppress unnecessary NMEA sentences while retaining ZDA time messages.

## gpsd date-time socket compatibility

gpsd 3.25 adds `/run/chrony.clk.ttyX.sock`, which forwards date-time derived from serial GPS messages. The older `/run/chrony.ttyX.sock` carries PPS only.

Use the `.clk.` socket as a non-selected source for PPS locking:

```conf
refclock SOCK /run/chrony.clk.ttyAMA3.sock poll 3 offset 0.35 noselect refid UART
```

With an older gpsd that does not provide the date-time socket, use `SHM 0` for the coarse lock source.

## Alpine serial-PPS startup

On Alpine's serial `pps_ldisc` path, gpsd creates `/dev/pps0`. The default OpenRC ordering starts gpsd after chronyd, so a direct PPS refclock configured on `/dev/pps0` can be unavailable when chronyd starts.

Load the line-discipline module at boot:

```text
# /etc/modules
pps_ldisc
```

Also change service ordering so `/dev/pps0` exists before chronyd starts. This ordering issue applies when using the direct device instead of the gpsd-created chrony socket.

## High-rate PPS through a PHC

A PPS signal connected to a NIC pin can be timestamped by the same PHC used for NTP packets. This avoids interrupt delay and cancels cross-clock timestamp asymmetry.

```conf
refclock PHC /dev/ptp0:extpps:pin=0 dpoll -4 poll -2 rate 16 width 0.03125 refid GPS lock NMEA maxlockage 32
refclock SHM 0 refid NMEA noselect offset 0.120 poll 6 delay 0.010
hwtimestamp * minpoll -4
```

The option values have coupled meanings:

- `dpoll -4` reads the PHC 16 times per second.
- `poll -2` emits four median samples per second.
- `rate 16` declares a 16 Hz pulse rate.
- `width 0.03125` rejects falling edges at half the 16 Hz period.
- `maxlockage 32` lets 16 Hz PPS lock to a one-sample-per-second SHM source.

The non-selected SHM source supplies time of day for PPS locking. Measure its `offset` for the actual receiver path. A wrong value can shift time by an integer multiple of the 62.5 ms pulse period.

## PHCs synchronized by PTP

Configuring a PHC refclock does not turn chronyd into a PTP client. A separate service such as `ptp4l` must keep the NIC clock synchronized; otherwise the PHC can become a falseticker or degrade synchronization.

A PHC using the TAI time scale can be handled in three ways:

```conf
# Convert TAI using leap-second data:
leapsectz right/UTC
refclock PHC /dev/ptp2 tai

# Manually maintain the TAI-UTC offset:
refclock PHC /dev/ptp2 offset -37

# Or use only the sub-second phase:
refclock PHC /dev/ptp2 pps
```

## RTC failures and RTC-less boot

### `513 RTC driver not running`

This error requires checking all three prerequisites: an RTC device, kernel RTC support, and an `rtcfile` configuration. If `/dev/rtc` is busy, another process owns the device.

`Could not enable RTC interrupt: Invalid argument` indicates missing `RTC_UIE_ON`/`RTC_UIE_OFF` support. A kernel built with `CONFIG_RTC_INTF_DEV_UIE_EMUL` can provide the needed emulation.

### Boot without a usable RTC

Even with no RTC or backup battery, starting `chronyd` with `-s` sets the system clock from the drift file's modification time. Applications started afterward then see increasing time across reboots instead of a backward jump.
