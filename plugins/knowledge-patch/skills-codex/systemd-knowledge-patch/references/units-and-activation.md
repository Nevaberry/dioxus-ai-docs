# Units and Activation

## Dependencies, mounts, and directories

### Soft mount dependencies (256, 257)

Use unit `WantsMountsFor=` for nonfatal mount dependencies. In fstab,
`x-systemd.wants=` adds a soft `Wants=` dependency and complements
`x-systemd.requires=`.

### Credential-aware graceful mounts (258)

Mount units accept `SetCredential=`, `LoadCredential=`, `ImportCredential=`,
and related settings. Fstab `x-systemd.graceful-option=` includes a kernel
mount option only if supported, such as optional tmpfs `usrquota`.

## Socket activation and descriptor handoff

### Descriptors in lifecycle hooks (256)

Socket `PassFileDescriptorsToExec=yes` exposes listening descriptors through
`LISTEN_FDS` to `ExecStartPost=`, `ExecStopPre=`, and `ExecStopPost=`. For
`Accept=yes` UNIX sockets, `MaxConnectionsPerSource=` limits simultaneous
connections per peer UID.

### Socket metadata, MPTCP, and peer address (257)

`FileDescriptorName=` is honored for `Accept=yes` rather than replaced by
`connection`; `SocketUser=`/`SocketGroup=` apply to POSIX message queues.
`SocketProtocol=mptcp` enables MPTCP. Per-connection AF_UNIX stream services
receive peer address in `REMOTE_ADDR`.

### Race-free process and descriptor handoff (257)

Transient services accept arbitrary activation fds through D-Bus
`ExtraFileDescriptor=`. `sd_notify()` can assign the main process with a pidfd
or pidfd inode instead of a recycled numeric PID.

### PIDFD, rights, and deferred triggers (258)

AF_UNIX sockets use `PassPIDFD=` for `SO_PASSPIDFD` and
`AcceptFileDescriptors=` for `SO_PASSRIGHTS`. `DeferTrigger=` with
`DeferTriggerMaxSec=` uses lenient jobs and retries a transaction that would
otherwise stop an active unit.

### Verify activation PID identity (259)

The descriptor protocol adds `LISTEN_PIDFDID`, the pidfd inode corresponding
to `LISTEN_PID`. Validate both to avoid PID-recycling races.

### Interface-bound sockets (260)

`BindNetworkInterface=` binds every unit-created socket to a named interface,
including a VRF.

## Commands, timers, and lifecycle hooks

### Deferred timers (257)

For calendar timers, `DeferReactivation=yes` discards an expiration that
occurred while the activated service was active instead of starting
immediately after completion.

### Shell execution and stable spreading (258)

A leading `|` on an `Exec*=` directive invokes a shell. Without it, shell
syntax is not interpreted. Timer `RandomizedOffsetSec=` gives a randomized
but stable schedule offset rather than new jitter each activation.

### Scope expansion (258)

`systemd-run --scope` enables command-line environment expansion by default.

### Post-reload and root descriptors (259)

`ExecReloadPost=` runs after configured reload. Transient services can receive
root through D-Bus `RootDirectoryFileDescriptor` instead of a path.

### Transient root selection (259)

`systemd-run --root-directory=` selects a root tree;
`--same-root-dir`/`-R` reuses the caller root. Run0 also accepts `-R`.

### Refresh on reload (260)

`RefreshOnReload=` determines whether reload also refreshes extensions and
credentials.

### Marked jobs (260)

Use `systemctl enqueue-marked` instead of deprecated `systemctl --marked`.
Unit `Markers=` accepts `needs-start` and `needs-stop`.

### Stricter systemd-run combinations (258.10-261.2)

All covered point releases reject `--no-block` and `--ignore-failure` in
scope mode. JSON is rejected with stdio forwarding, trigger units, scopes, or
verbose logs; waiting is rejected for remain-after-exit services. Trigger
units honor `--no-block` and accept explicit trigger-unit names.

### Oneshot exit tracking (258.10-261.2)

All covered point releases reject `ExitType=cgroup` with `Type=oneshot`. Keep
`ExitType=main` or choose a compatible service type.

## Presets, startup, and manager state

### Initrd presets and confext reloads (258)

The third preset scope controls initrd system services and defaults disabled,
unlike host system presets. Service reload also reloads associated confexts.

### Live startup logs and readiness (258)

`systemctl start --verbose` and related verbs stream unit logs until the job
finishes. `systemd-notify --fork` launches a child, waits for its `READY=1`,
then exits while leaving the ready child running for shell-friendly handoff.

### Generator and soft reboot inputs (257)

Generators receive `SYSTEMD_SOFT_REBOOTS_COUNT`, the soft reboot count since
the current kernel boot.

### System-wide protection default (256)

Manager `ProtectSystem=` defaults enabled in initrd, so early units must not
assume writable `/usr`.
