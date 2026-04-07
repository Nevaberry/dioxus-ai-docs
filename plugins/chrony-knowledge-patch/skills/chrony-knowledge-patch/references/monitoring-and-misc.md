# Monitoring & Miscellaneous

## opencommands Directive (4.7)

Controls which chronyc monitoring commands are accessible to remote hosts allowed by `cmdallow`. Without this directive, remote monitoring requires authenticated (NTS or key-based) access.

```
cmdallow 192.168.0.0/16
opencommands sources sourcestats tracking activity
```

Available commands for `opencommands`:

`activity`, `authdata`, `clients`, `manual`, `ntpdata`, `rtcdata`, `selectdata`, `serverstats`, `smoothing`, `sourcename`, `sources`, `sourcestats`, `tracking`

Only listed commands are accessible without authentication. All other chronyc commands still require authentication for remote access.

## driftfile interval Option (4.7)

Controls the minimum interval (in seconds) between driftfile updates. Default is 3600 (1 hour). Useful for flash-based storage to reduce write cycles.

```
driftfile /var/lib/chrony/drift interval 300
```

Lower values update the drift file more frequently, which helps preserve drift accuracy across reboots but increases storage writes.

## ptpdomain Directive (4.6)

Sets the PTP domain number for NTP-over-PTP messages. Default is 123.

```
ptpdomain 123
```

NTP-over-PTP encapsulates NTP packets within PTP event messages, enabling hardware timestamping on network hardware that supports PTP but not NTP.

## KoD on ratelimit (4.6)

The `kod` option on the `ratelimit` directive enables Kiss-o'-Death RATE responses for rate-limited NTP clients. KoD packets signal the client to reduce its polling rate.

```
ratelimit interval 1 burst 4 kod
```

Without `kod`, rate-limited requests are silently dropped. With `kod`, clients receive a KoD RATE packet telling them to back off.

## chronyc -u Option (4.8)

Drops root privileges in chronyc. The unprivileged user is set at compile time. Useful for security-hardened environments where chronyc should not retain elevated privileges.

```bash
chronyc -u sources
chronyc -u tracking
```
