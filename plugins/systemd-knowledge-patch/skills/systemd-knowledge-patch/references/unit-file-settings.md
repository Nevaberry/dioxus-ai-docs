# New Unit File Settings (v255--v260)

## Sandboxing & Namespaces

### PrivatePIDs= (v257)

Run processes as PID 1 in their own PID namespace with isolated `/proc/`:

```ini
[Service]
PrivatePIDs=yes
```

### ProtectControlGroups= Extended (v257)

New values beyond the existing boolean:

- `private` -- creates a new cgroup namespace
- `strict` -- creates cgroup namespace and mounts cgroupfs read-only

```ini
[Service]
ProtectControlGroups=strict
```

### PrivateUsers= New Modes

- `identity` (v257) -- identity-maps the first 65536 UIDs/GIDs in a user namespace
- `managed` (v260) -- auto-assigns a dynamic transient 65K range via `systemd-nsresourced`

```ini
[Service]
PrivateUsers=identity
```

### PrivateTmp=disconnected (v257)

Uses a separate tmpfs for `/tmp/` and `/var/tmp/` that is not shared with other services using `PrivateTmp=yes` (the default shared private tmp).

```ini
[Service]
PrivateTmp=disconnected
```

### StateDirectory= Read-Only Suffix (v257)

Append `:ro` to make managed directories read-only:

```ini
[Service]
StateDirectory=myapp:ro
```

Works with `RuntimeDirectory=`, `CacheDirectory=`, `LogsDirectory=`, and `ConfigurationDirectory=` as well.

## Service Lifecycle

### RestartMode=debug (v257)

On failure, restart the service with `$DEBUG_INVOCATION=1` environment variable and `LogLevelMax=debug`. Useful for automatic diagnostic collection on first failure:

```ini
[Service]
RestartMode=debug
Restart=on-failure
```

### SurviveFinalKillSignal= (v255)

Skip the unit during shutdown's final SIGTERM/SIGKILL sweep. Required for services that must survive soft-reboot:

```ini
[Service]
SurviveFinalKillSignal=yes
```

### RefreshOnReload= (v260)

Refresh extensions and credentials when a service is reloaded (via `systemctl reload`):

```ini
[Service]
RefreshOnReload=yes
```

## Resource Control

### BindNetworkInterface= (v260)

Bind all sockets created by the unit to a specific network interface. Useful for VRF or multi-homed setups:

```ini
[Service]
BindNetworkInterface=eth0
```

### MemoryTHP= (v260)

Per-service Transparent Huge Pages control:

```ini
[Service]
MemoryTHP=always    # or: madvise, never, inherit
```

### CPUSchedulingPolicy=ext (v260)

Enable the SCHED_EXT (extensible scheduler) scheduling policy:

```ini
[Service]
CPUSchedulingPolicy=ext
```

## Timer Settings

### DeferReactivation= (v257)

For calendar-based timers, skip immediate reactivation if the triggered service is still running from the previous invocation:

```ini
[Timer]
OnCalendar=hourly
DeferReactivation=yes
```

## Socket Settings

### PassFileDescriptorsToExec= (v256)

Pass socket file descriptors to `ExecStartPost=`, `ExecStopPre=`, and `ExecStopPost=` commands via the `$LISTEN_FDS` mechanism:

```ini
[Socket]
PassFileDescriptorsToExec=yes
```

## Unit Dependencies

### WantsMountsFor= (v256)

Like `RequiresMountsFor=` but creates `Wants=` dependencies instead of `Requires=`:

```ini
[Unit]
WantsMountsFor=/data/myapp
```

## fstab Options

### x-systemd.wants= (v257)

Creates `Wants=` dependencies from fstab entries (like the existing `x-systemd.requires=`):

```
/dev/sda1  /data  ext4  defaults,x-systemd.wants=backup.service  0 2
```
