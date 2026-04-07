---
name: systemd-knowledge-patch
description: "systemd changes since training cutoff (latest: v260) -- cgroup v2 only, SysV removal, PrivatePIDs=, BindNetworkInterface=, journalctl invocations, networkd MobileNetwork. Load before writing systemd unit files, journalctl commands, or networkd configs."
license: MIT
version: "1.0.0"
metadata:
  author: Nevaberry
---

# systemd Knowledge Patch (v255--v260)

Claude knows systemd unit files, journalctl, systemctl, and basic service management through systemd 254. This skill covers systemd v255 (December 2023) through v260 (February 2026).

## Index

| Topic | Reference | Key features |
|-------|-----------|--------------|
| Breaking Changes | [references/breaking-changes.md](references/breaking-changes.md) | cgroup v1 removed, SysV init removed, journal default persistent, IPForward deprecated, uaccess rules |
| Unit File Settings | [references/unit-file-settings.md](references/unit-file-settings.md) | PrivatePIDs, ProtectControlGroups, BindNetworkInterface, MemoryTHP, RestartMode=debug, DeferReactivation |
| journald & networkd | [references/journald-and-networkd.md](references/journald-and-networkd.md) | Invocation tracking, ForwardToSocket, MobileNetwork section |

## Breaking Changes at a Glance

| Change | Version | Impact |
|--------|---------|--------|
| cgroup v1 removed | v258 | Only cgroup v2 (unified hierarchy) supported |
| SysV init scripts removed | v260 | `systemd-sysv-generator`, `rc-local.service` gone; native units required |
| `!!` ExecStart prefix removed | v258 | Ambient capabilities compat prefix silently ignored |
| Journal default `persistent` | v259 | Was `auto`; override with `Storage=` in `journald.conf` |
| `IPForward=` deprecated | v256 | Use `IPv4Forwarding=`/`IPv6Forwarding=` in `.network` or `networkd.conf` |
| uaccess tag requires `ACTION!="remove"` | v258 | Rules using `ACTION=="add"` no longer work |
| TTY default mode 0600 | v258 | `mesg n` is default; restore with `-Dtty-mode=0620` |
| `KeepConfiguration=dynamic` | v257 | Replaces `dhcp`; preserves DHCPv4/v6, NDISC, IPv4LL |

### IPForward= Migration (v256)

Replace `IPForward=` in `.network` files with explicit per-family settings:

