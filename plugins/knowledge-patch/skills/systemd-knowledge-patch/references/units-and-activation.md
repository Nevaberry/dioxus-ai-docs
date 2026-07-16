# Units and Activation

## Express mount and condition dependencies

- `WantsMountsFor=` adds non-fatal mount dependencies for paths (since 256).
- In fstab, `x-systemd.wants=` adds a soft `Wants=` dependency, complementing `x-systemd.requires=` (since 257).
- `x-systemd.graceful-option=` includes a mount option only when the running kernel supports it, allowing optional settings such as tmpfs `usrquota` without failing older kernels (since 258).
- `ConditionVersion=` supersedes `ConditionKernelVersion=` and tests kernel, systemd, or glibc versions. `ConditionKernelModuleLoaded=` tests whether a module is loaded or built in (since 258).

## Pass socket and activation descriptors

- `PassFileDescriptorsToExec=yes` exposes a socket's listening descriptors through `LISTEN_FDS` to `ExecStartPost=`, `ExecStopPre=`, and `ExecStopPost=` (since 256).
- For `Accept=yes` AF_UNIX sockets, `MaxConnectionsPerSource=` limits simultaneous connections by peer UID (since 256).
- `FileDescriptorName=` is honored for `Accept=yes` instead of being replaced with `connection`. `SocketUser=` and `SocketGroup=` apply to POSIX message queues (since 257).
- Socket units support Multipath TCP. AF_UNIX per-connection services receive `REMOTE_ADDR` (since 257).
- Transient services receive arbitrary activation descriptors through the `ExtraFileDescriptor=` D-Bus property (since 257).
- `sd_notify()` can change a unit's main process using a pidfd or pidfd inode number rather than a numeric PID (since 257).
- AF_UNIX socket units support `PassPIDFD=` for `SO_PASSPIDFD` and `AcceptFileDescriptors=` for `SO_PASSRIGHTS` (since 258).
- The activation protocol's `LISTEN_PIDFDID` contains the pidfd inode ID corresponding to `LISTEN_PID`, allowing a consumer to reject PID-recycling races (since 259).

## Defer activation and timer work

- `RestartMode=debug` sets `DEBUG_INVOCATION=1` and temporarily raises `LogLevelMax=` only during an automatic restart attempt (since 257).

```ini
[Service]
Restart=on-failure
RestartMode=debug
```
- `DeferReactivation=yes` on a calendar timer discards an expiration that happened while the activated service was still running, instead of immediately retriggering on completion (since 257).
- `RandomizedOffsetSec=` adds a stable randomized offset to a timer schedule rather than fresh jitter at every activation (since 258).
- A socket's `DeferTrigger=` and `DeferTriggerMaxSec=` use lenient job mode and retry a transaction that would otherwise stop an active unit (since 258).

## Execute commands and transient services

- A leading `|` on an `Exec*=` directive invokes the command through a shell (since 258).
- `systemd-run --scope` expands command-line environment references by default (since 258).
- `systemd-run --root-directory=` selects a root tree. `systemd-run --same-root-dir` or `-R` reuses the caller's root (since 259).
- A transient service can receive its root through the `RootDirectoryFileDescriptor` property instead of `RootDirectory=` (since 259).

```ini
[Service]
ExecStart=|echo "$HOME"
```

## Reload services and attached content

- `ExecReloadPost=` runs after the configured service reload completes (since 259).
- Reloading a service also reloads its associated configuration-extension images (since 258).
- `RefreshOnReload=` controls whether reload refreshes attached extensions and credentials (since 260).
- `BindNetworkInterface=` binds every socket created for the service to a named interface or VRF (since 260).

## Build reliable generators and readiness handoff

- Generators receive `SYSTEMD_SOFT_REBOOTS_COUNT`, the number of soft reboots since the current kernel boot (since 257).
- Initrd system services have their own preset scope, disabled by default unlike host presets (since 258).
- `systemd-notify --fork` launches a child, waits for its `READY=1`, then exits while leaving the ready child running, enabling shell scripts to hand off readiness correctly (since 258).
- `systemctl start --verbose` and related verbs stream startup logs until the operation finishes (since 258).

## Manage native units

- SysV service loading and rc.local compatibility are gone; use native units. `getty@.service` must be explicitly enabled (since 260).
- `systemctl enqueue-marked` is the dedicated command for marked jobs. `Markers=` supports `needs-start` and `needs-stop` (since 260).
