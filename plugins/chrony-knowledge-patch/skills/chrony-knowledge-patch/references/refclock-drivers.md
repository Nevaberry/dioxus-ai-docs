# Refclock Drivers (4.7)

## RTC Refclock Driver

New refclock driver that uses the Real Time Clock as a time source. Useful for systems without network connectivity where the hardware RTC is the only time reference.

**Cannot be combined with `rtcfile` or `rtcsync`.** If migrating from RTC tracking to the refclock driver, remove the old directives.

Supports the `utc` option for clocks that keep UTC rather than local time.

```
refclock RTC /dev/rtc0
refclock RTC /dev/rtc0:utc
```

## PHC Refclock — Network Interface Name

The PHC (PTP Hardware Clock) driver parameter can now accept a network interface name instead of the `/dev/ptpN` device path. This eliminates the need to discover the PTP device number for a given NIC.

```
# By interface name (new in 4.7)
refclock PHC eth0 poll 0 dpoll -2

# With extpps and pin options
refclock PHC enp3s0:extpps:pin=0 width 0.2 poll 2

# Traditional device path still works
refclock PHC /dev/ptp0 poll 0 dpoll -2
```

The interface name is resolved to the corresponding `/dev/ptpN` device at startup. All existing PHC options (poll, dpoll, width, extpps, pin, etc.) work with both interface names and device paths.