```ini
# Old (.network file):
[Network]
IPForward=yes

# New (.network file -- per-link):
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

Or set globally in `networkd.conf`:

```ini
# /etc/systemd/networkd.conf
[Network]
IPv4Forwarding=yes
IPv6Forwarding=yes
```

Note: `IPv6SendRA=` and `IPMasquerade=` now imply per-link forwarding, not global sysctl.

### uaccess udev Rules Fix (v258)

Rules using `ACTION=="add"` for the `uaccess` tag silently stopped working:

```
# Broken since v258:
ACTION=="add", SUBSYSTEM=="hidraw", TAG+="uaccess"
# Correct:
ACTION!="remove", SUBSYSTEM=="hidraw", TAG+="uaccess"
```

See [references/breaking-changes.md](references/breaking-changes.md) for all breaking changes.

## Quick Reference -- Essential New Settings

### PrivatePIDs= (v257)

Run processes as PID 1 in their own PID namespace with isolated `/proc/`:

```ini
[Service]
PrivatePIDs=yes
```

### BindNetworkInterface= (v260)

Bind all sockets created by the unit to a specific interface (useful for VRF):

```ini
[Service]
BindNetworkInterface=eth0
```

### ProtectControlGroups= extended (v257)

`private` creates a new cgroup namespace; `strict` also mounts cgroupfs read-only:

```ini
[Service]
ProtectControlGroups=strict
```

### RestartMode=debug (v257)

On failure, restart with `$DEBUG_INVOCATION=1` and `LogLevelMax=debug`:

```ini
[Service]
RestartMode=debug
Restart=on-failure
```

### DeferReactivation= (v257)

For calendar timers, skip immediate reactivation if the service is still running:

```ini
[Timer]
OnCalendar=hourly
DeferReactivation=yes
```

### StateDirectory= read-only suffix (v257)

Make managed directories read-only with `:ro` suffix:

```ini
[Service]
StateDirectory=myapp:ro
```

### PrivateUsers= new modes (v257/v260)

- `identity` (v257) -- identity-maps the first 65536 UIDs/GIDs in a user namespace
- `managed` (v260) -- auto-assigns a dynamic transient 65K range via `systemd-nsresourced`

### MemoryTHP= (v260)

Per-service Transparent Huge Pages control:

```ini
[Service]
MemoryTHP=always
```

### SurviveFinalKillSignal= (v255)

Skip the unit during shutdown's final SIGTERM/SIGKILL. Required for soft-reboot survival:

```ini
[Service]
SurviveFinalKillSignal=yes
```

### PassFileDescriptorsToExec= (v256)

Pass socket FDs to `ExecStartPost=`/`ExecStopPre=`/`ExecStopPost=` via `$LISTEN_FDS`:

```ini
[Socket]
PassFileDescriptorsToExec=yes
```

See [references/unit-file-settings.md](references/unit-file-settings.md) for the full list including CPUSchedulingPolicy=ext, PrivateTmp=disconnected, WantsMountsFor=, RefreshOnReload=, and fstab options.

## journalctl Invocation Tracking (v257)

List and filter by service invocations (analogous to `--list-boots`/`--boot`):

```bash
journalctl --list-invocations -u myservice    # list all invocations
journalctl -I 2 -u myservice                  # 2nd-to-last invocation
```

## journald ForwardToSocket= (v256)

Forward journal entries to a remote socket in Journal Export Format:

```ini
[Journal]
ForwardToSocket=tcp:192.168.1.100:5555
MaxLevelSocket=info
```

## networkd MobileNetwork Section (v260)

ModemManager integration for cellular connections in `.network` files:

```ini
# /etc/systemd/network/50-mobile.network
[Match]
Type=wwan

[MobileNetwork]
APN=internet
AllowRoaming=no
IPFamily=both
```

| Setting | Values | Purpose |
|---------|--------|---------|
| `APN=` | string | Access Point Name for the carrier |
| `AllowRoaming=` | `yes`/`no` | Allow data roaming |
| `IPFamily=` | `ipv4`/`ipv6`/`both` | IP protocol family |

## New Settings Summary

| Setting | Version | Section | Purpose |
|---------|---------|---------|---------|
| `PrivatePIDs=` | v257 | `[Service]` | PID namespace isolation |
| `ProtectControlGroups=private\|strict` | v257 | `[Service]` | cgroup namespace / read-only cgroupfs |
| `StateDirectory=…:ro` | v257 | `[Service]` | Read-only managed directories |
| `DeferReactivation=` | v257 | `[Timer]` | Skip reactivation if service running |
| `RestartMode=debug` | v257 | `[Service]` | Debug restart with verbose logging |
| `BindNetworkInterface=` | v260 | `[Service]` | Bind sockets to interface |
| `MemoryTHP=` | v260 | `[Service]` | Per-service THP control |
| `CPUSchedulingPolicy=ext` | v260 | `[Service]` | SCHED_EXT scheduler |
| `PassFileDescriptorsToExec=` | v256 | `[Socket]` | Pass FDs to Exec*Post/Pre |
| `PrivateUsers=identity` | v257 | `[Service]` | Identity-mapped user namespace |
| `PrivateUsers=managed` | v260 | `[Service]` | Auto-assigned UID/GID range |
| `PrivateTmp=disconnected` | v257 | `[Service]` | Separate tmpfs (not shared) |
| `WantsMountsFor=` | v256 | `[Unit]` | Wants= for mount dependencies |
| `SurviveFinalKillSignal=` | v255 | `[Service]` | Survive shutdown kill |
| `RefreshOnReload=` | v260 | `[Service]` | Refresh extensions/credentials on reload |
| `x-systemd.wants=` | v257 | fstab | Wants= dependency from fstab |
