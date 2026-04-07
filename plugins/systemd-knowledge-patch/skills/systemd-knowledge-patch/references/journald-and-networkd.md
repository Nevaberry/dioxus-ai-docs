# journald & networkd Changes

## journalctl Invocation Tracking (v257)

List and filter journal entries by service invocations, analogous to `--list-boots`/`--boot` for system boots:

```bash
# List all invocations of a service
journalctl --list-invocations -u myservice

# Show logs from the 2nd-to-last invocation
journalctl -I 2 -u myservice

# Show logs from the most recent invocation
journalctl -I 1 -u myservice
```

Each invocation corresponds to one start-stop cycle of the service. This is useful for debugging services that restart frequently -- inspect logs from a specific run without noise from other invocations.

## journald ForwardToSocket= (v256)

Forward journal entries to a remote socket in Journal Export Format. Enables centralized log collection without additional log shippers:

```ini
# /etc/systemd/journald.conf
[Journal]
ForwardToSocket=tcp:192.168.1.100:5555
MaxLevelSocket=info
```

Supports `tcp:` and `udp:` prefixes. The receiving end must parse Journal Export Format.

## systemd-networkd MobileNetwork Section (v260)

New `[MobileNetwork]` section in `.network` files for ModemManager integration. Configures cellular/mobile broadband connections:

```ini
# /etc/systemd/network/50-mobile.network
[Match]
Type=wwan

[MobileNetwork]
APN=internet
AllowRoaming=no
IPFamily=both
```

### Available Settings

| Setting | Values | Purpose |
|---------|--------|---------|
| `APN=` | string | Access Point Name for the carrier |
| `AllowRoaming=` | `yes`/`no` | Allow data roaming |
| `IPFamily=` | `ipv4`/`ipv6`/`both` | IP protocol family to use |
