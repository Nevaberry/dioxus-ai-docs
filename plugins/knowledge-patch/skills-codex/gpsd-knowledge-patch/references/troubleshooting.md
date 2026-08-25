# Troubleshooting

### Localizing a udev hotplug failure
Trace hotplug across its boundaries: confirm the USB add/remove in `lsusb` and kernel logs, then look for `gpsd.hotplug` invocation, and finally for the daemon receiving the add over its control socket. A packaged installation can be isolated with a foreground daemon and a manual handler call; if the handler runs but the daemon sees no add, check that both use the same control-socket path.

```sh
gpsd -N -n -F /run/gpsd.sock -D 5
cd /lib/udev
./gpsd.hotplug add /dev/ttyUSB0
```

### Systemd socket activation owns the daemon lifecycle
Stopping `gpsd.service` alone is insufficient because `gpsd.socket` can activate it again; stop both units for a temporary shutdown. For isolated manual debugging on a packaged Debian system that reactivates them, disable both as well and reboot before launching the foreground daemon.

```sh
systemctl stop gpsd.socket gpsd.service
systemctl disable gpsd.socket gpsd.service
```

### Always-on systemd service
Debian-family packages normally let a client connection activate GPSD through `gpsd.socket`; a time-service host that must poll before any client connects can install an always-on service using the packaged environment and `-n` in `GPSD_OPTIONS`. After creating the unit, run `systemctl daemon-reload` and `systemctl reenable gpsd.service`.

```systemd
[Unit]
Requires=gpsd.socket
After=chronyd.service

[Service]
EnvironmentFile=-/etc/default/gpsd
EnvironmentFile=-/etc/sysconfig/gpsd
ExecStart=/usr/sbin/gpsd -N $GPSD_OPTIONS $DEVICES

[Install]
WantedBy=multi-user.target
Also=gpsd.socket
```

### Remote access with a systemd-owned socket
`-G` makes GPSD accept non-loopback clients, but it is not enough when systemd owns the listening sockets: set `GPSD_OPTIONS="-Gn"`, use `systemctl edit --full gpsd.socket` to replace the loopback TCP listener, open port 2947 in the firewall, and restart both units.

```systemd
[Socket]
ListenStream=/run/gpsd.sock
ListenStream=0.0.0.0:2947
SocketMode=0600
```

### USB-serial hotplug false positives
Because USB has no GPS or generic USB-to-serial device class, the hotplug rules match known bridge-chip vendor/product IDs and may stash a modem or microcontroller path as a possible GPS. GPSD delays device configuration until it recognizes a sensor and uses exclusive-open checks, but a losing process can still hit an open race; disable GPSD hotplug and start it with the GPS path explicitly if that conflict matters.

### Minimal reproducible receiver captures
Capture untouched receiver data with `gpscat` or raw `gpspipe`, replay it through `gpsfake`, repeatedly halve the log to the smallest reproducer, and use `gpsfake -l` to identify the triggering sentence or packet. For decoder crashes, verify that the minimized input also fails under `gpsdecode`; useful annotated logs prefix only `#` header lines and identify the receiver, chipset/firmware, date, and location.

```sh
gpspipe -R -n 100 > receiver.log
```

### Distinguishing receiver clock-lag signatures
A fixed leap-second-sized lag present immediately after startup usually means the receiver forgot its leap-second correction; wait up to about 20 minutes for the almanac update. SiRF binary timestamps that start correct and progressively fall behind instead indicate that a full report flood cannot clear a 4800-baud link before the next epoch, so raise it to at least 9600 baud.

### SiRF static-navigation control
For a SiRF receiver whose reported speed fluctuates while stationary, the interactive `M` command in `gpsmon` enables static-navigation mode. It freezes the solution after three seconds below 1.2 m/s and resumes updates above 1.4 m/s.

### Stable device paths across suspend
During suspend/resume, Linux can recreate a still-open USB serial receiver under a different `/dev/ttyUSBn`, leaving GPSD attached to the old descriptor. Define a udev-managed stable symlink keyed to that receiver and give the symlink, rather than the enumerated tty name, to GPSD.

