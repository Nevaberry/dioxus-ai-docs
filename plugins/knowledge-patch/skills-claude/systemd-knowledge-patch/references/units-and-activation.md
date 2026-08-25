# Units and Activation

## Compatibility and command behavior

### Getty enablement (260)

`getty@.service` has an `[Install]` section and must be explicitly enabled:

```sh
systemctl enable --now getty@tty1.service
```

### Stricter `systemd-run` combinations (258.10-261.2)

The affected point releases reject `--no-block` and `--ignore-failure` in
scope mode. JSON output is incompatible with stdio forwarding, trigger units,
scope mode, or verbose logs; waiting is rejected for remain-after-exit
services. Trigger units honor `--no-block` and accept explicit trigger names.

### Oneshot exit tracking (258.10-261.2)

`Type=oneshot` rejects `ExitType=cgroup`; use the default `ExitType=main` or a
service type compatible with cgroup tracking.

## Mount and root dependencies

### Soft mount dependencies (256, 257)

Use `WantsMountsFor=` for non-fatal unit-to-mount dependencies. In fstab,
`x-systemd.wants=` creates a non-fatal `Wants=` relationship and complements
`x-systemd.requires=`.

### Mount credentials and graceful kernel options (258)

Mount units accept `SetCredential=`, `LoadCredential=`, `ImportCredential=`,
and related settings. `x-systemd.graceful-option=` passes an option only when
the running kernel supports it, such as optional tmpfs `usrquota`.

## Commands, conditions, and transactions

### Scope expansion and shell execution (258)

`systemd-run --scope` expands command-line environment references by default.
A leading `|` on `ExecStart=` or another `Exec*=` directive invokes a shell;
without it, shell syntax is not interpreted.

### Conditions and fleet hostnames (258)

Question marks in `/etc/hostname` are deterministically replaced by nibbles
derived from the machine ID, so `web-????????` is stable per machine.
`ConditionVersion=` supersedes `ConditionKernelVersion=` and tests kernel,
systemd, or glibc versions; `ConditionKernelModuleLoaded=` accepts loaded or
built-in modules.

### Marked jobs and transaction diagnostics (259, 260)

Activation transactions have logged 64-bit IDs, and ordering cycles appear in
the `TransactionsWithOrderingCycle` D-Bus property. Use
`systemctl enqueue-marked`; `systemctl --marked` is deprecated. `Markers=` now
accepts `needs-start` and `needs-stop`.

### Select or inherit a root tree (259)

`systemd-run --root-directory=` runs a transient service in a named root.
`systemd-run --same-root-dir`/`-R` reuses the caller's root; `run0` supports
the same reuse option.

## Timers and restart behavior

### Debug retries and deferred reactivation (257)

`RestartMode=debug` sets `DEBUG_INVOCATION=1` and temporarily raises
`LogLevelMax=` for an automatic retry. `DeferReactivation=yes` discards a
calendar expiration that occurred while the activated service was still
running.

### Stable spreading (258)

`RandomizedOffsetSec=` adds a stable randomized offset to a timer schedule,
instead of selecting fresh jitter for each activation.

## Socket and descriptor activation

### Lifecycle-hook descriptors (256)

`PassFileDescriptorsToExec=yes` exposes listening descriptors through
`LISTEN_FDS` to `ExecStartPost=`, `ExecStopPre=`, and `ExecStopPost=`. For
`Accept=yes` UNIX sockets, `MaxConnectionsPerSource=` limits peers by UID.

### Socket metadata and transports (257)

`FileDescriptorName=` is preserved for `Accept=yes` sockets, and
`SocketUser=`/`SocketGroup=` apply to POSIX message queues. Socket units may
select MPTCP with `SocketProtocol=mptcp`; AF_UNIX per-connection services
receive the peer in `REMOTE_ADDR`.

### Deferred activation and descriptor policy (258)

AF_UNIX socket units accept `PassPIDFD=` (`SO_PASSPIDFD`) and
`AcceptFileDescriptors=` (`SO_PASSRIGHTS`). `DeferTrigger=` and
`DeferTriggerMaxSec=` submit lenient jobs and retry transactions that would
otherwise stop an active unit.

### Race-free identity and handoff (257, 259)

Transient services receive arbitrary activation fds through the
`ExtraFileDescriptor=` D-Bus property, and `sd_notify()` can assign the main
process with a pidfd or pidfd inode. Activated processes should validate both
`LISTEN_PID` and `LISTEN_PIDFDID` to defeat PID-reuse races.

## Reload and readiness

### Presets, confext, and post-reload actions (258, 259, 260)

Initrd system services have a separate preset scope that defaults disabled.
Reloading a service reloads associated confexts; `ExecReloadPost=` adds a
post-reload hook, and `RefreshOnReload=` explicitly controls whether reload
refreshes extensions and credentials.

### Interface-bound sockets (260)

`BindNetworkInterface=` binds every socket made for a service to a named
interface, including a VRF.

### Live logs and shell readiness (258)

`systemctl start --verbose` and related verbs stream unit logs until the job
finishes. `systemd-notify --fork` starts a child, waits for its `READY=1`, and
exits while leaving the ready child running.
